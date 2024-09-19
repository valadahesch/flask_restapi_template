from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema


class SeProjectProject(ResponseSchema):
    __subsystem__ = 'SEProject'
    __object__ = 'project'

    id = fields.Str(metadata={'label': 'ID'})
    project_type = fields.Str(metadata={'label': '项目类型'})
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
    # support_type_1st = fields.Dict(metadata={'label': '支持类型'})
    # support_type_2nd = fields.Dict(metadata={'label': '支持项'})
    last_modified_date = fields.DateTime(metadata={'label': '最后修改日期'})
    last_modified_by_id = fields.Str(metadata={'label': '最后修改者ID'})
    last_modified_by_name = fields.Str(metadata={'label': '最后修改者姓名'})
    participants = fields.List(fields.Dict(), metadata={'label': '参与人'}, load_default=[], allow_none=True)
    permission = fields.List(fields.Str, metadata={'label': '权限'})
    project_phase = fields.Dict(metadata={'label': '项目进展'}, load_default={}, allow_none=True)
    business_stage = fields.Str(metadata={'label': '商机阶段'}, load_default='', allow_none=True)
    competitors = fields.Str(metadata={'label': '竞争对手'}, load_default='', allow_none=True)
    pre_bidding_date = fields.Date(metadata={'label': '计划招标（采购）时间'}, load_default='', allow_none=True)
    contact_position = fields.Str(metadata={'label': '联系人职务'}, load_default='', allow_none=True)
    application_type = fields.Str(metadata={'label': '申请类型'}, load_default='', allow_none=True)
    opportunity_name = fields.Str(metadata={'label': '商机名称'}, load_default='', allow_none=True)
    opportunity_number = fields.Str(metadata={'label': '商机编号'}, load_default='', allow_none=True)
    sale_by_id = fields.Str(metadata={'label': '销售ID'}, load_default='', allow_none=True)
    sale_by_name = fields.Str(metadata={'label': '销售人员'}, load_default='', allow_none=True)
    taken_hours = fields.Float(metadata={'label': '耗时'}, load_default=0, allow_none=True)
    last_record_created_date = fields.DateTime(metadata={'label': '上次日志提交时间'}, load_default='')
    last_record_support_start_date = fields.DateTime(metadata={'label': '上次日志支持时间'}, load_default='')
    task_result = fields.Int(metadata={'label': '任务结果'}, load_default='')
    task_incomplete_reason = fields.Str(metadata={'label': '任务未完成原因'}, load_default='', allow_none=True)


class SeProjectProjectList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SeProjectProject(unknown="exclude")))


