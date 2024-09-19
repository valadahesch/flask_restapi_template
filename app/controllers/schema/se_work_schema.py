from app.models.se_work import SeWorkProject, SeWorkTask, SeWorkRecord, SeWorkApprovalRecord
from marshmallow import Schema, fields, post_load
from app.utils.func_util import nanoId, numberId


class SeWorkProjectSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    project_type = fields.Str(allow_none=True)
    project_number = fields.Str(allow_none=True, load_default=lambda: numberId())
    subject = fields.Str(allow_none=True)
    owner_id = fields.Str(allow_none=True)
    account_id = fields.Str(allow_none=True)
    account_name = fields.Str(allow_none=True)
    contact_name = fields.Str(allow_none=True)
    contact_info = fields.Str(allow_none=True)
    support_type_1st = fields.Str(allow_none=True)
    support_type_2nd = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    created_by_id = fields.Str(allow_none=True)
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    last_modified_by_id = fields.Str(allow_none=True)
    last_modified_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    deleted_by_id = fields.Str(allow_none=True)
    deleted_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SeWorkProject

    @post_load
    def make(self, data: dict, **kwargs):
        return SeWorkProject(**data)


class SeWorkTaskSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    parent_id = fields.Str(allow_none=True)
    project_id = fields.Str(allow_none=True)
    project_type = fields.Str(allow_none=True)
    task_number = fields.Str(allow_none=True, load_default=lambda: numberId())
    subject = fields.Str(allow_none=True)
    owner_id = fields.Str(allow_none=True)
    account_id = fields.Str(allow_none=True)
    account_name = fields.Str(allow_none=True)
    contact_name = fields.Str(allow_none=True)
    contact_info = fields.Str(allow_none=True)
    status = fields.Int(allow_none=True)
    support_mode = fields.Int(allow_none=True)
    support_type_1st = fields.Str(allow_none=True)
    support_type_2nd = fields.Str(allow_none=True)
    task_start_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    task_end_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    task_result = fields.Int(allow_none=True)
    task_incomplete_reason = fields.Str(allow_none=True)
    created_by_id = fields.Str(allow_none=True)
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    last_modified_by_id = fields.Str(allow_none=True)
    last_modified_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    deleted_by_id = fields.Str(allow_none=True)
    deleted_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SeWorkTask

    @post_load
    def make(self, data: dict, **kwargs):
        return SeWorkTask(**data)


class SeWorkRecordSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    support_start_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    support_end_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    support_duration = fields.Int(allow_none=True)
    published_date = fields.Str(allow_none=True)
    status = fields.Int(allow_none=True)
    task_id = fields.Str(allow_none=True)
    record_content = fields.Str(allow_none=True)
    created_by_id = fields.Str(allow_none=True)
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    last_modified_by_id = fields.Str(allow_none=True)
    last_modified_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    deleted_by_id = fields.Str(allow_none=True)
    deleted_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SeWorkRecord

    @post_load
    def make(self, data: dict, **kwargs):
        return SeWorkRecord(**data)


class SeWorkApprovalRecordSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    record_id = fields.Str(allow_none=True)
    project_id = fields.Str(allow_none=True)
    result = fields.Str(allow_none=True)
    incomplete_reason = fields.Str(allow_none=True)
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    approval_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SeWorkApprovalRecord

    @post_load
    def make(self, data: dict, **kwargs):
        return SeWorkApprovalRecord(**data)

