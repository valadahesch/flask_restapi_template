# coding: utf-8
from . import db


class PsUserMapping(db.Model):
    __tablename__ = 'ps_user_mapping'

    id = db.Column(db.Integer, primary_key=True, comment='ID')
    project_system_id = db.Column(db.String(20), comment='项目管理系统用户ID')
    technical_department_site_id = db.Column(db.String(20), comment='技术部站点用户ID')


class PsTask(db.Model):
    __tablename__ = 'ps_task'

    id = db.Column(db.Integer, primary_key=True, comment="ID")
    task_id = db.Column(db.String(10), comment="巡检任务ID")
    project_id = db.Column(db.String(10), comment="巡检项目ID")
    is_pass = db.Column(db.String(10), comment="是否校验通过")
    report_file_id = db.Column(db.String(255), comment="上传的文件对象")
    preview_file_id = db.Column(db.String(255), comment="预览文件")
    external = db.Column(db.Text, comment="任务总结")
    inspection_type = db.Column(db.String(255), comment="巡检类型")
    summary_file_id = db.Column(db.String(255), comment="下载总结后文件对象")


class PsTaskUploadHistory(db.Model):
    __tablename__ = "ps_task_upload_history"

    id = db.Column(db.String(20), primary_key=True, comment="ID")
    task_id = db.Column(db.String(20), comment="任务列表ID")
    subject = db.Column(db.String(255), comment="主题")
    file_name = db.Column(db.String(100), comment="文件名称")
    upload_file_id = db.Column(db.String(255), comment="上传的对象文件")
    deciphering = db.Column(db.String(10), comment="是否解析")
    created_by_id = db.Column(db.String(20), comment="创建人")
    created_by_date = db.Column(db.DateTime, comment="创建时间")
    delete_by_id = db.Column(db.String(20), comment="删除人")
    delete_by_date = db.Column(db.DateTime(0), comment="删除时间")
    report_file_id = db.Column(db.String(255), comment="导出报告文件")
    city = db.Column(db.String(255), comment="落地城市")
    area = db.Column(db.String(255), comment="部署区域")
    account_id = db.Column(db.String(50), comment="客户ID")
    account_name = db.Column(db.String(100), comment="客户名称")


class PsCustomerArchives(db.Model):
    __tablename__ = "ps_customer_archives"

    id = db.Column(db.String(20), primary_key=True, comment="ID")
    task_id = db.Column(db.String(20), comment="任务ID")
    city = db.Column(db.String(200), comment="城市")
    account_id = db.Column(db.String(50), comment="客户ID")
    account_name = db.Column(db.String(255), comment="客户名称")
    area = db.Column(db.String(255), comment="部署区域")
    device_name = db.Column(db.String(255), comment="设备名称")
    device_model = db.Column(db.String(255), comment="设备型号")
    device_sn = db.Column(db.String(255), comment="SN")
    ha_state = db.Column(db.String(255), comment="主备状态")
    software_version = db.Column(db.String(255), comment="软件版本")
    uptime = db.Column(db.String(100), comment="运行时间")
    feature = db.Column(db.String(255), comment="开启功能")
    plat_expiration = db.Column(db.String(255), comment="许可证有效期")
    session_info = db.Column(db.Text, comment="并发会话/最大会话")
    alloc_session = db.Column(db.String(255), comment="新建会话")
    cur_cpu = db.Column(db.String(255), comment="cpu利用率")
    cp_memory = db.Column(db.String(255), comment="cp利用率")
    dp_memory = db.Column(db.String(255), comment="dp利用率")
    throughput = db.Column(db.String(255), comment="整机吞吐")
    ps_status = db.Column(db.Text, comment="电源状态")
    fan_status = db.Column(db.Text, comment="风扇状态")
    module_status = db.Column(db.String(255), comment="办卡状态")
    env_cpu_temperature = db.Column(db.String(255), comment="模块温度")
    snat_rate = db.Column(db.String(255), comment="snat使用率")
    dnat_rate = db.Column(db.String(255), comment="dnat使用率")
    address_rate = db.Column(db.String(255), comment="地址簿使用率")
    server_rate = db.Column(db.String(255), comment="服务簿使用率")
    policy_rate = db.Column(db.String(255), comment="策略使用率")
    alg_staus = db.Column(db.Text, comment="ALG状态")
    ha_status_info = db.Column(db.Text, comment="HA状态信息")
    log_folder = db.Column(db.String(255), comment="日志是否开启")
    attack_info = db.Column(db.Text, comment="攻击信息")
    exception_log_info = db.Column(db.Text, comment="异常日志信息")
    clock = db.Column(db.String(255), comment="巡检时间")
    original_manager = db.Column(db.String(255), comment="原厂负责人")
    account_manager = db.Column(db.String(255), comment="客户负责人")
    contact_info = db.Column(db.String(255), comment="联系方式")
    purchase_date = db.Column(db.String, comment="购买时间")
    online_date = db.Column(db.Date, comment="上线时间")
    created_by_id = db.Column(db.String(20), comment="创建人")
    created_by_date = db.Column(db.DateTime, comment="创建时间")
    status = db.Column(db.String(255), comment="状态")
    is_publish = db.Column(db.String(255), comment="是否发布")
    raw_data = db.Column(db.Text, comment="原始数据")
    machine_room = db.Column(db.String(255), comment="机房文职")
    lic_expiration_time = db.Column(db.Date, comment="LIC到期时间")
    route_entry = db.Column(db.String(255), comment="路由条目利用率")
    inspection_type = db.Column(db.String(255), comment="巡检类型")
    compare_main_baseconfig = db.Column(db.Text, comment="主备配置一致性")
    password_policy = db.Column(db.String(255), comment="口令长度与复杂度")
    admin_lockout_duration = db.Column(db.String(255), comment="账号锁定策略")
    unsafe_interface = db.Column(db.String(255), comment="关闭不安全的管理方式")
    admin_host = db.Column(db.String(255), comment="配置可信主机")
    all_passrlue = db.Column(db.String(255), comment="检查是否有全通策略")
    logging_status = db.Column(db.Text, comment="查看事件、警告、配置、操作、威胁日志是否开启")
    log_threat = db.Column(db.Text, comment="Threat安全威胁日志分析")
    log_alarm = db.Column(db.Text, comment="告警日志分析")
    ha_group = db.Column(db.String(255), comment="ha配置检查")
    synced = db.Column(db.String(255), comment="ha统计信息检查")
    poor = db.Column(db.String(255), comment="ha会话同步检查")
    attr_str = db.Column(db.Text, comment="额外字段")
