from app.models.file_system import SysFileManage
from app.controllers.dao.file_system_dao import SysFileManageDao
from marshmallow import Schema, fields, post_load
from app.utils.func_util import nanoid_iterator

file_system_nanoid = nanoid_iterator(SysFileManageDao.uniqueId, 20)


class FileManageSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: next(file_system_nanoid))
    parent_id = fields.Str(allow_none=True)
    obj_type = fields.Str(allow_none=True)
    obj_name = fields.Str(allow_none=True)
    file_type = fields.Str(allow_none=True)
    file_size = fields.Int(allow_none=True)
    created_by_id = fields.Str(allow_none=False)
    deleted_by_id = fields.Str(allow_none=True)
    related_object_type = fields.Str(allow_none=True)
    related_object_id = fields.Str(allow_none=True)
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=False)
    deleted_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    contact_position = fields.Str(allow_none=True)

    class Meta:
        model = SysFileManage 

    @post_load
    def make(self, data: dict, **kwargs):
        return SysFileManage(**data)