import re
import copy
import sys
import time
import json
import threading
from app.extensions import logger
from datetime import datetime, timedelta
from app.utils.kvm.linux_util import LinuxUtil
from app.utils.api_util import AppException
from app.config import KvmConfig, KafkaConfig
from app.utils.kafka_util import KafkaProducer
from app.models.cloud_lab import ProgressStepData
from app.controllers.service.CloudLab import CloudLab
from app.utils.func_util import scanOpenPort, getTimeDifference
from app.controllers.dao.cloud_lab_redis_dao import RedisUtils
from app.controllers.dao.cloud_lab_dao import CloudLabServerHostDao, CloudLabUserTemplateInstanceDao, \
                                    CloudLabImageDao, CloudLabTemplateDao, CloudLabNodeDao
if not sys.platform.startswith('win'):
    import libvirt

class Instance:

    def __init__(self) -> None:
        self.cloud_lab_instance_sql = CloudLabUserTemplateInstanceDao()
        self.cloud_lab_template_sql = CloudLabTemplateDao()
        self.cloud_lab_server_host_sql = CloudLabServerHostDao()
        self.cloud_lab_node_sql = CloudLabNodeDao()
        self.cloud_lab_image_sql = CloudLabImageDao
        self.redis_util = RedisUtils()

    @staticmethod
    def generateNodesLoginData(template_data: dict, request_host: str, mgt_nodes: list, instance_id) -> dict:
        nodes, nodes_logins = template_data["nodes"], {}
        for node in nodes:
            node_id = node["id"]
            if node["id"] in mgt_nodes:
                login_data = CloudLabImageDao.getImageLoginData(image_id=node["image_key"])
            else:
                login_data = CloudLabImageDao.getImageConsoleLoginData(image_id=node["image_key"])
            for key in login_data:
                login_data[key]["url"] = f"https://{request_host}/api/cloud_lab/user/interface/" \
                                            f"{instance_id}/{node_id}/{key}"
            nodes_logins[node["id"]] = login_data
        return nodes_logins

    @staticmethod
    def getMgtNodes(template_data: dict) -> list:
        nodes, networks = template_data["nodes"], template_data["networks"]
        mgt_network, mgt_nodes = False, []
        for network in networks:
            if network.get("image_key") == "mgt_net":
                mgt_network = True
                mgt_network_id = network["id"]
        if mgt_network:
            for node in nodes:
                if node.get("image_key") not in CloudLabImageDao.getNotCheckIpImages():
                    for interface in node["node_interface"]:
                        if interface["network"][:10] == mgt_network_id:
                            mgt_nodes.append(node["id"])
        return mgt_nodes

    def getInstanceFreePort(self, instance_id: str) -> int:
        """
        function: 获取实例空闲端口
        """
        free_port = self.redis_util.getInstanceKvmFreePort(instance_id)
        self.redis_util.closeRedisConnect()
        return free_port

    def getInstanceList(self, user_id: str, name: str, status: int, page: int, size: int) -> dict:
        instance_data = self.cloud_lab_instance_sql.query_instances(user_id, name, status, page, size)
        return instance_data
    
    def getInstanceInfo(self, instance_id: str, request_user_id) -> dict:
        instance_info, instance_user_id = self.cloud_lab_instance_sql.getInstanceInfoView(instance_id)
        if request_user_id == instance_user_id:
            expire = self.redis_util.getInstanceTTL(instance_id=instance_id)
            self.redis_util.closeRedisConnect()
            if expire <= 0 and expire != -1:
                instance_info["status"] = 7
            return instance_info
        else:
            raise AppException(f"获取实例信息失败，请检查本人是否拥有该实例:{instance_id}")
    
    def getStartingInstanceByTemplateId(self, template_id: str, user_id: str):
        instance_data = self.cloud_lab_instance_sql.queryInstanceByStatus(user_id, template_id)
        return {"list": instance_data}

    def addInstanceTTL(self, instance_id: str) -> None:
        if self.redis_util.getInstanceTTL(instance_id=instance_id) > 3800:
            raise AppException("设备有效期大于1小时,无法进行续期操作,如有特殊需求请联系管理员")
        self.redis_util.addInstanceTTL(instance_id=instance_id)
        return None   
    
    def getInstanceProgressStarting(self, instance_id: str, local_time: str) -> dict:
        if not self.redis_util.redis_client.exists(f"techadmin:cloudlab:progress:{instance_id}"):
            raise AppException(message="实例不存在或者已经被删除")
        progress_data = self.redis_util.getProgressRedisValue(instance_id=instance_id)
        progress_data["local_time"] = local_time
        progress_data["server_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for step in progress_data["step"]:
            if step.get("status") != 2:
                step_start_time = step.get("start_time")
                if step_start_time:
                    start_time = datetime.strptime(step_start_time, "%Y-%m-%d %H:%M:%S")
                    step["spend_time"] = int((datetime.now() - start_time).total_seconds())
            if step.get("name") == "nodes":
                step["detail"] = self.redis_util.getNodeProgressDataByInstanceId(instance_id)
        self.redis_util.setProgressRedisKey(instance_id=instance_id, progress_data=progress_data)
        self.redis_util.closeRedisConnect()
        return progress_data

    def getInstanceProgressRunning(self, instance_id: str) -> dict:
        if not self.redis_util.redis_client.exists(f"techadmin:cloudlab:progress:{instance_id}"):
            raise AppException(message="实例不存在或者已经被删除")
        original_action_button = [
            {"type": "power_on", "label": "开机", "available": False},
            {"type": "power_off", "label": "强制关机", "available": True},
            {"type": "force_reboot", "label": "强制重启", "available": True},
            {"type": "shutdown", "label": "关闭操作系统", "available": True},
            {"type": "restart", "label": "重启操作系统", "available": True}]
        instance =  self.cloud_lab_instance_sql.getInstanceInfo(instance_id)
        nodes_status_data = self.redis_util.getNodeProgressDataByInstanceId(instance_id)
        instance_host_status, invisible_action_buttons = instance.get("status"), []
        template_data = instance.get("template_data")
        if instance_host_status == 2:
            if not scanOpenPort(instance["server_host_data"]["host"], instance["ssh_port"]):
                instance_host_status = 3
        for node_status_data in nodes_status_data:         
            node_status, node_id   = node_status_data.get("status"), node_status_data.get("id")
            node_login = node_status_data.get("login")
            for node in template_data.get("nodes"):
                if node.get("id") == node_id and node_login is not None:
                    invisible_action_buttons = self.cloud_lab_image_sql.getImageActionButton(node["image_key"])
                    invisible_action_buttons = [item["type"] for item in invisible_action_buttons]
            if node_login is None:
                node_status_data["login"], node_status_data["action"] = [], []
            elif node_status == 15 and node_login is not None:
                shutdown_action_button = copy.deepcopy(original_action_button)
                node_action_buttons =  [item for item in shutdown_action_button if item["type"] not in invisible_action_buttons]
                for button in node_action_buttons:
                    if button["type"] == "power_on":
                        button["available"] = True
                    else:
                        button["available"] = False
                node_status_data["login"] = []
                for key, value in node_login.items():
                    value["available"] = False
                    node_status_data["login"].append(value)
                node_status_data["action"] = node_action_buttons
            elif node_status == 2 and node_login is not None:
                running_action_button = copy.deepcopy(original_action_button)
                node_action_buttons =  [item for item in running_action_button if item["type"] not in invisible_action_buttons]
                node_status_data["login"] =  [value for value in node_login.values()]
                node_status_data["action"] = node_action_buttons
            elif node_status in [1, 3, 12] and node_login is not None:
                other_action_button = copy.deepcopy(original_action_button)
                node_action_buttons =  [item for item in other_action_button if item["type"] not in invisible_action_buttons]
                for node_action_button in node_action_buttons:
                    node_action_button["available"] = False
                node_status_data["action"] = node_action_buttons
                node_status_data["login"] = []
                for key, value in node_login.items():
                    if key != "console":
                        value["available"] = False
                    node_status_data["login"].append(value)
        expire = self.redis_util.getInstanceTTL(instance_id=instance_id)
        progress_running_data = {"status": instance_host_status, "device_status": nodes_status_data, "expire": expire}
        self.redis_util.closeRedisConnect()
        if instance_host_status == 2:
            node_status_thread = threading.Thread(target=self.asyncGetInstanceNodeStatus, args=(instance_id, nodes_status_data, 
                                                                                                instance_host_status, instance))
            node_status_thread.start()
        return progress_running_data
    

    def asyncGetInstanceNodeStatus(self, instance_id: str, nodes_status_data: list, instance_host_status: int, instance: dict):
        try:
            if instance_host_status == 2:
                host = instance["server_host_data"]["host"]
                libvirt_port = instance["mgt_port"]
                ssh_port = instance["ssh_port"]
                linux_util = LinuxUtil(host=host, libvirt_port=libvirt_port, port=ssh_port,
                                       username=KvmConfig["instance_username"], password=KvmConfig["instance_password"])
                running_vm_list = linux_util.getRunningVm()
                for node in nodes_status_data:
                    if node["id"] not in running_vm_list and node["status"] == 2 and node.get("login"):
                        progress_data = self.redis_util.getNodeProgress(instance_id, node["id"])
                        progress_data["status"] = 15
                        self.redis_util.updateNodeProgress(instance_id, node["id"], progress_data)
                    if node["id"] in running_vm_list and node["status"] == 15 and node.get("login"):
                        progress_data = self.redis_util.getNodeProgress(instance_id, node["id"])
                        progress_data["status"] = 2
                        self.redis_util.updateNodeProgress(instance_id, node["id"], progress_data)
                linux_util.close_all()
            return True
        except Exception as error:
            logger.debug(f"实例ID: {instance_id}, 从服务器中获取节点状态失败,原因是:{error}")
        

    def requestdeleteInstance(self, instance_id: str) -> None:
        if self.cloud_lab_instance_sql.getInstanceStatus(instance_id) == 7:
            raise AppException("设备已经被删除！")
        else:
            manual_release_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            server_host_data, iptables_rule = self.cloud_lab_instance_sql.deleteInstanceById(instance_id=instance_id, 
                                                                                             manual_release_time=manual_release_time)    
            self.redis_util.deleteInstanceRedisKey(instance_id)
            self.redis_util.deleteProgressRedisKey(instance_id)
            self.redis_util.deleteNodeProgressByInstanceId(instance_id)
            delete_instance_thread = threading.Thread(target=self.deleteInstance, args=(instance_id, server_host_data, iptables_rule))
            delete_instance_thread.start()
            return None

    def deleteInstance(self, instance_id: str, server_host_data: dict, iptables_rule: list) -> True:
        instance_storage = server_host_data["instance_storage"]
        instance_cpu = server_host_data["instance_cpu"]
        instance_ram = server_host_data["instance_ram"]
        server_host_id = server_host_data["id"]
        linux_util = LinuxUtil(username=server_host_data["username"], password=server_host_data["password"],
                               port=server_host_data["ssh_port"], libvirt_port=server_host_data["libvirt_port"],
                               host=server_host_data["host"])
        linux_util.deleteVm(vm_id=instance_id)
        commands=[]
        if iptables_rule is not None:
            iptables_rule = [item for item in iptables_rule if item]
            free_ports = set()
            for rule in iptables_rule:
                match = re.search(r'--dport (\d+)', rule)
                if match:
                    free_ports.add(match.group(1))  
            self.redis_util.addKvmFreePort(kvm_host_ip=server_host_data["host"], free_ports=free_ports)
            for rule in iptables_rule:
                commands.append(rule.replace("-A", "-D"))
        linux_util.ssh_send_batch_command(commands)
        linux_util.close_all()
        self.cloud_lab_server_host_sql.updateServerHostAvailableResource(server_host_id, int(instance_cpu), 
                                                                         int(instance_ram), int(instance_storage))
        return True

    def shutdownInstance(self, instance_id: str):
        try:     
            self.redis_util.updateProgressDataStepStatus(instance_id=instance_id, status=9, host_status=2,
                                                         networks_status=2, nodes_status=2, schedule=100,
                                                         queue_status=2, login_status=2)
            self.cloud_lab_instance_sql.updateInstanceOnDeploy(instance_id=instance_id, status=9)
            self.redis_util.setShutdownInstanceKey(instance_id)
            shutdown_instance_thread = threading.Thread(target=self.asyncShutdownInstance, args=(instance_id,))
            shutdown_instance_thread.start()
            return True
        except Exception as error:
            logger.error("【cloudlab】: Failed to shutdown instance! error data:{}".format(error))
            return False
        
    def asyncShutdownInstance(self, instance_id: str):
        try:
            instance = self.cloud_lab_instance_sql.getInstanceInfo(instance_id=instance_id)
            server_host_data = instance.get("server_host_data")
            host = server_host_data["host"]
            libvirt_port = server_host_data["libvirt_port"]
            ssh_port = server_host_data["ssh_port"]
            username = server_host_data["username"]
            password = server_host_data["password"]
            instance_ssh_port = instance.get("ssh_port")
            instance_mgt_port = instance.get("mgt_port")
            linux_util = LinuxUtil(host=host, libvirt_port=libvirt_port, port=ssh_port, username=username, password=password)
            linux_util_instance = LinuxUtil(host=host, libvirt_port=instance_mgt_port, port=instance_ssh_port, 
                                            username=KvmConfig["instance_username"], password=KvmConfig["instance_password"])
            linux_util_instance.ssh_send_command(command="sudo sh -c iptables-save > /etc/iptables.rules")
            linux_util_instance.close_all()
            if linux_util.getVmStatus(vm_id=instance_id) != libvirt.VIR_DOMAIN_SHUTDOWN:
                linux_util.powerOffVm(vm_id=instance_id)
            linux_util.close_all()
            return True
        except Exception as error:
            logger.error("【cloudlab】: Failed to shutdown instance! error data:{}".format(error))
            return False

    def powerOnInstance(self, instance_id: str):
        self.redis_util.updateProgressDataStepStatus(instance_id=instance_id, status=10, host_status=2, queue_status=2,
                                                     networks_status=2, nodes_status=2, schedule=100, login_status=2)
        self.cloud_lab_instance_sql.updateInstanceOnDeploy(instance_id=instance_id, status=10)
        poweron_instance_thread = threading.Thread(target=self.asyncPowerOnInstance, args=(instance_id,))
        poweron_instance_thread.start()
        logger.info(f"实例ID: {instance_id}, 启动实例宿主机,异步探测宿主机端口连通性,开始异步操作")

        return True

    def asyncPowerOnInstance(self, instance_id: str):
        instance = self.cloud_lab_instance_sql.getInstanceInfo(instance_id=instance_id)
        server_host_data = instance.get("server_host_data")
        host = server_host_data["host"]
        libvirt_port = server_host_data["libvirt_port"]
        ssh_port = server_host_data["ssh_port"]
        username = server_host_data["username"]
        password = server_host_data["password"]
        mgt_port = instance.get("mgt_port")
        time.sleep(10)
        linux_util = LinuxUtil(host=host, libvirt_port=libvirt_port, port=ssh_port, username=username, password=password)
        if linux_util.getVmStatus(vm_id=instance_id) != libvirt.VIR_DOMAIN_RUNNING:
            linux_util.startVm(vm_id=instance_id)
        start_time = datetime.now()
        logger.info(f"实例ID: {instance_id}, 开始探测实例宿主机端口连通性host:{host},port:{mgt_port}")
        while not scanOpenPort(host=host, port=mgt_port):
            time.sleep(1)
            logger.info(f"实例ID: {instance_id}, 探测实例宿主机端口连通性host:{host},port:{mgt_port}失败,一秒钟后再次尝试")
            if int((datetime.now() - start_time).total_seconds()) > 100: 
                logger.error(f"实例ID: {instance_id}, 实例宿主机启动失败请联系管理员处理")
                RedisUtils().updateProgressDataStepStatus(instance_id=instance_id, status=3, host_status=2, queue_status=2,
                                                             networks_status=2, nodes_status=2, schedule=100, login_status=2)
                CloudLabUserTemplateInstanceDao.updateInstanceOnDeploy(instance_id=instance_id, status=3)
                break
        else:
            logger.info(f"实例ID: {instance_id}, 探测实例宿主机端口连通性host:{host},port:{mgt_port}正常")
            RedisUtils().updateProgressDataStepStatus(instance_id=instance_id, status=2, host_status=2, queue_status=2,
                                                         networks_status=2, nodes_status=2, schedule=100, login_status=2)
            RedisUtils().setPowerOnInstanceKey(instance_id)
            CloudLabUserTemplateInstanceDao.updateInstanceOnDeploy(instance_id=instance_id, status=2)
            return True

    def CreateInstance(self, template_data: dict, instance_id: str, create_time: str, request_host: str,
                       instance_cpu: int, instance_memory: int, host_image_path: str, server_host_data: dict) -> str:
        try:
            
            self.redis_util.updateProgressDataStepStatus(instance_id=instance_id, status=1, host_status=1,networks_status=4, 
                                                         nodes_status=4, schedule=20, queue_status=2, login_status=4)
            self.redis_util.generateInstanceFreePortSet(instance_id)
            host_create_start_time, cloudlab = datetime.now(), CloudLab()
            create_host_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            mgt_nodes = Instance.getMgtNodes(template_data)
            logger.info(f"实例ID:{instance_id}, 开始创建实例虚拟宿主机,接入管理的设备列表, {mgt_nodes}")
            self.redis_util.addProgressDataStepStartTime(instance_id=instance_id, step="host")
            linux_util = LinuxUtil(host=server_host_data["host"], libvirt_port=server_host_data["libvirt_port"],
                                   username=server_host_data["username"], password=server_host_data["password"],
                                   port=server_host_data["ssh_port"])
            image_name = re.search(r'/([^/]+)\.[^.]+$', host_image_path).group(1)
            linux_util.createInstance(instance_cpu, instance_memory, instance_id, image_name, host_image_path)  
            logger.info(f"实例ID:{instance_id}, 成功创建实例宿主机, 等待设备启动获取其管理IP")
            start_time = datetime.now()
            while not linux_util.getMgtIP(vm_name=instance_id):
                if datetime.now() - start_time > timedelta(seconds=180):
                    raise ValueError("实例宿主机创建时间超过180秒,超时退出")
                time.sleep(1)
            instance_ip = linux_util.getMgtIP(vm_name=instance_id)
            logger.info(f"实例ID:{instance_id}, 宿主机已启动, 成功获取宿主机管理IP")
            libvirt_port = cloudlab.getFreePort(linux_util.host)
            ssh_port = cloudlab.getFreePort(linux_util.host)
            libvirt_nat_rule = linux_util.addIptablesRule(source_port=libvirt_port, dst_ip_port=instance_ip + ":16509")
            ssh_nat_rule = linux_util.addIptablesRule(source_port=ssh_port, dst_ip_port=instance_ip + ":22")
            iptables_rule = libvirt_nat_rule + ";" + ssh_nat_rule
            logger.info(f"实例ID:{instance_id}, 已为宿主机分配外网管理端口, ssh: {ssh_port}, kvm: {libvirt_port}")
            start_time = datetime.now()
            while not scanOpenPort(host=linux_util.host, port=libvirt_port):
                if datetime.now() - start_time > timedelta(seconds=180):
                    raise ValueError("实例宿主机libvirt端口不通")
                time.sleep(1)
            logger.info(f"实例ID:{instance_id}, 实例宿主机kvm管理端口连通性正常")
            host_spend = getTimeDifference(host_create_start_time, datetime.now())
            self.redis_util.updateProgressDataStepStatus(instance_id=instance_id, status=1, host_status=2, networks_status=1, 
                                                         nodes_status=4, schedule=30, queue_status=2, login_status=4)
            update_data = vars(ProgressStepData(name="host", label="创建实验主机", status=2, spend_time=host_spend, detail=[]))
            update_data["detail"] = [{"id": "kvm_host", "name": "host", "status": 2}]
            self.redis_util.updateProgressRedisStepValue(instance_id, update_data, "host")

            logger.info(f"实例ID:{instance_id}, 开始创建实例宿主机网络")
            nodes, networks = template_data["nodes"], template_data["networks"]
            kvm = LinuxUtil(host=linux_util.host, libvirt_port=libvirt_port, username=KvmConfig['instance_username'], 
                            password=KvmConfig['instance_password'], port=ssh_port)
            for network in networks:
                network_id=network.get("id")[:10]
                if network.get("image_key") == "hub":
                    kvm.createNetwork(network_id=network_id, network_xml_path="default_xml/network_hub.xml")
                    self.redis_util.updateNodeStatus(instance_id, network["id"])
                    self.redis_util.updateNodeProgressStatusNetwork(instance_id=instance_id, network_id=network["id"], status=2, description="设备初始化成功")
                if network.get("image_key") == "internet":
                    kvm.createNetwork(network_id=network_id, network_xml_path="default_xml/network_internet.xml")
                    self.redis_util.updateNodeStatus(instance_id, network["id"])
                    self.redis_util.updateNodeProgressStatusNetwork(instance_id=instance_id, network_id=network["id"], status=2, description="设备初始化成功")
                if network.get("image_key") == "mgt_net":
                    kvm.createNetwork(network_id=network_id, network_xml_path="default_xml/network_mgt_net.xml")
                    self.redis_util.updateNodeStatus(instance_id, network["id"])
                    self.redis_util.updateNodeProgressStatusNetwork(instance_id=instance_id, network_id=network["id"], status=2, description="设备初始化成功")
                if network.get("image_key") == "layer_two" or network.get("image_key") == "lab_default":
                    kvm.createNetwork(network_id=network_id)
            update_data = vars(ProgressStepData(name="networks", label="创建内部网络", status=2, spend_time=2, detail=[]))
            for network in networks:
                network_progress = {"id": network["id"], "name": network["id"], "status": 2}
                update_data["detail"].append(network_progress)
                
            self.redis_util.updateProgressRedisStepValue(instance_id=instance_id, update_data=update_data, step_name="networks")
            self.redis_util.updateProgressDataStepStatus(instance_id=instance_id, status=1, host_status=2, networks_status=2, 
                                                         nodes_status=1, schedule=65, queue_status=2, login_status=4)


            logger.info(f"实例ID:{instance_id}, 创建实例临时网卡(init_cmd),用于初始化节点配置")
            kvm.createNetwork(network_id="init_cmd", network_xml_path="default_xml/network_init_cmd.xml")
            kvm.ssh_send_command("sudo iptables -F FORWARD")

            logger.info(f"实例ID:{instance_id}, 开始创建实例节点")
            nodes_create_start_time = datetime.now()
            self.redis_util.addProgressDataStepStartTime(instance_id=instance_id, step="nodes")
            for node in nodes:    
                id, image_key = node["id"], node["image_key"]
                cpu, ram = self.cloud_lab_node_sql.getNodeCPUAndRam(node_key=node["type_key"])                
                interfaces = sorted(node["node_interface"], key=lambda x: x['index'])
                node["node_interface"] = interfaces
                image_path = self.cloud_lab_image_sql.getImageFtpPath(image_key=image_key)
                image_name = re.search(r'/([^/]+)$', image_path).group(1)
                initial_configuration = self.cloud_lab_image_sql.getImageInitializationOperation(image_key)
                if initial_configuration:
                    interfaces[0]["old_network"] = interfaces[0]["network"]
                    interfaces[0]["network"] = "init_cmd"
                if CloudLab.getImages(path=image_path, hostname=linux_util.host, port=ssh_port, node_id=id):
                    if "console_telnet" in self.cloud_lab_image_sql.getImageConsoleLoginData(image_key):
                        node_telnet_port = str(self.getInstanceFreePort(instance_id))
                        node_vnc_port = str(self.getInstanceFreePort(instance_id))
                        kvm.createVmByQcow2Telnet(id, cpu, ram, interfaces, image_name, id, node_telnet_port, node_vnc_port)
                    else: 
                        node_vnc_port = str(self.getInstanceFreePort(instance_id))
                        kvm.createVmByQcow2(id, cpu, ram, interfaces, image_name, id, node_vnc_port)
                    self.redis_util.updateNodeProgressStatus(instance_id=instance_id, node_id=id, status=12, description="设备启动中")
            nodes_spend = getTimeDifference(nodes_create_start_time, datetime.now())
            update_data = vars(ProgressStepData(name="nodes", label="创建节点", status=2, detail=[], spend_time=nodes_spend))
            self.redis_util.updateProgressRedisStepValue(instance_id=instance_id, update_data=update_data, step_name="nodes")
            self.redis_util.updateProgressDataStepStatus(instance_id=instance_id, status=1, host_status=2, networks_status=2, 
                                                            nodes_status=2, schedule=85, queue_status=2, login_status=1)
            

            logger.info(f"实例ID:{instance_id}, 将节点未插线的接口置为Down状态")
            self.redis_util.addProgressDataStepStartTime(instance_id=instance_id, step="login")
            for node in nodes:
                for interface in node["node_interface"]:
                    if interface.get("status") == "unplugged":
                        kvm.downVmInterface(vm_id=node["id"], interface_index=interface["index"])
            

            logger.info(f"实例ID:{instance_id}, 尝试获取节点console管理方式")
            nodes_logins = Instance.generateNodesLoginData(template_data, request_host, mgt_nodes, instance_id)
            self.cloud_lab_instance_sql.updateInstanceOnDeploy(instance_id=instance_id, nodes_login=json.dumps(nodes_logins),
                                                               create_host_time=create_host_time)
            for node in nodes_logins:
                for login_key in nodes_logins[node]:
                    if login_key == "console": 
                        vnc_port = kvm.getVncPort(vm=node)
                        public_port = cloudlab.getFreePort(linux_util.host)
                        public_port = str(public_port)
                        public_manage = linux_util.host + ":" + public_port
                        instance_manage = instance_ip + ":" + vnc_port
                        rule = linux_util.addIptablesRule(source_port=public_port, dst_ip_port=instance_manage)
                        logger.info(f"生成Console管理方式,实例ID:{instance_id},节点ID:{login_key}, VNC port: {vnc_port}")
                        iptables_rule = iptables_rule + ";" + rule
                        nodes_logins[node][login_key]["instance_manage"] = instance_manage
                        nodes_logins[node][login_key]["public_manage"] = public_manage
                        node_progress_data = self.redis_util.getNodeProgress(instance_id, node)
                        node_progress_data['login'] = nodes_logins[node]
                        self.redis_util.updateNodeProgress(instance_id, node, node_progress_data)

                    if login_key == "console_telnet": 
                        public_port = cloudlab.getFreePort(linux_util.host)
                        public_port = str(public_port)
                        public_manage = linux_util.host + ":" + public_port
                        instance_manage = instance_ip + ":" + node_telnet_port
                        rule = linux_util.addIptablesRule(source_port=public_port, dst_ip_port=instance_manage)
                        logger.info(f"生成Console管理方式,实例ID:{instance_id},节点ID:{login_key}, telnet port: {node_telnet_port}")
                        iptables_rule = iptables_rule + ";" + rule
                        nodes_logins[node][login_key]["instance_manage"] = instance_manage
                        nodes_logins[node][login_key]["public_manage"] = public_manage
                        node_progress_data = self.redis_util.getNodeProgress(instance_id, node)
                        node_progress_data['login'] = nodes_logins[node]
                        self.redis_util.updateNodeProgress(instance_id, node, node_progress_data)
            self.redis_util.updateProgressDataStepStatus(instance_id=instance_id, status=2, host_status=2,
                            networks_status=2, nodes_status=2, schedule=100, queue_status=2, login_status=2)
            self.redis_util.setInstanceTTL(instance_id=instance_id)
            create_time = datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
            actual_time = int((datetime.now() - create_time).total_seconds()) 
            self.cloud_lab_instance_sql.updateInstanceOnDeploy(instance_id=instance_id, iptables_rule=iptables_rule, 
                                                            status=2, mgt_port=libvirt_port, mgt_ip=instance_ip,
                                                            ssh_port=str(ssh_port), actual_time= actual_time, 
                                                            nodes_login=json.dumps(nodes_logins))
            linux_util.close_all(), kvm.close_all()

            logger.info(f"实例ID:{instance_id}, 推送节点信息到初始化节点配置队列")
            for node in nodes:
                instance_server_data = {
                    "hostname": linux_util.host,
                    "libvirt_port": libvirt_port,
                    "ssh_port": ssh_port,
                    "username": KvmConfig['instance_username'],
                    "password": KvmConfig['instance_password']
                }
                server_host_data = {
                    "hostname": linux_util.host,
                    "libvirt_port": linux_util.libvirt_port,
                    "ssh_port": linux_util.port,
                    "username": linux_util.username,
                    "password": linux_util.password
                }
                produce_data = {
                    "retry_count": 0,
                    "instance_id": instance_id,
                    "node_id": node["id"],
                    "image_key": node["image_key"],
                    "node_interface": node["node_interface"],
                    "mgt_nodes": mgt_nodes,
                    "create_time": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                    "last_consumption_time": "",
                    "instance_server_data": instance_server_data,
                    "server_host_data": server_host_data,
                    "instance_ip": instance_ip,
                    "node_name": node["name"]
                }
                KafkaProducer().produce_message(topic=KafkaConfig['topic_node'], message=produce_data)          
            logger.info(f"实例ID:{instance_id}, 实例创建成功")
            return instance_id
        except Exception as error:
            self.cloud_lab_instance_sql.updateInstanceOnDeploy(instance_id=instance_id, status=3)
            self.cloud_lab_server_host_sql.updateServerHost(server_host_data['id'], -instance_cpu, -instance_memory, 
                                                            -server_host_data['instance_storage'])  
            self.redis_util.updateProgressDataStepStatus(instance_id=instance_id, status=3, host_status=2, networks_status=2, 
                                                         nodes_status=3, schedule=100, queue_status=2, login_status=2)
            self.redis_util.closeRedisConnect()
            logger.error(f"实例ID:{instance_id}, 创建实例失败,原因是: {error}")


