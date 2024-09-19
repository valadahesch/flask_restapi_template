from app.models.ps_inspection import PsTask, PsTaskUploadHistory, PsUserMapping, PsCustomerArchives
from marshmallow import Schema, fields, post_load
from app.utils.func_util import nanoId, numberId


class PsUserMappingSchema(Schema):
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    project_system_id = fields.Str(allow_none=True)
    technical_department_site_id = fields.Str(allow_none=True)

    class Meta:
        model = PsUserMapping

    @post_load
    def make(self, data: dict, **kwargs):
        return PsUserMapping(**data)


class PsTaskSchema(Schema):
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    task_id = fields.Str(allow_none=True)
    project_id = fields.Str(allow_none=True)
    is_pass = fields.Str(allow_none=True)
    report_field_id = fields.Str(allow_none=True)
    preview_field_id = fields.Str(allow_none=True)
    external = fields.Str(allow_none=True)
    inspection_type = fields.Str(allow_none=True)

    class Meta:
        model = PsTask

    @post_load
    def make(self, data: dict, **kwargs):
        return PsTask(**data)


class PsTaskUploadHistorySchema(Schema):
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    task_id = fields.Str(allow_none=True)
    subject = fields.Str(allow_none=True)
    file_name = fields.Str(allow_none=True)
    upload_file_id = fields.Str(allow_none=True)
    deciphering = fields.Str(allow_none=True)
    created_by_id = fields.Str(allow_none=True)
    created_by_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    delete_by_id = fields.Str(allow_none=True)
    delete_by_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    report_file_id = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    area = fields.Str(allow_none=True)
    account_id = fields.Str(allow_none=True)
    account_name = fields.Str(allow_none=True)

    class Meta:
        model = PsTaskUploadHistory

    @post_load
    def make(self, data: dict, **kwargs):
        return PsTaskUploadHistory(**data)


class PsCustomerArchivesSchema(Schema):
    id = fields.Str(allow_none=False, load_default=lambda: nanoId())
    task_id = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    account_id = fields.Str(allow_none=False)
    account_name = fields.Str(allow_none=True)
    area = fields.Str(allow_none=True)
    device_name = fields.Str(allow_none=True, load_from='hostname')
    device_model = fields.Str(allow_none=True, load_from='product_name')
    device_sn = fields.Str(allow_none=True, load_from='sn')
    ha_state = fields.Str(allow_none=True)
    software_version = fields.Str(allow_none=True, load_from='version')
    uptime = fields.Str(allow_none=True)
    feature = fields.Str(allow_none=True)
    plat_expiration = fields.Str(allow_none=True)
    session_info = fields.Str(allow_none=True)
    alloc_session = fields.Str(allow_none=True, load_from='rampup_session')
    cur_cpu = fields.Str(allow_none=True)
    cp_memory = fields.Str(allow_none=True)
    dp_memory = fields.Str(allow_none=True)
    throughput = fields.Str(allow_none=True)
    ps_status = fields.Str(allow_none=True)
    fan_status = fields.Str(allow_none=True, load_from='env_fan_status')
    module_status = fields.Str(allow_none=True)
    env_cpu_temperature = fields.Str(allow_none=True)
    snat_rate = fields.Str(allow_none=True, load_form='snat')
    dnat_rate = fields.Str(allow_none=True, load_form='dnat')
    address_rate = fields.Str(allow_none=True, load_form='address')
    server_rate = fields.Str(allow_none=True, load_form='server')
    policy_rate = fields.Str(allow_none=True, load_form='policy')
    alg_staus = fields.Str(allow_none=True, load_form='alg')
    ha_status_info = fields.Str(allow_none=True, load_form='ha')
    log_folder = fields.Str(allow_none=True, load_form='logging_status')
    attack_info = fields.Str(allow_none=True, load_form='log_threat')
    exception_log_info = fields.Str(allow_none=True, load_form='log_event')
    clock = fields.Str(allow_none=True)
    original_manager = fields.Str(allow_none=True)
    account_manager = fields.Str(allow_none=True)
    contact_info = fields.Str(allow_none=True)
    purchase_date = fields.Str(allow_none=True)
    online_date = fields.Date(format="%Y-%m-%d", allow_none=True)
    created_by_id = fields.Str(allow_none=True)
    created_by_date = fields.DateTime(format="%Y-%m-%d %H:%M:%S", allow_none=True)
    status = fields.Str(allow_none=True)
    is_publish = fields.Str(allow_none=True)
    raw_data = fields.Str(allow_none=True)
    machine_room = fields.Str(allow_none=True)
    lic_expiration_time = fields.Date(format="%Y-%m-%d", allow_none=True)
    route_entry = fields.Str(allow_none=True)
    inspection_type = fields.Str(allow_none=True)
    compare_main_baseconfig = fields.Str(allow_none=True)
    password_policy = fields.Str(allow_none=True)
    admin_lockout_duration = fields.Str(allow_none=True)
    unsafe_interface = fields.Str(allow_none=True)
    admin_host = fields.Str(allow_none=True)
    all_passrlue = fields.Str(allow_none=True)
    logging_status = fields.Str(allow_none=True)
    log_threat = fields.Str(allow_none=True)
    log_alarm = fields.Str(allow_none=True)
    ha_group = fields.Str(allow_none=True)
    synced = fields.Str(allow_none=True)
    poor = fields.Str(allow_none=True)

    class Meta:
        model = PsCustomerArchives

    @post_load
    def make(self, data: dict, **kwargs):
        return PsCustomerArchives(**data)
