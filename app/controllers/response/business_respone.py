from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema


class BusinessLead(ResponseSchema):
    __subsystem__ = 'Business'
    __object__ = 'lead'

    city = fields.Str(metadata={"label": "城市"})
    company_name = fields.Str(metadata={"label": "公司名称"})
    contact_name = fields.Str(metadata={"label": "联系人姓名"})
    contact_role = fields.Int(metadata={"label": "联系人角色"})
    contact_way = fields.Str(metadata={"label": "联系方式"})
    create_time = fields.Str(metadata={"label": "创建时间"})
    customer_name = fields.Str(metadata={"label": "CRM客户名称"}, data_key='crm_customer_name')
    owner_name = fields.Str(metadata={"label": "CRM归属销售"}, data_key='crm_owner_name')
    email_pushed = fields.Int(metadata={"label": "邮件推送"}, load_default=0, allow_none=True)
    id = fields.Str(metadata={"label": "ID"})
    lead_code = fields.Str(metadata={"label": "线索编号"}, load_default='', allow_none=True)
    province = fields.Str(metadata={"label": "省份"})
    wework_pushed = fields.Int(metadata={"label": "企业微信推送"}, load_default=0, allow_none=True)


class LeadDetail(BusinessLead):
    __subsystem__ = 'Business'
    __object__ = 'lead.detail'
    customer_id = fields.Str(metadata={"label": "CRM客户名称"}, data_key='crm_customer_id')
    owner_id = fields.Str(metadata={"label": "CRM归属销售"}, data_key='crm_owner_id')
    description = fields.Str(metadata={"label": "描述"}, data_key='description')


class BusinessLeadList(ResponseSchema):
    page = fields.Int(allow_none=True)
    size = fields.Int(allow_none=True)
    total = fields.Int(allow_none=True)
    list = fields.List(fields.Nested(BusinessLead(unknown="exclude")))