class SeProjectProjectDetail(ResponseSchema):
    __subsystem__ = 'SEProject'
    __object__ = 'project_detail'

    id = fields.Str(metadata={'label': 'ID'})
    project_number = fields.Str(metadata={'label': '项目编号'})
    project_type = fields.Str(metadata={'label': '项目类型'})
    subject = fields.Str(metadata={'label': '主题'})
    created_date = fields.DateTime(metadata={'label': '创建日期'})
    owner_id = fields.Str(metadata={'label': '所有者ID'})
    owner_name = fields.Str(metadata={'label': '所有者姓名'})
    created_by_id = fields.Str(metadata={'label': '创建者ID'})
    created_by_name = fields.Str(metadata={'label': '创建者姓名'})
    account_id = fields.Str(metadata={'label': '账户ID'})
    account_name = fields.Str(metadata={'label': '账户名称'})
    customer_requirement = fields.Str(metadata={'label': '客户需求描述'})
    project_phase = fields.Dict(metadata={'label': '项目进展'})
    sale_by_id = fields.Str(metadata={'label': '销售ID'})
    sale_by_name = fields.Str(metadata={'label': '销售名称'})
    status = fields.Int(metadata={'label': '状态'})
    contact_name = fields.Str(metadata={'label': '联系人姓名'})
    contact_info = fields.Str(metadata={'label': '联系人信息'})
    support_type_1st = fields.Dict(metadata={'label': '支持类型'})
    support_type_2nd = fields.Dict(metadata={'label': '支持项'})
    last_modified_by_id = fields.Str(metadata={'label': '最后修改者ID'})
    last_modified_name = fields.Str(metadata={'label': '最后修改者姓名'})
    last_modified_date = fields.DateTime(metadata={'label': '最后修改日期'})
    focused = fields.Bool(metadata={'label': '是否关注项目'})
    application_type = fields.Str(metadata={'label': '申请类型'})
    opportunity_level = fields.Str(metadata={'label': '商机分级'})
    opportunity_number = fields.Str(metadata={'label': '商机编号'})
    is_itai_project = fields.Str(metadata={'label': '是否大项目'})
    business_stage = fields.Str(metadata={'label': '商机阶段'}, load_default='', allow_none=True)
    competitors = fields.Str(metadata={'label': '竞争对手'}, load_default='', allow_none=True)
    pre_bidding_date = fields.Date(metadata={'label': '计划招标（采购）时间'}, load_default='', allow_none=True)
    contact_position = fields.Str(metadata={'label': '联系人职务'}, load_default='', allow_none=True)
    background_description = fields.Str(metadata={'label': '项目背景描述'}, load_default='', allow_none=True)
    return_reason = fields.Str(metadata={'label': '回退原因'})
    deploy_core = fields.Str(metadata={'label': '是否部署在核心区域'})
    is_big_project_support = fields.Str(metadata={'label': '是否大项目支持'})
    parent_project = fields.Str(metadata={'label': '父项目ID'}, load_default='', allow_none=True)
    parent_opportunity_number = fields.Str(metadata={'label': '父项目主题'}, load_default='', allow_none=True)
    task_incomplete_reason = fields.Str(metadata={'label': '备注'}, load_default='', allow_none=True)
    task_result = fields.Int(metadata={'label': '项目结果'}, load_default='', allow_none=True)
    last_record_created_date = fields.DateTime(metadata={'label': '上次日志提交时间'}, load_default='', allow_none=True)
    last_record_support_start_date = fields.DateTime(metadata={'label': '上次日志支持时间'}, load_default='', allow_none=True)


class SeSubProjectProjectDetailList(ResponseSchema):
    list = fields.List(fields.Nested(SeProjectProjectDetail(unknown="exclude")))


class SeProjectTask(ResponseSchema):
    __subsystem__ = 'SEProject'
    __object__ = 'task'

    contact_name = fields.Str(metadata={"label": "联系人姓名"})
    parent_id = fields.Str(metadata={"label": "上级ID"}, load_default='', allow_none=True)
    task_incomplete_reason = fields.Str(metadata={"label": "任务未完成原因"})
    unapproval_reason = fields.Str(metadata={"label": "任务审批未通过原因"})
    last_modified_by_id = fields.Str(metadata={"label": "最后修改者ID"})
    last_modified_by_name = fields.Str(metadata={'label': '最后修改者姓名'})
    project_id = fields.Str(metadata={"label": "项目ID"})
    account_id = fields.Str(metadata={"label": "客户ID"})
    support_mode = fields.Int(metadata={"label": "支持模式"})
    task_number = fields.Str(metadata={"label": "任务编号"})
    event_number = fields.Str(metadata={"label": "活动编号"})
    support_type_1st = fields.Dict(metadata={"label": "一级支持类型"})
    created_date = fields.DateTime(metadata={"label": "创建日期"})
    id = fields.Str(metadata={"label": "ID"})
    status = fields.Int(metadata={"label": "状态"})
    support_type_2nd = fields.Dict(metadata={"label": "二级支持类型"})
    account_name = fields.Str(metadata={"label": "账户名称"})
    subject = fields.Str(metadata={"label": "主题"})
    created_by_id = fields.Str(metadata={"label": "创建者ID"})
    owner_id = fields.Str(metadata={"label": "所有者ID"})
    task_end_date = fields.DateTime(metadata={"label": "任务结束日期"}, load_default='', allow_none=True)
    task_start_date = fields.DateTime(metadata={"label": "任务开始日期"}, load_default='', allow_none=True)
    last_modified_date = fields.DateTime(metadata={"label": "最后修改日期"})
    task_result = fields.Int(metadata={"label": "任务结果"})
    contact_info = fields.Str(metadata={"label": "联系人信息"})
    created_by_name = fields.Str(metadata={"label": "创建者姓名"})
    owner_name = fields.Str(metadata={"label": "所有者姓名"})
    permission = fields.List(fields.Str(), metadata={"label": "所有者姓名"})
    application_type = fields.Str(metadata={"label": "申请类型"})
    taken_hours = fields.Float(metadata={"label": "任务耗时"}, load_default=0, allow_none=True)
    contact_position = fields.Str(metadata={'label': '联系人职务'}, load_default='', allow_none=True)
    all_taken_hours = fields.Float(metadata={"label": "主任务下全部任务耗时"}, load_default=0, allow_none=True)
    record_count = fields.Float(metadata={"label": "日志数量"}, load_default=0, allow_none=True)
    assign_number = fields.Str(metadata={"label": "分派编号"}, load_default='', allow_none=True)


