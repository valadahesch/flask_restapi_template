from app.models.eco_partner import SeEcoRecord, SeEcoTask, SeEcoApprovalRecord
from marshmallow import Schema, fields, post_load
from app.utils.func_util import nanoId, numberId


class SeEcoTaskSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    parent_id = fields.Str(allow_none=True)
    task_number = fields.Str(allow_none=True, load_default=lambda: numberId())
    subject = fields.Str(allow_none=True)
    partner_id = fields.Str(allow_none=True)
    partner_name = fields.Str(allow_none=True)
    partner_status = fields.Str(allow_none=True)
    partner_industry = fields.Str(allow_none=True)
    partner_contact = fields.Str(allow_none=True)
    partner_contact_info = fields.Str(allow_none=True)
    channel_manager_id = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    owner_id = fields.Str(allow_none=True)
    support_mode = fields.Str(allow_none=True)
    support_type_1st = fields.Str(allow_none=True)
    support_type_2nd = fields.Str(allow_none=True)
    start_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    end_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    duration = fields.Int(allow_none=True)
    task_result = fields.Str(allow_none=True)
    task_incomplete_reason = fields.Str(allow_none=True)
    created_by_id = fields.Str(allow_none=True)
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    last_modified_by_id = fields.Str(allow_none=True)
    last_modified_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    deleted_by_id = fields.Str(allow_none=True)
    deleted_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SeEcoTask

    @post_load
    def make(self, data: dict, **kwargs):
        return SeEcoTask(**data)


class SeEcoRecordSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    support_start_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    support_end_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    support_duration = fields.Int(allow_none=True)
    published_date = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    task_id = fields.Str(allow_none=True)
    record_content = fields.Str(allow_none=True)
    unapproval_reason = fields.Str(allow_none=True)
    created_by_id = fields.Str(allow_none=True)
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    last_modified_by_id = fields.Str(allow_none=True)
    last_modified_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    deleted_by_id = fields.Str(allow_none=True)
    deleted_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SeEcoRecord

    @post_load
    def make(self, data: dict, **kwargs):
        return SeEcoRecord(**data)


class SeEcoApprovalRecordSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    record_id = fields.Str(allow_none=True)
    main_task_id = fields.Str(allow_none=True)
    result = fields.Str(allow_none=True)
    incomplete_reason = fields.Str(allow_none=True)
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    approval_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SeEcoApprovalRecord

    @post_load
    def make(self, data: dict, **kwargs):
        return SeEcoApprovalRecord(**data)





