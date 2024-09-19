import json
import os
from app.models import db
from sqlalchemy import desc
from datetime import datetime
from app.utils.api_util import AppException
from app.extensions import logger
from app.utils.func_util import getRandomString10
from app.controllers.dao.cloud_lab_redis_dao import RedisUtils
from app.models.cloud_lab import CloudLabTemplate, CloudLabUserTemplateInstance, CloudLabImage, \
                                CloudLabNode, CloudLabServerHost
from app.models.techadmin import SysUser
from app.extensions import DBSession   

class CloudLabTemplateDao:

    @staticmethod
    def addTemplate(name: str, description: str, picture: str, template_data: str, user_id: str, template_data_view: str) -> str:
        try:
            lab_session = DBSession()
            user = lab_session.query(SysUser).filter(SysUser.id ==user_id).first()
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            template = CloudLabTemplate(
                id=getRandomString10(),
                name=name,
                description=description,
                enable = 1,
                picture=picture,
                template_data=template_data,
                create_by=user_id,
                create_time=create_time,
                create_by_name=user.display_name,
                update_by=user_id,
                update_time=create_time,
                update_by_name=user.display_name,
                key=description,
                template_data_view=template_data_view,
            )
            lab_session.add(template)
            lab_session.commit()
            return template.id
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def getTemplateList() -> dict:
        try:
            lab_session = DBSession()
            templates = lab_session.query(CloudLabTemplate).filter(CloudLabTemplate.enable == 1).all()
            result = []
            for template in templates:
                template_dict = {
                    "id": template.id,
                    "name": template.name,
                    "key": template.key,
                    "description": template.description,
                    "picture": template.picture,
                    "create_by": template.create_by,
                    "create_time": template.create_time,
                    "create_by_name": template.create_by_name,
                    "update_by": template.update_by,
                    "update_time": template.update_time,
                    "update_by_name": template.update_by_name
                }
                result.append(template_dict)
            return result
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def getTemplateDataView(template_id: str = "") -> dict:
        try:
            lab_session = DBSession()
            template = lab_session.query(CloudLabTemplate).filter(CloudLabTemplate.id == template_id).first()
            template_data_view = json.loads(template.template_data_view).get("cells")
            template_data = {
                "id": template.id,
                "name": template.name,
                "key": template.key,
                "description": template.description,
                "picture": template.picture,
                "create_by": template.create_by,
                "create_time": template.create_time,
                "create_by_name": template.create_by_name,
                "update_by": template.update_by,
                "update_time": template.update_time,
                "update_by_name": template.update_by_name,
                "cells": template_data_view
            }
            return template_data
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def getTemplateData(template_id: str = "") -> dict:
        try:
            lab_session = DBSession()
            template = lab_session.query(CloudLabTemplate).filter(CloudLabTemplate.id == template_id).first()
            template_data = json.loads(template.template_data)
            template_data_view = json.loads(template.template_data_view)
            return template_data, template_data_view
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

