import jwt
import datetime
from flask import Blueprint, request
from flask_restful import Resource
from app.utils.api_util import Api
from app.utils.func_util import seconds_to_minutes_and_seconds
from app.controllers.dao.cloud_lab_dao import CloudLabUserTemplateInstanceDao
from app.controllers.dao.cloud_lab_dao import CloudLabUserTemplateInstanceDao, RedisUtils
from app.controllers.service.CloudLab import CloudLab
from app.controllers.service.CloudLab.Instance import Instance


async_cloudlab_app = Blueprint('async_cloudlab', __name__, url_prefix='/api/async_cloud_lab')
async_cloud_lab_api = Api(async_cloudlab_app)


class TokenAuth:
    def __init__(self, secret_key: str = "hillstone_dic_cloudlab"):
        self.secret_key = secret_key

    def generateToken(self, payload):
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        token = jwt.encode({"exp": expiration_time, **payload}, self.secret_key, algorithm="HS256")
        return token

    def verifyToken(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            if "exp" in payload and datetime.datetime.utcnow() > datetime.datetime.fromtimestamp(payload["exp"]):
                return {"error": "Token has expired"}
            return payload
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False


@async_cloud_lab_api.resource('/instance/delete/<string:instance_id>')
class DeleteInstance(Resource):
    def get(self, instance_id):
        """
        异步删除实例
        """
        token = request.args.get('token')
        payload = TokenAuth().verifyToken(token=token)

        if payload:
            target = payload.get("target_email")
            sql = CloudLabUserTemplateInstanceDao()
            instance = sql.getInstanceInfo(instance_id=instance_id)
            if instance.get("status") == 7:
                return {"code": 0, "data": {}, "message": "Instance has been deleted and no further action is required !"}
            else:
                Instance().requestdeleteInstance(instance_id)
                auto_release_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sql.deleteInstanceById(instance_id=instance_id, auto_release_time=auto_release_time)
                CloudLab.sendInstanceDeleteEmail(target, instance)
                return {"code": 0, "data": {}, "message": "Instance deleted successfully !"}
        else:
            return {"code": -1, "data": {}, "message": "Instance deletion failed, token is invalid !"}


@async_cloud_lab_api.resource('/instance/extend/<string:instance_id>')
class ExtendInstance(Resource):
    def get(self, instance_id):
        """
        延长实例使用时间,并发送邮件告知实例已经延长使用时间
        """
        token = request.args.get('token')
        payload = TokenAuth().verifyToken(token=token)
        try:
            if payload:
                sql, redis_util = CloudLabUserTemplateInstanceDao(), RedisUtils()
                instance = sql.getInstanceInfo(instance_id=instance_id)
                expire = redis_util.getInstanceTTL(instance_id=instance_id)
                if instance.get("status") == 7 or expire <= 0:
                    redis_util.closeRedisConnect()
                    return {"code": 0, "data": {}, "message": "Instance has been deleted and no further action is required !"}
                elif expire > 3800:
                    redis_util.closeRedisConnect()
                    return {"code": 0, "data": {}, "message": "The instance has been renewed or the remaining time exceeds 1 hour and no operation is required !"}
                else:
                    target = payload.get("target_email")
                    redis_util.addInstanceTTL(instance_id=instance_id)
                    expire = redis_util.getInstanceTTL(instance_id=instance_id)
                    expire_minutes = seconds_to_minutes_and_seconds(expire)
                    CloudLab.sendInstanceExtendEmail(target, instance, expire_minutes)
                    redis_util.closeRedisConnect()
                    return {"code": 0, "data": {}, "message": "The instance has been extended for 2 hour !"}
                
            else:
                return {"code": -1, "data": {}, "message": "Failed to extend instance usage time !"}
        except Exception as error:
            return {"code": -1, "data": {}, "message": f"Failed to extend instance usage time ! reason:{error}"}
