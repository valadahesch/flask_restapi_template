import os
import re
import sys
import time
import socket
from netmiko import ConnectHandler
import xml.etree.ElementTree as ET
import paramiko
from app.utils.api_util import AppException
from app.extensions import logger
if not sys.platform.startswith('win'):
    import libvirt


class LinuxUtil:

    def __init__(self, username: str, host: str, port: int, libvirt_port: str, password: str):

        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.libvirt_port = libvirt_port
        self.kvm_client = self.kvmClient()
        self.ssh_config = {
            'device_type': 'linux',
            'host': self.host,
            'username': self.username,
            'password': self.password,
            'port': self.port,
        }
        self.ssh_client = self.sshClient()


    def kvmClient(self):
        try:
            with socket.create_connection((self.host, self.libvirt_port), timeout=1):
                kvm_client = libvirt.open(f"qemu+tcp://{self.host}:{self.libvirt_port}/system")
                if not kvm_client:
                    raise AppException("连接实验服务器失败,请联系管理员")
                return kvm_client
        except (socket.timeout, ConnectionRefusedError):
            raise AppException("连接实验服务器失败,请联系管理员")
        
    def sshClient(self):
        logger.debug(f"准备连接ssh {self.username}@{self.host}:{self.port}")
        
        start_time = time.time()
        connect=None
        try:
            connect= ConnectHandler(**self.ssh_config)
            logger.debug(f"连接ssh {self.username}@{self.host}:{self.port}成功")
        except Exception as e: 
            logger.error(f"连接ssh {self.username}@{self.host}:{self.port}出错：{e}")
        finally:
            time_diff = time.time()-start_time
            logger.debug(f"连接ssh {self.username}@{self.host}:{self.port}耗时：{time_diff:.2f}秒")
            return connect        

    def __ssh_send_command(self,command:str)->str :
        logger.debug(f"准备在{self.host}:{self.port}上执行命令：{command}")
        start_time = time.time()
        output=""
        try:
            output = self.ssh_client.send_command(command, read_timeout=30)
            logger.debug(f"在ssh {self.username}@{self.host}:{self.port}上执行命令{command}成功，输出:{output}")
        except Exception as e: 
            logger.error(f"在{self.host}:{self.port}上执行{command}命令出错：{e}")
        finally:
            time_diff = time.time()-start_time
            logger.debug(f"在{self.host}:{self.port}上执行命令{command}耗时:{time_diff:.2f}秒")
            return output

    def ssh_send_command(self,command:str)->str :
        logger.debug(f"准备在{self.host}:{self.port}上执行命令：{command}")
        try:
            with ConnectHandler(**self.ssh_config) as connect:
                output = connect.send_command(command, read_timeout=30)
                logger.debug(f"在{self.host}:{self.port}上执行命令：{command}的输出:{output}")
                return output
        except Exception as e: 
            logger.error(f"在{self.host}:{self.port}上执行{command}命令出错：{e}")
    
    def ssh_send_batch_command(self,commands:list)->list:
        logger.debug(f"准备在{self.host}:{self.port}上执行批量命令：{commands}")
        batch_start_time = time.time()
        outputs=[]
        try:
            for command in commands:
                output=""
                start_time = time.time()
                try:
                    output = self.ssh_client.send_command(command)
                    outputs.append(output)
                    # logger.debug(f"在ssh {self.username}@{self.host}:{self.port}上执行命令{command}成功，输出:{output}")
                except Exception as e:
                    outputs.append(None)
                    # logger.error(f"在ssh {self.username}@{self.host}:{self.port}上执行命令{command}出错：{e}")
                finally:
                    time_diff = time.time()-start_time
                    # logger.debug(f"在ssh {self.username}@{self.host}:{self.port}上执行命令（耗时:{time_diff:.2f}秒）")
            # logger.debug(f"在ssh {self.username}@{self.host}:{self.port}上执行批量命令{commands}成功，输出:{outputs}")
        except Exception as e: 
            logger.error(f"在ssh {self.username}@{self.host}:{self.port}上执行批量命令{commands}出错：{e}")
        finally:
            batch_time_diff = time.time()-batch_start_time
            logger.debug(f"在ssh {self.username}@{self.host}:{self.port}上执行批量命令{commands}耗时:{batch_time_diff:.2f}秒")
            return outputs
 
    def __ssh_send_batch_command(self,commands:list)->list:
        logger.debug(f"准备在{self.host}:{self.port}上执行批量命令：{commands}")
        batch_start_time = time.time()
        outputs=[]
        try:
            for command in commands:
                output=""
                start_time = time.time()
                try:
                    output = self.ssh_client.send_command(command)
                    outputs.append(output)
                    logger.debug(f"在ssh {self.username}@{self.host}:{self.port}上执行命令{command}成功，输出:{output}")
                except Exception as e:
                    outputs.append(None)
                    logger.error(f"在ssh {self.username}@{self.host}:{self.port}上执行命令{command}出错：{e}")
                finally:
                    time_diff = time.time()-start_time
                    logger.debug(f"在ssh {self.username}@{self.host}:{self.port}上执行命令（耗时:{time_diff:.2f}秒）")
            logger.debug(f"在ssh {self.username}@{self.host}:{self.port}上执行批量命令{commands}成功，输出:{outputs}")
        except Exception as e: 
            logger.error(f"在ssh {self.username}@{self.host}:{self.port}上执行批量命令{commands}出错：{e}")
        finally:
            batch_time_diff = time.time()-batch_start_time
            logger.debug(f"在ssh {self.username}@{self.host}:{self.port}上执行批量命令{commands}耗时:{batch_time_diff:.2f}秒")
            return outputs
        
    def close_all(self):
        try:
            self.kvm_client.close()
        except Exception as e:
            logger.debug(f"关闭KVM({self.host}:{self.libvirt_port})连接失败：{e}")

        try:
            self.ssh_client.disconnect()
        except Exception as e:
            logger.debug(f"关闭KVM SSH({self.host}:{self.libvirt_port})连接失败：{e}")
            
    def isMemoryEnough(self):
        """
        function: 判断服务器内存资源是否充足
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host, username=self.username, password=self.password)
        stdin, stdout, stderr = ssh.exec_command("free -m")
        memory_info_output = stdout.read().decode('utf-8')
        match = re.search(r"Mem:\s+(\d+[\.\d]*)\s+(\d+[\.\d]*)\s+(\d+[\.\d]*)", memory_info_output)
        if match:
            total, used, free = map(float, match.groups())
            if free/total > 0.6:
                return True
            else:
                return False
        return False

    def isCpuEnough(self):
        """
        function: 判断服务器CPU资源是否充足
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.host, username=self.username, password=self.password)
        stdin, stdout, stderr = ssh.exec_command("top -bn1 | grep 'Cpu(s)'")
        cpu_info_output = stdout.read().decode('utf-8')
        match = re.search(r"%Cpu\(s\):\s+(\d+\.\d+)\s+us,\s+(\d+\.\d+)\s+sy,", cpu_info_output)
        if match:
            user_percent, system_percent = map(float, match.groups())
            cpu_used = int(user_percent + system_percent)
            if cpu_used < 60:
                return True
            else:
                return False
        return False


    def getRunningVm(self) -> list:
        running_vm_list = []
        domains = self.kvm_client.listAllDomains(libvirt.VIR_CONNECT_LIST_DOMAINS_RUNNING)
        for domain in domains:
            running_vm_list.append(domain.name())
        return running_vm_list

    def getXmlStr(self, path: str) -> str:
        abspath = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(abspath, path)
        tree = ET.parse(path)
        root = tree.getroot()
        xml_string = ET.tostring(root, encoding='utf-8', method='xml').decode()
        return xml_string

    def getMgtIP(self, vm_name: str = "") -> str :
        """
        function: 获取实例管理地址IP
        return: 网卡名， 网卡IP地址, 网卡MAC地址
        """
        try:
            dom = self.kvm_client.lookupByName(vm_name)
            status, _ = dom.state()
            logger.debug(f"vm:{vm_name} status:{status}")
            if status == libvirt.VIR_DOMAIN_RUNNING:
                interfaces = dom.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_LEASE)
                logger.info(f"实例ID:{vm_name}, 获取虚拟机接口信息{interfaces}")
                if interfaces:
                    for (name, val) in interfaces.items():
                        return val['addrs'][0]['addr']
        except libvirt.libvirtError as le:
            logger.error(f"libvirtError:{le}")
            return None
        except Exception as e:
            logger.error(f"Exception:{e}")


    def deleteVm(self, vm_id: str = "") -> str:
        """
        function: 删除实例
        """
        try:
            dom = self.kvm_client.lookupByName(vm_id)
            command = f""" virsh dumpxml {vm_id} """
            command = command + """ | grep "source file" | awk -F"'" '{print $2}'  """
            output=self.__ssh_send_command(command)
            disk_path = re.compile(r'(.*)/([^/]+)$').match(output.replace("\n", "")).group(1)
            logger.info(f"虚拟机{vm_id}的磁盘路径为: {disk_path}")
            status, _ = dom.state()
            if disk_path:
                command = f"rm -rf {disk_path}"
                if status == libvirt.VIR_DOMAIN_SHUTOFF:
                    dom.undefine()
                else:
                    dom.destroy()
                    dom.undefine()
                self.__ssh_send_command(command)
            return disk_path
        except libvirt.libvirtError:
            logger.error("Unable to open connection to libvirt")

    def getVmStatus(self, vm_id: str = ""):
        """
        function: 获取虚拟机状态
        """
        dom = self.kvm_client.lookupByName(vm_id)
        status, _ = dom.state()
        return status

    def getVncPort(self, vm: str = ""):
        """
        function: 获取实例中虚拟机console管理方式的VNC的端口
        """
        try:
            dom = self.kvm_client.lookupByName(vm)
            xml = dom.XMLDesc(0)
            graphics = re.search(r'<graphics[^>]*>.*?</graphics>', xml, re.DOTALL)
            port = re.search(r"port='(\d+)'", str(graphics))
            return port.group(1)
        except Exception as error:
            logger.error(f"Error: {error}")

    def addIptablesRule(self, source_port: str = "", dst_ip_port: str = "") -> str:
        """
        function: 配置DNAT映射规则，方便于管理实例
        params: source_port访问宿主机的端口， dst_ip_port转换为宿主机内部虚拟机的访问方式
        """
        # try:
        command = f"sudo iptables -t nat -A PREROUTING -p tcp --dport {source_port} -j DNAT --to {dst_ip_port}"
        self.__ssh_send_command(command)
        return command

    def deleteIptablesRule(self, source_port: str = "", dst_ip_port: str = "") -> str:
        """
        function: 删除DNAT规则，用于删除实例场景
        """
        try:
            command = f"sudo iptables -t nat -D PREROUTING -p tcp --dport {source_port} -j DNAT --to {dst_ip_port}"
            output = self.__ssh_send_command(command)
            return output
        except Exception as error:
            logger.error(f"Error: {error}")

    def createNetwork(self, network_id: str = "", network_xml_path: str = "default_xml/network.xml"):
        """
        function: 创建实例网卡
        """
        network_xml = self.getXmlStr(path=network_xml_path)
        network_xml = network_xml.format(network_id=network_id)
        network = self.kvm_client.networkDefineXML(network_xml)
        network.create()
        if network.name():
            network_object = self.kvm_client.networkLookupByName(network_id)
            network_object.setAutostart(True)
        return True

    def createVmByQcow2(self, name: str, cpu: int, ram: int, interfaces: list, image_id: str, node_id: str, node_vnc_port: str):
        """
        function: 创建实例虚拟机
        """
        interfaces_xml, ram = "", ram*1024*1024
        for interface in interfaces:
            interface_name = interface.get("network")[:10]
            interface_xml = self.getXmlStr(path="default_xml/interface.xml")
            interface_xml = interface_xml.format(interface_name=interface_name)
            interfaces_xml += interface_xml
        vm_xml = self.getXmlStr(path="default_xml/vm.xml")
        vm_xml = vm_xml.format(name=name, ram=ram, cpu=cpu, image_id=image_id, node_id=node_id,
                                interfaces_xml=interfaces_xml, vnc_port=node_vnc_port)
        domain = self.kvm_client.defineXML(vm_xml)
        domain.setAutostart(True)
        domain.create()
        return domain.name()
    
    def createVmByQcow2Telnet(self, name: str, cpu: int, ram: int, interfaces: list, image_id: str, node_id: str, telnet_port: str, node_vnc_port: str):
        """
        function: 创建实例虚拟机
        """
        interfaces_xml, ram = "", ram*1024*1024
        for interface in interfaces:
            interface_name = interface.get("network")[:10]
            interface_xml = self.getXmlStr(path="default_xml/interface.xml")
            interface_xml = interface_xml.format(interface_name=interface_name)
            interfaces_xml += interface_xml
        vm_xml = self.getXmlStr(path="default_xml/vm_telnet.xml")
        vm_xml = vm_xml.format(name=name, ram=ram, cpu=cpu, image_id=image_id, node_id=node_id, interfaces_xml=interfaces_xml, 
                               telnet_port=telnet_port, vnc_port=node_vnc_port)
        domain = self.kvm_client.defineXML(vm_xml)
        domain.setAutostart(True)
        domain.create()
        return domain.name()

    def createInstance(self, cpu: int, ram: int, instance_id: str, image_id: str, path: str):
        """
        function: 创建实例宿主机
        """
        command = f""" mkdir /cloudlab/images/{instance_id} """
        output = self.__ssh_send_command(command)
        # command = f""" lftp lab.hillstonenet.com -e "get {path}  -o /cloudlab/images/{instance_id}/;quit" """
        command = f"wget -P /cloudlab/images/{instance_id}/ http://lab.hillstonenet.com{path}"
        output = self.__ssh_send_command(command)
        vm_xml = self.getXmlStr(path="default_xml/instance.xml")
        vm_xml = vm_xml.format(name=instance_id, ram=ram*1024*1024, cpu=cpu, instance_id=instance_id, image_id=image_id)
        domain = self.kvm_client.defineXML(vm_xml)
        domain.setAutostart(True)
        domain.create()
        return domain.name()
    
    def shutdownVm(self, vm_id: str):
        """
        function: 关闭实例虚拟机,系统层面
        """
        domain = self.kvm_client.lookupByName(vm_id)
        domain.shutdown()
        return domain.name()

    def startVm(self, vm_id: str):
        """
        function: 开启实例虚拟机
        """
        domain = self.kvm_client.lookupByName(vm_id)
        domain.create()
        return domain.name()
    
    def powerOffVm(self, vm_id: str):
        """
        function: 关闭实例虚拟机，强制断电
        """
        domain = self.kvm_client.lookupByName(vm_id)
        domain.destroy()
        return domain.name()
    
    def restartVm(self, vm_id: str):
        """
        function: 重启虚拟机操作系统(尝试通过 ACPI(高级配置与电源界面)来重启虚拟机)
        """
        domain = self.kvm_client.lookupByName(vm_id)
        domain.reboot(libvirt.VIR_DOMAIN_REBOOT_ACPI_POWER_BTN)
        return domain.name()
    
    def forceReboot(self, vm_id: str):
        """
        function: 强制重启虚拟机(拔掉电源再重新连接)
        """    
        domain = self.kvm_client.lookupByName(vm_id)
        domain.destroy()
        domain = self.kvm_client.lookupByName(vm_id)
        status, _ = domain.state()
        if status == libvirt.VIR_DOMAIN_SHUTOFF:
            domain.create()
            return True
        else:
            return False

    def getMacByNetworkName(self, vm_name: str, network_name: str) -> str :
        """
        function: 在虚拟机中根据网卡名查询对应mac(不适用于虚拟机中存在多个网卡具有相同网卡名)
        """
        mac = None
        command = f"virsh domiflist {vm_name}"
        out_put = self.__ssh_send_command(command)
        lines = out_put.strip().split('\n')[2:]
        for line in lines:
            parts = line.split()
            if len(parts) == 5 and parts[2] == network_name:
                mac = parts[4]
        return mac

    def updateNetWorkHot(self, vm_name: str, old_network_name: str, new_network_name: str, reboot: bool = False) -> str:
        """
        function: 在不修改mac情况下,修改接口网卡;
        备注:
            情况一: 接口[ip + mac] ----> 接口[mac]  需要重启
            情况二: 接口[mac] ----> 接口[ip + mac]  无需重启
        """
        network_mac = self.getMacByNetworkName(vm_name, old_network_name)
        dom = self.kvm_client.lookupByName(vm_name)
        xml_desc = f"""
            <interface type='network'>
                <mac address='{network_mac}'/>
                <source network='{new_network_name}'/>
                <model type='e1000'/>
            </interface>
        """
        dom.updateDeviceFlags(xml_desc, flags=libvirt.VIR_DOMAIN_AFFECT_LIVE | libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        if reboot:
            time.sleep(1)
            self.restartVm(vm_name)
        return dom.name()    

    def downVmInterface(self, vm_id: str, interface_index: int):
        """
        function: 把虚拟机的指定接口的物理状态置于DOWN状态
        """
        command = f"virsh domiflist {vm_id}"
        out_put = self.__ssh_send_command(command)
        lines = out_put.strip().split('\n')[2:]
        commands=[]
        interface = lines[interface_index].split()
        commands.append(f"""virsh domif-setlink {vm_id} {interface[0]} down """)
        commands.append(f"""virsh domif-setlink {vm_id} {interface[4]} down --config""")
        self.__ssh_send_batch_command(commands)
        return True

    def upVmInterface(self, vm_id: str, interface_index: int):
        """
        function: 把虚拟机的指定接口的物理状态置于UP状态
        """
        command = f"virsh domiflist {vm_id}"
        out_put = self.__ssh_send_command(command)
        commands=[]
        lines = out_put.strip().split('\n')[2:]
        interface = lines[interface_index].split()
        commands.append(f"""virsh domif-setlink {vm_id} {interface[0]} up""")
        commands.append(f"""virsh domif-setlink {vm_id} {interface[4]} up --config""")
        self.__ssh_send_batch_command(commands)
        return True

    def addNetWorkCold(self, vm_name: str, network_name: str, network_type: str) -> str:
        """
        function: 虚拟机关机状态下添加网卡
        params: 
            vm_name: 虚拟机名称;
            network_name: 网卡名称;
            network_type: 网卡类型(e1000, rtl8139, virtio);
            备注: virtio支持热插拔;
        """
        dom = self.kvm_client.lookupByName(vm_name)
        xml_desc = f"""
            <interface type='network'>
            <source network='{network_name}'/>
            <model type='{network_type}'/>
            </interface>
        """
        dom.attachDevice(xml_desc)
        return dom.name()

    def deleteNetworkCold(self, vm_name: str, network_name: str, mac: str) -> str:
        """
        function: 虚拟机关机状态下删除网卡；
        params:
            mac: 格式:"52:54:00:40:07:4a"
        """
        dom = self.kvm_client.lookupByName(vm_name)
        xml_desc = f"""
            <interface type='network'>
                <mac address='{mac}'/>
                <source network='{network_name}'/>
            </interface>
        """
        dom.detachDevice(xml_desc)
        return dom.name()

    def addNetWorkHot(self, vm_name: str, network_name: str, network_type: str) -> str:
        """
        function: 虚拟机开机状态下添加网卡
        """
        dom = self.kvm_client.lookupByName(vm_name)
        xml_desc = f"""
            <interface type='network'>
            <source network='{network_name}'/>
            <model type='{network_type}'/>
            </interface>
        """
        dom.attachDeviceFlags(xml_desc)
        return dom.name()

    def deleteNetworkHot(self, vm_name: str, network_name: str, mac: str) -> str:
        """
        function: 虚拟机开机状态下删除网卡(linux支持, StoneOS支持但操作复杂不建议使用)
        """
        dom = self.kvm_client.lookupByName(vm_name)
        xml_desc = f"""
            <interface type='network'>
                <mac address='{mac}'/>
                <source network='{network_name}'/>
            </interface>

        """
        dom.detachDeviceFlags(xml_desc, flags=libvirt.VIR_DOMAIN_AFFECT_CONFIG)
        return dom.name()
    

