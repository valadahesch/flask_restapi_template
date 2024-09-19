from app.models.se_project import SeProjectProject, SeProjectTask, SeProjectRecord, SeProjectApprovalRecord, \
    SeProjectFocus, SeWeekly
from marshmallow import Schema, fields, post_load
from app.utils.func_util import nanoId, numberId


class SeProjectProjectSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    parent_project = fields.Str(allow_none=True)
    project_type = fields.Str(allow_none=True)
    project_number = fields.Str(allow_none=True, load_default=lambda: numberId())
    subject = fields.Str(allow_none=True)
    opportunity_number = fields.Str(allow_none=False)
    opportunity_name = fields.Str(allow_none=True)
    sale_by_id = fields.Str(allow_none=True)
    opportunity_value = fields.Int(allow_none=True)
    customer_requirement = fields.Str(allow_none=True)
    owner_id = fields.Str(allow_none=True)
    account_id = fields.Str(allow_none=True)
    account_name = fields.Str(allow_none=True)
    contact_name = fields.Str(allow_none=True)
    contact_info = fields.Str(allow_none=True)
    status = fields.Str(allow_none=True)
    created_by_id = fields.Str(allow_none=True)
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    last_modified_by_id = fields.Str(allow_none=True)
    last_modified_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    deleted_by_id = fields.Str(allow_none=True)
    deleted_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    project_phase = fields.Str(allow_none=True)
    crm_raw_data = fields.Str(allow_none=True)

    application_type = fields.Str(allow_none=True)
    is_big_project_support = fields.Str(allow_none=True)
    opportunity_level = fields.Str(allow_none=True)
    is_itai_project = fields.Str(allow_none=True)
    order_prediction = fields.Str(allow_none=True)
    expected_order_completion_date = fields.Date(format="%Y-%m-%d", allow_none=True)
    sales_leader_id = fields.Str(allow_none=True)
    business_stage = fields.Str(allow_none=True)
    competitors = fields.Str(allow_none=True)
    pre_bidding_date = fields.Date(format="%Y-%m-%d", allow_none=True)
    contact_position = fields.Str(allow_none=True)
    background_description = fields.Str(allow_none=True)
    return_reason = fields.Str(allow_none=True)
    deploy_core = fields.Str(allow_none=True)
    task_incomplete_reason = fields.Str(allow_none=True)
    task_result = fields.Int(allow_none=True)

    class Meta:
        model = SeProjectProject

    @post_load
    def make(self, data: dict, **kwargs):
        return SeProjectProject(**data)


class SeProjectTaskSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    parent_id = fields.Str(allow_none=True)
    project_id = fields.Str(allow_none=True)
    task_number = fields.Str(allow_none=True, load_default=lambda: numberId())
    event_number = fields.Str(allow_none=False)
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
    unapproval_reason = fields.Str(allow_none=True)
    created_by_id = fields.Str(allow_none=True)
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    last_modified_by_id = fields.Str(allow_none=True)
    last_modified_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    deleted_by_id = fields.Str(allow_none=True)
    deleted_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    crm_raw_data = fields.Str(allow_none=True)
    taken_hours = fields.Float(allow_none=True, load_default=0)
    contact_position = fields.Str(allow_none=True)
    origin_project = fields.Str(allow_none=True)
    task_location = fields.Str(allow_none=True)
    task_location_adcode = fields.Str(allow_none=True)
    assign_number = fields.Str(allow_none=True)

    class Meta:
        model = SeProjectTask

    @post_load
    def make(self, data: dict, **kwargs):
        return SeProjectTask(**data)


class SeProjectRecordSchema(Schema):
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
    support_location = fields.Str(allow_none=True)
    support_location_adcode = fields.Str(allow_none=True)
    support_mode = fields.Int(allow_none=True)
    support_type_1st = fields.Str(allow_none=True)
    support_type_2nd = fields.Str(allow_none=True)

    class Meta:
        model = SeProjectRecord

    @post_load
    def make(self, data: dict, **kwargs):
        return SeProjectRecord(**data)


class SeProjectApprovalRecordSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    record_id = fields.Str(allow_none=True)
    task_id = fields.Str(allow_none=True)
    main_task_id = fields.Str(allow_none=True)
    project_id = fields.Str(allow_none=True)
    result = fields.Str(allow_none=True)
    incomplete_reason = fields.Str(allow_none=True)
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    approval_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SeProjectApprovalRecord

    @post_load
    def make(self, data: dict, **kwargs):
        return SeProjectApprovalRecord(**data)


class SeProjectFocusSchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    project_id = fields.Str(allow_none=False)
    follower_id = fields.Str(allow_none=False)
    followed_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    deleted_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SeProjectFocus

    @post_load
    def make(self, data: dict, **kwargs):
        return SeProjectFocus(**data)


class SeWeeklySchema(Schema):
    # load(dict) -> obj
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    template = fields.Str(allow_none=False)
    version = fields.Str(allow_none=False)
    subject = fields.Str(allow_none=False)
    receiver = fields.Str(allow_none=False)
    cc = fields.Str(allow_none=False)
    department_ids = fields.Str(allow_none=False)
    status = fields.Str(allow_none=False)
    start_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    end_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    send_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    created_by_id = fields.Str(allow_none=False)
    created_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    last_modified_by_id = fields.Str(allow_none=False)
    last_modified_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    deleted_by_id = fields.Str(allow_none=False)
    deleted_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)

    class Meta:
        model = SeWeekly

    @post_load
    def make(self, data: dict, **kwargs):
        return SeWeekly(**data)
