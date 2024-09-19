from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema


class UserInfo(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'User.info'

    id = fields.Str(metadata={"label": "ID"})
    user_id = fields.Str(metadata={"label": "用户ID"})
    user_name = fields.Str(metadata={"label": "用户名"})
    display_name = fields.Str(metadata={"label": "显示名"})
    first_name = fields.Str(metadata={"label": "姓"})
    last_name = fields.Str(metadata={"label": "名"})
    nick_name = fields.Str(metadata={"label": "昵称"})
    # birthday = fields.Date("%Y-%m-%d", metadata={"label": "生日"})
    user_type = fields.Int(metadata={"label": "用户类型"})
    company_name = fields.Str(metadata={"label": "公司名"})
    mobile = fields.Str(metadata={"label": "电话"})
    email = fields.Str(metadata={"label": "邮箱"})
    time_diff = fields.Int(metadata={"label": "变更次数"})
    oem_brand = fields.Str(metadata={"label": "语言"})
    language = fields.Str(metadata={"label": "语言"})
    profile_url = fields.Str(metadata={"label": "个人信息页面"})


class SysSubsystemObject(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'SubsystemObject'

    id = fields.Str(metadata={"label": "ID"})
    name = fields.Str(metadata={"label": "名称"})
    description = fields.Str(metadata={"label": "描述"})


class SysSubsystemObjectList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SysSubsystemObject(unknown="exclude")))


class SysField(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Field'

    id = fields.Str(metadata={"label": "ID"})
    name = fields.Str(metadata={"label": "字段KEY"})
    label = fields.Str(metadata={"label": "字段名称"})
    ui_type = fields.Str(metadata={"label": "字段类型"}, data_key="type")
    required = fields.Bool(metadata={"label": "必填"})
    values = fields.List(fields.Dict(), metadata={"label": "可选项"})
    object = fields.Str(metadata={"label": "对象KEY"})
    object_id = fields.Str(metadata={"label": "对象ID"})
    object_label = fields.Str(metadata={"label": "对象显示名"})


class SysFieldList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SysField(unknown="exclude")))


class SysDeletedField(SysField):
    __subsystem__ = 'System'
    __object__ = 'deleted_field'

    delete_time = fields.DateTime(format="%Y-%m-%d %H:%M:%S", metadata={"label": "删除时间"})
    expired_time = fields.DateTime(format="%Y-%m-%d %H:%M:%S", metadata={"label": "到期时间"})
    subsystem = fields.Str(metadata={"label": "子系统KEY"})
    subsystem_id = fields.Str(metadata={"label": "子系统ID"})
    subsystem_label = fields.Str(metadata={"label": "子系统显示名"})


class SysDeletedFieldList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SysDeletedField(unknown="exclude")))


class MenuInfo(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Menu.info'

    id = fields.Str(metadata={"label": "功能ID"})
    parentid = fields.Str(metadata={"label": "父节点ID"}, data_key='parent_id')
    hidden = fields.Boolean(metadata={"label": "是否隐藏"}, load_default=False, allow_none=True)
    link = fields.Str(metadata={"label": "链接"}, load_default='', allow_none=True)
    link_type = fields.Int(metadata={"label": "链接类型"}, load_default=0, allow_none=True)
    page_key = fields.Str(metadata={"label": "链接类型"}, load_default='', allow_none=True)
    permission = fields.Str(metadata={"label": "权限标识"}, load_default='', allow_none=True)
    title = fields.Str(metadata={"label": "菜单名称"}, load_default='', allow_none=True)
    type = fields.Int(metadata={"label": "菜单类型"}, data_key='menu_type')
    index = fields.Int(metadata={"label": "排序索引"}, data_key='menu_sort')
    object_id = fields.Str(metadata={"label": "子系统对象ID"}, data_key='field_object', load_default='', allow_none=True)
    object_name = fields.Str(metadata={"label": "子系统对象Key"}, load_default='', allow_none=True)
    object_description = fields.Str(metadata={"label": "子系统对象名称"}, load_default='', allow_none=True)


class MenuInfoList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(MenuInfo(unknown="exclude")))


class PermissionInfo(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Permission.info'

    id = fields.Str(metadata={"label": "权限ID"})
    permission_info = fields.Nested(MenuInfo(exclude=['index'], unknown="exclude"), metadata={"label": "功能信息"})
    data_scope = fields.Int(metadata={"label": "数据范围"}, load_default=0, allow_none=True)
    field_scope = fields.List(fields.Str(), metadata={"label": "字段范围"})
    effect = fields.Str(metadata={"label": "动作"})


class PermissionInfoList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(PermissionInfo(unknown="exclude")))


class EmployeeInfo(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Employee'

    id = fields.Str(metadata={"label": "员工ID"})
    user_id = fields.Str(metadata={"label": "用户ID"}, data_key='userid')
    user_name = fields.Str(metadata={"label": "成员名称"}, data_key='name')
    department = fields.Str(metadata={"label": "部门名称"})
    position = fields.Str(metadata={"label": "职位"})
    gender = fields.Int(metadata={"label": "性别"})
    company_name = fields.Str(metadata={"label": "公司名称"})
    mobile = fields.Str(metadata={"label": "手机号"})
    email = fields.Str(metadata={"label": "邮箱"})
    leader = fields.Str(metadata={"label": "直属上级"}, load_default='', allow_none=True)
    employee_number = fields.Str(metadata={"label": "员工工号"}, load_default='', allow_none=True)
    local_name = fields.Str(metadata={"label": "系统用户名"}, load_default='', allow_none=True)
    extattr_local = fields.Dict(metadata={"label": "附属信息"}, load_default={}, allow_none=True)
    has_the_role = fields.Bool(metadata={"label": "是否附属角色"}, load_default=False, allow_none=True)
    sys_user_id = fields.Str(metadata={"label": "系统用户ID"}, load_default='', allow_none=True)


class EmployeeDetail(ResponseSchema):
    user_detail = fields.Nested(EmployeeInfo(unknown="exclude"))


class EmployeeInfoList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(EmployeeInfo(unknown="exclude")))