class CloudLabUserTemplateInstanceDao:

    def __init__(self):
        pass

    @staticmethod
    def getAllInstanceId() -> list:
        try:
            lab_session = DBSession()
            all_ids = lab_session.query(CloudLabUserTemplateInstance.id).all()
            id_list = [result.id for result in all_ids]
            return id_list
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def getEamilByInstanceId(instance_id: str) -> str:
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).first()
            user_id = instance.user_id
            user = lab_session.query(SysUser).filter(SysUser.id == user_id).first()
            email = user.email
            return email
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def getInstanceStatus(instance_id: str):
        status=""
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).one_or_none()
            status = instance.status
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
            return status


    def getInstanceInfoById(self, instance_id: str):
        instance_info = None
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).one_or_none()
            instance_info = {
                "template_data": json.loads(instance.template_data),
                "create_time": str(instance.create_time),
                "name": instance.name
            }     
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
            return instance_info

    @staticmethod
    def getInstanceRunningData(instance_id: str = "") -> dict:
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).first()
            return json.loads(instance.template_data)
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def getInstanceStatusCount() -> int:
        try:
            lab_session = DBSession()
            starting_count = lab_session.query(CloudLabUserTemplateInstance).filter_by(status=1).count()
            running_count = lab_session.query(CloudLabUserTemplateInstance).filter_by(status=2).count()
            shutdown_count = lab_session.query(CloudLabUserTemplateInstance).filter_by(status=9).count()
            return starting_count, running_count, shutdown_count
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
    
    @staticmethod
    def getInstanceServerHostData(instance_id: str):
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).first()
            return json.loads(instance.server_host_data)
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def getInstanceHostData(instance_id: str):
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).first()
            login_data = {
                "ssh_port": instance.ssh_port,
                "libvirt_port": instance.mgt_port
            }
            return login_data
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def getCreatingInstance(create_time: str) -> int:
        try:
            lab_session = DBSession()
            create_time = datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
            query = lab_session.query(CloudLabUserTemplateInstance).filter(
                CloudLabUserTemplateInstance.actual_time.is_(None)
            ).all()
            return len(query)
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
            return 0
        finally:
            lab_session.close()

    @staticmethod
    def getInstanceByName(instance_name: str, user_id: str)-> bool:
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.name == instance_name,
                                                                              CloudLabUserTemplateInstance.user_id == user_id,
                                                                              CloudLabUserTemplateInstance.status != 7).first()
            if instance:
                return True
            else:
                return False
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
            return 0
        finally:
            lab_session.close()      

    @staticmethod
    def getInstanceNodeName(instance_id: str, node_id: str) -> tuple:
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).first()
            template_data = json.loads(instance.template_data)
            instance_name = instance.name
            nodes = template_data.get("nodes")
            for node in nodes:
                if node.get("id") == node_id:
                    node_name = node.get("name")
            return instance_name, node_name
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
            return instance_id, node_id
        finally:
            lab_session.close()     
    
    @staticmethod
    def getInstanceList(user_id) -> dict:
        try:
            lab_session = DBSession()
            instances = (
                lab_session.query(CloudLabUserTemplateInstance, CloudLabTemplate.name)
                .outerjoin(CloudLabTemplate, CloudLabUserTemplateInstance.template_id == CloudLabTemplate.id)
                .filter(CloudLabUserTemplateInstance.user_id == user_id)
                .order_by(desc(CloudLabUserTemplateInstance.create_time))
                .all()
            )
            result = []
            rds=RedisUtils()
            for instance, template_name in instances:            
                expire = rds.getInstanceTTL(instance_id=instance.id)
                status = instance.status
                if expire <= 0:
                    status = 7
                template_dict = {
                    "id": instance.id,
                    "template_id": instance.template_id,
                    "template_name": template_name,
                    "create_time": str(instance.create_time),
                    "status": status,
                    "name": instance.name,
                    "expire": expire
                }
                result.append(template_dict)
            rds.closeRedisConnect()
            return {"list": result}
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def query_instances(user_id: str, name: str = None, status: int = None, page: int=1, size: int=1000):
        try:
            page = page if page else 1
            size = size if size else 1000
            lab_session = DBSession()
            base_query = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.user_id == user_id)
            if name:
                base_query = base_query.filter(CloudLabUserTemplateInstance.name.ilike(f'%{name}%'))
            if status:
                if type(status) == int:
                    base_query = base_query.filter(CloudLabUserTemplateInstance.status == status)
                if type(status) == list:
                    base_query = base_query.filter(CloudLabUserTemplateInstance.status.in_(status))
            total_count = base_query.count()
            offset = (page - 1) * size
            query = base_query.order_by(CloudLabUserTemplateInstance.create_time.desc()).offset(offset).limit(size)
            instances = query.all()
            result, rds, template_name = [], RedisUtils(), None
            for instance in instances:
                expire = rds.getInstanceTTL(instance_id=instance.id)
                status = instance.status
                if expire <= 0:
                    status = 7
                if instance.template_id:
                    template_name = lab_session.query(CloudLabTemplate).filter(CloudLabTemplate.id == instance.template_id).first().name
                instance_dict = {
                    "id": instance.id,
                    "template_id": instance.template_id,
                    "template_name": template_name,
                    "create_time": str(instance.create_time),
                    "status": status,
                    "name": instance.name,
                    "expire": expire,
                    "status": instance.status,
                }
                result.append(instance_dict)

            return {"list": result, "total": total_count}
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
    
    @staticmethod
    def addInstanceInfo(user_id: str = "", template_id: str = "", create_time: str = "", update_time: str = "",
                        status: int = "", instance_data: str = "", name: str = "", instance_id: str = "",
                        nodes_login: str = "", template_data: str = "", estimated_time: str = "",
                        exclusive_time: str = "") -> str:
        try:
            lab_session = DBSession()
            instance_info = CloudLabUserTemplateInstance(
                id=instance_id,
                user_id=user_id,
                template_id=template_id,
                create_time=create_time,
                update_time=update_time,
                status=status,
                instance_data=instance_data,
                name=name,
                nodes_login=nodes_login,
                template_data=template_data,
                exclusive_time=exclusive_time,
                estimated_time=estimated_time
            )
            lab_session.add(instance_info)
            lab_session.commit()
            return instance_id
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def queryInstanceByStatus(user_id: str = "", template_id: str = "") -> dict:
        try:
            lab_session = DBSession()
            instances = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.template_id == template_id,
                                                                CloudLabUserTemplateInstance.user_id == user_id,
                                                                CloudLabUserTemplateInstance.status == 1).all()
            result = []
            for instance in instances:
                instance_dict = {
                    "id": instance.id,
                    "template_id": instance.template_id,
                    "template_name": instance.name,
                    "create_time": str(instance.create_time),
                    "status": instance.status,
                    "name": instance.name
                }
                result.append(instance_dict)
            return result
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def queryAllInstanceByStatus() -> int:
        try:
            lab_session = DBSession()
            instances = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.status == 1).all()
            count = 0
            for instance in instances:
                count = count + 1
            return count
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def updateInstanceOnDeploy(instance_id: str = "", status: int = 0, instance_data: str = "", mgt_ip: str = "",
                               mgt_port: str = "", nodes_login: str = "", iptables_rule: str = None,
                               update_time: str = "", ssh_port: str = "", estimated_time: str = "",
                               exclusive_time: str = "", actual_time: str = "", server_host_data: str = "",
                               create_host_time: str = "") -> None:
        
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).one_or_none()
            if update_time != "":
                instance.update_time = update_time
            if status != 0:
                instance.status = status
            if instance_data != "":
                instance.instance_data = instance_data
            if mgt_port != "":
                instance.mgt_port = mgt_port
            if ssh_port != "":
                instance.ssh_port = ssh_port
            if mgt_ip != "":
                instance.mgt_ip = mgt_ip
            if nodes_login != "":
                instance.nodes_login = nodes_login
            if server_host_data != "":
                instance.server_host_data = server_host_data
            if estimated_time != "":
                instance.estimated_time = estimated_time
            if exclusive_time != "":
                instance.exclusive_time = exclusive_time
            if actual_time != "":
                instance.actual_time = actual_time
            if create_host_time != "":
                instance.create_host_time = create_host_time
            if iptables_rule is not None:
                if instance.iptables_rule is None:
                    instance.iptables_rule = iptables_rule
                else:
                    instance.iptables_rule = instance.iptables_rule + ";" + iptables_rule
            lab_session.commit()
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def updateLoginAndIptablesRule(instance_id: str = "", nodes_login: str = "", iptables_rule: str = "") -> None:
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).first()
            instance.nodes_login = nodes_login
            if iptables_rule is not None:
                instance.iptables_rule = instance.iptables_rule + ";" + iptables_rule
            lab_session.commit()
            return None
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def getIptablesRuleByInstanceId(instance_id: str = "") -> list:
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).first()
            if instance.iptables_rule:
                iptables_rule_list = instance.iptables_rule.split(';')
                return iptables_rule_list
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    @staticmethod
    def deleteInstanceById(instance_id: str = "", manual_release_time: str = "", auto_release_time: str = "") -> set:
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).first()
            if instance.iptables_rule:
                iptables_rule_list = instance.iptables_rule.split(';')
            else: 
                iptables_rule_list = []
            if instance:
                if manual_release_time != "":
                    instance.manual_release_time = manual_release_time
                if auto_release_time != "":
                    instance.auto_release_time = auto_release_time
                instance.status = 7
                lab_session.commit()
            else:
                raise Exception("记录不存在或已被删除")
            return json.loads(instance.server_host_data), iptables_rule_list
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()

    def getInstanceInfo(self, instance_id: str = "") -> dict:
        instance_={}
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).first()
            if instance.server_host_data:
                server_host_data = json.loads(instance.server_host_data)
            else:
                server_host_data = instance.server_host_data
            instance_data = json.loads(instance.instance_data)
            instance_ = {
                "id": instance.id,
                "user_id": instance.user_id,
                "template_id": instance.template_id,
                "create_time": str(instance.create_time),
                "update_time": instance.update_time,
                "status": instance.status,
                "instance_data": instance_data,
                "name": instance.name,
                "mgt_ip": instance.mgt_ip,
                "mgt_port": instance.mgt_port,
                "nodes_login": instance.nodes_login,
                "iptables_rule": instance.iptables_rule,
                "ssh_port": instance.ssh_port,
                "server_host_data": server_host_data,
                "template_data": json.loads(instance.template_data)
            }
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
            return instance_

    @staticmethod
    def getInstanceInfoView(instance_id: str = "") -> dict:
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).first()
            template_name = instance.template_id
            if instance.template_id:
                template_object= CloudLabTemplate.query.filter(CloudLabTemplate.id == instance.template_id).first()
                if template_object:
                    template_name = template_object.name
            instance_data =  json.loads(instance.instance_data)
            instance_data["id"] = instance.id
            instance_data["create_time"] = str(instance.create_time)
            instance_data["template_id"] = instance.template_id
            instance_data["template_name"] = template_name
            instance_data["status"] = instance.status
            return instance_data, instance.user_id
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
    
    @staticmethod
    def getViewData(instance_id: str = "") -> dict:
        try:
            lab_session = DBSession()
            instance = lab_session.query(CloudLabUserTemplateInstance).filter(CloudLabUserTemplateInstance.id == instance_id).first()
            return json.loads(instance.instance_data), json.loads(instance.template_data)
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()


