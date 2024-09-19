# coding: utf-8
from . import db


class SeProjectApprovalRecord(db.Model):
    __tablename__ = 'se_project_approval_record'

    id = db.Column(db.String(20, 'utf8_general_ci'), primary_key=True)
    record_id = db.Column(db.String(20, 'utf8_general_ci'), nullable=False, info='日志ID')
    task_id = db.Column(db.String(20, 'utf8_general_ci'), nullable=False, info='任务ID')
    main_task_id = db.Column(db.String(20, 'utf8_general_ci'), nullable=False, info='主任务ID')
    project_id = db.Column(db.String(20, 'utf8_general_ci'), nullable=False, info='项目ID')
    result = db.Column(db.String(5, 'utf8_general_ci'), info='审批结果')
    incomplete_reason = db.Column(db.String(100, 'utf8_general_ci'), info='不通过原因')
    created_date = db.Column(db.DateTime, info='创建时间')
    approval_date = db.Column(db.DateTime, info='审批时间')


class SeProjectProject(db.Model):
    __tablename__ = 'se_project_project'

    id = db.Column(db.String(20, 'utf8_general_ci'), primary_key=True, info='ID')
    parent_project = db.Column(db.String(20, 'utf8_general_ci'), primary_key=True, info='父项目ID')
    project_type = db.Column(db.String(30, 'utf8_general_ci'), info='项目类型：固定为商机管理')
    project_number = db.Column(db.String(10, 'utf8_general_ci'), nullable=False, unique=True, info='项目编号')
    opportunity_number = db.Column(db.String(30, 'utf8_general_ci'), info='商机编号')
    opportunity_name = db.Column(db.String(100, 'utf8_general_ci'), info='商机名称')
    subject = db.Column(db.String(100, 'utf8_general_ci'), info='项目主题：默认为CRM的资源申请名称')
    sale_by_id = db.Column(db.String(20, 'utf8_general_ci'), info='申请人：销售')
    owner_id = db.Column(db.String(20, 'utf8_general_ci'), info='责任人：被分配SE')
    account_id = db.Column(db.String(50, 'utf8_general_ci'), info='客户id')
    account_name = db.Column(db.String(100, 'utf8_general_ci'), info='客户名称')
    contact_name = db.Column(db.String(20, 'utf8_general_ci'), info='客户联系人')
    contact_info = db.Column(db.String(50, 'utf8_general_ci'), info='客户联系方式')
    status = db.Column(db.SmallInteger, info='状态')
    opportunity_value = db.Column(db.String(20, 'utf8_general_ci'), info='商机金额')
    customer_requirement = db.Column(db.Text(collation='utf8_general_ci'), info='客户需求描述')
    created_by_id = db.Column(db.String(20, 'utf8_general_ci'), info='创建人：SE分派员邮箱')
    created_date = db.Column(db.DateTime, info='创建时间')
    last_modified_by_id = db.Column(db.String(20, 'utf8_general_ci'), info='上次修改人')
    last_modified_date = db.Column(db.DateTime, info='上次修改时间')
    deleted_by_id = db.Column(db.String(20, 'utf8_general_ci'), info='删除人')
    deleted_date = db.Column(db.DateTime, info='删除时间')
    crm_raw_data = db.Column(db.Text(collation='utf8_general_ci'), info='crm原始数据')
    project_phase = db.Column(db.String(20, 'utf8_general_ci'), info='项目阶段')
    task_result = db.Column(db.String(255, 'utf8_general_ci'), info='项目归档结果')
    task_incomplete_reason = db.Column(db.String(255, 'utf8_general_ci'), info='项目归档结果备注')

    application_type = db.Column(db.String(10, 'utf8_general_ci'), info='申请类型')
    is_big_project_support = db.Column(db.String(10, 'utf8_general_ci'), info='是否大项目支持')
    opportunity_level = db.Column(db.String(10, 'utf8_general_ci'), info='商机分级')
    is_itai_project = db.Column(db.String(10, 'utf8_general_ci'), info='是否信创项目')
    order_prediction = db.Column(db.String(10, 'utf8_general_ci'), info='下单预测')
    expected_order_completion_date = db.Column(db.Date, info='关单日期')
    sales_leader_id = db.Column(db.String(50, 'utf8_general_ci'), info='销售上级')
    business_stage = db.Column(db.String(50, 'utf8_general_ci'), info='商机阶段')
    competitors = db.Column(db.String(500, 'utf8_general_ci'), info='竞争对手')
    pre_bidding_date = db.Column(db.Date, info='计划招标时间')
    contact_position = db.Column(db.String(50, 'utf8_general_ci'), info='联系人职务')
    background_description = db.Column(db.Text(collation='utf8_general_ci'), info='背景描述')
    return_reason = db.Column(db.String(255, 'utf8_general_ci'), info="回退原因")
    deploy_core = db.Column(db.String(255, 'utf8_general_ci'), info="是否部署在核心位置")


