from datetime import datetime
from app.models.techadmin import BusinessLead
from marshmallow import Schema, fields, post_load
from app.utils.func_util import nanoId


class BusinessLeadSchema(Schema):
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    contact_name = fields.Str()
    contact_role = fields.Int()
    contact_way = fields.Str()
    company_name = fields.Str()
    crm_customer_id = fields.Str()
    crm_customer_name = fields.Str()
    crm_owner_id = fields.Str()
    crm_owner_name = fields.Str()
    province = fields.Str()
    city = fields.Str()
    description = fields.Str()
    lead_code = fields.Str()
    lead_id = fields.Str()
    email_pushed = fields.Int()
    wework_pushed = fields.Int()
    create_by = fields.Str()
    create_time = fields.DateTime(
        format="%Y-%m-%d %H:%M:%S", load_default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    class Meta:
        model = BusinessLead

    @post_load
    def make_load(self, data: dict, **kwargs):
        return BusinessLead(**data)