class CloudLabImageDao:

    @staticmethod
    def getNotCheckIpImages() -> list:
        try:
            not_check_ip_images = []
            lab_session = DBSession()
            images = lab_session.query(CloudLabImage).all()
            for image in images:
                if image.boot_check_ip is False:
                    not_check_ip_images.append(image.key)
        except Exception as e:
            lab_session.rollback()
            not_check_ip_images = []
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
            return not_check_ip_images

    @staticmethod
    def getImageLoginInfo(image_key: str) -> set:
        username, password = "", ""
        try:
            lab_session = DBSession()
            image_object = lab_session.query(CloudLabImage).filter(CloudLabImage.key == image_key).first()
            login_data = json.loads(image_object.console_login_data)
            username = login_data.get("console").get("username")
            password = login_data.get("console").get("password")
        except Exception as e:
            lab_session.rollback()
            username, password = "root", "hillstone"
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
            return username, password

    @staticmethod
    def getImageLoginData(image_id: str):
        redis_object = RedisUtils()
        login_data={}
        try:
            lab_session = DBSession()
            login_data = redis_object.getImageLoginData(image_id)
            if login_data is None:
                image = lab_session.query(CloudLabImage).filter(CloudLabImage.key == image_id).first()
                console_login_data = json.loads(image.console_login_data)
                if image.ip_login_data:
                    ip_login_data = json.loads(image.ip_login_data)
                else:
                    ip_login_data = {}
                login_data = {**console_login_data, **ip_login_data}
                redis_object.setImageLoginData(image_id=image_id, data=login_data)
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            redis_object.closeRedisConnect()
            lab_session.close()
        return login_data

    
    @staticmethod
    def getImageConsoleLoginData(image_id: str):
        redis_object = RedisUtils()
        login_data={}
        try:
            lab_session = DBSession()
            login_data = redis_object.getImageConsoleLoginData(image_id)
            if login_data is None:
                image = lab_session.query(CloudLabImage).filter(CloudLabImage.key == image_id).first()
                login_data = json.loads(image.console_login_data)
                redis_object.setImageConsoleLoginData(image_id=image_id, data=login_data)
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
            redis_object.closeRedisConnect()
        return login_data

    @staticmethod
    def getImageActionButton(image_key: str):
        action_button=[]
        try:
            lab_session = DBSession()
            redis_object = RedisUtils()
            action_button = redis_object.getImageActionButton(image_key)
            if action_button is None:
                image_object = lab_session.query(CloudLabImage).filter(CloudLabImage.key == image_key).first()
                action_button = image_object.action_button
                if action_button:
                    action_button =  json.loads(action_button)
                    redis_object.setImageActionButton(image_key, action_button)
                else:
                    redis_object.setImageActionButton(image_key, [])
                action_button = redis_object.getImageActionButton(image_key)
        except Exception as e:
            lab_session.rollback()
            logger.error(e)
        finally:
            lab_session.close()            
            redis_object.closeRedisConnect()
            return action_button

    @staticmethod
    def getImageFtpPath(image_key: str):
        ftp_path=""
        try:
            lab_session = DBSession()
            images_object = lab_session.query(CloudLabImage).filter(CloudLabImage.key == image_key).first()
            ftp_path=images_object.path
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
            return ftp_path
    
    @staticmethod
    def getImageSize(image_key: str):
        try:
            lab_session = DBSession()
            image = lab_session.query(CloudLabImage).filter(CloudLabImage.key == image_key).first()
            return image.size 
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
    
    @staticmethod
    def getImageInitializationOperation(image_key: str) -> bool:
        try:
            lab_session = DBSession()
            image = lab_session.query(CloudLabImage).filter(CloudLabImage.key == image_key).first()
            init_cmd = image.init_cmd
            change_password = image.change_password
            initial_configuration = {}
            if init_cmd:
                initial_configuration["init_cmd"] = json.loads(init_cmd)
            if change_password:
                initial_configuration["change_password"] = change_password
            return initial_configuration
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()


