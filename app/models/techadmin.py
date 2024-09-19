from . import db


class CasbinRule(db.Model):
    __tablename__ = 'casbin_rule'

    id = db.Column(db.Integer, primary_key=True)
    ptype = db.Column(db.String(5), nullable=False)
    v0 = db.Column(db.String(50), nullable=False)
    v1 = db.Column(db.String(50), nullable=False)
    v2 = db.Column(db.String(20))
    v3 = db.Column(db.String(20))
    v4 = db.Column(db.String(20))
    v5 = db.Column(db.String(20))


class SysField(db.Model):
    __tablename__ = 'sys_field'

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(50))
    type = db.Column(db.String(20))
    required = db.Column(db.Integer)
    values = db.Column(db.Text)
    object_id = db.Column(db.String(20))
    create_by = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    update_by = db.Column(db.String(50))
    update_time = db.Column(db.DateTime)
    delete_time = db.Column(db.DateTime)


class SysSubsystemObject(db.Model):
    __tablename__ = 'sys_subsystem_object'

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50))
    type = db.Column(db.Integer)
    parent_id = db.Column(db.String(20))
    description = db.Column(db.String(100))


class SysMenu(db.Model):
    __tablename__ = 'sys_menu'

    id = db.Column(db.String(20), primary_key=True)
    parent_id = db.Column(db.String(20), nullable=False)
    full_path = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(30), nullable=False)
    name = db.Column(db.String(30))
    menu_type = db.Column(db.Integer)
    menu_sort = db.Column(db.Integer)
    page_key = db.Column(db.String(100))
    permission = db.Column(db.String(200))
    link = db.Column(db.String(200))
    link_type = db.Column(db.Integer)
    field_object = db.Column(db.String(200))
    hidden = db.Column(db.Integer)
    create_by = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    update_by = db.Column(db.String(50))
    update_time = db.Column(db.DateTime)
    is_deleted = db.Column(db.Integer)
    deleted_time = db.Column(db.DateTime)


class SysRole(db.Model):
    __tablename__ = 'sys_role'

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(100))
    type = db.Column(db.Integer)
    description = db.Column(db.String(500))
    is_deactivate = db.Column(db.Integer)
    expires_time = db.Column(db.DateTime)
    create_by = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)
    update_by = db.Column(db.String(50))
    update_time = db.Column(db.DateTime)
    is_deleted = db.Column(db.Integer)
    deleted_time = db.Column(db.DateTime)


class SysRoleMenu(db.Model):
    __tablename__ = 'sys_role_menu'

    id = db.Column(db.String(20), primary_key=True)
    role_id = db.Column(db.String(20))
    menu_id = db.Column(db.String(20))
    data_scope = db.Column(db.Integer)
    effect = db.Column(db.String(10))


class SysRoleUser(db.Model):
    __tablename__ = 'sys_role_user'

    id = db.Column(db.String(20), primary_key=True)
    role_id = db.Column(db.String(20))
    user_id = db.Column(db.String(50))


class SysUser(db.Model):
    __tablename__ = 'sys_user'

    id = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.String(50))
    user_name = db.Column(db.String(100))
    dp_name = db.Column(db.String(100))
    display_name = db.Column(db.String(100))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    nick_name = db.Column(db.String(100))
    birthday = db.Column(db.Date)
    user_type = db.Column(db.Integer)
    company_name = db.Column(db.String(100))
    mobile = db.Column(db.String(20))
    email = db.Column(db.String(50))
    time_diff = db.Column(db.Integer)
    oem_brand = db.Column(db.String(100))
    language = db.Column(db.String(20))
    employee_id = db.Column(db.String(100))
    extattr = db.Column(db.Text)
    manage_id = db.Column(db.String(20))
    work_city_adcode = db.Column(db.String(20))
    work_city = db.Column(db.String(100))
    first_login_time = db.Column(db.DateTime)


