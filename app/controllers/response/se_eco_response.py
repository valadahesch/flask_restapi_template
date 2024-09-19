from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema


class SeEcoTask(ResponseSchema):
    __subsystem__ = 'SEEco'
    __object__ = 'task'

    parent_id = fields.Str(metadata={"label": "上级ID"}, load_default='', allow_none=True)
    last_modified_by_id = fields.Str(metadata={"label": "最后修改者ID"})
    last_modified_by_name = fields.Str(metadata={'label': '最后修改者姓名'})
    partner_id = fields.Str(metadata={"label": "客户ID"})
    support_mode = fields.Str(metadata={"label": "支持模式"})
    task_number = fields.Str(metadata={"label": "任务编号"})
    support_type_1st = fields.Dict(metadata={"label": "一级支持类型"})
    created_date = fields.DateTime(metadata={"label": "创建日期"})
    id = fields.Str(metadata={"label": "ID"})
    status = fields.Str(metadata={"label": "状态"})
    support_type_2nd = fields.Dict(metadata={"label": "二级支持类型"})
    partner_name = fields.Str(metadata={"label": "账户名称"})
    subject = fields.Str(metadata={"label": "主题"})
    created_by_id = fields.Str(metadata={"label": "创建者ID"})
    owner_id = fields.Str(metadata={"label": "所有者ID"})
    task_end_date = fields.DateTime(metadata={"label": "任务结束日期"})
    task_start_date = fields.DateTime(metadata={"label": "任务开始日期"})
    last_modified_date = fields.DateTime(metadata={"label": "最后修改日期"})
    task_result = fields.Str(metadata={"label": "任务结果"}, load_default='', allow_none=True)
    task_incomplete_reason = fields.Str(metadata={"label": "任务未完成原因"}, load_default='', allow_none=True)
    partner_contact_info = fields.Str(metadata={"label": "联系人信息"})
    created_by_name = fields.Str(metadata={"label": "创建者姓名"})
    owner_name = fields.Str(metadata={"label": "所有者姓名"})
    duration = fields.Int(metadata={"label": "任务所用时间"})
    participants = fields.List(fields.Dict(), metadata={'label': '参与人'}, load_default=[], allow_none=True)
    manager_id = fields.Str(metadata={"label": "渠道经理ID"}, data_key="channel_manager_id", load_default='', allow_none=True)
    manager_name = fields.Str(metadata={"label": "渠道经理名称"}, data_key="channel_manager_name", load_default='', allow_none=True)


class SeEcoTaskList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SeEcoTask(unknown="exclude")))


class SeEcoTaskDetail(ResponseSchema):
    __subsystem__ = 'SEEco'
    __object__ = 'task'

    partner_contact = fields.Str(metadata={"label": "联系人姓名"})
    parent_id = fields.Str(metadata={"label": "上级ID"})
    parent_task_number = fields.Str(metadata={"label": "父任务编号"}, load_default='', allow_none=True)
    task_incomplete_reason = fields.Str(metadata={"label": "任务未完成原因"}, load_default='', allow_none=True)
    last_modified_by_id = fields.Str(metadata={"label": "最后修改者ID"})
    last_modified_by_name = fields.Str(metadata={'label': '最后修改者姓名'})
    project_id = fields.Str(metadata={"label": "项目ID"})
    partner_id = fields.Str(metadata={"label": "客户ID"})
    support_mode = fields.Str(metadata={"label": "支持模式"})
    task_number = fields.Str(metadata={"label": "任务编号"})
    support_type_1st = fields.Dict(metadata={"label": "一级支持类型"})
    created_date = fields.DateTime(metadata={"label": "创建日期"})
    id = fields.Str(metadata={"label": "ID"})
    status = fields.Str(metadata={"label": "状态"})
    support_type_2nd = fields.Dict(metadata={"label": "二级支持类型"})
    partner_name = fields.Str(metadata={"label": "账户名称"})
    subject = fields.Str(metadata={"label": "主题"})
    created_by_id = fields.Str(metadata={"label": "创建者ID"})
    owner_id = fields.Str(metadata={"label": "所有者ID"})
    task_end_date = fields.DateTime(metadata={"label": "任务结束日期"}, data_key="end_date")
    task_start_date = fields.DateTime(metadata={"label": "任务开始日期"}, data_key="start_date")
    last_modified_date = fields.DateTime(metadata={"label": "最后修改日期"})
    task_result = fields.Str(metadata={"label": "任务结果"}, load_default='', allow_none=True)
    partner_contact_info = fields.Str(metadata={"label": "联系人信息"})
    created_by_name = fields.Str(metadata={"label": "创建者姓名"})
    owner_name = fields.Str(metadata={"label": "所有者姓名"})
    duration = fields.Int(metadata={"label": "任务所用时间"})
    partner_industry = fields.Str(metadata={"label": "合作伙伴行业"})
    manager_id = fields.Str(metadata={"label": "渠道经理ID"}, data_key="channel_manager_id")
    manager_name = fields.Str(metadata={"label": "渠道经理名称"}, data_key="channel_manager_name")


