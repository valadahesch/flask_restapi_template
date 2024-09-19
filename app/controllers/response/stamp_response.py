from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema


class ListStampRecordListResponse(ResponseSchema):
    file_id = fields.Str(metadata={"label": "文件id"}, load_default="", allow_none=False)
    reason = fields.Str(metadata={"label": "盖章原因"}, load_default="", allow_none=True)
    request_by_id = fields.Str(metadata={"label": "申请人"}, load_default="", allow_none=True)
    request_by_name = fields.Str(metadata={"label": "申请人"}, load_default="", allow_none=True)
    stamp_by_id = fields.Str(metadata={"label": "盖章人"}, load_default="", allow_none=True)
    stamp_by_name = fields.Str(metadata={"label": "盖章人"}, load_default="", allow_none=True)
    created_date = fields.Str(metadata={"label": "申请盖章时间"}, load_default="", allow_none=True)
    stamp_date = fields.Str(metadata={"label": "盖章时间"}, load_default="", allow_none=True)
    file_name = fields.Str(metadata={"label": "文件名"}, load_default="", allow_none=True)
    status = fields.Integer(metadata={"label": "状态"}, load_default="", allow_none=True)

class StampRecordListResponse(ResponseSchema):
    page = fields.Int(metadata={"label": "第几页"}, load_default=1, allow_none=True)
    size = fields.Int(metadata={"label": "页面大小"}, load_default=10, allow_none=True)
    total = fields.Int(metadata={"label": "数据条目总和"}, load_default=0, allow_none=True)
    list = fields.List(fields.Nested(ListStampRecordListResponse(unknown="exclude")), required=True, data_key="list")