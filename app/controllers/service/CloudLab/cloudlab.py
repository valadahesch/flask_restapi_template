import os
import re
import json
import time
import requests
from datetime import datetime
from app.config import KvmConfig, EmailConfig, KafkaConfig
from app.extensions import logger
from app.utils.kafka_util import KafkaProducer
from netmiko import ConnectHandler
from app.controllers.dao.cloud_lab_redis_dao import RedisUtils
from app.utils.api_util import AppException
from app.utils.func_util import nanoId
from app.utils.func_util import getRandomString20, getRandomString10
from app.controllers.dao.cloud_lab_dao import CloudLabImageDao, CloudLabNodeDao, CloudLabTemplateDao, \
    CloudLabServerHostDao, CloudLabUserTemplateInstanceDao
from app.models.cloud_lab import ProgressData, ProgressStepData, ProgressStepDetailData
from app.utils.kvm.linux_util import LinuxUtil


class CloudLab:

    def __init__(self) -> object:
        self.cloud_lab_instance_sql = CloudLabUserTemplateInstanceDao()
        self.cloud_lab_template_sql = CloudLabTemplateDao()
        self.cloud_lab_server_host_sql = CloudLabServerHostDao()
        self.cloud_lab_node_sql = CloudLabNodeDao()
        self.cloud_lab_image_sql = CloudLabImageDao
        self.redis_util = RedisUtils()


    @staticmethod
    def assignServerHost(instance_cpu: int, instance_memory: int, instance_storage: int) -> object:
        """
        function: 根据裸金属服务器剩余资源情况自动分配宿主机
        return: 裸金属服务器管理信息
        """
        server_hosts_list = CloudLabServerHostDao.getServerHostInfo()
        class ServerHost:
            def __init__(self, id, cpu_available, memory_available, storage_available, ip_address, 
                         username, password):
                self.id = id
                self.cpu_available = cpu_available
                self.memory_available = memory_available
                self.storage_available = storage_available
                self.ip_address = ip_address
                self.username = username
                self.password = password
        def compareServerHost(server_host):
            return server_host.cpu_available + server_host.memory_available
        server_hosts = []
        for server_host in server_hosts_list:
            server_hosts.append(ServerHost(server_host.get("id"), server_host.get("cpu_available"), 
                                           server_host.get("memory_available"), server_host.get("storage_available"),
                                           server_host.get("ip_address"), server_host.get("username"),
                                           server_host.get("password")))
        best_server_host = max(server_hosts, key=compareServerHost)
        if instance_cpu > best_server_host.cpu_available or \
        instance_memory > best_server_host.memory_available or \
        instance_storage > best_server_host.storage_available:
            linux_host = LinuxUtil(username=best_server_host.username, password=best_server_host.password,
                                   host=best_server_host.ip_address, port=22, libvirt_port="16509")
            if linux_host.isCpuEnough and linux_host.isMemoryEnough:
                logger.info("数据库服务器资源不足,从物理服务器获取资源使用情况，资源充足")
                return best_server_host
            else:
                logger.error("获取适配裸金属服务器失败,服务器资源不足")
                return None
        else:
            return best_server_host
        
    @staticmethod
    def updateResources(server_host_id: str, instance_cpu: int, instance_memory: int, instance_storage: int):
        """
        更新裸金属服务器资源剩余情况
        """
        CloudLabServerHostDao.updateServerHost(server_host_id, instance_cpu, instance_memory, instance_storage)
        return True
    
    @staticmethod
    def generatetExclusiveTime(template_data: str) -> int:
        nodes, networks = template_data.get("nodes"), template_data.get("networks")
        nodes_spend = len(nodes)*25
        networks_spend = len(networks)*1
        instance_spend = 30
        console_login_spend = len(nodes)*2
        exclusive_time = nodes_spend + networks_spend + instance_spend + console_login_spend
        return exclusive_time
    
    @staticmethod
    def computingResources(template_data: str) -> set:
        nodes = template_data.get("nodes")
        cpu, ram, storage = 0, 0, 2
        for node in nodes:
            node_cpu, node_ram = CloudLabNodeDao.getNodeCPUAndRam(node_key=node.get("type_key"))
            node_storage = CloudLabImageDao.getImageSize(image_key=node.get("image_key"))
            cpu =  cpu + node_cpu
            ram = ram + node_ram
            storage = storage + node_storage
        return cpu, ram, int(storage)

    @staticmethod
    def generatetProgressData(template_data: dict, create_time: str, server_time: str, estimated_time: int) -> dict:
        progress_data = ProgressData(status=1, queue=0, estimate_create_time=estimated_time, create_time=create_time,
                                    server_time=server_time, local_time="2106-01-01 00:00:00", schedule=10, steps=[])
        progress_data = vars(progress_data)
        step_queue = vars(ProgressStepData(name="queue", label="排队中", status=1, spend_time=0, detail=[]))
        step_queue["start_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        step_host = vars(ProgressStepData(name="host", label="创建实验主机", status=4, spend_time=0, detail=[]))
        step_networks = vars(ProgressStepData(name="networks", label="创建内部网络", status=4, spend_time=0, detail=[]))
        step_nodes = vars(ProgressStepData(name="nodes", label="创建节点", status=4, spend_time=0, detail=[]))
        step_login = vars(ProgressStepData(name="login", label="获取登录方式", status=4, spend_time=0, detail=[]))

        nodes, networks = template_data.get("nodes"), template_data.get("networks")
        step_queue_progress = [{"id": "queue", "name": "queue", "status": 2}]
        step_queue["detail"] = step_queue_progress
        step_host_progress = [{"id": "kvm_host", "name": "宿主机环境", "status": 1}]
        step_host["detail"] = step_host_progress
        step_login_progress = [{"id": "login", "name": "登录信息", "status": 1}]
        step_login["detail"] = step_login_progress
        for network in networks:
            network_proggress = {"id": network["id"], "name": "网卡" + network["id"], "status": 1}
            step_networks["detail"].append(network_proggress)

        progress_data["step"].append(step_queue)
        progress_data["step"].append(step_host)
        progress_data["step"].append(step_networks)
        progress_data["step"].append(step_nodes)
        progress_data["step"].append(step_login)
        return progress_data
    
    @staticmethod
    def generatetNodesData(instance_id: str, cells: list, template_data: dict):
        redis_object = RedisUtils()
        node_port_status = []
        node_name, nodes, networks = "", template_data.get("nodes"), template_data.get("networks")
        for cell in cells:
            if cell["graph"]["shape"] == "lab-node":
                for input in cell["data"]["input_struct"]:
                    if input["key"] == "name":
                        node_name = input["value"]
                for node in nodes:
                    if node["id"] == cell["id"]:
                        node_port_status= node["node_interface"]
                for network in networks:
                    if network["id"] == cell["id"][:10]:
                        node_port_status= network["node_interface"]
                node_proggress = {"id": cell["id"], "name": node_name or cell["id"], "status": 1, 
                                  "port_status": node_port_status, "description": "正在创建设备"}
                redis_object.setNodeProgress(instance_id, cell.get("id"), node_proggress)
        redis_object.closeRedisConnect()


    @staticmethod
    def configureTranslation(cells: list) -> set:
        """
        将前端拓扑配置转换成后端节点配置
        """
        network_relations = []
        edge_source_dst_port = []
        edges_data = []
        network_node = ["internet", "mgt_net", "hub"]
        edges, nodes, switch = [], [], []
        template_data = {"nodes": [], "networks": []}
        # 更新cell id
        for cell in cells:
            new_cell_id = getRandomString20()
            old_node_id = cell["id"]
            cell["id"] = new_cell_id
            cell["__id"] = old_node_id
            for cell in cells:
                if cell["graph"]["shape"] == "edge":
                    if cell["graph"]["source"]["cell"] == old_node_id:
                        cell["graph"]["source"]["cell"] = new_cell_id
                    elif cell["graph"]["target"]["cell"] == old_node_id:
                        cell["graph"]["target"]["cell"] = new_cell_id
        for cell in cells:
            if cell["graph"]["shape"] == "edge":
                edges.append(cell)
            elif cell["graph"]["shape"] == "lab-node":
                nodes.append(cell)
            elif cell["graph"]["shape"] == "lab-node" and node["data"]["key"] in network_node:
                switch.append[cell["id"]]
        for edge in edges:
            # 情况一： edge一端为傻瓜交换机一端为可用node --> 不需要新建network
            # 情况二： edge两端都为可用node(但是node不是"internet", "mgt_net", "hub") --> 新建一张network
            source_cell_port_id = edge["graph"]["source"]["port"]
            dst_cell_port_id = edge["graph"]["target"]["port"]
            edge_source_dst_port.append(source_cell_port_id)
            edge_source_dst_port.append(dst_cell_port_id)

            source_cell_id = edge["graph"]["source"]["cell"]
            dst_cell_id = edge["graph"]["target"]["cell"]
            for cell in cells:
                if cell["id"] == source_cell_id:
                    source_cell_key = cell["data"]["key"]
                if cell["id"] == dst_cell_id:
                    dst_cell_key = cell["data"]["key"]
            if source_cell_key not in network_node and dst_cell_key not in network_node:
                network_id =getRandomString10()
                network = {
                       "id": network_id, 
                       "type": "edge",
                       "source_port": edge["graph"]["source"]["port"], 
                       "dst_port": edge["graph"]["target"]["port"],
                       "image_key": "layer_two"
                }
                template_data["networks"].append(network)
        lab_default_network_id = getRandomString10()
        network = {
                    "id": lab_default_network_id, 
                    "type": "edge",
                    "image_key": "lab_default",
                    "node_type": "network"
            }
        template_data["networks"].append(network)

        for edge in edges:
            source_node_port_id = edge["graph"]["source"]["port"]
            source_node_id = edge["graph"]["source"]["cell"]
            dst_node_port_id = edge["graph"]["target"]["port"]
            dst_node_id = edge["graph"]["target"]["cell"]
            edge_data = { 
                "source_node": source_node_id, 
                "source_node_port": source_node_port_id, 
                "dst_node": dst_node_id, 
                "dst_node_port": dst_node_port_id
            }
            edges_data.append(edge_data)


        # 情况一： node属于switch创建network 
        for node in nodes:
            if node["data"]["key"] in network_node:
                network = {"id": node["id"][:10], "type": "node", "image_key": node["data"]["key"], "node_type": "network"}
                for edge in edges:
                    if edge["graph"]["source"]["cell"] == node["id"]:
                        data = {"network": node["id"], "connect_node_id": edge["graph"]["target"]["cell"], 
                                "connect_node_port_id": edge["graph"]["target"]["port"]}
                        network_relations.append(data)
                    if edge["graph"]["target"]["cell"] == node["id"]: 
                        data = {"network": node["id"], "connect_node_id": edge["graph"]["source"]["cell"], 
                                "connect_node_port_id": edge["graph"]["source"]["port"]}
                        network_relations.append(data)
                for input in node["data"]["input_struct"]:
                    if input["key"] == "interface_list":
                        node_interface = input["value"]    
                        for interface in node_interface:
                            interface["id"] = interface["_id"]
                            if interface["_id"] in str(edges_data):
                                interface["status"] = "up"
                            else:
                                interface["status"] = "unplugged"
                        network["node_interface"] = node_interface
                template_data["networks"].append(network)


        # 情况二： node属于实验设备创建设备并分配network
        for node in nodes:
             if node["data"]["key"] not in network_node:
                for input in node["data"]["input_struct"]:
                    if input["key"] == "name":
                        node_name = input["value"]
                    elif input["key"] == "software_version":
                        node_image_key = input["value"]
                    elif input["key"] == "interface_list":    
                        for interface in input["value"]:
                            # 情况一： 连接非管理网等特殊网卡，走edge新建流程网卡的接口
                            for network in template_data["networks"]:
                                if network.get("source_port") == interface["_id"] or network.get("dst_port") == interface["_id"]:
                                    interface["network"] = network["id"]
                                    interface["status"] = "up"
                                    interface["id"] = interface["_id"]
                            # 情况二：连接"internet", "mgt_net", "hub"的接口
                            relation = [network_relation["connect_node_port_id"] for network_relation in network_relations]
                            if interface["_id"] in relation:
                                mapping = {item["connect_node_port_id"]: item["network"] for item in network_relations}
                                interface["network"] = mapping.get(interface["_id"])
                                interface["status"] = "up"
                                interface["id"] = interface["_id"]
                            # 情况三：有接口但是未进行连线的接口
                            if interface["_id"] not in edge_source_dst_port:
                                interface["network"] = lab_default_network_id
                                interface["status"] = "unplugged"
                                interface["id"] = interface["_id"]
                        node_interface = input["value"]
                node = {
                    "id": node["id"],
                    "type_key": node["data"]["key"],
                    "name": node_name,
                    "image_key": node_image_key,
                    "node_interface": node_interface,
                    "node_type": "device"
                }
                template_data["nodes"].append(node)
        return template_data, cells
    

    def requestCreateInstanceByTemplate(self, template_id: str, instance_name: str, user_id: str, 
                                        request_host: str) -> dict:
        template_data, template_data_view = self.cloud_lab_template_sql.getTemplateData(template_id=template_id)
        instance_id = nanoId()
        all_instance_id =self.cloud_lab_instance_sql.getAllInstanceId()
        while instance_id in all_instance_id:
            instance_id = nanoId()
        template_data, cells = CloudLab.configureTranslation(template_data_view.get("cells"))
        template_data_view["cells"] = cells
        exclusive_time = CloudLab.generatetExclusiveTime(template_data)
        estimated_time = exclusive_time 
        self.redis_util.setInstanceTTL(instance_id=instance_id)
        create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cloud_lab_instance_sql.addInstanceInfo(instance_id=instance_id, user_id=user_id, create_time=create_time, 
                                    template_data=json.dumps(template_data, ensure_ascii=False), name=instance_name, status=1,
                                    estimated_time=estimated_time, exclusive_time=exclusive_time,
                                    instance_data=json.dumps(template_data_view, ensure_ascii=False), template_id=template_id)   
        CloudLab.generatetNodesData(instance_id, cells, template_data)
        progress_data = CloudLab.generatetProgressData(template_data, create_time, create_time, estimated_time)
        self.redis_util.setProgressRedisKey(instance_id=instance_id, progress_data=progress_data)
        self.redis_util.closeRedisConnect()
        cpu, ram, storage = CloudLab.computingResources(template_data)
        produce_data = {
            "instance_id": instance_id,
            "request_host": request_host,
            "cpu": cpu,
            "ram": ram,
            "storage": storage
        }
        KafkaProducer().produce_message(topic=KafkaConfig["topic_host_image"], message=produce_data)
        return {"id": instance_id}


    def requestCreateInstance(self, user_id, request_host: str, params: dict) -> dict:
        instance_name, cells= params.get("name"), params.get("cells")
        description, picture = params.get("description"), params.get("picture")
        instance_id = nanoId()
        all_instance_id =self.cloud_lab_instance_sql.getAllInstanceId()
        while instance_id in all_instance_id:
            instance_id = nanoId()
        template_data, cells = CloudLab.configureTranslation(cells)
        template_data_view = {"name": instance_name, "description": description, "picture": picture, "cells": cells}
        exclusive_time = CloudLab.generatetExclusiveTime(template_data)
        estimated_time = exclusive_time 
        self.redis_util.setInstanceTTL(instance_id=instance_id)
        create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cloud_lab_instance_sql.addInstanceInfo(instance_id=instance_id, template_data=json.dumps(template_data, ensure_ascii=False),
                                    user_id=user_id, instance_data=json.dumps(template_data_view, ensure_ascii=False), 
                                    create_time=create_time, status=1, exclusive_time=exclusive_time,
                                    estimated_time=estimated_time, name=instance_name)
        CloudLab.generatetNodesData(instance_id, cells, template_data)
        progress_data = CloudLab.generatetProgressData(template_data, create_time, create_time, estimated_time)
        self.redis_util.setProgressRedisKey(instance_id=instance_id, progress_data=progress_data)
        self.redis_util.closeRedisConnect()
        cpu, ram, storage = CloudLab.computingResources(template_data)
        produce_data = {
            "instance_id": instance_id,
            "request_host": request_host,
            "cpu": cpu,
            "ram": ram,
            "storage": storage
        }
        KafkaProducer().produce_message(topic=KafkaConfig["topic_host_image"], message=produce_data)
        return {"id": instance_id}    
    
    
    @staticmethod
    def getImages(path: str, hostname: str, port: int, node_id: str):
        ssh_config = {
            'device_type': 'linux',
            'host': hostname,
            'username': KvmConfig["instance_username"],
            'password': KvmConfig["instance_password"],
            'port': port,
            'global_delay_factor': 0,
        }        
        start_time = time.time()
        try:
            with ConnectHandler(**ssh_config) as connect:
                time_diff = time.time()-start_time
                logger.debug(f"连接ssh {ssh_config['username']}@{ssh_config['host']}:{ssh_config['port']}成功，耗时：{time_diff:.2f}秒")
                command = f""" mkdir /instance/images/{node_id} """
                start_time = time.time()
                output = connect.send_command(command)  
                time_diff = time.time()-start_time
                logger.debug(f"在ssh {ssh_config['username']}@{ssh_config['host']}:{ssh_config['port']}执行{command}命令，耗时：{time_diff:.2f}秒，输出{output}")
                # command = f""" lftp lab.hillstonenet.com -e "get {path}  -o /instance/images/{node_id}/;quit" """
                command = f"wget -P /instance/images/{node_id} http://lab.hillstonenet.com{path}"
                start_time = time.time()
                output = connect.send_command(command, read_timeout=2*60)
                time_diff = time.time()-start_time
                logger.debug(f"在ssh {ssh_config['username']}@{ssh_config['host']}:{ssh_config['port']}执行{command}命令，耗时：{time_diff:.2f}秒，输出{output}")        
                return True
        except Exception as e: 
            logger.error(f"在ssh {ssh_config['username']}@{ssh_config['host']}:{ssh_config['port']}上执行命令出错：{e}")  


    @staticmethod
    def sendInstanceExtendEmail(target: str, instance: dict, expire_minutes: str)-> str:
        header = {'Content-Type': 'application/json'}
        data = {
            "media_type": "email",
            "target": target,
            "bcc": EmailConfig["email_bcc"],
            "template_id": "5518",
            "data": {
                "instance_id": instance.get("id"),
                "expire_minutes": expire_minutes,
                "instance_name": instance.get("name")
            },
            "resend": True
        }
        resp = requests.post(url=EmailConfig["email_server"], headers=header, json=data)
        logger.info(f"实例ID:{instance.get('id')}, 发送告警邮件结果:{resp.text}")
        return resp.text
    
    @staticmethod
    def sendInstanceDeleteEmail(target, instance: dict):
        header = {'Content-Type': 'application/json'}
        data = {
            "media_type": "email",
            "target": target,
            "bcc": EmailConfig["email_bcc"],
            "template_id": "5519",
            "data": {
                "instance_id": instance.get("id"),
                "instance_name": instance.get("name")
            },
            "resend": True
        }
        resp = requests.post(url=EmailConfig["email_server"], headers=header, json=data)
        logger.info(f"实例ID:{instance.get('id')}, 发送删除邮件结果:{resp.text}")
        return resp.text

    @staticmethod
    def sendInstanceWarnEmail(target: str, instance_id: str, instance_name: str, create_time: str,
                expire: str, button: str):
        url = 'http://10.86.249.61/support/messagegw'
        header = {'Content-Type': 'application/json'}
        data = {
            "media_type": "email",
            "target": target,
            "bcc": EmailConfig["email_bcc"],
            "template_id": "5911",
            "data": {
                "instance_id": instance_id,
                "instance_name": instance_name,
                "create_time": create_time,
                "expire_minutes": expire,
                "button": button
            },
            "resend": True
        }
        response = requests.post(url=url, headers=header, json=data)
        logger.info(f"邮件响应内容{response.text}")
        return response.text
    

    def getFreePort(self, kvm_host_ip: str) -> int:
        """
        kvm管理端口从10000开始, ssh端口从20000开始, 虚拟机管理端口从30000开始
        """
        free_port = self.redis_util.getKvmFreePort(kvm_host_ip)
        self.redis_util.closeRedisConnect()
        return free_port
    

    def getTemplateList(self) -> dict:
        templates_data = self.cloud_lab_template_sql.getTemplateList()
        return {"list": templates_data}
    

    def getTemplateDataView(self, template_id: str = "") -> dict:
        templates_data_view = self.cloud_lab_template_sql.getTemplateDataView(template_id)
        return templates_data_view

    @staticmethod
    def getNodeMeta()-> list:
        abspath = os.path.abspath(os.path.dirname(__file__))
        with open(os.path.join(abspath, '../../../../config/node_mate.json'), 'r', encoding="utf-8") as f:
            node_meta = json.load(f)
        node_meta = {"code": 0, "message": "", "data": {"list": node_meta.get("data")}}
        return node_meta
    

    def getServerHostResource(self) -> dict:
        memory, cpu_count, used_memory, used_cpu_count, memory_percent, cpu_percent = self.cloud_lab_server_host_sql.getServerHostResource()
        instance_starting, instance_running, instance_shutdown = self.cloud_lab_instance_sql.getInstanceStatusCount()
        instance_queue = instance_starting - 1
        memory = max(0, memory)
        cpu_count = max(0, cpu_count)
        used_memory = max(0, used_memory)
        used_cpu_count = max(0, used_cpu_count)
        memory_percent = max(0, memory_percent)
        cpu_percent = max(0, cpu_percent)
        instance_queue = max(0, instance_starting-1)
        resource_data = {
            "instance_queue": instance_queue,
            "instance_starting": instance_starting,
            "instance_running": instance_running,
            "instance_pause": instance_shutdown,
            "server": {
                "memory": memory*1024*1024*1024,
                "cpu_count": cpu_count,
                "used_memory": used_memory*1024*1024*1024,
                "used_cpu_count": used_cpu_count,
                "memory_percent": float(round(memory_percent, 4)),
                "cpu_percent": float(round(cpu_percent, 4))
            }
        }
        return resource_data


    def createTemplate(self, template_data_view: dict, user_id: str) -> None:
        template_data, cells = CloudLab.configureTranslation(template_data_view.get("cells"))
        template_data_view["cells"] = cells
        self.cloud_lab_template_sql.addTemplate(name=template_data_view.get("name"), picture=template_data_view.get("picture"), 
                                        user_id=user_id, description=template_data_view.get("description"), 
                                        template_data=json.dumps(template_data, ensure_ascii=False),
                                        template_data_view=json.dumps(template_data_view, ensure_ascii=False))
        return None
    


