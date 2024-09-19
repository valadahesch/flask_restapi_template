from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema


class CrmSysCustomer(ResponseSchema):
    status = fields.Str(metadata={"label": "状态"}, data_key='Status')
    hide = fields.Bool(metadata={"label": "隐藏"}, data_key='Hide')
    is_assign_account = fields.Bool(metadata={"label": "是否分配账户"}, data_key='IsAssignAccount')
    account_id = fields.Str(metadata={"label": "账户ID"}, data_key='AccountId')
    account_service_level = fields.Str(metadata={"label": "账户服务级别"}, data_key='AccountServiceLeveL')
    is_effective_account = fields.Bool(metadata={"label": "是否有效账户"}, data_key='IsEffectiveAccount')
    sales_unit = fields.Str(metadata={"label": "销售单位"}, data_key='SalesUnit')
    sales_platform = fields.Str(metadata={"label": "销售平台"}, data_key='SalesPlatform')
    city = fields.Str(metadata={"label": "城市"}, data_key='City')
    tac_account_log_type = fields.Str(metadata={"label": "Tac账户日志类型"}, data_key='TacAccountLogType')
    account_type = fields.Str(metadata={"label": "账户类型"}, data_key='AccountType')
    industry_2nd = fields.Str(metadata={"label": "第二行业"}, data_key='Industry2nd')
    approval_status = fields.Str(metadata={"label": "审核状态"}, data_key='ApprovalStatus')
    province = fields.Str(metadata={"label": "省份"}, data_key='Province')
    industry_1st = fields.Str(metadata={"label": "第一行业"}, data_key='Industry1st')
    industry_3_dim = fields.Str(metadata={"label": "第三维行业"}, data_key='Industry3Dim')
    account_log_type = fields.Str(metadata={"label": "账户日志类型"}, data_key='AccountLogType')
    account_name = fields.Str(metadata={"label": "账户名称"}, data_key='AccountName')
    crm_account_id = fields.Str(metadata={"label": "CRM账户ID"}, data_key='CrmAccountId')
    # owner_name = fields.Str(metadata={"label": "所有者姓名"}, data_key='OwnerName')
    # owner_id = fields.Str(metadata={"label": "所有者ID"}, data_key='OwnerId')
    owner_name = fields.Str(metadata={"label": "所有者姓名"}, load_default="", allow_none=True)
    owner_id = fields.Str(metadata={"label": "所有者ID"}, load_default="", allow_none=True)


class CrmSysCustomerList(ResponseSchema):
    list = fields.List(fields.Nested(CrmSysCustomer(unknown="exclude")))


class CrmSysUser(ResponseSchema):
    user_id = fields.Str(metadata={"label": "用户ID"}, data_key='userid')
    user_name = fields.Str(metadata={"label": "用户名"}, data_key='username')
    sales_unit = fields.Str(metadata={"label": "销售单位"}, data_key='salesunit')
    state = fields.Str(metadata={"label": "状态"})
    internal_email = fields.Str(metadata={"label": "内部邮箱"}, data_key='internalemail')
    system_user_id = fields.Str(metadata={"label": "系统用户ID"}, data_key='systemuserid')


class CrmSysUserList(ResponseSchema):
    list = fields.List(fields.Nested(CrmSysUser(unknown="exclude")))


class PersonInfo(ResponseSchema):

    id = fields.Str(metadata={"label": "用户ID"})
    display_name = fields.Str(metadata={"label": "用户名"})
    employee_name = fields.Str(metadata={"label": "姓名"})
    mobile = fields.Str(metadata={"label": "手机号"})
    email = fields.Str(metadata={"label": "邮箱"})
    employee_number = fields.Str(metadata={"label": "工号"}, load_default="", allow_none=True)
    company = fields.Str(metadata={"label": "隶属公司"}, load_default="", allow_none=True)
    rank = fields.Str(metadata={"label": "职级"}, load_default="", allow_none=True)
    manage_id = fields.Str(metadata={"label": "上级ID"}, load_default="", allow_none=True)
    manage_name = fields.Str(metadata={"label": "上级名称"}, load_default="", allow_none=True)
    entry_time = fields.Str(metadata={"label": "入职时间"}, load_default="", allow_none=True)
    department = fields.Str(metadata={"label": "部门"}, load_default="", allow_none=True)
    position = fields.Str(metadata={"label": "职位"}, load_default="", allow_none=True)
    work_city_adcode = fields.Str(metadata={"label": "工作地区"}, load_default="", allow_none=True)
    work_city = fields.Str(metadata={"label": "工作地区"}, load_default="", allow_none=True)
    manage_ehr_name = fields.Str(metadata={"label": "工作地区"}, load_default="", allow_none=True)


class SysUserInfoResponse(ResponseSchema):

    id = fields.Str(metadata={"label": "系统用户id"})
    display_name = fields.Str(metadata={"label": "用户名"}, load_default="", allow_none=True)
    mobile = fields.Str(metadata={"label": "手机号"}, load_default="", allow_none=True)
    email = fields.Str(metadata={"label": "邮箱"}, load_default="", allow_none=True)
    status = fields.Str(metadata={"label": "员工状态"}, load_default="", allow_none=True)
    avatar = fields.Str(metadata={"label": "企业信息"}, load_default="", allow_none=True)
    employee_number = fields.Str(metadata={"label": "工号"}, load_default="", allow_none=True)
    company = fields.Str(metadata={"label": "隶属公司"}, load_default="", allow_none=True)
    rank = fields.Str(metadata={"label": "职级"}, load_default="", allow_none=True)
    manage_ehr_id = fields.Str(metadata={"label": "上级ID"}, load_default="", allow_none=True)
    manage_ehr_name = fields.Str(metadata={"label": "上级名称"}, load_default="", allow_none=True)
    entry_time = fields.Str(metadata={"label": "入职时间"}, load_default="", allow_none=True)
    departments = fields.List(fields.Raw(), metadata={"label": "上级部门"}, load_default=[], allow_none=False)
    position = fields.Str(metadata={"label": "职位"}, load_default="", allow_none=True)
    gender = fields.Str(metadata={"label": "性别"}, load_default="", allow_none=True)
    work_city_adcode = fields.Str(metadata={"label": "工作地区"}, load_default="", allow_none=True)
    work_city = fields.Str(metadata={"label": "工作地区"}, load_default="", allow_none=True)
