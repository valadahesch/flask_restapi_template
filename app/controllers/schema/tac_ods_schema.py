from app.models.tac_ods import OdsWecomUser
from marshmallow import Schema, fields, post_load


class OdsWecomUserSchema(Schema):
    # load(dict) -> obj
    userid = fields.Str(allow_none=False)
    name = fields.Str()
    mobile = fields.Str()
    department = fields.Str()
    main_department = fields.Int()
    order = fields.Str()
    position = fields.Str()
    gender = fields.Str()
    email = fields.Str()
    is_leader_in_dept = fields.Str()
    direct_leader = fields.Str()
    avatar = fields.Str()
    thumb_avatar = fields.Str()
    telephone = fields.Str()
    alias = fields.Str()
    extattr = fields.Str()
    status = fields.Int()
    qr_code = fields.Str()
    external_profile = fields.Str()
    external_position = fields.Str()
    address = fields.Str()
    last_sync_time = fields.DateTime()
    is_deleted = fields.Bool()
    deleted_time = fields.DateTime()

    class Meta:
        model = OdsWecomUser

    @post_load
    def make_user(self, data: dict, **kwargs):
        return OdsWecomUser(**data)


class OdsWecomDepartmentSchema(Schema):
    # load(dict) -> obj
    id = fields.Int(allow_none=False)
    name = fields.Str()
    name_en = fields.Str(allow_none=True)
    department_leader = fields.Str(allow_none=True)
    parentid = fields.Int(allow_none=True)
    order = fields.Int(allow_none=True)
    last_sync_time = fields.DateTime()
    is_deleted = fields.Int(allow_none=True)
    deleted_time = fields.DateTime()