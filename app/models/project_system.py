from . import db


class MainCollectField(db.Model):
    __tablename__ = 'main_collect_field'
    __bind_key__ = 'project_system'

    id = db.Column(db.Integer, primary_key=True, comment='ID')
    issue_id = db.Column(db.Integer, comment='Issue_ID')
    org_name = db.Column(db.String(64), comment='客户名称')
    sale = db.Column(db.String(255), comment='销售')
    second_level = db.Column(db.String(255), comment='销售二级部门')
    three_level = db.Column(db.String(255), comment='销售三级部门')
    first_name = db.Column(db.String(255), comment='行业')
    project_name = db.Column(db.String(64), comment='项目名称')
    project_tpl = db.Column(db.String(20), comment='项目类型')
    source = db.Column(db.String(255), comment='项目来源')
    affiliation = db.Column(db.String(255), comment='项目落地')
    major_project = db.Column(db.String(255), comment='项目级别')
    difficulty = db.Column(db.String(255), comment='难度指数')
    Support_types = db.Column(db.String(255), comment='支持类型')
    issue_type = db.Column(db.String(60), comment='任务类型')
    status_name = db.Column(db.String(60), comment='状态')
    Task_level = db.Column(db.String(255), comment='任务级别')
    Security_classification = db.Column(db.String(255), comment='保障类型')
    The_implementation_of_type = db.Column(db.String(255), comment='实施类型')
    product_type = db.Column(db.String(255), comment='产品类型')
    classify = db.Column(db.String(20), comment='业务群')
    city = db.Column(db.String(255), comment='支持城市')
    display_user_name = db.Column(db.String(255), comment='工程师')
    user_area = db.Column(db.String(255), comment='所属区域')
    serv_name = db.Column(db.String(255), comment='服务中心')
    on_business = db.Column(db.String(255), comment='是否出差')
    duration = db.Column(db.Float(10), comment='工时')
    start_date = db.Column(db.DateTime, comment='开始时间')
    due_date = db.Column(db.DateTime, comment='结束时间')
    hsc_type = db.Column(db.String(60), comment='派单类型')
    planned_time = db.Column(db.Float(100), comment='计划耗时')
    summary = db.Column(db.String(255), comment='任务标题')
    creator_name = db.Column(db.String(100), comment='创建人')
    created_time = db.Column(db.String(100), comment='创建时间')
    updated_time = db.Column(db.String(100), comment='更新时间')
    plan_start_time = db.Column(db.DateTime, comment='计划开始时间')
    plan_due_time = db.Column(db.DateTime, comment='计划结束时间')
    uid = db.Column(db.Integer, comment='执行人ID')
    creator_uid = db.Column(db.Integer, comment='创建人ID')
    project_id = db.Column(db.Integer, comment='项目ID')
    agency = db.Column(db.String(255), comment='省份')
    supporting_basis = db.Column(db.String(255), comment='支持依据')
    protocol_number = db.Column(db.String(255), comment='框架协议')
    order_reference = db.Column(db.String(255), comment='服务订单')
    sale_id = db.Column(db.Integer, comment='销售ID')


class MainInventory(db.Model):
    __tablename__ = 'main_inventory'
    __bind_key__ = 'project_system'

    id = db.Column(db.Integer, primary_key=True, comment='ID')
    org_id = db.Column(db.Integer, comment='客户id')
    LIC = db.Column(db.String(255), comment='客户名称')
    devicename = db.Column(db.String(255), comment='设备型号')
    serial_number = db.Column(db.String(255), comment='序列号')
    version = db.Column(db.String(255), comment='软件版本')
    classify = db.Column(db.String(255), comment='业务群')
    pattern = db.Column(db.String(255), comment='部署模式')
    district = db.Column(db.String(255), comment='部署区域')
    product_type = db.Column(db.String(255), comment='产品类型')
    issue_id = db.Column(db.Integer, comment='任务id')
    Launch_date = db.Column(db.Date, comment='上线日期')
    protocol_stack = db.Column(db.String(255), comment='协议栈')
    project_id = db.Column(db.Integer, comment='项目id')
    Dev_Name = db.Column(db.String(255), comment='设备名称')
    Number = db.Column(db.Integer, comment='数量为默认1')
    Service_Validity_Period = db.Column(db.Date, comment='服务有效期')
    Lic_Validity_Period = db.Column(db.Date, comment='许可证有效期')


class MainOrg(db.Model):
    __tablename__ = 'main_org'
    __bind_key__ = 'project_system'

    id = db.Column(db.Integer, primary_key=True, comment="ID")
    path = db.Column(db.String(64), comment="路径")
    name = db.Column(db.String(255), comment="名称")
    description = db.Column(db.Text, comment="描述")
    avatar = db.Column(db.String(256), comment="头像")
    create_uid = db.Column(db.Integer, comment="创建人")
    created = db.Column(db.Integer, comment="创建时间")
    updated = db.Column(db.Integer, comment="更新时间")
    scope = db.Column(db.Integer, comment="权限范围")
    sale = db.Column(db.String(255), comment="销售")
    unit = db.Column(db.String(255), comment="办事处")
    first = db.Column(db.String(255), comment="一级行业")
    second = db.Column(db.String(255), comment="二级行业")
    subid = db.Column(db.Integer, comment="主客户id")
    grade = db.Column(db.String(255), comment="")
    crm_id = db.Column(db.String(255), comment="crmID")