class CloudLabNodeDao:
    
    @staticmethod
    def getNodeCPUAndRam(node_key: str):
        abspath = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(abspath, '../../../config/node_mate.json'), 'r', encoding="utf-8") as f:
            node_mate = json.load(f)
        node_mate = node_mate.get("data")
        cpu, memory = 0, 0
        try:
            lab_session = DBSession()
            for node in node_mate:
                if node.get("key") == node_key:
                    cpu = node.get("cpu")
                    memory = node.get("memory")
            if cpu is None or memory is None:
                node = lab_session.query(CloudLabNode).filter(CloudLabNode.node_key == node_key).first()
                cpu = node.cpu
                memory = node.memory
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
            return cpu, memory
    
class CloudLabServerHostDao:

    @staticmethod
    def updateServerHost(server_host_id: str, cpu_available: int, memory_available: int, storage_available: int) -> object:
        result = False
        try:
            lab_session = DBSession()
            server_host = lab_session.query(CloudLabServerHost).filter(CloudLabServerHost.id == server_host_id).first()
            server_host.cpu_available = server_host.cpu_available - cpu_available
            server_host.memory_available = server_host.memory_available - memory_available
            server_host.storage_available = server_host.storage_available - storage_available
            lab_session.commit()
            result = True
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
            return result


    @staticmethod
    def getServerHostInfo() -> list:
        server_hosts_list = []
        try:
            lab_session = DBSession()
            server_hosts = lab_session.query(CloudLabServerHost).filter(CloudLabServerHost.is_active == 1).all()
            for server_host in server_hosts:
                data_dict = {
                    'id': server_host.id,
                    'name': server_host.name,
                    'ip_address': server_host.ip_address,
                    'username': server_host.user_name,
                    'password': server_host.password,
                    'is_active': server_host.is_active,
                    'cpu': server_host.cpu,
                    'memory': server_host.memory,
                    'storage': server_host.storage,
                    'cpu_available': server_host.cpu_available,
                    'memory_available': server_host.memory_available,
                    'storage_available': server_host.storage_available
                }
                server_hosts_list.append(data_dict)
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
            return server_hosts_list


    @staticmethod
    def updateServerHostAvailableResource(server_host_id: str, cpu: int, ram: int, storage: int):
        try:
            lab_session = DBSession()
            server_host = lab_session.query(CloudLabServerHost).filter(CloudLabServerHost.id == server_host_id).first()
            server_host.cpu_available = server_host.cpu_available + cpu
            server_host.memory_available = server_host.memory_available + ram
            server_host.storage_available = server_host.storage_available + storage
            lab_session.commit()
            return True
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
    
    @staticmethod
    def getServerHostResource():
        try:
            lab_session = DBSession()
            server_hosts = lab_session.query(CloudLabServerHost).filter(CloudLabServerHost.is_active == 1).all()
            cpu, memory, storage = 0, 0, 0
            cpu_available, memory_available, storage_available = 0, 0, 0
            for server_host in server_hosts:
                cpu = cpu + server_host.cpu
                memory = memory + server_host.memory
                storage = storage + server_host.storage
                cpu_available = cpu_available + server_host.cpu_available
                memory_available = memory_available + server_host.memory_available
                storage_available = storage_available + server_host.storage_available
            used_memory = memory - memory_available
            used_cpu_count = cpu - cpu_available
            memory_percent = used_memory/memory
            cpu_percent = used_cpu_count/cpu
            return memory, cpu, used_memory, used_cpu_count, memory_percent, cpu_percent
        except Exception as e:
            lab_session.rollback()
            logger.error('Exception Type:{0},Message:{1}'.format(type(e), e))
        finally:
            lab_session.close()
        