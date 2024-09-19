from datetime import datetime
from app.models.online_tools import AuxiliaryConf2Hs
from marshmallow import Schema, fields, post_load
from app.utils.func_util import nanoId


class Conf2HsSchema(Schema):
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    file_name = fields.Str()
    brand_name = fields.Str()
    brand_version = fields.Str()
    models = fields.Str()
    export = fields.Str()
    description = fields.Str()
    result = fields.Str()
    failed_reason = fields.Str()
    created_by_id = fields.Str()
    created_date = fields.DateTime(
        format="%Y-%m-%d %H:%M:%S", load_default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    class Meta:
        model = AuxiliaryConf2Hs

    @post_load
    def make_load(self, data: dict, **kwargs):
        return AuxiliaryConf2Hs(**data)