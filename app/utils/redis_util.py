import redis
import json

from datetime import datetime


class RedisClient(redis.Redis):
    online_expire = 3600

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            host, password, port = self.getConfig(app)
            super().__init__(host=host, password=password, port=port, db=0, decode_responses=True)

    def init_app(self, app):
        host, password, port = self.getConfig(app)
        super().__init__(host=host, password=password, port=port, db=0, decode_responses=True)

    @staticmethod
    def getConfig(flask_app):
        if flask_app.config.get('SERVER_REDIS_HOST'):
            host = flask_app.config['SERVER_REDIS_HOST']
            password = flask_app.config['SERVER_REDIS_PASSWORD']
            port = flask_app.config['SERVER_REDIS_PORT']
        else:
            host = flask_app.config["SESSION_REDIS_HOST"]
            password = flask_app.config['SESSION_REDIS_PASSWORD']
            port = flask_app.config['SESSION_REDIS_PORT']
        return host, password, port

    def updateOnlineUser(self, user_id: str, value: dict, expire=3600):
        """
        设置会话的登陆时间
        :param user_id: 用户IDi
        :param value: 用户SSO登陆信息
        :param expire: 会话超时时间
        :return:
        """
        self.online_expire = expire
        key = f"techadmin:online:userid:{user_id}"
        value["refresh_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.set(key, json.dumps(value, ensure_ascii=False))
        self.expire(key, expire)

    def updateSimulationOnlineUser(self, user_id: str, value: dict, expire=3600):
        """
        设置会话的登陆时间
        :param user_id: 用户IDi
        :param value: 用户SSO登陆信息
        :param expire: 会话超时时间
        :return:
        """
        self.online_expire = expire
        key = f"techadmin:online:simulation:userid:{user_id}"
        value["refresh_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.set(key, json.dumps(value, ensure_ascii=False))
        self.expire(key, expire)

    def updateWxOnlineUser(self, user_id: str, value: dict, expire=3600):
        """
        设置会话的登陆时间
        :param user_id: 用户IDi
        :param value: 用户SSO登陆信息
        :param expire: 会话超时时间
        :return:
        """
        self.online_expire = expire
        key = f"techadmin:online:qywx:userid:{user_id}"
        value["refresh_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.set(key, json.dumps(value, ensure_ascii=False))
        self.expire(key, expire)

    def updateUserRole(self, user_id, role):
        key = f"techadmin:online:userid:{user_id}"
        user = self.getValueToJson(key)
        if not user:
            return

        user['roles'] = role
        self.updateOnlineUser(user_id, user, self.online_expire)

    def getValueToJson(self, key):
        value = self.get(key)
        if value:
            return json.loads(value)
        return None