class SeProjectRecord(db.Model):
    __tablename__ = 'se_project_record'

    id = db.Column(db.String(20, 'utf8_general_ci'), primary_key=True, info='ID')
    support_start_date = db.Column(db.DateTime, info='支持开始时间')
    support_end_date = db.Column(db.DateTime, info='支持结束时间')
    support_duration = db.Column(db.Integer, info='所用工时')
    published_date = db.Column(db.DateTime, info='发布时间')
    status = db.Column(db.SmallInteger, info='状态')
    unapproval_reason = db.Column(db.String(100, 'utf8_general_ci'), info='未通过原因')
    task_id = db.Column(db.String(20, 'utf8_general_ci'), info='任务Id')
    created_by_id = db.Column(db.String(20, 'utf8_general_ci'), info='创建人')
    created_date = db.Column(db.DateTime, info='创建时间')
    last_modified_by_id = db.Column(db.String(100, 'utf8_general_ci'), info='上次修改人')
    last_modified_date = db.Column(db.DateTime, info='上次修改时间')
    deleted_by_id = db.Column(db.String(20, 'utf8_general_ci'), info='删除人')
    deleted_date = db.Column(db.DateTime, info='删除时间')
    record_content = db.Column(db.Text(collation='utf8_general_ci'), info='其他动态字段')
    support_location = db.Column(db.String(100, 'utf8_general_ci'), info='支持地点')
    support_location_adcode = db.Column(db.String(20, 'utf8_general_ci'), info='支持地点编码')
    support_mode = db.Column(db.SmallInteger, info='支持方式')
    support_type_1st = db.Column(db.String(50, 'utf8_general_ci'), info='支持类型')
    support_type_2nd = db.Column(db.String(50, 'utf8_general_ci'), info='支持项')


class SeProjectTask(db.Model):
    __tablename__ = 'se_project_task'

    id = db.Column(db.String(20, 'utf8_general_ci'), primary_key=True, info='ID')
    task_number = db.Column(db.String(10, 'utf8_general_ci'), nullable=False, info='任务编号')
    event_number = db.Column(db.String(20, 'utf8_general_ci'), nullable=False, info='活动编号')
    subject = db.Column(db.String(100, 'utf8_general_ci'), info='主题')
    created_date = db.Column(db.DateTime, info='创建时间')
    created_by_id = db.Column(db.String(20, 'utf8_general_ci'), info='创建人')
    owner_id = db.Column(db.String(20, 'utf8_general_ci'), info='责任人')
    account_id = db.Column(db.String(50, 'utf8_general_ci'), info='客户id')
    account_name = db.Column(db.String(100, 'utf8_general_ci'), info='客户名称')
    contact_name = db.Column(db.String(20, 'utf8_general_ci'), info='客户联系人')
    contact_info = db.Column(db.String(50, 'utf8_general_ci'), info='客户联系方式')
    status = db.Column(db.SmallInteger, info='状态')
    support_mode = db.Column(db.SmallInteger, info='支持方式')
    support_type_1st = db.Column(db.String(50, 'utf8_general_ci'), info='支持类型')
    support_type_2nd = db.Column(db.String(50, 'utf8_general_ci'), info='支持项')
    task_start_date = db.Column(db.DateTime, info='任务开始时间')
    task_end_date = db.Column(db.DateTime, info='任务结束时间')
    task_result = db.Column(db.String(255, 'utf8_general_ci'), info='任务结果')
    task_incomplete_reason = db.Column(db.String(255, 'utf8_general_ci'), info='任务未完成原因')
    unapproval_reason = db.Column(db.String(255, 'utf8_general_ci'), info='任务审批未通过原因')
    last_modified_by_id = db.Column(db.String(20, 'utf8_general_ci'), info='上次修改人')
    last_modified_date = db.Column(db.DateTime, info='上次修改时间')
    deleted_by_id = db.Column(db.String(20, 'utf8_general_ci'), info='删除人')
    deleted_date = db.Column(db.DateTime, info='删除时间')
    parent_id = db.Column(db.String(20, 'utf8_general_ci'), info='父任务id')
    project_id = db.Column(db.String(20, 'utf8_general_ci'), info='项目id')
    crm_raw_data = db.Column(db.Text(collation='utf8_general_ci'), info='crm原始数据')
    taken_hours = db.Column(db.Float, info='任务耗时')
    contact_position = db.Column(db.String(50, 'utf8_general_ci'), info='联系人职务')
    origin_project = db.Column(db.String(20, 'utf8_general_ci'), info='源项目ID')
    task_location = db.Column(db.String(100, 'utf8_general_ci'), info='支持地点')
    task_location_adcode = db.Column(db.String(20, 'utf8_general_ci'), info='支持地点编码')
    assign_number = db.Column(db.String(50, 'utf8_general_ci'), info='分派编号')


class SeProjectFocus(db.Model):
    __tablename__ = 'se_project_focus'

    id = db.Column(db.String(20, 'utf8_general_ci'), primary_key=True, info='ID')
    project_id = db.Column(db.String(20, 'utf8_general_ci'), nullable=True, info='项目ID')
    follower_id = db.Column(db.String(20, 'utf8_general_ci'), nullable=True, info='关注者ID')
    followed_date = db.Column(db.DateTime, info='关注时间')
    deleted_date = db.Column(db.DateTime, info='删除时间')


class SeWeekly(db.Model):
    __tablename__ = 'se_weekly'

    id = db.Column(db.String(20), primary_key=True)
    template = db.Column(db.String(20), comment='模板ID')
    version = db.Column(db.String(20), comment='版本')
    subject = db.Column(db.String(50), comment='主题')
    receiver = db.Column(db.String(500), comment='收件人')
    cc = db.Column(db.VARCHAR(500), comment='抄送')
    department_ids = db.Column(db.VARCHAR(100), comment='部门ID列表')
    status = db.Column(db.String(10), comment='状态')
    send_date = db.Column(db.DateTime, comment='发送时间')
    start_date = db.Column(db.DateTime, comment='起始时间')
    end_date = db.Column(db.DateTime, comment='截止时间')
    created_by_id = db.Column(db.String(20), comment='创建人')
    created_date = db.Column(db.DateTime, comment='创建时间')
    last_modified_by_id = db.Column(db.String(20), comment='上次修改人')
    last_modified_date = db.Column(db.DateTime, comment='上次修改时间')
    deleted_by_id = db.Column(db.String(20, 'utf8_general_ci'), info='删除人')
    deleted_date = db.Column(db.DateTime, info='删除时间')
