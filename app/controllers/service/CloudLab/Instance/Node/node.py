import json
import sys
import time
import requests
import paramiko
import threading
from datetime import datetime
from netmiko import ConnectHandler
from app.config import KvmConfig
from app.extensions import logger
from app.utils.func_util import nanoId
from app.config import KvmConfig, KafkaConfig
from app.utils.kafka_util import KafkaProducer
from app.utils.api_util import AppException
from app.utils.kvm.linux_util import LinuxUtil
from app.controllers.service.CloudLab import CloudLab
from app.controllers.dao.cloud_lab_redis_dao import RedisUtils
from app.controllers.service.CloudLab.Instance import Instance
from app.utils.func_util import getIpPort, JwtTokenAuth, scanOpenPort, getMd5sum
from app.controllers.dao.cloud_lab_dao import CloudLabUserTemplateInstanceDao, CloudLabImageDao, CloudLabNodeDao,\
                                            CloudLabServerHostDao, CloudLabTemplateDao
from app.controllers.dao.techadmin_dao import SysUserDao
if not sys.platform.startswith('win'):
    import libvirt


class Node:

    def __init__(self) -> None:
        self.cloud_lab_instance_sql = CloudLabUserTemplateInstanceDao()
        self.cloud_lab_template_sql = CloudLabTemplateDao()
        self.cloud_lab_server_host_sql = CloudLabServerHostDao()
        self.cloud_lab_node_sql = CloudLabNodeDao()
        self.cloud_lab_image_sql = CloudLabImageDao
        self.cloud_lab_user_sql = SysUserDao()
        self.redis_util = RedisUtils()
    
    @staticmethod
    def sshCommand(hostname: str,  port: int, initial_configuration: dict, node_id: str, node_name: str,instance_id: str,
                   username: str = "hillstone", password: str = "hillstone"):
        logger.debug(f"{instance_id} {node_id} ssh {username}@{hostname} -p {port} {initial_configuration}")
        init_cmd = initial_configuration.get("init_cmd")
        change_password = initial_configuration.get("change_password")

        if init_cmd:
            ssh_config = {
                'device_type': 'linux',
                'host': hostname,
                'port': port,
                'username': username,
                'password': password,
                'global_delay_factor': 0,
            }
            start_time = time.time()
            command_list = init_cmd
            try:
                with ConnectHandler(**ssh_config) as connect:
                    time_diff = time.time()-start_time
                    logger.debug(f"连接ssh {ssh_config['username']}@{ssh_config['host']}:{ssh_config['port']}成功，耗时：{time_diff:.2f}秒")
                    for command in command_list:
                        logger.info(f"the command is [before format]: {command} , instance id is {instance_id}, node id {node_id}")
                        command = command.format(node_id=node_id, node_name=node_name, instance_id=instance_id)
                        logger.info(f"the command is [after format]: {command}, instance id is {instance_id}, node id {node_id}")
                        start_time = time.time()
                        output = connect.send_command(command, read_timeout=5*60)
                        time_diff = time.time()-start_time
                        logger.debug(f"instance id {instance_id},node id {node_id} 在ssh {ssh_config['username']}@{ssh_config['host']}:{ssh_config['port']}执行{command}命令，耗时：{time_diff:.2f}秒，输出{output}")
                
            except Exception as e: 
                logger.error(f"在ssh {ssh_config['username']}@{ssh_config['host']}:{ssh_config['port']}上执行命令出错：{e}")      

        if change_password:
            trans = paramiko.Transport((hostname, port))
            trans.banner_timeout = 1000
            command_list = [password, password, "save", "y", "y"]
            password = change_password
            try:
                trans.connect(username=username, password=password)
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh._transport = trans
                shell = ssh.invoke_shell()
                time.sleep(1)
                for command in command_list:
                    logger.info(f"the command is [before format]: {command} , instance id is {instance_id}, node id {node_id}")
                    command = command.format(node_id=node_id, node_name=node_name, instance_id=instance_id)
                    logger.info(f"the command is [after format]: {command}, instance id is {instance_id}, node id {node_id}")
                    shell.send('{0}\n'.format(command))
                    time.sleep(0.2)
                time.sleep(2)
                output = shell.recv(4096).decode('utf-8')
                logger.info(f"the instance id is {instance_id},node id {node_id}, output is : {output}")
                shell.close()
                trans.close()
            except Exception as error:
                logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 认证失败, 用户名{username}, 密码{password}, 原因:{error}")


    def powerOnInstanceNode(self, instance_id: str, node_id: str):
        try:
            node_progress_data = self.redis_util.getNodeProgress(instance_id, node_id)
            node_progress_data["status"] = 12
            self.redis_util.updateNodeProgress(instance_id, node_id, node_progress_data)
            power_on_node_thread = threading.Thread(target=self.asyncPowerOnInstanceNode, args=(instance_id, node_id))
            power_on_node_thread.start()
            return True
        except Exception as error:
            logger.error("【cloudlab】: Failed to start node! error data:{}".format(error))
            return False
        
    def asyncPowerOnInstanceNode(self, instance_id: str, node_id: str):
        try:
            instance = self.cloud_lab_instance_sql.getInstanceInfo(instance_id=instance_id)
            server_host_data = instance.get("server_host_data")
            host  =server_host_data["host"]
            mgt_port = instance.get("mgt_port")
            ssh_port = instance.get("ssh_port")
            linux_util = LinuxUtil(host=host, libvirt_port=mgt_port, port=ssh_port, 
                                   username=KvmConfig["instance_username"], password=KvmConfig["instance_password"])
            linux_util.startVm(vm_id=node_id)
            linux_util.close_all()
            return True
        except Exception as error:
            logger.error("【cloudlab】: Failed to start node! error data:{}".format(error))
            return False

    def powerOffInstanceNode(self, instance_id: str, node_id: str):
        try:
            node_progress_data = self.redis_util.getNodeProgress(instance_id, node_id)
            node_progress_data["status"] = 15
            self.redis_util.updateNodeProgress(instance_id, node_id, node_progress_data)
            power_off_node_thread = threading.Thread(target=self.asyncPowerOffInstanceNode, args=(instance_id, node_id))
            power_off_node_thread.start()
            return True
        except Exception as error:
            logger.error("【cloudlab】:Failed to power off node! error data:{}".format(error))
            return False
        
    def asyncPowerOffInstanceNode(self, instance_id: str, node_id: str):
        try:
            instance = self.cloud_lab_instance_sql.getInstanceInfo(instance_id=instance_id)
            server_host_data = instance.get("server_host_data")
            host  =server_host_data["host"]
            mgt_port = instance.get("mgt_port")
            ssh_port = instance.get("ssh_port")
            linux_util = LinuxUtil(host=host, libvirt_port=mgt_port, port=ssh_port, 
                                   username=KvmConfig["instance_username"], password=KvmConfig["instance_password"])
            linux_util.powerOffVm(vm_id=node_id)
            linux_util.close_all()
            return True
        except Exception as error:
            logger.error("【cloudlab】:Failed to power off node! error data:{}".format(error))
            return False
        

    def forceRebootInstanceNode(self, instance_id: str, node_id: str):
        try:
            force_reboot_node_thread = threading.Thread(target=self.asyncForceRebootInstanceNode, args=(instance_id, node_id))
            force_reboot_node_thread.start()
            return True
        except Exception as error:
            logger.error("【cloudlab】: Failed to force reboot node! error data:{}".format(error))
            return False
        
    def asyncForceRebootInstanceNode(self, instance_id: str, node_id: str):
        try:
            instance = self.cloud_lab_instance_sql.getInstanceInfo(instance_id=instance_id)
            server_host_data = instance.get("server_host_data")
            host  =server_host_data["host"]
            mgt_port = instance.get("mgt_port")
            ssh_port = instance.get("ssh_port")
            linux_util = LinuxUtil(host=host, libvirt_port=mgt_port, port=ssh_port,
                                   username=KvmConfig["instance_username"], password=KvmConfig["instance_password"])
            linux_util.forceReboot(vm_id=node_id)
            linux_util.close_all()
            return True
        except Exception as error:
            logger.error("【cloudlab】: Failed to force reboot node! error data:{}".format(error))
            return False

    def shutdownInstanceNode(self, instance_id: str, node_id : str):
        try:
            shutdown_thread = threading.Thread(target=self.asyncShutdownInstanceNode, args=(node_id, instance_id))
            shutdown_thread.start()
            return True
        except Exception as error:
            logger.error("【cloudlab】: Failed to force reboot node! error data:{}".format(error))
            return False
    
    def restartInstanceNode(self, instance_id: str, node_id: str):
        try:
            restart_node_thread = threading.Thread(target=self.asyncRestartInstanceNode, args=(instance_id, node_id))
            restart_node_thread.start()
            return True
        except Exception as error:
            logger.error("【cloudlab】: Failed to force reboot node! error data:{}".format(error))
            return False
        
    def asyncRestartInstanceNode(self, instance_id: str, node_id: str):
        try:
            instance = self.cloud_lab_instance_sql.getInstanceInfo(instance_id=instance_id)
            server_host_data = instance.get("server_host_data")
            host  =server_host_data["host"]
            mgt_port = instance.get("mgt_port")
            ssh_port = instance.get("ssh_port")
            linux_util = LinuxUtil(host=host, libvirt_port=mgt_port, port=ssh_port,
                                   username=KvmConfig["instance_username"], password=KvmConfig["instance_password"])
            linux_util.restartVm(vm_id=node_id)
            linux_util.close_all()
            return True
        except Exception as error:
            logger.error("【cloudlab】: Failed to force reboot node! error data:{}".format(error))
            return False
        
    def asyncShutdownInstanceNode(self, node_id: str, instance_id: str):
        instance = self.cloud_lab_instance_sql.getInstanceInfo(instance_id=instance_id)
        server_host_data = instance.get("server_host_data")
        host  =server_host_data["host"]
        mgt_port = instance.get("mgt_port")
        ssh_port = instance.get("ssh_port")
        linux_util = LinuxUtil(host=host, libvirt_port=mgt_port, port=ssh_port,
                               username=KvmConfig["instance_username"], password=KvmConfig["instance_password"])
        linux_util.shutdownVm(vm_id=node_id)
        time.sleep(15)
        domain = linux_util.kvm_client.lookupByName(node_id)
        status, _ = domain.state()
        linux_util.close_all()
        if status == libvirt.VIR_DOMAIN_SHUTOFF:
            node_progress_data = self.redis_util.getNodeProgress(instance_id, node_id)
            node_progress_data["status"] = 15
            self.redis_util.updateNodeProgress(instance_id, node_id, node_progress_data)
        return True
    
    
    def initializeNode(self, node_data: dict):
        instance_id = node_data.get("instance_id")
        node_id = node_data.get("node_id")
        image_key = node_data.get("image_key")
        mgt_nodes = node_data.get("mgt_nodes")
        instance_server_data = node_data.get("instance_server_data")
        node_interface = node_data.get("node_interface")
        server_host_data = node_data.get("server_host_data")
        instance_ip = node_data.get("instance_ip")
        node_name = node_data.get("node_name")
        logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 实例部署成功,开始针对节点进行初始化配置")  


        nodes_logins = json.loads(self.cloud_lab_instance_sql.getInstanceInfo(instance_id).get("nodes_login"))
        logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 尝试获取nodeslogin配置")
        finish, iptables_rule = False, ""
        cloudlab, instance = CloudLab(), Instance()
        if not scanOpenPort(host=instance_server_data["hostname"], port=instance_server_data["ssh_port"]):
            logger.error(f"实例ID:{instance_id}, 节点ID:{node_id}, 实例宿主机端口不通请排查网络连通性")
            finish = False
            if self.cloud_lab_instance_sql.getInstanceStatus(instance_id) == 7:
                logger.error(f"实例ID:{instance_id}, 节点ID:{node_id}, 实例已经被删除")
                finish = True
        else:
            initial_configuration = self.cloud_lab_image_sql.getImageInitializationOperation(image_key)
            logger.debug(f"实例ID:{instance_id}, 节点ID:{node_id}, 初始化配置内容:{initial_configuration},标注")
            instance_kvm = LinuxUtil(host=instance_server_data["hostname"], libvirt_port=instance_server_data["libvirt_port"],
                                     username=instance_server_data["username"], password=instance_server_data["password"],
                                     port=instance_server_data["ssh_port"])
            host_kvm = LinuxUtil(host=server_host_data["hostname"], libvirt_port=server_host_data["libvirt_port"],
                                 username=server_host_data["username"], password=server_host_data["password"],
                                 port=server_host_data["ssh_port"])
            if node_id in mgt_nodes:
                logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 节点已接入管理网络")
                vm_ip = instance_kvm.getMgtIP(node_id)
                if initial_configuration and vm_ip is not None:
                    self.redis_util.updateNodeProgressStatus(instance_id=instance_id, node_id=node_id, status=12, description="初始化配置中")
                    logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 已获取到节点临时网络IP,该节点需要进行配置下发")
                    init_cmd_insatnce_port = instance.getInstanceFreePort(instance_id)
                    instance_kvm.addIptablesRule(source_port=str(init_cmd_insatnce_port), dst_ip_port=vm_ip + ":22")
                    init_cmd_public_port = cloudlab.getFreePort(server_host_data["hostname"])
                    nat_rule = host_kvm.addIptablesRule(source_port=str(init_cmd_public_port),
                                                        dst_ip_port=instance_ip + ":" + str(init_cmd_insatnce_port))
                    iptables_rule = iptables_rule + ";" + nat_rule
                    logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 节点已分配公网管理端口,尝试探测端口连通性")
                    start_time, node_port_status = datetime.now(), False
                    while not node_port_status and int((datetime.now()-start_time).total_seconds()) < 60:
                        node_port_status=scanOpenPort(host=host_kvm.host, port=init_cmd_public_port)
                        time.sleep(1)

                    if node_port_status:
                        username, password = self.cloud_lab_image_sql.getImageLoginInfo(image_key)
                        logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 节点用户名密码:{username}, {password}")
                        logger.debug(f"实例ID:{instance_id}, 节点ID:{node_id} 准备连接ssh {username}@{host_kvm.host}:{init_cmd_public_port} 执行：{initial_configuration}")
                        Node.sshCommand(hostname=host_kvm.host, port=int(init_cmd_public_port), username=username,
                                        initial_configuration=initial_configuration, password=password, node_id=node_id,
                                        node_name=node_name, instance_id=instance_id)
                        interface_index_0 = node_interface[0]["old_network"][:10]
                        self.redis_util.updateNodeProgressStatus(instance_id=instance_id, node_id=node_id, status=12, description="设备正在切换网络")
                        instance_kvm.updateNetWorkHot(vm_name=node_id, new_network_name=interface_index_0, old_network_name="init_cmd")
                        instance_kvm.downVmInterface(vm_id=node_id, interface_index=0)
                        time.sleep(5)
                        instance_kvm.upVmInterface(vm_id=node_id, interface_index=0)
                        time.sleep(1)
                        logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 切换接口网卡成功, 重新获取IP以生成登录方式")
                        start_time = datetime.now()
                        while not instance_kvm.getMgtIP(node_id):
                            if int((datetime.now() - start_time).total_seconds()) > 60:
                                logger.debug(f"实例ID:{instance_id}, 节点ID:{node_id}, 切换网卡后节点超过60s未获取到IP,非console管理方式失效")
                                finish = True
                                break
                            else:
                                time.sleep(1)
                        vm_ip = instance_kvm.getMgtIP(node_id)
                        if vm_ip:
                            initial_configuration = None
                if not initial_configuration and vm_ip is not None:
                    logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 节点接入管理网但是不需要下发配置或者已经完成下发配置, 生成登录信息")
                    self.redis_util.updateNodeProgressStatus(instance_id=instance_id, node_id=node_id, status=12, description="生成非console登录信息中")
                    for node_key in nodes_logins:
                        if node_key == node_id:
                            for login_key in nodes_logins[node_key]:
                                vm_manage_port = nodes_logins[node_key][login_key].get("vm_manage_port")
                                if vm_manage_port:
                                    vm_manage = vm_ip + ":" + vm_manage_port
                                    instance_port = instance.getInstanceFreePort(instance_id)
                                    instance_kvm.addIptablesRule(source_port=str(instance_port), dst_ip_port=vm_manage)
                                    instance_manage = instance_ip + ":" + str(instance_port)
                                    public_port = cloudlab.getFreePort(server_host_data["hostname"])
                                    nat_rule = host_kvm.addIptablesRule(source_port=str(public_port), dst_ip_port=instance_manage)
                                    iptables_rule = iptables_rule + ";" + nat_rule
                                    public_manage = host_kvm.host + ":" + str(public_port)
                                    nodes_logins[node_key][login_key]["vm_manage"] = vm_manage
                                    nodes_logins[node_key][login_key]["instance_manage"] = instance_manage
                                    nodes_logins[node_key][login_key]["public_manage"] = public_manage
                            node_progress_data = self.redis_util.getNodeProgress(instance_id, node_id)
                            node_progress_data['login'] = nodes_logins[node_key]
                            self.redis_util.updateNodeProgress(instance_id, node_id, node_progress_data)
                    finish = True
                    logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 已生成节点非console登录信息")
                    instance_kvm.close_all()
                    
            if initial_configuration and node_id not in mgt_nodes:
                logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 设备未接入管理网但是需要初始化配置")
                if node_data.get("retry_count") == 0:
                    instance_kvm.upVmInterface(vm_id=node_id, interface_index=0)
                node_ip = instance_kvm.getMgtIP(node_id)
                if node_ip:
                    self.redis_util.updateNodeProgressStatus(instance_id=instance_id, node_id=node_id, status=12, description="初始化配置中")
                    logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 设备未接入管理网但是需要下发配置, 已获取到设备临时网络IP")
                    init_cmd_insatnce_port = instance.getInstanceFreePort(instance_id)
                    instance_kvm.addIptablesRule(source_port=str(init_cmd_insatnce_port), dst_ip_port=node_ip + ":22")
                    init_cmd_public_port = cloudlab.getFreePort(server_host_data["hostname"])
                    nat_rule = host_kvm.addIptablesRule(source_port=str(init_cmd_public_port),
                                                        dst_ip_port=instance_ip + ":" + str(init_cmd_insatnce_port))
                    iptables_rule = iptables_rule + ";" + nat_rule
                    while not scanOpenPort(host=host_kvm.host, port=init_cmd_public_port):
                        time.sleep(1)
                    username, password = self.cloud_lab_image_sql.getImageLoginInfo(image_key)
                    logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 节点用户名密码:{username}, {password},节点镜像{image_key}")
                    Node.sshCommand(hostname=host_kvm.host, port=int(init_cmd_public_port), username=username,
                                    initial_configuration=initial_configuration, password=password, node_id=node_id,
                                    node_name=node_name, instance_id=instance_id)
                    interface_index_0 = node_interface[0]["old_network"][:10]
                    self.redis_util.updateNodeProgressStatus(instance_id=instance_id, node_id=node_id, status=12, description="设备正在切换网络")
                    instance_kvm.updateNetWorkHot(vm_name=node_id, new_network_name=interface_index_0, old_network_name="init_cmd")
                    instance_kvm.downVmInterface(vm_id=node_id, interface_index=0)
                    time.sleep(1)
                    if node_interface[0]["status"] == "up":
                        instance_kvm.upVmInterface(vm_id=node_id, interface_index=0)
                    finish = True
                    instance_kvm.close_all()
                logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 设备未接入管理网但是需要下发配置, 未获取到设备临时网络IP")

            if not initial_configuration and node_id not in mgt_nodes:
                logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 设备未接入管理网并且不需要下发配置,无需任何操作")
                finish = True

        if finish:
            self.redis_util.updateNodeProgressStatus(instance_id=instance_id, node_id=node_id, status=2, description="设备初始化成功")
            self.cloud_lab_instance_sql.updateInstanceOnDeploy(instance_id=instance_id, iptables_rule=iptables_rule)
            logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 初始化节点成功")
        if not finish:
            time.sleep(2)
            msg_id=nanoId()
            node_data["msg_id"] = msg_id
            node_data["retry_count"] = node_data["retry_count"] + 1
            node_data["last_consumption_time"] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            create_time =  datetime.strptime(node_data['create_time'], "%Y-%m-%d %H:%M:%S")
            spend_time = int((datetime.now() - create_time).total_seconds())
            if spend_time < 600:
                KafkaProducer().produce_message(topic=KafkaConfig['topic_node'], message=node_data)
                logger.info(f"实例ID:{instance_id}, 节点ID:{node_id}, 初始化节点失败,重新推入队列[消息ID:{msg_id}]再次尝试")
            else:
                self.redis_util.updateNodeProgressStatus(instance_id=instance_id, node_id=node_id, status=3, description="设备初始化失败")
                logger.error(f"实例ID:{instance_id}, 节点ID:{node_id}, 初始化节点失败,初始化时间已超过10分钟")
        self.redis_util.closeRedisConnect()
        return instance_id


    def nodeLogin(self, instance_id: str, node_id: str, login_key: str, user_id: str, request_host: str) -> dict:
        node_data =  self.redis_util.getNodeProgress(instance_id, node_id)
        node_login_info = node_data['login'][login_key]
        login_mode = node_login_info.get("type")
        system_user_info = self.cloud_lab_user_sql.queryUsernameByUserId(user_id)
        public_manage = getIpPort(node_login_info.get("public_manage"))
        if len(public_manage[0]) < 7:
            raise AppException("设备正在启动或者未启动, 请检查设备状态！")
        if not scanOpenPort(host=public_manage[0], port=public_manage[1]):
            raise AppException("设备正在启动或者未启动, 请检查设备状态！")
        else:
            redis_key = f"techadmin:cloudlab:{instance_id}:{node_id}:{login_key}"
            payload = {"user_id": user_id, "instance_id": instance_id}
            token = JwtTokenAuth().generateToken(payload=payload)
            instance_name, node_name = self.cloud_lab_instance_sql.getInstanceNodeName(instance_id, node_id)
            redis_value = {
                "user_id": user_id,
                "user_name": system_user_info.get("user_name"),
                "host": public_manage[0],
                "port": public_manage[1],
                "login_user": node_login_info.get("username"),
                "login_password": node_login_info.get("password"),
                "login_mode": login_key,
                "token": token,
                "instance_redis_key": f"ttl:cloudlab:{instance_id}:delete",
                "instance_name": instance_name,
                "node_name": node_name,
                "login_name": node_login_info.get("name")
            }
            self.redis_util.setNodeLoginKey(key=redis_key, value=redis_value)
            url = f"https://{request_host}/webagent/manager/{instance_id}/{node_id}/{login_key}?token={token}"
            if login_mode == "webui":
                proxy_server = KvmConfig["proxy_server"]
                proxy_server_token = KvmConfig["proxy_server_token"]
                session_id = getMd5sum(node_id + ":" + login_key)
                url = f"https://{proxy_server}/node?session_id={session_id}"
                header = {"Authorization": proxy_server_token}
                data = {
                    "node_id": node_id,
                    "login_key": login_key,
                    "scheme": node_login_info.get("protocol") or "https",
                    "host": public_manage[0],
                    "port": public_manage[1],
                    "username": node_login_info.get("username"),
                    "password": node_login_info.get("password"),
                    "set_host": f"{session_id}.{proxy_server}",
                    "referer": f"https://{session_id}.{proxy_server}/",
                    "login_page_uri": node_login_info.get("login_page_uri") or ["/"],
                    "auth_token": token,
                    "user_id": system_user_info.get("user_id"),
                    "user_display_name": system_user_info.get("display_name"),
                    "login_name": node_login_info.get("name"),
                    "instance_name": instance_name,
                    "node_name": node_name
                }
                resp = requests.post(headers=header, json=data, url=url).text
                logger.info(f"web代理服务器响应结果:{resp}")
                url = f"https://{proxy_server}/login?session_id={session_id}&token={token}"
        self.redis_util.closeRedisConnect()
        return {"url": url}
    

    def portOperations(self, instance_id: str, action: str, port_id: str) -> None:
        template_view_data, template_data = self.cloud_lab_instance_sql.getViewData(instance_id=instance_id)
        cells = template_view_data.get("cells")
        edges, edges_data = [], []
        for cell in cells:
            if cell["graph"]["shape"] == "edge":
                edges.append(cell)
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
        server_host_data = self.cloud_lab_instance_sql.getInstanceServerHostData(instance_id)
        login_data = self.cloud_lab_instance_sql.getInstanceHostData(instance_id)
        linux_util = LinuxUtil(host=server_host_data["host"], username=KvmConfig["instance_username"], 
                               port=login_data.get("ssh_port"), password=KvmConfig["instance_password"], 
                               libvirt_port=login_data.get("libvirt_port"))
        for edge in edges_data:
            if edge["source_node_port"] == port_id:
                node_id = edge["source_node"]
                peer_node_id = edge["dst_node"]
                peer_port_id = edge["dst_node_port"]
            if edge["dst_node_port"] == port_id:
                node_id = edge["dst_node"]
                peer_node_id = edge["source_node"]
                peer_port_id = edge["source_node_port"]  

        interface_name = None
        for node in template_data.get("nodes"):
            if node.get("id") == node_id:
                for interface in node.get("node_interface"):
                    if interface.get("id") == port_id:
                        interface_name = interface.get("network")[:10]
                        interface_index = interface.get("index")
        # 主动操作的一段是傻瓜交换机类
        if interface_name is None:
            if action == "up":
                active_node_progress = self.redis_util.getNodeProgress(instance_id, node_id)
                for port in active_node_progress["port_status"]:
                    if port["id"]== port_id:
                        port["status"] = "up"
                self.redis_util.setNodeProgress(instance_id, node_id, active_node_progress)
            if action == "down":
                active_node_progress = self.redis_util.getNodeProgress(instance_id, node_id)
                for port in active_node_progress["port_status"]:
                    if port["id"]== port_id:
                        port["status"] = "active_down"
                self.redis_util.setNodeProgress(instance_id, node_id, active_node_progress)
        # 主动操作的一端是虚拟机
        else:
            if action == "up":
                linux_util.upVmInterface(vm_id=node_id, interface_index=interface_index)
                active_node_progress = self.redis_util.getNodeProgress(instance_id, node_id)
                for port in active_node_progress["port_status"]:
                    if port["id"]== port_id:
                        port["status"] = "up"
                self.redis_util.setNodeProgress(instance_id, node_id, active_node_progress)
            if action == "down":
                linux_util.downVmInterface(vm_id=node_id, interface_index=interface_index)
                active_node_progress = self.redis_util.getNodeProgress(instance_id, node_id)
                for port in active_node_progress["port_status"]:
                    if port["id"]== port_id:
                        port["status"] = "active_down"
                self.redis_util.setNodeProgress(instance_id, node_id, active_node_progress)
        
    
        peer_interface_name = None
        for node in template_data.get("nodes"):
            if node.get("id") == peer_node_id:
                for interface in node.get("node_interface"):
                    if interface.get("id") == peer_port_id:
                        peer_interface_name = interface.get("network")[:10]
                        peer_interface_index = interface.get("index")
         # 被动操作的一端是傻瓜交换机类
        if peer_interface_name is None:
            if action == "up":
                passive_node_progress = self.redis_util.getNodeProgress(instance_id, peer_node_id)
                for port in passive_node_progress["port_status"]:
                    if port["id"]== peer_port_id:
                        port["status"] = "up"
                self.redis_util.setNodeProgress(instance_id, peer_node_id, passive_node_progress)
            if action == "down":
                passive_node_progress = self.redis_util.getNodeProgress(instance_id, peer_node_id)
                for port in passive_node_progress["port_status"]:
                    if port["id"]== peer_port_id:
                        port["status"] = "passive_down"
                self.redis_util.setNodeProgress(instance_id, peer_node_id, passive_node_progress)
        # 被动操作的一端是虚拟机
        else:
            if action == "up":
                linux_util.upVmInterface(vm_id=peer_node_id, interface_index=peer_interface_index)
                passive_node_progress = self.redis_util.getNodeProgress(instance_id, peer_node_id)
                for port in passive_node_progress["port_status"]:
                    if port["id"]== peer_port_id:
                        port["status"] = "up"
                self.redis_util.setNodeProgress(instance_id, peer_node_id, passive_node_progress)
            if action == "down":
                linux_util.downVmInterface(vm_id=peer_node_id, interface_index=peer_interface_index)
                passive_node_progress = self.redis_util.getNodeProgress(instance_id, peer_node_id)
                for port in passive_node_progress["port_status"]:
                    if port["id"]== peer_port_id:
                        port["status"] = "passive_down"
                self.redis_util.setNodeProgress(instance_id, peer_node_id, passive_node_progress)
        self.redis_util.closeRedisConnect()
        linux_util.kvm_client.close()
        return None