class SeEcoTaskPartner(ResponseSchema):
    __subsystem__ = 'SEEco'
    __object__ = 'task_partner'

    id = fields.Str(metadata={"label": "合作伙伴ID"})
    partner_name = fields.Str(metadata={"label": "合作伙伴名称"})
    first_support_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "第一次支持时间"})
    last_support_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "上次支持时间"})
    handing_number = fields.Int(metadata={'label': '正在处理的数量'})
    all_number = fields.Int(metadata={"label": "所有任务数量"})


class SeEcoTaskPartnerList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SeEcoTaskPartner(unknown="exclude")))


class SeAttachment(ResponseSchema):
    id = fields.Str(metadata={"label": "ID"})
    filename = fields.Str(metadata={"label": "文件名"})
    file_size = fields.Int(metadata={"label": "文件大小"})
    file_type = fields.Str(metadata={"label": "文件类型"})


class SeEcoRecord(ResponseSchema):
    status = fields.Str(metadata={"label": "状态"})
    support_duration = fields.Int(metadata={"label": "支持时长"})
    task_id = fields.Str(metadata={"label": "任务ID"})
    last_modified_by_id = fields.Str(metadata={"label": "最后修改者ID"})
    last_modified_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "最后修改日期"})
    support_end_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "支持结束日期"})
    created_by_id = fields.Str(metadata={"label": "创建者ID"})
    created_by_name = fields.Str(metadata={"label": "创建者姓名"})
    unapproval_reason = fields.Str(metadata={"label": "不通过原因"})
    published_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "发布日期"})
    id = fields.Str(metadata={"label": "ID"})
    created_date = fields.Str(metadata={"label": "创建日期"})
    support_start_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "支持开始日期"})
    record_content = fields.List(fields.Dict(), metadata={"label": "记录内容"})
    attachments = fields.List(fields.Nested(SeAttachment(unknown="exclude")), metadata={"label": "附件信息"})
    approval_name = fields.Str(metadata={"label": "审批人"})
    approval_id = fields.Str(metadata={"label": "审批人ID"})


class SeEcoRecordList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SeEcoRecord(unknown="exclude")))


class SeEcoRecordApproval(ResponseSchema):
    status = fields.Str(metadata={"label": "状态"})
    support_duration = fields.Int(metadata={"label": "支持时长"})
    task_id = fields.Str(metadata={"label": "任务ID"})
    last_modified_by_id = fields.Str(metadata={"label": "最后修改者ID"})
    last_modified_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "最后修改日期"})
    support_end_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "支持结束日期"})
    created_by_id = fields.Str(metadata={"label": "创建者ID"})
    created_by_name = fields.Str(metadata={"label": "创建者姓名"})
    unapproval_reason = fields.Str(metadata={"label": "不通过原因"})
    published_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "发布日期"})
    id = fields.Str(metadata={"label": "ID"})
    created_date = fields.Str(metadata={"label": "创建日期"})
    support_start_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "支持开始日期"})
    record_content = fields.List(fields.Dict(), metadata={"label": "记录内容"})
    task_number = fields.Str(metadata={"label": "任务编号"})
    task_subject = fields.Str(metadata={"label": "任务主题"})
    attachments = fields.List(fields.Nested(SeAttachment(unknown="exclude")), metadata={"label": "附件信息"})


class SeEcoRecordApprovalList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SeEcoRecordApproval(unknown="exclude")))


class SeEcoPendingRecord(ResponseSchema):
    status = fields.Str(metadata={"label": "状态"})
    support_duration = fields.Int(metadata={"label": "支持时长"})
    task_id = fields.Str(metadata={"label": "任务ID"})
    task_number = fields.Str(metadata={"label": "任务编号"})
    task_subject = fields.Str(metadata={"label": "任务主题"})
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


class SeEcoPendingRecordList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SeEcoPendingRecord(unknown="exclude")))