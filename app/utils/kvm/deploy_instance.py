import json
from app.controllers.dao.techadmin_dao import SysUserDao
from app.extensions import logger, message_gw
from confluent_kafka import Consumer, KafkaError
from app.config import KafkaConfig
from app.controllers.dao.cloud_lab_dao import CloudLabImageDao, CloudLabUserTemplateInstanceDao
from app.controllers.service.CloudLab import CloudLab
from app.controllers.service.CloudLab.Instance import Instance
from app.controllers.dao.cloud_lab_redis_dao import RedisUtils
from app.utils.http_api.msg_template.template import CloudLabFailCreateEmail


def deploy_instance():
    kafka_config_consumer_hostimage = {
        'bootstrap.servers': KafkaConfig['host'],
        'group.id': KafkaConfig['topic_host_image_group'],
        'auto.offset.reset': 'earliest',
        'max.poll.interval.ms': 600000
    }
    consumer_hostimage = Consumer(kafka_config_consumer_hostimage)
    consumer_hostimage.subscribe([KafkaConfig['topic_host_image']])
    image_path = CloudLabImageDao.getImageFtpPath(image_key="kvm")
    
    while True:
        msg_host_image = consumer_hostimage.poll(1.0)
        if msg_host_image is not None:
            if msg_host_image.error():
                if msg_host_image.error().code() == KafkaError._PARTITION_EOF:
                    logger.error('Reached end of partition for topic')
                else:
                    logger.error('Error while consuming message from topic: {}'.format(msg_host_image.error()))
            else:
                msg_offset=msg_host_image.offset()
                producer_msg = json.loads(msg_host_image.value().decode(encoding="utf-8"))
                logger.debug("message offset:{0},message content:{1}".format(msg_offset,json.dumps(producer_msg,ensure_ascii=False)))
                instance_id = producer_msg.get("instance_id")
                instance_cpu,  instance_ram = producer_msg.get("cpu"), producer_msg.get("ram")
                instance_storage, request_host = producer_msg.get("storage"), producer_msg.get("request_host")
                logger.info(f"实例ID:{instance_id}, 收到生产者发送的消息")
                instance = CloudLabUserTemplateInstanceDao().getInstanceInfo(instance_id)
                template_data, create_time = instance.get("template_data"), instance.get("create_time")
                logger.info(f"实例ID:{instance_id}, 根据实例ID查询数据库中对应数据")
                server_host_object = CloudLab.assignServerHost(instance_cpu, instance_ram, instance_storage)
                if server_host_object:
                    logger.info(f"实例ID:{instance_id}, 分配裸金属服务器")
                    CloudLab.updateResources(server_host_object.id, instance_cpu, instance_ram, instance_storage)   
                    logger.info(f"实例ID:{instance_id}, 更新裸金属服务器资源") 
                    server_host_data = {"id": server_host_object.id, "host": server_host_object.ip_address, 
                                        "ssh_port": 22, "libvirt_port": 16509, "username": server_host_object.username,
                                        "password": server_host_object.password, "instance_cpu": instance_cpu,
                                        "instance_ram": instance_ram, "instance_storage": instance_storage}
                    logger.info(f"实例ID:{instance_id}, 将实例裸金属服务器信息存储到实例")
                    CloudLabUserTemplateInstanceDao.updateInstanceOnDeploy(instance_id=instance_id, 
                                                                        server_host_data=json.dumps(server_host_data))
                    logger.info(f"实例ID:{instance_id}, 开始创建实例")
                    Instance().CreateInstance(template_data, instance_id, create_time, request_host, instance_cpu, 
                                            instance_ram, image_path, server_host_data)
                else:
                    CloudLabUserTemplateInstanceDao.updateInstanceOnDeploy(instance_id=instance_id, status=3)
                    RedisUtils().updateProgressDataHostStatus(instance_id=instance_id, status=3)
                    template = CloudLabFailCreateEmail()
                    instance_name, user_id = instance.get("name"), instance.get("user_id")
                    template.update({"instance_id": instance_id, "instance_name": instance_name, "create_time": create_time, 
                                     "reason": "服务器资源不足"})
                    user = SysUserDao.querySysUserById(user_id)
                    if user and user.email:
                        message_gw.push(target=user.email, template=template)

