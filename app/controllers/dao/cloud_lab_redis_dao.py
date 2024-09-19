import redis
import json
from app.config import RedisConfig
from app.extensions import logger
from datetime import datetime


class RedisUtils:

    def __init__(self, host: str = RedisConfig["global"]["host"], 
                 password: str = RedisConfig["global"]["password"], port: int = RedisConfig["global"]["port"]):
        self.host = host
        self.password = password
        self.port = port
        self.redis_client = redis.StrictRedis(host=self.host, password=self.password, port=self.port)

    def setShutdownInstanceKey(self, instance_id: str):
        key_delete = f"ttl:cloudlab:{instance_id}:delete"
        key_alarm = f"ttl:cloudlab:{instance_id}:alarm"
        self.redis_client.setex(name=key_delete, time=129600, value="")
        self.redis_client.setex(name=key_alarm, time=126000, value="")
        return True

    def setPowerOnInstanceKey(self, instance_id: str):
        key_delete = f"ttl:cloudlab:{instance_id}:delete"
        key_alarm = f"ttl:cloudlab:{instance_id}:alarm"
        self.redis_client.setex(name=key_delete, time=28800, value="")
        self.redis_client.setex(name=key_alarm, time=25200, value="")
        return True

    def updateNodeStatus(self, instance_id: str, network_id: str) -> str:
        try:
            redis_key = f"techadmin:cloudlab:progress:{instance_id}:{network_id}*"
            keys = self.redis_client.keys(redis_key)
            node_key = keys[0].decode(encoding="utf-8")[-20:]
            node_proggress = self.getNodeProgress(instance_id, node_key)
            node_proggress["status"] = 2 
            self.setNodeProgress(instance_id, node_key, node_proggress)
        except:
            node_key = network_id
            node_proggress = {"id": node_key, "name": node_key, "status": 2}
            self.setNodeProgress(instance_id, node_key, node_proggress)
        return True

    def getImageLoginData(self, image_id: str) -> dict or None:
        redis_key = f"techadmin:cloudlab:image:login:{image_id}"
        if self.redis_client.exists(redis_key):
            value = self.redis_client.get(name=redis_key).decode(encoding="utf-8")
            return json.loads(value)
        else:
            return None
        
    def getImageConsoleLoginData(self, image_id: str) -> dict or None:
        redis_key = f"techadmin:cloudlab:image:console:login:{image_id}"
        if self.redis_client.exists(redis_key):
            value = self.redis_client.get(name=redis_key).decode(encoding="utf-8")
            return json.loads(value)
        else:
            return None
        
    def setImageLoginData(self, image_id: str, data: dict) -> bool:
        redis_key = f"techadmin:cloudlab:image:login:{image_id}"
        expiration_time_seconds = 3600
        self.redis_client.set(redis_key, json.dumps(data))
        self.redis_client.expire(redis_key, expiration_time_seconds)
        return True

    def setImageConsoleLoginData(self, image_id: str, data: dict) -> bool:
        redis_key = f"techadmin:cloudlab:image:console:login:{image_id}"
        expiration_time_seconds = 3600
        self.redis_client.set(redis_key, json.dumps(data))
        self.redis_client.expire(redis_key, expiration_time_seconds)
        return True

    def getHostFreeStartPort(self, host, start_port) -> int or bool:
        redis_key = f"techadmin:cloudlab:instance_kvm:host:port:{host}"
        if self.redis_client.exists(redis_key):
            port = int(self.redis_client.get(name=redis_key).decode(encoding="utf-8"))
        else:
            self.redis_client.set(name=redis_key, value=str(start_port))
            port = start_port
        return port
    
    def setHostFreeStartPort(self, host, start_port) -> int or bool:
        redis_key = f"techadmin:cloudlab:instance_kvm:host:port:{host}"
        self.redis_client.set(name=redis_key, value=str(start_port))
        return True

    def verifyRedisKey(self, key: str) -> bool:
        redis_key = f"techadmin:cloudlab:host:image:{key}"
        key_exists = self.redis_client.exists(redis_key)
        if key_exists:
            return True
        else:
            return False
        
    def getImageActionButton(self, image_key: str) -> dict:
        try:
            redis_key = f"techadmin:cloudlab:image:action:button:{image_key}"
            if self.redis_client.exists(redis_key):
                value = self.redis_client.get(name=redis_key).decode(encoding="utf-8")
                return json.loads(value)
        except:
            return []
    
    def setImageActionButton(self, image_key: str, action_button: dict) -> bool:
        redis_key = f"techadmin:cloudlab:image:action:button:{image_key}"
        expiration_time_seconds = 3600
        self.redis_client.set(redis_key, json.dumps(action_button))
        self.redis_client.expire(redis_key, expiration_time_seconds)
        return True
        
    def setNodeProgress(self, instance_id: str, node_id: str, progress_data: dict):
        redis_key = f"techadmin:cloudlab:progress:{instance_id}:{node_id}"
        self.redis_client.set(name=redis_key, value=json.dumps(progress_data))
        return True
    
    def updateNodeProgress(self, instance_id: str, node_id: str, progress_data: dict):
        redis_key = f"techadmin:cloudlab:progress:{instance_id}:{node_id}"
        self.redis_client.set(name=redis_key, value=json.dumps(progress_data))
        return True
    
    
    def deleteNodeProgressByInstanceId(self, instance_id: str):
        key = f"techadmin:cloudlab:progress:{instance_id}:*"
        nodes_keys = self.redis_client.keys(key)
        for node_key in nodes_keys:
            node_key_str = node_key.decode('utf-8')
            if self.redis_client.exists(node_key_str):
                self.redis_client.delete(node_key_str)
        return True
    
    def getNodeProgressDataByInstanceId(self, instance_id: str) -> list:
        key = f"techadmin:cloudlab:progress:{instance_id}:*"
        nodes_keys = self.redis_client.keys(key)
        nodes_progress_data = []
        for node_key in nodes_keys:
            node_key_str = node_key.decode('utf-8')
            value = self.redis_client.get(name=node_key_str).decode(encoding="utf-8")
            nodes_progress_data.append(json.loads(value))
        return nodes_progress_data
    
    def getNodeProgress(self, instance_id: str, node_id: str) -> dict:
        key = f"techadmin:cloudlab:progress:{instance_id}:{node_id}"
        if self.redis_client.exists(key):
            value = self.redis_client.get(name=key).decode(encoding="utf-8")
            return json.loads(value)
        else:
            logger.error(f"不存在实例{instance_id},节点{node_id}的redis key")

    def setInstanceTTL(self, instance_id: str):
        key_delete = f"ttl:cloudlab:{instance_id}:delete"
        key_alarm = f"ttl:cloudlab:{instance_id}:alarm"
        self.redis_client.setex(name=key_delete, time=28800, value="")
        self.redis_client.setex(name=key_alarm, time=25200, value="")
        return True

    def getInstanceTTL(self, instance_id: str):
        key = f"ttl:cloudlab:{instance_id}:delete"
        ttl = self.redis_client.ttl(key)
        ttl = ttl -2 
        if ttl < 0:
            ttl = 0
        return ttl

    def addInstanceTTL(self, instance_id: str):
        key_delete = f"ttl:cloudlab:{instance_id}:delete"
        key_alarm = f"ttl:cloudlab:{instance_id}:alarm"
        key_delete_ttl = self.redis_client.ttl(key_delete)
        key_alarm_ttl = self.redis_client.ttl(key_alarm)
        self.redis_client.expire(key_delete, 7200 + key_delete_ttl)
        self.redis_client.expire(key_alarm, 7200 + key_alarm_ttl)
        return True
    
    def addNewInstanceAlarmKey(self, instance_id: str, ttl: int):
        key_alarm = f"ttl:cloudlab:{instance_id}:alarm"
        self.redis_client.setex(name=key_alarm, time=ttl, value="")
        return True

    def updateProgressRedisStepValue(self, instance_id: str, update_data: dict, step_name: str) -> None:
        try:
            redis_key = f"techadmin:cloudlab:progress:{instance_id}"
            progress_data = json.loads(self.redis_client.get(name=redis_key).decode(encoding="utf-8"))
            for step in progress_data["step"]:
                if step.get("name") == step_name:
                    index = progress_data["step"].index(step)
                    progress_data["step"][index] = update_data
            self.redis_client.set(name=redis_key, value=json.dumps(progress_data))
        except Exception as e:
            logger.error(f"更新redis数据失败status: {e}")

    def addProgressDataStepStartTime(self, instance_id: str, step: str):
        try:
            redis_key = f"techadmin:cloudlab:progress:{instance_id}"
            progress_data = json.loads(self.redis_client.get(name=redis_key).decode(encoding="utf-8"))
            for _step in progress_data["step"]:
                if _step.get("name") == step:
                    _step["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.redis_client.set(name=redis_key, value=json.dumps(progress_data))
        except Exception as e:
            logger.error(f"更新redis数据失败step: {e}")

    def updateProgressDataStepStatus(self, instance_id: str, status: int, host_status: int, networks_status: int,
                                     nodes_status: int, schedule: int, queue_status: int, login_status: int):
        try:
            redis_key = f"techadmin:cloudlab:progress:{instance_id}"
            progress_data = json.loads(self.redis_client.get(name=redis_key).decode(encoding="utf-8"))
            progress_data["status"] = status
            progress_data["schedule"] = schedule
            for step in progress_data["step"]:
                if step.get("name") == "queue":
                    step["status"] = queue_status
                if step.get("name") == "host":
                    step["status"] = host_status
                if step.get("name") == "networks":
                    step["status"] = networks_status
                if step.get("name") == "nodes":
                    step["status"] = nodes_status
                if step.get("name") == "login":
                    step["status"] = login_status
            self.redis_client.set(name=redis_key, value=json.dumps(progress_data))
        except Exception as e:
            logger.error(f"更新redis数据失败step: {e}")
    
    def updateProgressDataHostStatus(self, instance_id: str, status: int):
        try:
            redis_key = f"techadmin:cloudlab:progress:{instance_id}"
            progress_data = json.loads(self.redis_client.get(name=redis_key).decode(encoding="utf-8"))
            progress_data["status"] = status
            self.redis_client.set(name=redis_key, value=json.dumps(progress_data))
        except Exception as e:
            logger.error(f"更新redis数据失败step: {e}")

    def updateProgressRedisValueStatus(self, instance_id: str) -> bool:
        redis_key = f"techadmin:cloudlab:progress:{instance_id}"
        progress_data = json.loads(self.redis_client.get(name=redis_key).decode(encoding="utf-8"))
        progress_data["status"] = 2
        self.redis_client.set(name=redis_key, value=json.dumps(progress_data))

    def setProgressRedisKey(self, instance_id: str, progress_data: dict):
        key = f"techadmin:cloudlab:progress:{instance_id}"
        self.redis_client.set(name=key, value=json.dumps(progress_data))

    def deleteProgressRedisKey(self, instance_id: str):
        key = f"techadmin:cloudlab:progress:{instance_id}"
        if self.redis_client.exists(key):
            self.redis_client.delete(key)
        else:
            pass

    def getProgressRedisValue(self, instance_id: str) ->dict:
        key = f"techadmin:cloudlab:progress:{instance_id}"
        value = self.redis_client.get(name=key).decode(encoding="utf-8")
        return json.loads(value)

    def setNodeLoginKey(self, key: str, value: dict):
        expiration_time_seconds = 180
        self.redis_client.set(key, json.dumps(value))
        self.redis_client.expire(key, expiration_time_seconds)
        return True

    def getNodeLoginValue(self, key: str):
        value = self.redis_client.get(key)
        return value

    def deleteInstanceRedisKey(self, instance_id: str):
        key_delete = f"ttl:cloudlab:{instance_id}:delete"
        if self.redis_client.exists(key_delete):
            self.redis_client.delete(key_delete)
        key_alarm = f"ttl:cloudlab:{instance_id}:alarm"
        if self.redis_client.exists(key_alarm):
            self.redis_client.delete(key_alarm)
        return True

    def generateInstanceFreePortSet(self, instance_id: str) -> bool:
        key = f"techadmin:cloudlab:instance_kvm:free_port:{instance_id}"
        free_ports = set(range(5900, 6000))
        self.redis_client.sadd(key, *free_ports)
        self.redis_client.expire(key, 1000)
        return True

    def getInstanceKvmFreePort(self, instance_id: str) -> int:
        """
        获取实例宿主机的空闲端口
        """
        key = f"techadmin:cloudlab:instance_kvm:free_port:{instance_id}"
        if self.redis_client.exists(key):
            free_port = self.redis_client.spop(key).decode(encoding="utf-8")
        else:
            self.generateInstanceFreePortSet(instance_id)
            free_port = self.redis_client.spop(key).decode(encoding="utf-8")
        return int(free_port)

    def getKvmFreePort(self, kvm_host_ip: str) -> int:
        """
        获取裸金属服务器的空闲端口
        """
        key = f"techadmin:cloudlab:kvm:free_port:{kvm_host_ip}"
        if self.redis_client.exists(key):
            free_port = self.redis_client.spop(key).decode(encoding="utf-8")
        else:
            free_ports = set(range(9000, 60000))
            self.redis_client.sadd(key, *free_ports)
            free_port = self.redis_client.spop(key).decode(encoding="utf-8")
        return int(free_port)


    def addKvmFreePort(self, kvm_host_ip: str, free_ports: set) -> int:
        """
        获取裸金属服务器的空闲端口
        """
        key = f"techadmin:cloudlab:kvm:free_port:{kvm_host_ip}"
        if self.redis_client.exists(key):
            self.redis_client.sadd(key, *free_ports)
        return True
    
    def updateNodeProgressStatus(self, instance_id: str, node_id: str, status: int, description: str):
        logger.info(f"实例ID{instance_id}, 节点ID{node_id}, 状态{str(status)},描述{description}")
        node_progress_data = self.getNodeProgress(instance_id, node_id)
        if node_progress_data:
            node_progress_data["status"] = status
            node_progress_data["description"] = description
            self.updateNodeProgress(instance_id, node_id, node_progress_data)
        return True
    
    def updateNodeProgressStatusNetwork(self, instance_id: str, network_id: str, status: int, description: str) -> str:
        try:
            redis_key = f"techadmin:cloudlab:progress:{instance_id}:{network_id}*"
            keys = self.redis_client.keys(redis_key)
            node_key = keys[0].decode(encoding="utf-8")[-20:]
            node_progress_data = self.getNodeProgress(instance_id, node_key)
            node_progress_data["status"] = status
            node_progress_data["description"] = description
            self.updateNodeProgress(instance_id, node_key, node_progress_data)
        except:
            node_key = network_id
            node_proggress = {"id": node_key, "name": node_key, "status": 2}
            self.setNodeProgress(instance_id, network_id, node_proggress)
        return True
    
    def closeRedisConnect(self):
        self.redis_client.close()
        