class TblEmployee(db.Model):
    __tablename__ = 'tbl_employee'

    id = db.Column(db.String(64), primary_key=True)
    userid = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(100))
    mobile = db.Column(db.String(15))
    department = db.Column(db.String(200))
    main_department = db.Column(db.Integer)
    order = db.Column(db.String(200))
    position = db.Column(db.String(50))
    gender = db.Column(db.String(1))
    email = db.Column(db.String(200))
    is_leader_in_dept = db.Column(db.String(200))
    direct_leader = db.Column(db.String(200))
    avatar = db.Column(db.String(200))
    thumb_avatar = db.Column(db.String(200))
    telephone = db.Column(db.String(20))
    alias = db.Column(db.String(100))
    extattr = db.Column(db.String(800))
    extattr_local = db.Column(db.String(800))
    status = db.Column(db.Integer)
    qr_code = db.Column(db.String(200))
    external_profile = db.Column(db.String(500))
    external_position = db.Column(db.String(500))
    employee_number = db.Column(db.String(10))
    address = db.Column(db.String(100))
    leader = db.Column(db.String(64))
    is_deleted = db.Column(db.Integer)
    update_time = db.Column(db.DateTime)


class TblDepartment(db.Model):
    __tablename__ = 'tbl_department'

    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(50), index=True)
    name_en = db.Column(db.String(100), index=True)
    department_leader = db.Column(db.String(32), index=True)
    parentid = db.Column(db.Integer, index=True)
    order = db.Column(db.BigInteger, index=True)
    is_deleted = db.Column(db.Integer)
    update_time = db.Column(db.DateTime)


class SysFieldPermission(db.Model):
    __tablename__ = 'sys_field_permission'

    id = db.Column(db.String(20), primary_key=True)
    role_menu_id = db.Column(db.String(20))
    field_id = db.Column(db.String(20))
    effect = db.Column(db.String(20))


class BusinessLead(db.Model):
    __tablename__ = 'business_leads'

    id = db.Column(db.String(20), primary_key=True)
    contact_name = db.Column(db.String(50), nullable=False)
    contact_role = db.Column(db.SmallInteger, nullable=False)
    contact_way = db.Column(db.String(50), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    crm_customer_id = db.Column(db.String(50), nullable=False)
    crm_customer_name = db.Column(db.String(100), nullable=False)
    crm_owner_id = db.Column(db.String(50), nullable=False)
    crm_owner_name = db.Column(db.String(50), nullable=False)
    province = db.Column(db.String(100))
    city = db.Column(db.String(100))
    description = db.Column(db.String(500))
    lead_code = db.Column(db.String(20))
    lead_id = db.Column(db.String(50))
    email_pushed = db.Column(db.SmallInteger)
    wework_pushed = db.Column(db.SmallInteger)
    create_by = db.Column(db.String(50))
    create_time = db.Column(db.DateTime)


class SysAttachment(db.Model):
    __tablename__ = 'sys_attachment'

    id = db.Column(db.String(50), primary_key=True)
    file_name = db.Column(db.String(100))
    file_type = db.Column(db.String(100))
    file_size = db.Column(db.Integer)
    related_object = db.Column(db.String(20))
    related_object_id = db.Column(db.String(50))
    created_by_id = db.Column(db.String(20))
    created_date = db.Column(db.DateTime)
    deleted_by_id = db.Column(db.String(20))
    deleted_date = db.Column(db.DateTime)


class OperateHistory(db.Model):
    __tablename__ = 'operate_history'

    id = db.Column(db.INTEGER, primary_key=True, comment='ID')
    action = db.Column(db.String(20), comment='动作')
    log = db.Column(db.Text, comment='操作日志')
    created_by_id = db.Column(db.String(20), comment='创建人ID')
    created_date = db.Column(db.DateTime, comment='创建时间')
    target = db.Column(db.String(50), comment='目标')
    target_id = db.Column(db.String(20), comment='目标ID')
    params_data = db.Column(db.Text, comment='参数数据')