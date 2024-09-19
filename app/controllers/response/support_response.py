from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema


class CallDetailRecord(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'User.info'

    additional_broker = fields.Str(metadata={"label": "额外的经纪人"}, data_key="AdditionalBroker")
    agent_ids = fields.Str(metadata={"label": "坐席ID"}, data_key="AgentIds")
    agent_names = fields.Str(metadata={"label": "坐席姓名"}, data_key="AgentNames")
    broker = fields.Str(metadata={"label": "经纪人"}, data_key="Broker")
    call_duration = fields.Int(metadata={"label": "通话时长"}, data_key="CallDuration", load_default=0, allow_none=True)
    called_number = fields.Str(metadata={"label": "被叫号码"}, data_key="CalledNumber")
    callee_location = fields.Str(metadata={"label": "被叫位置"}, data_key="CalleeLocation")
    caller_location = fields.Str(metadata={"label": "主叫位置"}, data_key="CallerLocation")
    calling_number = fields.Str(metadata={"label": "主叫号码"}, data_key="CallingNumber")
    contact_disposition = fields.Str(metadata={"label": "联系结果"}, data_key="ContactDisposition")
    contact_id = fields.Str(metadata={"label": "联系ID"}, data_key="ContactId")
    contact_type = fields.Str(metadata={"label": "联系类型"}, data_key="ContactType")
    dialing_time = fields.Int(metadata={"label": "拨号时间"}, data_key="DialingTime")
    established_time = fields.Int(metadata={"label": "建立时间"}, data_key="EstablishedTime")
    instance_id = fields.Str(metadata={"label": "实例ID"}, data_key="InstanceId")
    ivr_time = fields.Int(metadata={"label": "IVR时间"}, data_key="IvrTime")
    queue_time = fields.Int(metadata={"label": "排队时间"}, data_key="QueueTime")
    recording_duration = fields.Int(metadata={"label": "录音时长"}, data_key="RecordingDuration")
    recording_ready = fields.Bool(metadata={"label": "录音是否准备好"}, data_key="RecordingReady")
    release_initiator = fields.Str(metadata={"label": "释放发起者"}, data_key="ReleaseInitiator")
    release_reason = fields.Str(metadata={"label": "释放原因"}, data_key="ReleaseReason")
    release_time = fields.Int(metadata={"label": "释放时间"}, data_key="ReleaseTime")
    ring_time = fields.Int(metadata={"label": "振铃时间"}, data_key="RingTime")
    satisfaction_description = fields.Str(metadata={"label": "满意度描述"}, data_key="SatisfactionDescription")
    satisfaction_survey_channel = fields.Str(metadata={"label": "满意度调查渠道"}, data_key="SatisfactionSurveyChannel")
    satisfaction_survey_offered = fields.Bool(metadata={"label": "是否提供满意度调查"}, data_key="SatisfactionSurveyOffered")
    skill_group_ids = fields.Str(metadata={"label": "技能组ID"}, data_key="SkillGroupIds")
    skill_group_names = fields.Str(metadata={"label": "技能组名称"}, data_key="SkillGroupNames")
    start_time = fields.Int(metadata={"label": "开始时间"}, data_key="StartTime")
    talk_time = fields.Int(metadata={"label": "通话时间"}, data_key="TalkTime")
    wait_time = fields.Int(metadata={"label": "等待时间"}, data_key="WaitTime")


class CallDetailRecordList(ResponseSchema):
    page = fields.Int(allow_none=True, data_key="PageNumber", load_default=0)
    size = fields.Int(allow_none=True, data_key="PageSize", load_default=0)
    total = fields.Int(allow_none=True, data_key="TotalCount", load_default=0)
    list = fields.List(fields.Nested(CallDetailRecord(unknown="exclude")), data_key="List")


class CallMono(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'User.info'

    file_url = fields.Str(metadata={"label": "文件URL"})
    file_name = fields.Str(metadata={"label": "文件名"})


class SkillLevel(ResponseSchema):
    skill_level = fields.Int(metadata={"label": "技能等级"}, data_key="SkillLevel")
    skill_group_name = fields.Str(metadata={"label": "技能组名称"}, data_key="SkillGroupName")
    skill_group_id = fields.Str(metadata={"label": "技能组ID"}, data_key="SkillGroupId")


class AliyunUser(ResponseSchema):
    login_name = fields.Str(metadata={"label": "登录名"}, data_key="LoginName")
    email = fields.Str(metadata={"label": "邮箱"}, data_key="Email")
    device_id = fields.Str(metadata={"label": "设备ID"}, data_key="DeviceId")
    primary_account = fields.Bool(metadata={"label": "主账号"}, data_key="PrimaryAccount")
    skill_level_list = fields.List(fields.Nested(SkillLevel(unknown="exclude")), metadata={"label": "技能组列表"}, data_key="SkillLevelList")
    ram_id = fields.Int(metadata={"label": "RAM ID"}, data_key="RamId")
    display_id = fields.Str(metadata={"label": "显示ID"}, data_key="DisplayId")
    mobile = fields.Str(metadata={"label": "手机号码"}, data_key="Mobile")
    role_id = fields.Str(metadata={"label": "角色ID"}, data_key="RoleId")
    extension = fields.Str(metadata={"label": "分机号码"}, data_key="Extension")
    role_name = fields.Str(metadata={"label": "角色名称"}, data_key="RoleName")
    device_state = fields.Str(metadata={"label": "设备状态"}, data_key="DeviceState")
    user_id = fields.Str(metadata={"label": "用户ID"}, data_key="UserId")
    display_name = fields.Str(metadata={"label": "显示名称"}, data_key="DisplayName")
    device_ext = fields.Str(metadata={"label": "设备分机号码"}, data_key="DeviceExt")
    work_mode = fields.Str(metadata={"label": "工作模式"}, data_key="WorkMode")


class AliyunUserList(ResponseSchema):
    page = fields.Int(allow_none=True, data_key="PageNumber")
    size = fields.Int(allow_none=True, data_key="PageSize")
    total = fields.Int(allow_none=True, data_key="TotalCount")
    list = fields.List(fields.Nested(AliyunUser(unknown="exclude")), data_key="List")

