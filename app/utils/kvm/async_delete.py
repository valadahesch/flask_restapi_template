import redis
import requests
from app.extensions import logger
from app.controllers.dao.cloud_lab_dao import CloudLabUserTemplateInstanceDao
from app.utils.func_util import seconds_to_minutes_and_seconds, JwtTokenAuth
from app.config import RedisConfig, OtherConfig
from app.controllers.dao.cloud_lab_redis_dao import RedisUtils
from app.controllers.service.CloudLab import CloudLab


server_host = OtherConfig['api_server_host']


class RedisSubPub:
    def __init__(self, host_='127.0.0.1', port_=6379, db_=0, password_=None):
        self.conn = redis.StrictRedis(host=host_, port=port_, db=db_, password=password_)

    def publish(self, channel, message):
        self.conn.publish(channel, message)

    def subscribe(self, channels):
        pub = self.conn.pubsub()
        pub.psubscribe(channels)
        pub.parse_response()
        return pub

    def unsubscribe(self, channel):
        self.conn.pubsub().unsubscribe(channel)


def listen_instance():

    r = RedisSubPub(host_=RedisConfig["global"]["host"], port_=RedisConfig["global"]["port"], 
                    db_=0, password_=RedisConfig["global"]["password"])
    channels = ['__keyspace@0__:ttl:cloudlab:*:delete', '__keyspace@0__:ttl:cloudlab:*:alarm']  
    sub = r.subscribe(channels=channels)
    for message in sub.listen():
        if message['type'] == 'pmessage':
            channel = message['channel'].decode()
            event = message['data'].decode()
            expired_instance_id = channel.split(":")[-2]
            expired_key_type = channel.split(":")[-1]
            if event == "expired":
                logger.info(f"过期的实例ID: {expired_instance_id}, 过期事件类型{expired_key_type}")
                target_email = CloudLabUserTemplateInstanceDao.getEamilByInstanceId(instance_id=expired_instance_id)
                payload = {"instance_id": expired_instance_id, "target_email": target_email}
                token = JwtTokenAuth().generateToken(payload=payload)
                if target_email is None:
                    logger.info(f"实例疑似被手动删除")
                if expired_key_type == "delete" and target_email is not None:
                    delete_url = f"http://{server_host}/api/async_cloud_lab/instance/delete/{expired_instance_id}?token={token}"
                    resp = requests.get(url=delete_url)
                    logger.info(f"实例删除结果{expired_instance_id}:{resp.text}")
                if expired_key_type == "alarm" and target_email is not None:
                    instance_ttl = RedisUtils().getInstanceTTL(instance_id=expired_instance_id)
                    expire = seconds_to_minutes_and_seconds(instance_ttl)
                    instance_info = CloudLabUserTemplateInstanceDao().getInstanceInfo(instance_id=expired_instance_id)
                    delete_url = f"http://{server_host}/api/async_cloud_lab/instance/delete/{expired_instance_id}?token={token}"
                    continue_use_url = f"http://{server_host}/api/async_cloud_lab/instance/extend/{expired_instance_id}?token={token}"
                    button = f"""<a href="{delete_url}" target="_blank" rel="noopener"><button>确认删除</button></a>
                                <a href="{continue_use_url}" target="_blank" rel="noopener"><button>延长使用</button></a>"""
                    if 3800 > instance_ttl and instance_ttl > 3000:
                        logger.info("实例剩余1小时发送第一次告警邮件, 新建一个30min的alarm的key")
                        RedisUtils().addNewInstanceAlarmKey(instance_id=expired_instance_id, ttl=1800)
                        CloudLab.sendInstanceWarnEmail(instance_id=expired_instance_id, instance_name=instance_info.get("name"),
                                  target=target_email,  create_time=instance_info.get("create_time"), expire=expire, button=button)
                        
                    if 2000 > instance_ttl and instance_ttl > 1500:
                        logger.info("实例剩余0.5小时发送第一次告警邮件, 新建一个25min的alarm的key")
                        RedisUtils().addNewInstanceAlarmKey(instance_id=expired_instance_id, ttl=1500)
                        CloudLab.sendInstanceWarnEmail(instance_id=expired_instance_id, instance_name=instance_info.get("name"),
                                  target=target_email,  create_time=instance_info.get("create_time"), expire=expire, button=button)
                    if 360 > instance_ttl:
                        logger.info("实例剩余5分钟发送第三次告警邮件")
                        CloudLab.sendInstanceWarnEmail(instance_id=expired_instance_id, instance_name=instance_info.get("name"),
                                  target=target_email,  create_time=instance_info.get("create_time"), expire=expire, button=button)
                        