class SeProjectTaskList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    totality = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SeProjectTask(unknown="exclude")))


class SeProjectTaskDetail(ResponseSchema):
    __subsystem__ = 'SEProject'
    __object__ = 'task_detail'

    contact_name = fields.Str(metadata={"label": "联系人姓名"})
    parent_id = fields.Str(metadata={"label": "上级ID"})
    task_incomplete_reason = fields.Str(metadata={"label": "任务未完成原因"})
    unapproval_reason = fields.Str(metadata={"label": "任务审批未通过原因"})
    last_modified_by_id = fields.Str(metadata={"label": "最后修改者ID"})
    last_modified_name = fields.Str(metadata={'label': '最后修改者姓名'})
    project_id = fields.Str(metadata={"label": "项目ID"})
    account_id = fields.Str(metadata={"label": "账户ID"})
    support_mode = fields.Int(metadata={"label": "支持模式"})
    task_number = fields.Str(metadata={"label": "任务编号"})
    event_number = fields.Str(metadata={"label": "活动编号"})
    support_type_1st = fields.Dict(metadata={"label": "一级支持类型"})
    created_date = fields.DateTime(metadata={"label": "创建日期"})
    id = fields.Str(metadata={"label": "ID"})
    status = fields.Int(metadata={"label": "状态"})
    support_type_2nd = fields.Dict(metadata={"label": "二级支持类型"})
    account_name = fields.Str(metadata={"label": "账户名称"})
    subject = fields.Str(metadata={"label": "主题"})
    created_by_id = fields.Str(metadata={"label": "创建者ID"})
    owner_id = fields.Str(metadata={"label": "所有者ID"})
    task_end_date = fields.DateTime(metadata={"label": "任务结束日期"}, load_default='', allow_none=True)
    task_start_date = fields.DateTime(metadata={"label": "任务开始日期"}, load_default='', allow_none=True)
    last_modified_date = fields.DateTime(metadata={"label": "最后修改日期"})
    task_result = fields.Int(metadata={"label": "任务结果"})
    contact_info = fields.Str(metadata={"label": "联系人信息"})
    created_by_name = fields.Str(metadata={"label": "创建者姓名"})
    owner_name = fields.Str(metadata={"label": "所有者姓名"})
    project_number = fields.Str(metadata={"label": "项目编号"})
    project_subject = fields.Str(metadata={"label": "项目主题"})
    opportunity_number = fields.Str(metadata={'label': '商机编号'})
    application_type = fields.Str(metadata={"label": "申请类型"})
    taken_hours = fields.Float(metadata={"label": "任务耗时"}, load_default=0, allow_none=True)
    contact_position = fields.Str(metadata={'label': '联系人职务'}, load_default='', allow_none=True)
    last_modified_by_name = fields.Str(metadata={'label': '最后修改人'}, load_default='', allow_none=True)
    assign_number = fields.Str(metadata={"label": "分派编号"}, load_default='', allow_none=True)


class SeAttachment(ResponseSchema):
    id = fields.Str(metadata={"label": "ID"})
    filename = fields.Str(metadata={"label": "文件名"})
    file_size = fields.Int(metadata={"label": "文件大小"})
    file_type = fields.Str(metadata={"label": "文件类型"})


