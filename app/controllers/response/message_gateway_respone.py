from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema
from datetime import datetime


class AddMessageGatewayTemplateResponse(ResponseSchema):
    __subsystem__ = 'Message_Gateway'
    __object__ = 'message_gateway.info'
    id = fields.Str(metadata={"label": "新创建的工单ID"}, load_default="", allow_none=False)
    
    
    
class GetMessageGatewayTemplateResponse(ResponseSchema):
    __subsystem__ = 'Message_Gateway'
    __object__ = 'message_gateway.info'
    
    id = fields.Str(metadata={"label": "唯一标识"}, load_default="", allow_none=False)
    template_number = fields.Str(metadata={"label": "模版编号"}, load_default="", allow_none=False)
    subject = fields.Str(metadata={"label": "模版主题"}, load_default="", allow_none=False)
    content = fields.Str(metadata={"label": "模版内容"}, load_default="", allow_none=False)
    created_by_id = fields.Str(metadata={"label": "创建人"}, load_default="", allow_none=False)
    created_by_name = fields.Str(metadata={"label": "创建人昵称"}, load_default="", allow_none=False)
    created_date = fields.Str(metadata={"label": "创建时间"}, load_default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    last_modified_by_id = fields.Str(metadata={"label": "最后修改人"}, load_default="", allow_none=False)
    last_modified_by_name = fields.Str(metadata={"label": "最后修改人昵称"}, load_default="", allow_none=False)
    last_modified_date = fields.Str(metadata={"label": "最后修改时间"}, load_default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    enable = fields.Bool(metadata={"label": "是否可用"}, load_default="", allow_none=False)
    media_type = fields.Str(metadata={"label": "媒体类型"}, load_default="email", allow_none=False)
    language = fields.Str(metadata={"label": "语种"}, load_default="zh_cn", allow_none=False)
    remark = fields.Str(metadata={"label": "备注"}, load_default="", allow_none=False)


class PutMessageGatewayTemplateResponse(ResponseSchema):
    __subsystem__ = 'Message_Gateway'
    __object__ = 'message_gateway.info'


class ListMessageGatewayTemplateResponse(ResponseSchema):
    __subsystem__ = 'Message_Gateway'
    __object__ = 'message_gateway.info'

    page = fields.Int(metadata={"label": "第几页"}, load_default="", allow_none=False)
    size = fields.Int(metadata={"label": "页面大小"}, load_default="", allow_none=False)
    total = fields.Int(metadata={"label": "数据条目总和"}, load_default="", allow_none=False)
    list = fields.List(fields.Nested(GetMessageGatewayTemplateResponse(unknown="exclude")), required=True, data_key="list")




