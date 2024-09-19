from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema


class LicenseRecordListResponse(ResponseSchema):
    id = fields.Str(metadata={"label": "id"}, allow_none=False)
    order_id = fields.Str(metadata={"label": "订单id"}, load_default="", allow_none=True)
    account_id = fields.Str(metadata={"label": "客户"}, load_default="", allow_none=True)
    account_name = fields.Str(metadata={"label": "客户"}, load_default="", allow_none=True)
    created_by_name = fields.Str(metadata={"label": "申请人"})
    created_by_id = fields.Str(metadata={"label": "申请人"})
    sn = fields.Str(metadata={"label": "sn"})
    product_name = fields.Str(metadata={"label": "产品名"})
    lic_params = fields.List(fields.Raw(), metadata={"label": "许可类型"})
    created_date = fields.DateTime(metadata={"label": "创建时间"}, load_default="", allow_none=True)
    end_time = fields.Date(metadata={"label": "许可有效期"}, load_default="", allow_none=True)
    status = fields.Str(metadata={"label": "状态"}, load_default="", allow_none=True)
    error_msg = fields.Str(metadata={"label": "失败原因"}, load_default="", allow_none=True)

class LicenseRecordResponse(ResponseSchema):
    page = fields.Int(metadata={"label": "第几页"}, load_default=1, allow_none=True)
    size = fields.Int(metadata={"label": "页面大小"}, load_default=10, allow_none=True)
    total = fields.Int(metadata={"label": "数据条目总和"}, load_default=0, allow_none=True)
    list = fields.List(fields.Nested(LicenseRecordListResponse(unknown="exclude")), required=True, data_key="list")