class SeProjectRecord(ResponseSchema):
    status = fields.Int(metadata={"label": "状态"})
    support_duration = fields.Int(metadata={"label": "支持时长"})
    task_id = fields.Str(metadata={"label": "任务ID"})
    last_modified_by_id = fields.Str(metadata={"label": "最后修改者ID"})
    last_modified_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "最后修改日期"})
    support_end_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "支持结束日期"})
    created_by_id = fields.Str(metadata={"label": "创建者ID"})
    support_location = fields.Str(metadata={"label": "支持地点"}, load_default='', allow_none=True)
    support_location_adcode = fields.Str(metadata={"label": "支持地点编码"}, load_default='', allow_none=True)
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
    account_id = fields.Str(metadata={"label": "客户ID"})
    account_name = fields.Str(metadata={"label": "客户名称"})
    customer_requirement = fields.Str(metadata={"label": "客户需求描述"})
    project = fields.Dict(metadata={"label": "所属项目"})
    permission = fields.List(fields.Str(), metadata={"label": "权限"})
    support_type_1st = fields.Dict(metadata={"label": "一级支持类型"}, load_default={}, allow_none=False)
    support_type_2nd = fields.Dict(metadata={"label": "二级支持类型"}, load_default={}, allow_none=False)
    task_event_number = fields.Str(metadata={"label": "活动编号"})
    assign_number = fields.Str(metadata={"label": "分派编号"}, load_default='', allow_none=True)
    task_parent_id = fields.Str(metadata={"label": "上级ID"}, load_default="", allow_none=False)


class SeProjectRecordList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SeProjectRecord(unknown="exclude")))


class SeProjectOwner(ResponseSchema):
    id = fields.Str(metadata={"label": "用户ID"})
    internal_email = fields.Str(metadata={"label": "用户邮箱"}, load_default='', allow_none=True)
    user_name = fields.Str(metadata={"label": "用户名"})


class SeProjectOwnerList(ResponseSchema):
    list = fields.List(fields.Nested(SeProjectOwner(unknown="exclude")))


class SeProjectParticipant(ResponseSchema):
    id = fields.Str(metadata={"label": "用户ID"})
    display_name = fields.Str(metadata={"label": "系统显示名"}, load_default='', allow_none=True)
    name = fields.Str(metadata={"label": "企业用户名"})
    department = fields.Str(metadata={"label": "部门"})
    position = fields.Str(metadata={"label": "职位"}, load_default='', allow_none=True)
    role = fields.Str(metadata={"label": "角色"})
    leader = fields.Str(metadata={"label": "上级"}, load_default='', allow_none=True)
    leader_id = fields.Str(metadata={"label": "上级ID"}, load_default='', allow_none=True)


class SeProjectParticipantList(ResponseSchema):
    list = fields.List(fields.Nested(SeProjectParticipant(unknown="exclude")))


class SeProjectFocus(ResponseSchema):
    id = fields.Str(metadata={"label": "ID"})
    project_id = fields.Str(metadata={"label": "项目ID"})
    follower_id = fields.Str(metadata={"label": "关注者ID"})
    followed_date = fields.Str(metadata={"label": "关注日期"})
    deleted_date = fields.Str(metadata={"label": "关注日期"})


class SeProjectTaskApproval(ResponseSchema):
    __subsystem__ = 'SEProject'
    __object__ = 'task'

    project_id = fields.Str(metadata={"label": "项目ID"})
    support_mode = fields.Int(metadata={"label": "支持模式"})
    task_number = fields.Str(metadata={"label": "任务编号"})
    event_number = fields.Str(metadata={"label": "活动编号"})
    assign_number = fields.Str(metadata={"label": "分派编号"}, load_default='', allow_none=True)
    support_type_1st = fields.Dict(metadata={"label": "一级支持类型"})
    created_date = fields.DateTime(metadata={"label": "创建日期"})
    id = fields.Str(metadata={"label": "ID"})
    status = fields.Int(metadata={"label": "状态"})
    support_type_2nd = fields.Dict(metadata={"label": "二级支持类型"})
    subject = fields.Str(metadata={"label": "主题"})
    created_by_id = fields.Str(metadata={"label": "创建者ID"})
    owner_id = fields.Str(metadata={"label": "所有者ID"})
    task_end_date = fields.DateTime(metadata={"label": "任务结束日期"})
    task_start_date = fields.DateTime(metadata={"label": "任务开始日期"})
    created_by_name = fields.Str(metadata={"label": "创建者姓名"})
    owner_name = fields.Str(metadata={"label": "所有者姓名"})
    project_subject = fields.Str(metadata={"label": "所属项目主题"})
    task_result = fields.Int(metadata={"label": "任务结果"})
    task_incomplete_reason = fields.Str(metadata={"label": "未完成原因"})
    last_modified_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "最后修改日期"})
    last_modified_name = fields.Str(metadata={'label': '最后修改者姓名'})
    account_id = fields.Str(metadata={"label": "客户ID"})
    account_name = fields.Str(metadata={"label": "账户名称"})
    parent_id = fields.Str(metadata={"label": "上级ID"})