class EmployeeSimple(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'EmployeeSimple'

    id = fields.Str(metadata={"label": "员工ID"})
    name = fields.Str(metadata={"label": "成员名称"})
    department_id = fields.Str(metadata={"label": "部门名称"}, data_key='main_department'),
    sys_user_id = fields.Str(metadata={"label": "系统用户ID"})


class EmployeeSimpleList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(EmployeeSimple(unknown="exclude")))


class SysUser(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'SysUser'

    id = fields.Str(metadata={"label": "员工ID"})
    display_name = fields.Str(metadata={"label": "显示名称"})
    company_name = fields.Str(metadata={"label": "公司名称"}, load_default='', allow_none=True)
    user_type = fields.Int(metadata={"label": "用户类型"}, load_default='', allow_none=True)
    mobile = fields.Str(metadata={"label": "手机号"}, load_default='', allow_none=True)
    email = fields.Str(metadata={"label": "邮箱"}, load_default='', allow_none=True)
    is_employee = fields.Bool(metadata={"label": "是否企业员工"}, load_default=False, allow_none=True)
    extattr = fields.List(fields.Dict(), metadata={"label": "附属信息"}, load_default=[], allow_none=True)
    first_login_time = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "首次登陆时间"}, load_default='',
                                       allow_none=True)
    has_the_role = fields.Bool(metadata={"label": "是否附属角色"}, load_default=False, allow_none=True)


class SysUserList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SysUser(unknown="exclude")))


class SysUserDetail(ResponseSchema):
    user_detail = fields.Nested(SysUser(unknown="exclude"))


class SysMenuUser(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'MenuUser'

    id = fields.Str(metadata={"label": "员工ID"})
    name = fields.Str(metadata={"label": "显示名称"}, data_key='display_name')
    employee_name = fields.Str(metadata={"label": "企业用户名"}, data_key='employee_name')


class SysMenuUserList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SysMenuUser(unknown="exclude")))


class SysRoleUser(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'RoleUser'

    id = fields.Str(metadata={"label": "员工ID"})
    local_name = fields.Str(metadata={"label": "显示名称"}, data_key='display_name', load_default='', allow_none=True)
    user_type = fields.Int(metadata={"label": "用户类型"}, load_default=-1, allow_none=True)
    company_name = fields.Str(metadata={"label": "公司名称"}, load_default='', allow_none=True)
    employee_name = fields.Str(metadata={"label": "企业用户名"})
    gender = fields.Int(metadata={"label": "性别"}, load_default=0, allow_none=True)
    department = fields.Str(metadata={"label": "部门"})
    first_login_time = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "首次登陆时间"}, load_default='',
                                       allow_none=True)


class SysRoleUserList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SysRoleUser(unknown="exclude")))


class SysRoleEmployee(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'RoleEmployee'

    id = fields.Str(metadata={"label": "员工ID"})
    employee = fields.Str(metadata={"label": "显示名称"}, data_key='name', load_default='', allow_none=True)
    department = fields.Str(metadata={"label": "部门"})
    sys_user_id = fields.Str(metadata={"label": "系统用户ID"})


class SysRoleEmployeeList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SysRoleEmployee(unknown="exclude")))


class Department(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Department'

    id = fields.Int(metadata={"label": "部门ID"})
    name = fields.Str(metadata={"label": "部门名称"})
    name_en = fields.Str(metadata={"label": "部门英文名称"}, load_default='', allow_none=True)
    # department_leader = fields.List(fields.String(), metadata={"label": "部门领导"})
    parentid = fields.Int(metadata={"label": "父节点ID"})
    order = fields.Int(metadata={"label": "排序"})


class DepartmentList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(Department(unknown="exclude")))


class SysRole(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Role'

    id = fields.Str(metadata={"label": "角色ID"})
    name = fields.Str(metadata={"label": "角色名"})
    type = fields.Int(metadata={"label": "角色类型"})
    description = fields.Str(metadata={"label": "角色描述"})
    is_deactivate = fields.Bool(metadata={"label": "停用"})
    expires_time = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "到期时间"}, load_default='', allow_none=True)
    purview = fields.Nested(PermissionInfo(unknown="exclude"))


class SysRoleList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SysRole(unknown="exclude")))


class SysAttachment(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'attachment'

    id = fields.Str(metadata={"label": "文件ID"})
    filename = fields.Str(metadata={"label": "文件名"})
    file_type = fields.Str(metadata={"label": "文件类型"})
    file_size = fields.Int(metadata={"label": "文件大小"})
    created_by_id = fields.Str(metadata={"label": "创建人ID"})
    created_by_name = fields.Str(metadata={"label": "创建人"})
    created_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "创建时间"}, load_default='', allow_none=True)


class SysAttachmentList(ResponseSchema):
    list = fields.List(fields.Nested(SysAttachment(unknown="exclude")))


class SysAttachmentDownload(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'attachment.download'

    file_url = fields.Str(metadata={"label": "文件URL"})


class SysSimulationUser(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'simulation.user'

    token = fields.Str(metadata={"label": "登录用户token"})