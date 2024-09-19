from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema


class SeWorkProject(ResponseSchema):
    __subsystem__ = 'SEWork'
    __object__ = 'project'

    id = fields.Str(metadata={'label': 'ID'})
    project_number = fields.Str(metadata={'label': '项目编号'})
    subject = fields.Str(metadata={'label': '主题'})
    created_date = fields.DateTime(metadata={'label': '创建日期'})
    owner_id = fields.Str(metadata={'label': '所有者ID'})
    owner_name = fields.Str(metadata={'label': '所有者姓名'})
    created_by_id = fields.Str(metadata={'label': '创建者ID'})
    created_by_name = fields.Str(metadata={'label': '创建者姓名'})
    account_id = fields.Str(metadata={'label': '账户ID'})
    account_name = fields.Str(metadata={'label': '账户名称'})
    status = fields.Int(metadata={'label': '状态'})
    contact_name = fields.Str(metadata={'label': '联系人姓名'})
    support_type_1st = fields.Dict(metadata={'label': '支持类型'})
    support_type_2nd = fields.Dict(metadata={'label': '支持项'})
    last_modified_date = fields.DateTime(metadata={'label': '最后修改日期'})
    last_modified_by_id = fields.Str(metadata={'label': '最后修改者ID'})
    last_modified_by_name = fields.Str(metadata={'label': '最后修改者姓名'})
    participants = fields.List(fields.Dict(), metadata={'label': '参与人'}, load_default=[], allow_none=True)


class SeWorkProjectList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SeWorkProject(unknown="exclude")))


class SeWorkProjectDetail(ResponseSchema):
    __subsystem__ = 'SEWork'
    __object__ = 'project_detail'

    id = fields.Str(metadata={'label': 'ID'})
    project_number = fields.Str(metadata={'label': '项目编号'})
    subject = fields.Str(metadata={'label': '主题'})
    created_date = fields.DateTime(metadata={'label': '创建日期'})
    owner_id = fields.Str(metadata={'label': '所有者ID'})
    owner_name = fields.Str(metadata={'label': '所有者姓名'})
    created_by_id = fields.Str(metadata={'label': '创建者ID'})
    created_by_name = fields.Str(metadata={'label': '创建者姓名'})
    account_id = fields.Str(metadata={'label': '账户ID'})
    account_name = fields.Str(metadata={'label': '账户名称'})
    status = fields.Int(metadata={'label': '状态'})
    contact_name = fields.Str(metadata={'label': '联系人姓名'})
    contact_info = fields.Str(metadata={'label': '联系人信息'})
    support_type_1st = fields.Dict(metadata={'label': '支持类型'})
    support_type_2nd = fields.Dict(metadata={'label': '支持项'})
    last_modified_by_id = fields.Str(metadata={'label': '最后修改者ID'})
    last_modified_name = fields.Str(metadata={'label': '最后修改者姓名'})
    last_modified_date = fields.DateTime(metadata={'label': '最后修改日期'})


class SeWorkTask(ResponseSchema):
    __subsystem__ = 'SEWork'
    __object__ = 'task'

    contact_name = fields.Str(metadata={"label": "联系人姓名"})
    parent_id = fields.Str(metadata={"label": "上级ID"})
    task_incomplete_reason = fields.Str(metadata={"label": "任务未完成原因"})
    last_modified_by_id = fields.Str(metadata={"label": "最后修改者ID"})
    last_modified_by_name = fields.Str(metadata={'label': '最后修改者姓名'})
    project_id = fields.Str(metadata={"label": "项目ID"})
    account_id = fields.Str(metadata={"label": "客户ID"})
    support_mode = fields.Int(metadata={"label": "支持模式"})
    task_number = fields.Str(metadata={"label": "任务编号"})
    support_type_1st = fields.Dict(metadata={"label": "一级支持类型"})
    created_date = fields.DateTime(metadata={"label": "创建日期"})
    id = fields.Str(metadata={"label": "ID"})
    status = fields.Int(metadata={"label": "状态"})
    support_type_2nd = fields.Dict(metadata={"label": "二级支持类型"})
    account_name = fields.Str(metadata={"label": "账户名称"})
    subject = fields.Str(metadata={"label": "主题"})
    created_by_id = fields.Str(metadata={"label": "创建者ID"})
    owner_id = fields.Str(metadata={"label": "所有者ID"})
    task_end_date = fields.DateTime(metadata={"label": "任务结束日期"})
    task_start_date = fields.DateTime(metadata={"label": "任务开始日期"})
    last_modified_date = fields.DateTime(metadata={"label": "最后修改日期"})
    task_result = fields.Int(metadata={"label": "任务结果"})
    contact_info = fields.Str(metadata={"label": "联系人信息"})
    created_by_name = fields.Str(metadata={"label": "创建者姓名"})
    owner_name = fields.Str(metadata={"label": "所有者姓名"})
    permission = fields.List(fields.Str(), metadata={"label": "所有者姓名"})


class SeWorkTaskList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SeWorkTask(unknown="exclude")))