class SeProjectTaskApprovalList(ResponseSchema):
    list = fields.List(fields.Nested(SeProjectTaskApproval(unknown="exclude")))
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)


class UserTaskListAPIResponseList(ResponseSchema):
    id = fields.Str(metadata={"label": "ID"}, load_default="", allow_none=False)
    subject = fields.Str(metadata={"label": "主题"}, load_default="", allow_none=False)
    task_number = fields.Str(metadata={"label": "任务编号"}, load_default="", allow_none=False)
    event_number = fields.Str(metadata={"label": "活动编号"}, load_default="", allow_none=False)
    assign_number = fields.Str(metadata={"label": "分派编号"}, load_default='', allow_none=True)
    created_date = fields.DateTime(metadata={"label": "创建日期"}, load_default="", allow_none=False)
    created_by_id = fields.Str(metadata={"label": "创建者ID"}, load_default="", allow_none=False)
    created_by_name = fields.Str(metadata={"label": "创建者姓名"}, load_default="", allow_none=False)
    owner_id = fields.Str(metadata={"label": "所有者ID"}, load_default="", allow_none=False)
    owner_name = fields.Str(metadata={"label": "所有者姓名"}, load_default="", allow_none=False)
    status = fields.Int(metadata={"label": "状态"}, load_default="", allow_none=False)
    support_mode = fields.Int(metadata={"label": "支持模式"}, load_default="", allow_none=False)
    support_type_1st = fields.Dict(metadata={"label": "一级支持类型"}, load_default={}, allow_none=False)
    support_type_2nd = fields.Dict(metadata={"label": "二级支持类型"}, load_default={}, allow_none=False)    
    task_end_date = fields.DateTime(metadata={"label": "任务结束日期"}, load_default="", allow_none=False)
    task_start_date = fields.DateTime(metadata={"label": "任务开始日期"}, load_default="", allow_none=False)
    task_result = fields.Int(metadata={"label": "任务结果"}, load_default="", allow_none=False)
    task_incomplete_reason = fields.Str(metadata={"label": "未完成原因"}, load_default="", allow_none=False)
    unapproval_reason = fields.Str(metadata={"label": "未完成原因"}, load_default="", allow_none=False)
    last_modified_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "最后修改日期"})
    last_modified_name = fields.Str(metadata={'label': '最后修改者姓名'}, load_default="", allow_none=False)
    last_modified_by_id = fields.Str(metadata={'label': '最后修改者姓名'}, load_default="", allow_none=False)
    permission = fields.List(fields.Raw(), metadata={"label": "权限"}, load_default=[], allow_none=False)
    project_id = fields.Str(metadata={"label": "项目ID"}, load_default="", allow_none=False)
    project_subject = fields.Str(metadata={"label": "所属项目主题"}, load_default="", allow_none=False)
    project_number = fields.Str(metadata={"label": "所属项目编号"}, load_default="", allow_none=False)
    opportunity_number = fields.Str(metadata={"label": "所属项目编号"}, load_default="", allow_none=False)
    account_id = fields.Str(metadata={"label": "客户ID"})
    account_name = fields.Str(metadata={"label": "客户名称"}, load_default="", allow_none=False)
    taken_hours = fields.Float(metadata={"label": "任务耗时"}, load_default=0.00, allow_none=False)
    parent_id = fields.Str(metadata={"label": "上级ID"}, load_default="", allow_none=False)
    assign_number = fields.Str(metadata={"label": "分派编号"}, load_default='', allow_none=True)


