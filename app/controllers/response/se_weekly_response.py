from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema


class SeWeekly(ResponseSchema):
    id = fields.Str(metadata={"label": "ID"})
    template = fields.Str(metadata={"label": "模板"})
    version = fields.Str(metadata={"label": "版本"})
    subject = fields.Str(metadata={"label": "主题"})
    receiver = fields.List(fields.Dict, metadata={"label": "收件人"})
    cc = fields.List(fields.Dict, metadata={"label": "抄送人"}, load_default=[], allow_none=True)
    department = fields.List(fields.Dict, metadata={"label": "部门列表"}, load_default=[], allow_none=True)
    status = fields.Str(metadata={"label": "状态"})
    send_date = fields.DateTime(metadata={'label': '发送时间'}, load_default='', allow_none=True)
    start_date = fields.DateTime(metadata={'label': '起始时间'}, load_default='', allow_none=True)
    end_date = fields.DateTime(metadata={'label': '截止时间'}, load_default='', allow_none=True)
    created_by_id = fields.Str(metadata={"label": "创建人"})
    created_date = fields.DateTime(metadata={'label': '创建时间'})
    last_modified_by_id = fields.Str(metadata={"label": "上次修改人"})
    last_modified_date = fields.DateTime(metadata={"label": "上次修改时间"})
    deleted_by_id = fields.Str(metadata={"label": "删除人"}, load_default='', allow_none=True)
    deleted_date = fields.DateTime(metadata={"label": "删除时间"}, load_default='', allow_none=True),
    data = fields.Dict(metadata={"label": "模板数据"}, load_default={}, allow_none=True)


class SeWeeklyList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(SeWeekly(unknown="exclude")))