class UserMain(db.Model):
    __tablename__ = "user_main"
    __bind_key__ = "project_system"

    uid = db.Column(db.Integer, primary_key=True, comment="")
    schema_source = db.Column(db.String(12), comment="")
    directory_id = db.Column(db.Integer, comment="")
    phone = db.Column(db.String(16), comment="")
    username = db.Column(db.String(255), comment="")
    openid = db.Column(db.String(32), comment="")
    status = db.Column(db.Integer, comment="")
    first_name = db.Column(db.String(255), comment="")
    last_name = db.Column(db.String(255), comment="")
    display_name = db.Column(db.String(255), comment="")
    display_user_name = db.Column(db.String(255), comment="")
    email = db.Column(db.String(255), comment="")
    password = db.Column(db.String(255), comment="")
    sex = db.Column(db.Integer, comment="")
    birthday = db.Column(db.String(20), comment="")
    create_time = db.Column(db.Integer, comment="")
    update_time = db.Column(db.Integer, comment="")
    avatar = db.Column(db.String(100), comment="")
    source = db.Column(db.String(20), comment="")
    ios_token = db.Column(db.String(128), comment="")
    android_token = db.Column(db.String(128), comment="")
    version = db.Column(db.String(20), comment="")
    token = db.Column(db.String(64), comment="")
    last_login_time = db.Column(db.Integer, comment="")
    is_system = db.Column(db.Integer, comment="")
    login_counter = db.Column(db.Integer, comment="")
    title = db.Column(db.String(32), comment="")
    sign = db.Column(db.String(64), comment="")
    user_area = db.Column(db.String(255), comment="")
    user_rank = db.Column(db.String(255), comment="")
    user_agency = db.Column(db.String(255), comment="")
    user_city = db.Column(db.String(255), comment="")
    initial = db.Column(db.String(255), comment="")
    company = db.Column(db.String(255), comment="")
    hiredate = db.Column(db.Date, comment="")
    classify_ = db.Column(db.String(255), comment="")
    depart_date = db.Column(db.Date, comment="")


class ProjectMain(db.Model):
    __tablename__ = "project_main"
    __bind_key__ = "project_system"

    id = db.Column(db.Integer, primary_key=True, comment="")
    org_id = db.Column(db.Integer, comment="")
    org_path = db.Column(db.String(64), comment="")
    name = db.Column(db.String(64), comment="")
    url = db.Column(db.String(255), comment="")
    lead = db.Column(db.Integer, comment="")
    description = db.Column(db.String(2000), comment="")
    key = db.Column(db.String(80), comment="")
    pcounter = db.Column(db.Integer, comment="")
    default_assignee = db.Column(db.Integer, comment="")
    assignee_type = db.Column(db.Integer, comment="")
    avatar = db.Column(db.String(255), comment="")
    category = db.Column(db.Integer, comment="")
    type = db.Column(db.Integer, comment="")
    type_child = db.Column(db.Integer, comment="")
    permission_scheme_id = db.Column(db.Integer, comment="")
    workflow_scheme_id = db.Column(db.Integer, comment="")
    create_uid = db.Column(db.Integer, comment="")
    create_time = db.Column(db.Integer, comment="")
    un_done_count = db.Column(db.Integer, comment="")
    done_count = db.Column(db.Integer, comment="")
    closed_count = db.Column(db.Integer, comment="")
    archived = db.Column(db.String(), comment="")
    issue_update_time = db.Column(db.Integer, comment="")
    is_display_issue_catalog = db.Column(db.Integer, comment="")
    subsystem_json = db.Column(db.String(5012), comment="")
    project_view = db.Column(db.String(32), comment="")
    issue_view = db.Column(db.String(32), comment="")
    issue_ui_scheme_id = db.Column(db.Integer, comment="")
    project_tpl_id = db.Column(db.Integer, comment="")
    default_issue_type_id = db.Column(db.Integer, comment="")
    is_remember_last_issue = db.Column(db.Integer, comment="")
    remember_last_issue_field = db.Column(db.String(256), comment="")
    remember_last_issue_data = db.Column(db.String(1024), comment="")
    pid = db.Column(db.Integer, comment="")
    project_update_time = db.Column(db.Integer, comment="")
    have_children = db.Column(db.Integer, comment="")
    handover = db.Column(db.String(255), comment="")
    manager = db.Column(db.Integer, comment="")


class FieldCustomValue(db.Model):
    __tablename__ = 'field_custom_value'
    __bind_key__ = 'project_system'

    id = db.Column(db.Integer, primary_key=True, comment='ID')
    issue_id = db.Column(db.Integer, comment='Issue_ID')
    project_id = db.Column(db.Integer, comment='Project_ID')
    custom_field_id = db.Column(db.Integer, comment='Custom_Field_ID')
    parent_key = db.Column(db.String(255), comment='parent_key')
    string_value = db.Column(db.Text, comment='选项值')
    number_value = db.Column(db.String(255), comment='数值')
    text_value = db.Column(db.Text, comment='文本框值')
    date_value = db.Column(db.DateTime, comment='日期')
    value_type = db.Column(db.String(32), comment='类型')
