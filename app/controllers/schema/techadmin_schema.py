from datetime import datetime
from app.models.techadmin import SysUser, CasbinRule, SysField, SysMenu, SysSubsystemObject, SysRoleUser, \
    TblEmployee, TblDepartment, SysRoleMenu, SysRole, SysFieldPermission, SysAttachment, OperateHistory
from marshmallow import Schema, fields, post_load
from app.utils.func_util import nanoId


class SysUserSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    user_id = fields.Str(allow_none=True)
    user_name = fields.Str(allow_none=True)
    dp_name = fields.Str(allow_none=True)
    display_name = fields.Str(allow_none=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    nick_name = fields.Str(allow_none=True)
    birthday = fields.Date(allow_none=True)
    user_type = fields.Int(allow_none=True)
    company_name = fields.Str(allow_none=True)
    mobile = fields.Str(allow_none=True)
    email = fields.Str(allow_none=True)
    time_diff = fields.Int(allow_none=True)
    oem_brand = fields.Str(allow_none=True)
    language = fields.Str(allow_none=True)
    employee_id = fields.Str(allow_none=True)
    extattr = fields.Str(allow_none=True)
    manage_id = fields.Str(allow_none=True)
    work_city_adcode = fields.Str(allow_none=True)
    work_city = fields.Str(allow_none=True)
    first_login_time = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SysUser

    @post_load
    def make_user(self, data: dict, **kwargs):
        return SysUser(**data)


class SysRoleUserSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    role_id = fields.Str()
    user_id = fields.Str()

    class Meta:
        model = SysRoleUser

    @post_load
    def make_policy(self, data: dict, **kwargs):
        return SysRoleUser(**data)


class SysCasbinPolicySchema(Schema):
    # load(dict) -> obj
    id = fields.Int(allow_none=False)
    ptype = fields.Str(allow_none=False)
    v0 = fields.Str(allow_none=False)
    v1 = fields.Str()
    v2 = fields.Str()
    v3 = fields.Str()
    v4 = fields.Str()

    class Meta:
        model = CasbinRule

    @post_load
    def make_policy(self, data: dict, **kwargs):
        return CasbinRule(**data)


class SysFieldSchema(Schema):
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    name = fields.Str()
    label = fields.Str()
    type = fields.Str()
    required = fields.Bool(load_default=False)
    values = fields.Str()
    object_id = fields.Str()
    create_by = fields.Str()
    create_time = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    update_by = fields.Str()
    update_time = fields.DateTime(
        format="%Y-%m-%d %H:%M:%S", load_default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    delete_time = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SysField

    @post_load
    def make_field(self, data: dict, **kwargs):
        return SysField(**data)


class SysMenuSchema(Schema):
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    parent_id = fields.Str(load_default='')
    full_path = fields.Str()
    title = fields.Str()
    name = fields.Str()
    menu_type = fields.Int()
    menu_sort = fields.Int()
    page_key = fields.Str()
    permission = fields.Str()
    link = fields.Str()
    link_type = fields.Int()
    field_object = fields.Str()
    hidden = fields.Bool()
    create_by = fields.Str()
    create_time = fields.DateTime(
        format="%Y-%m-%d %H:%M:%S", load_default=lambda: datetime.now()
    )
    update_by = fields.Str()
    update_time = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    is_deleted = fields.Int()
    deleted_time = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SysMenu

    @post_load
    def make_field(self, data: dict, **kwargs):
        return SysMenu(**data)


class SysSubsystemObjectSchema(Schema):

    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    name = fields.Str()
    type = fields.Int()
    parent_id = fields.Str(allow_none=True)
    description = fields.Str()

    class Meta:
        model = SysSubsystemObject

    @post_load
    def make_field(self, data: dict, **kwargs):
        return SysSubsystemObject(**data)


class TbEmployeeSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    userid = fields.Str()
    name = fields.Str()
    mobile = fields.Str(allow_none=True)
    department = fields.Str(allow_none=True)
    main_department = fields.Int(allow_none=True)
    order = fields.Str(allow_none=True)
    position = fields.Str(allow_none=True)
    gender = fields.Str(allow_none=True)
    email = fields.Str(allow_none=True)
    is_leader_in_dept = fields.Str(allow_none=True)
    direct_leader = fields.Str(allow_none=True)
    avatar = fields.Str(allow_none=True)
    thumb_avatar = fields.Str(allow_none=True)
    telephone = fields.Str(allow_none=True)
    alias = fields.Str(allow_none=True)
    extattr = fields.Str(allow_none=True)
    extattr_local = fields.Str(allow_none=True)
    status = fields.Int(allow_none=True)
    qr_code = fields.Str(allow_none=True)
    external_profile = fields.Str(allow_none=True)
    external_position = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    employee_number = fields.Str(allow_none=True)
    leader = fields.Str(allow_none=True)
    is_deleted = fields.Bool(allow_none=True)
    update_time = fields.DateTime(
        format="%Y-%m-%d %H:%M:%S", load_default=lambda: datetime.now()
    )

    class Meta:
        model = TblEmployee

    @post_load
    def make_user(self, data: dict, **kwargs):
        return TblEmployee(**data)


class TblDepartmentSchema(Schema):
    # load(dict) -> obj
    id = fields.Int(allow_none=False)
    name = fields.Str()
    name_en = fields.Str(allow_none=True)
    department_leader = fields.Str(allow_none=True)
    parentid = fields.Int(allow_none=True)
    order = fields.Int(allow_none=True)
    is_deleted = fields.Bool(allow_none=True)

    class Meta:
        model = TblDepartment

    @post_load
    def make_user(self, data: dict, **kwargs):
        return TblDepartment(**data)


class SysRoleMenuSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    role_id = fields.Str()
    menu_id = fields.Str()
    data_scope = fields.Int(allow_none=True)
    effect = fields.Str()

    class Meta:
        model = SysRoleMenu

    @post_load
    def make_load(self, data: dict, **kwargs):
        return SysRoleMenu(**data)


class SysRoleSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    name = fields.Str()
    type = fields.Int()
    description = fields.Str()
    is_deactivate = fields.Bool(load_default=False)
    expires_time = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    create_by = fields.Str()
    create_time = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    update_by = fields.Str()
    update_time = fields.DateTime(
        format="%Y-%m-%d %H:%M:%S", load_default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    is_delete = fields.Bool()
    deleted_time = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SysRole

    @post_load
    def make_load(self, data: dict, **kwargs):
        return SysRole(**data)


class SysFieldPermissionSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    role_menu_id = fields.Str()
    field_id = fields.Str()
    effect = fields.Str()

    class Meta:
        model = SysFieldPermission

    @post_load
    def make_load(self, data: dict, **kwargs):
        return SysFieldPermission(**data)


class SysAttachmentSchema(Schema):
    id = fields.Str(allow_none=False)
    file_name = fields.Str()
    file_type = fields.Str()
    file_size = fields.Int()
    related_object = fields.Str()
    related_object_id = fields.Str()
    created_by_id = fields.Str()
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    deleted_by_id = fields.Str()
    deleted_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = SysAttachment

    @post_load
    def make_load(self, data: dict, **kwargs):
        return SysAttachment(**data)


class OperateHistorySchema(Schema):
    id = fields.Int()
    action = fields.Str()
    log = fields.Str()
    created_by_id = fields.Str()
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S")
    target = fields.Str()
    target_id = fields.Str()
    params_data = fields.Str()

    class Meta:
        model = OperateHistory

    @post_load
    def make_load(self, data: dict, **kwargs):
        return OperateHistory(**data)