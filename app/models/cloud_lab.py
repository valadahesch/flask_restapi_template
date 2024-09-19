from . import db


class CloudLabTemplate(db.Model):
    __tablename__ = 'cloud_lab_template'

    id = db.Column(db.String(20), primary_key=True, comment='模板ID')
    name = db.Column(db.String(20), nullable=False, comment='模板名称')
    key = db.Column(db.String(40), nullable=False, comment='模板key')
    description = db.Column(db.String(300), default=None, comment='模板描述')
    enable = db.Column(db.Integer, nullable=False, comment='模板是否启用/发布（常见于管理员新建/管理模板，enable不能编辑）')
    picture = db.Column(db.String(40), nullable=False, comment='模板图片链接')
    template_data = db.Column(db.Text, nullable=False, comment='模板数据')
    create_by = db.Column(db.String(20), default=None, comment='创建人ID')
    create_time = db.Column(db.DateTime, default=None, comment='创建时间')
    create_by_name = db.Column(db.String(40), default=None, comment='创建人名称')
    update_by = db.Column(db.String(20), default=None, comment='最近更新人ID')
    update_time = db.Column(db.String(40), default=None, comment='最近更新时间')
    update_by_name = db.Column(db.String(20), default=None, comment='更新人名称')
    template_data_view = db.Column(db.Text, nullable=False, comment='前端显示模板数据')


class CloudLabUserTemplateInstance(db.Model):
    __tablename__ = 'cloud_lab_user_template_instance'

    id = db.Column(db.String(60), primary_key=True, comment='instance_id')
    user_id = db.Column(db.String(40), nullable=False, comment='用户ID')
    name = db.Column(db.String(40), nullable=False, comment='模板名')
    template_id = db.Column(db.String(40), nullable=False, comment='模板ID')
    create_time = db.Column(db.String(40), default=None, comment='模板创建时间')
    update_time = db.Column(db.String(40), default=None, comment='模板更新时间')
    status = db.Column(db.String(10), nullable=False, comment='状态 using/delete/failure')
    instance_data = db.Column(db.Text, comment='模板数据, 格式参考cell, list(cell)')
    mgt_ip = db.Column(db.String(40), default=None, comment='实例的内网管理IP（连接宿主机MGT网卡）')
    mgt_port = db.Column(db.String(40), default=None, comment='实例的外网libvirt管理端口（内网实例IP映射到宿主机端口）')
    ssh_port = db.Column(db.String(40), default=None, comment='实例的外网ssh管理端口（内网实例IP映射到宿主机端口）')
    nodes_login = db.Column(db.Text, default=None, comment='实例中实验设备的登录信息')
    iptables_rule = db.Column(db.Text, default=None, comment='关联该实例的所有iptables rule方便后续删除')
    template_data = db.Column(db.Text, comment='模板数据, 格式参考cell, list(cell)')
    estimated_time = db.Column(db.String(100), default=None, comment='创建实例预计花费时间')
    exclusive_time = db.Column(db.String(100), default=None, comment='创建实例预计独占时间（不需要排队情况）')
    actual_time = db.Column(db.String(100), default=None, comment='创建实例实际花费时间（包含排队）')
    server_host_data = db.Column(db.Text, default=None, comment='实例所属物理服务器')
    create_host_time = db.Column(db.DATETIME, default=None, comment='创建是实例宿主机时间')
    auto_release_time = db.Column(db.DATETIME, default=None, comment='自动释放时间')
    manual_release_time = db.Column(db.DATETIME, default=None, comment='手动释放时间')


class CloudLabNode(db.Model):
    __tablename__ = 'cloud_lab_node'

    id = db.Column(db.String(10), primary_key=True, comment='设备ID')
    node_key = db.Column(db.String(20), nullable=False, comment='设备 key')
    name = db.Column(db.String(20), nullable=False, comment='设备名称')
    group_name = db.Column(db.String(10), nullable=False, comment='设备类型所属组')
    description = db.Column(db.Text, default=None, comment='设备描述')
    picture_url = db.Column(db.String(255), default=None, comment='设备图标链接')
    cpu = db.Column(db.Integer, nullable=False, comment='设备最低CPU分配')
    memory = db.Column(db.Integer, nullable=False, comment='设备最低内存分配')
    storage = db.Column(db.Integer, default=None, comment='设备存储大小')
    is_active = db.Column(db.Integer, default=None, comment='是否可用')
    is_hide = db.Column(db.Integer, default=None, comment='前端是否隐藏')

class CloudLabImage(db.Model):
    __tablename__ = 'cloud_lab_image'

    id = db.Column(db.String(10), primary_key=True, comment='唯一标识')
    key = db.Column(db.String(50), nullable=False, comment='可读性标识')
    name = db.Column(db.String(50), nullable=False, comment='名称用于显示')
    description = db.Column(db.Text, default=None, comment='描述')
    ip_login_data = db.Column(db.Text, default=None, comment='登录入口数据(仅包含非console数据)')
    path = db.Column(db.String(200), nullable=False, comment='镜像存储路径')
    init_cmd = db.Column(db.Text, nullable=False, comment='初始化后需要执行的命令')
    is_active = db.Column(db.Integer, default=None, comment='是否可用')
    console_login_data = db.Column(db.Text, default=None, comment='登录入口数据(仅包含console方式)')
    action_button = db.Column(db.Text, default=None, comment='开机状态下设备的操作按钮的状态(开关机，强制开关机等)')
    size = db.Column(db.Float, default=None, comment='镜像占用空间GB')
    boot_check_ip = db.Column(db.Boolean, default=None, comment='镜像占用空间GB')
    change_password = db.Column(db.Text, default=None, comment='镜像占用空间GB')
    os_type = db.Column(db.String(100), default=None, comment='镜像占用空间GB')

class CloudLabServerHost(db.Model):
    __tablename__ = 'cloud_lab_server_host'

    id = db.Column(db.String(10), primary_key=True, comment='唯一标识')
    name = db.Column(db.String(20), nullable=False, comment='物理服务器名称')
    ip_address = db.Column(db.String(15), default=None, comment='物理服务器管理IP地址')
    user_name = db.Column(db.String(10), default=None, comment='服务器用户名')
    password = db.Column(db.String(20), default=None, comment='服务器密码')
    is_active = db.Column(db.Boolean, default=None, comment='是否可用')
    cpu = db.Column(db.INT, default=None, comment='CPU核数')
    memory = db.Column(db.INT, default=None, comment='内存大小GB')
    storage = db.Column(db.INT, default=None, comment='硬盘存储空间GB')
    cpu_available = db.Column(db.INT, default=None, comment='可用CPU核数')
    memory_available = db.Column(db.INT, default=None, comment='可用内存大小GB')
    storage_available = db.Column(db.INT, default=None, comment='可用存储空间GB')


class ProgressData:
    def __init__(self, status: int, queue: int, estimate_create_time: int, create_time: str, server_time: str,
                 local_time: str, schedule: int, steps: list):
        self.status = status
        self.queue = queue
        self.estimate_create_time = estimate_create_time
        self.create_time = create_time
        self.server_time = server_time
        self.local_time = local_time
        self.schedule = schedule
        self.step = steps


class ProgressStepData:
    def __init__(self, name: str, label: str, status: int, spend_time: int, detail: list):
        self.name = name
        self.label = label
        self.status = status
        self.spend_time = spend_time
        self.detail = detail


class ProgressStepDetailData:
    def __init__(self, id: str, name: str, status: int):
        self.status = status
        self.id = id
        self.name = name