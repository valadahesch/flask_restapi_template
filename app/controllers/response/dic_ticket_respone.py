from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema


# /api/dic/ticket
class CreateTicketResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Ticket.info'
    id = fields.Str(metadata={"label": "新创建的工单ID"}, load_default="", allow_none=False)


# /api/dic/ticket/: ticket_id

class UpdateTicketResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Ticket.info'

class DeleteTicketResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Ticket.info'

# /api/dic/ticket/list


class ListTicketResponseList(ResponseSchema):
    id = fields.Str(metadata={"label": "id"}, load_default="", allow_none=False)
    parent_id = fields.Str(metadata={"label": "parenet_id"}, load_default="", allow_none=True)
    number = fields.Str(metadata={"label": "number"}, load_default="", allow_none=False)
    subject = fields.Str(metadata={"label": "主题"}, load_default="", allow_none=False)
    status = fields.Str(metadata={"label": "状态"}, load_default="", allow_none=False)
    privacy = fields.Str(metadata={"label": "私有性"}, load_default="", allow_none=True)
    commit_by_id = fields.Str(metadata={"label": "提交人ID"}, load_default="", allow_none=False)
    commit_by_name = fields.Str(metadata={"label": "提交人"}, load_default="", allow_none=False)
    created_by_id = fields.Str(metadata={"label": "提交人ID"}, load_default="", allow_none=False)
    created_by_name = fields.Str(metadata={"label": "提交人"}, load_default="", allow_none=False)
    created_date = fields.Str(metadata={"label": "提交时间"}, load_default="", allow_none=False)
    last_modified_by_id = fields.Str(metadata={"label": "最后修改人ID"}, load_default="", allow_none=False)
    last_modified_date = fields.Str(metadata={"label": "最后修改时间"}, load_default="", allow_none=False)
    support_type = fields.Str(metadata={"label": "支持类型"}, load_default="", allow_none=False)
    priority = fields.Str(metadata={"label": "优先级"}, load_default="", allow_none=False)
    created_date = fields.Str(metadata={"label": "创建时间"}, load_default="", allow_none=False)
    functional_module_id = fields.Str(metadata={"label": "功能模块ID"}, load_default="", allow_none=False)
    functional_module_name = fields.Str(metadata={"label": "功能模块名称"}, load_default="", allow_none=False)


class ListTicketResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Ticket.info'
    page = fields.Int(metadata={"label": "第几页"}, load_default="", allow_none=False)
    size = fields.Int(metadata={"label": "页面大小"}, load_default="", allow_none=False)
    total = fields.Int(metadata={"label": "数据条目总和"}, load_default="", allow_none=False)
    list = fields.List(fields.Nested(ListTicketResponseList(unknown="exclude")), required=True, data_key="list")


# /api/dic/ticket/: ticket_id
class GetTicketResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Ticket.info'
    id = fields.Str(metadata={"label": "工单ID"}, load_default="", allow_none=False)
    parent_id = fields.Str(metadata={"label": "工单父级ID"}, load_default="", allow_none=False)
    number = fields.Str(metadata={"label": "工单编号"}, load_default="", allow_none=False)
    subject = fields.Str(metadata={"label": "主题"}, load_default="", allow_none=False)
    description = fields.Str(metadata={"label": "描述"}, load_default="", allow_none=False)
    status = fields.Str(metadata={"label": "状态"}, load_default="", allow_none=False)
    commit_by_id = fields.Str(metadata={"label": "提交人"}, load_default="", allow_none=False)
    commit_by_name = fields.Str(metadata={"label": "提交人"}, load_default="", allow_none=False)
    created_date = fields.Str(metadata={"label": "提交时间"}, load_default="", allow_none=False)
    created_by_id = fields.Str(metadata={"label": "创建人"}, load_default="", allow_none=False)
    created_by_name = fields.Str(metadata={"label": "创建人昵称"}, load_default="", allow_none=False)
    last_modified_by_id = fields.Str(metadata={"label": "最好修改人"}, load_default="", allow_none=True)
    last_modified_date = fields.Str(metadata={"label": "最后修改时间"}, load_default="", allow_none=True)
    support_type = fields.Str(metadata={"label": "支持类型"}, load_default="", allow_none=False)
    priority = fields.Str(metadata={"label": "优先级"}, load_default="", allow_none=False)
    functional_module_id = fields.Str(metadata={"label": "功能模块"}, load_default="", allow_none=False)
    functional_module_name = fields.Str(metadata={"label": "功能模块ID"}, load_default="", allow_none=False)
    privacy = fields.Str(metadata={"label": "私有 公有"}, load_default="", allow_none=False)
    first_delivery_date = fields.Str(metadata={"label": "首次交付时间"}, load_default="", allow_none=False)
    due_time = fields.Str(metadata={"label": "预计交付时间"}, load_default="", allow_none=False)
    cancel_by_reason = fields.Str(metadata={"label": "取消原因"}, load_default="", allow_none=True)
    feasibility = fields.Str(metadata={"label": "驳回原因"}, load_default="", allow_none=True)


# /api/dic/ticket/permission/:page_title
class GetTicketDetailPermissionResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Ticket.info'
    list = fields.List(fields.Raw(), metadata={"label": "权限"}, load_default=[], allow_none=False)

# /api/dic/ticket/: ticket_id/task
class CreateTaskResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Ticket.info'
    id = fields.Str(metadata={"label": "新创建的工单ID"}, load_default="", allow_none=False)