class SeWorkTaskDetail(ResponseSchema):
    __subsystem__ = 'SEWork'
    __object__ = 'task_detail'

    contact_name = fields.Str(metadata={"label": "联系人姓名"})
    parent_id = fields.Str(metadata={"label": "上级ID"})
    task_incomplete_reason = fields.Str(metadata={"label": "任务未完成原因"})
    last_modified_by_id = fields.Str(metadata={"label": "最后修改者ID"})
    last_modified_by_name = fields.Str(metadata={'label': '最后修改者姓名'})
    project_id = fields.Str(metadata={"label": "项目ID"})
    account_id = fields.Str(metadata={"label": "账户ID"})
    support_mode = fields.Int(metadata={"label": "支持模式"})
    task_number = fields.Str(metadata={"label": "任务编号"})
    support_type_1st = fields.Dict(metadata={"label": "一级支持类型"})
    created_date = fields.DateTime(metadata={"label": "创建日期"})
    id = fields.Str(metadata={"label": "ID"})
    status = fields.Int(metadata={"label": "状态"})
    support_type_2nd = fields.Dict(metadata={"label": "二级支持类型"})
    account_name = fields.Str(metadata={"label": "账户名称"})
    subject = fields.Str(metadata={"label": "主题"})
    created_by_id = fields.Str(metadata={"label": "创建者ID"})
    owner_id = fields.Str(metadata={"label": "所有者ID"})
    task_end_date = fields.DateTime(metadata={"label": "任务结束日期"})
    task_start_date = fields.DateTime(metadata={"label": "任务开始日期"})
    last_modified_date = fields.DateTime(metadata={"label": "最后修改日期"})
    task_result = fields.Int(metadata={"label": "任务结果"})
    contact_info = fields.Str(metadata={"label": "联系人信息"})
    created_by_name = fields.Str(metadata={"label": "创建者姓名"})
    owner_name = fields.Str(metadata={"label": "所有者姓名"})
    project_number = fields.Str(metadata={"label": "项目编号"})
    project_subject = fields.Str(metadata={"label": "项目主题"})


class SeAttachment(ResponseSchema):
    id = fields.Str(metadata={"label": "ID"})
    filename = fields.Str(metadata={"label": "文件名"})
    file_size = fields.Int(metadata={"label": "文件大小"})
    file_type = fields.Str(metadata={"label": "文件类型"})


class SeWorkRecord(ResponseSchema):
    status = fields.Int(metadata={"label": "状态"})
    support_duration = fields.Int(metadata={"label": "支持时长"})
    task_id = fields.Str(metadata={"label": "任务ID"})
    last_modified_by_id = fields.Str(metadata={"label": "最后修改者ID"})
    last_modified_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "最后修改日期"})
    support_end_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "支持结束日期"})
    created_by_id = fields.Str(metadata={"label": "创建者ID"})
    created_by_name = fields.Str(metadata={"label": "创建者姓名"})
    published_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "发布日期"})
    id = fields.Str(metadata={"label": "ID"})
    created_date = fields.Str(metadata={"label": "创建日期"})
    support_start_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "支持开始日期"})
    record_content = fields.List(fields.Dict(), metadata={"label": "记录内容"})
    attachments = fields.List(fields.Nested(SeAttachment(unknown="exclude")), metadata={"label": "附件信息"})
    task_number = fields.Str(metadata={"label": "任务编号"})
    task_subject = fields.Str(metadata={"label": "任务主题"})
    approval_id = fields.Str(metadata={"label": "审批人ID"})
    approval_name = fields.Str(metadata={"label": "审批人用户名"})
    unapproval_reason = fields.Str(metadata={"label": "审批不通过的原因"})


class SeWorkRecordList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SeWorkRecord(unknown="exclude")))


class SeWorkOwner(ResponseSchema):
    id = fields.Str(metadata={"label": "用户ID"})
    internal_email = fields.Str(metadata={"label": "用户邮箱"}, load_default='', allow_none=True)
    user_name = fields.Str(metadata={"label": "用户名"})


class SeWorkOwnerList(ResponseSchema):
    list = fields.List(fields.Nested(SeWorkOwner(unknown="exclude")))


class SeWorkParticipant(ResponseSchema):
    id = fields.Str(metadata={"label": "用户ID"})
    display_name = fields.Str(metadata={"label": "系统显示名"}, load_default='', allow_none=True)
    name = fields.Str(metadata={"label": "企业用户名"})
    department = fields.Str(metadata={"label": "部门"})
    position = fields.Str(metadata={"label": "职位"}, load_default='', allow_none=True)
    role = fields.Str(metadata={"label": "角色"})
    leader = fields.Str(metadata={"label": "上级"}, load_default='', allow_none=True)
    leader_id = fields.Str(metadata={"label": "上级ID"}, load_default='', allow_none=True)


class SeWorkParticipantList(ResponseSchema):
    list = fields.List(fields.Nested(SeWorkParticipant(unknown="exclude")))


