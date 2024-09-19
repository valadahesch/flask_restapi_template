from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema




class QueryDirectoryDetailResponseList(ResponseSchema):
    id = fields.Str(metadata={"label": "id"}, load_default="", allow_none=False)
    parent_id = fields.Str(metadata={"label": "parenet_id"}, load_default="", allow_none=True)
    obj_type = fields.Str(metadata={"label": "对象类型"}, load_default="", allow_none=True)
    obj_name = fields.Str(metadata={"label": "对象名"}, load_default="", allow_none=True)
    file_type = fields.Str(metadata={"label": "文件类型"}, load_default="", allow_none=False)
    file_size = fields.Int(metadata={"label": "文件大小(字节)"}, load_default=0, allow_none=False)
    created_by_id = fields.Str(metadata={"label": "创建人ID"}, load_default="", allow_none=False)
    created_date = fields.Str(metadata={"label": "创建时间"}, load_default="", allow_none=False)
    created_by_name = fields.Str(metadata={"label": "创建人昵称"}, load_default="", allow_none=False)


class QueryDirectoryDetailResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Directory.info'
    list = fields.List(fields.Nested(QueryDirectoryDetailResponseList(unknown="exclude")), required=True, data_key="list")