# /api/dic/ticket/project/list

class ListProjectsResponseList(ResponseSchema):
    id = fields.Str(metadata={"label": "id"}, load_default="", allow_none=False)
    key = fields.Str(metadata={"label": "唯一key"}, load_default="", allow_none=False)
    project_name = fields.Str(metadata={"label": "项目名"}, load_default="", allow_none=False)
    project_path = fields.Str(metadata={"label": "项目路径"}, load_default="", allow_none=False)
    created_by_id = fields.Str(metadata={"label": "创建人ID"}, load_default="", allow_none=False)
    created_date = fields.Str(metadata={"label": "创建时间"}, load_default="", allow_none=False)



class ListProjectsResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Ticket.info'

    list = fields.List(fields.Nested(ListProjectsResponseList(unknown="exclude")), required=True, data_key="list")


# /api/dic/ticket/:ticket_id/message

class CreateMessageResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Ticket.info'
    id = fields.Str(metadata={"label": "id"}, load_default="", allow_none=False)



# /api/dic/ticket/project/list

class GetMessageResponseList(ResponseSchema):
    id = fields.Str(metadata={"label": "id"}, load_default="", allow_none=False)
    created_by_id = fields.Str(metadata={"label": "评论人"}, load_default="", allow_none=False)
    created_username = fields.Str(metadata={"label": "评论人昵称"}, load_default="", allow_none=False)
    to_username = fields.Str(metadata={"label": "被回复人"}, load_default="", allow_none=False)
    created_date = fields.Str(metadata={"label": "创建时间"}, load_default="", allow_none=False)
    parent_id = fields.Str(metadata={"label": "父级ID"}, load_default="", allow_none=False)
    content = fields.Str(metadata={"label": "评论"}, load_default="", allow_none=False)
    need_reply = fields.Bool(metadata={"label": "是否需要回复"}, load_default="", allow_none=False)



class GetMessageResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Ticket.info'
    page = fields.Int(metadata={"label": "第几页"}, load_default="", allow_none=False)
    size = fields.Int(metadata={"label": "页面大小"}, load_default="", allow_none=False)
    total = fields.Int(metadata={"label": "数据条目总和"}, load_default="", allow_none=False)
    list = fields.List(fields.Nested(GetMessageResponseList(unknown="exclude")), required=True, data_key="list")

# /api/dic/ticket/functional_module/list

class ListFunctionalModuleResponseList(ResponseSchema):
    id = fields.Str(metadata={"label": "id"}, load_default="", allow_none=False)
    name = fields.Str(metadata={"label": "名称"}, load_default="", allow_none=False)
    description = fields.Str(metadata={"label": "描述"}, load_default="", allow_none=True)
    

class ListFunctionalModuleResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Ticket.info'

    list = fields.List(fields.Nested(ListFunctionalModuleResponseList(unknown="exclude")), required=True, data_key="list")




class GetTaskResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Ticket.info'
    page = fields.Int(metadata={"label": "第几页"}, load_default="", allow_none=False)
    size = fields.Int(metadata={"label": "页面大小"}, load_default="", allow_none=False)
    total = fields.Int(metadata={"label": "数据条目总和"}, load_default="", allow_none=False)
    list = fields.List(fields.Raw(), metadata={"label": "任务数据"}, load_default=[], allow_none=False)


#/api/dic/ticket/tasks
class GetMyTaskResponseList(ResponseSchema):
    id = fields.Str(metadata={"label": "id"}, load_default="", allow_none=False)
    subject = fields.Str(metadata={"label": "任务主题"}, load_default="", allow_none=False)
    created_date = fields.Str(metadata={"label": "提交时间"}, load_default="", allow_none=False)
    created_by_id = fields.Str(metadata={"label": "创建人"}, load_default="", allow_none=False)
    created_by_name = fields.Str(metadata={"label": "创建人昵称"}, load_default="", allow_none=False)
    assign_by_id = fields.Str(metadata={"label": "指派人"}, load_default="", allow_none=False)
    assign_by_name = fields.Str(metadata={"label": "指派人"}, load_default="", allow_none=False)
    handle_type = fields.Str(metadata={"label": "任务类型"}, load_default="", allow_none=False)
    ticket_id = fields.Str(metadata={"label": "id"}, load_default="", allow_none=False)
    ticket_subject = fields.Str(metadata={"label": "工单主题"}, load_default="", allow_none=False)
    ticket_status = fields.Str(metadata={"label": "工单状态"}, load_default="", allow_none=False)
    ticket_number = fields.Str(metadata={"label": "工单编号"}, load_default="", allow_none=False)
    ticket_support_type = fields.Str(metadata={"label": "工单支持类型"}, load_default="", allow_none=False)
    ticket_priority = fields.Str(metadata={"label": "工单优先级"}, load_default="", allow_none=False)
    functional_module_id = fields.Str(metadata={"label": "工单功能模块"}, load_default="", allow_none=False)
    functional_module_name = fields.Str(metadata={"label": "工单功能模块"}, load_default="", allow_none=False)


class GetMyTaskResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Task.info'
    page = fields.Int(metadata={"label": "第几页"}, load_default="", allow_none=False)
    size = fields.Int(metadata={"label": "页面大小"}, load_default="", allow_none=False)
    total = fields.Int(metadata={"label": "数据条目总和"}, load_default="", allow_none=False)
    list = fields.List(fields.Nested(GetMyTaskResponseList(unknown="exclude")), required=True, data_key="list")