class UserTaskListAPIResponse(ResponseSchema):
    page = fields.Int(metadata={"label": "第几页"}, load_default="", allow_none=False)
    size = fields.Int(metadata={"label": "页面大小"}, load_default="", allow_none=False)
    total = fields.Int(metadata={"label": "数据条目总和"}, load_default="", allow_none=False)
    list = fields.List(fields.Nested(UserTaskListAPIResponseList(unknown="exclude")), required=True, data_key="list")


class SeProjectRecordMine(ResponseSchema):
    id = fields.Str(metadata={"label": "ID"})
    support_start_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "支持开始日期"})
    support_end_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "支持结束日期"})
    support_duration = fields.Int(metadata={"label": "支持时长"})
    created_by_id = fields.Str(metadata={"label": "创建者ID"})
    created_by_name = fields.Str(metadata={"label": "创建者姓名"})
    created_date = fields.Str(metadata={"label": "创建日期"})
    published_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "发布日期"})
    status = fields.Int(metadata={"label": "状态"})
    task_id = fields.Str(metadata={"label": "任务ID"})
    task_number = fields.Str(metadata={"label": "任务编号"})
    task_subject = fields.Str(metadata={"label": "任务主题"})
    last_modified_by_id = fields.Str(metadata={"label": "最后修改者ID"})
    last_modified_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "最后修改日期"})
    support_location_adcode = fields.Str(metadata={"label": "支持地点编码"}, load_default='', allow_none=True)
    support_location = fields.Str(metadata={"label": "支持地点"}, load_default='', allow_none=True)
    task_parent_id = fields.Str(metadata={"label": "上级ID"}, load_default="", allow_none=False)
    task_event_number = fields.Str(metadata={"label": "活动编号"})
    project_number = fields.Str(metadata={'label': '项目编号'})
    project_subject = fields.Str(metadata={"label": "所属项目主题"}, load_default="", allow_none=False)
    support_type_1st = fields.Dict(metadata={"label": "一级支持类型"}, load_default={}, allow_none=False)
    support_type_2nd = fields.Dict(metadata={"label": "二级支持类型"}, load_default={}, allow_none=False)
    project_id = fields.Str(metadata={"label": "项目ID"}, load_default="", allow_none=False)
    opportunity_number = fields.Str(metadata={"label": "所属项目编号"}, load_default="", allow_none=False)
    attachments_count = fields.Int(metadata={"label": "附件数量"})
    support_mode = fields.Int(metadata={"label": "支持模式"})
    assign_number = fields.Str(metadata={"label": "分派编号"}, load_default='', allow_none=True)


class SeProjectRecordMineList(ResponseSchema):
    page = fields.Int(metadata={"label": "第几页"}, load_default="", allow_none=False)
    size = fields.Int(metadata={"label": "页面大小"}, load_default="", allow_none=False)
    total = fields.Int(metadata={"label": "数据条目总和"}, load_default="", allow_none=False)
    list = fields.List(fields.Nested(SeProjectRecordMine(unknown="exclude")), required=True, data_key="list")


class SeProjectOperateHistoryResponse(ResponseSchema):
    id = fields.Int(metadata={"label": "ID"})
    action = fields.Str(metadata={"label": "动作"})
    log = fields.Str(metadata={"label": "操作日志"})
    created_by_id = fields.Str(metadata={"label": "创建人ID"})
    created_by_name = fields.Str(metadata={"label": "创建人名称"})
    created_date = fields.DateTime('%Y-%m-%d %H:%M:%S', metadata={"label": "创建时间"})


class SeProjectOperateHistoryList(ResponseSchema):
    page = fields.Int(metadata={"label": "第几页"}, load_default="", allow_none=False)
    size = fields.Int(metadata={"label": "页面大小"}, load_default="", allow_none=False)
    total = fields.Int(metadata={"label": "数据条目总和"}, load_default="", allow_none=False)
    list = fields.List(fields.Nested(SeProjectOperateHistoryResponse(unknown="exclude")), required=True, data_key="list")