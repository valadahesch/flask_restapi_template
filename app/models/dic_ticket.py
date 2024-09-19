from . import db

class DICTickets(db.Model):
    __tablename__ = 'dic_tickets'

    id = db.Column(db.String(20), primary_key=True, comment='ID')
    parent_id = db.Column(db.String(20), default=None, comment='父级工单，重复包含的工单进行归类')
    number = db.Column(db.String(10), nullable=False, comment='系统10位工单编号')
    subject = db.Column(db.String(200), nullable=False, comment='主题')
    description = db.Column(db.Text, comment='描述')
    support_type = db.Column(db.String(30), nullable=False, comment='支持类型（需求、故障、咨询、其他）')
    privacy = db.Column(db.String(20), nullable=False, comment='私有、公有')
    save_time = db.Column(db.Integer, nullable=False, comment='单次节省工时，转化成分钟')
    status = db.Column(db.String(30), nullable=False, comment='工单状态：已提交、已取消、已受理、处理中、交付中、归档')
    commit_by_id = db.Column(db.String(20), nullable=False, comment='提交人')
    to_process = db.Column(db.Boolean, default=None, comment='是否开发')
    usage_annual = db.Column(db.Integer, nullable=False, comment='年使用次数')
    approval_reason = db.Column(db.Text, comment='审批原因')
    priority = db.Column(db.String(20), nullable=False, comment='优先级（低、中、高、紧急）')
    approval_by_id = db.Column(db.String(20), default=None, comment='审批人')
    approval_time = db.Column(db.DateTime, default=None, comment='审批时间（受理人确认时间）')
    feasibility = db.Column(db.Text, comment='可行性描述')
    due_time = db.Column(db.DateTime, default=None, comment='预估工单完成时间')
    accepted_by_id = db.Column(db.String(20), default=None, comment='受理人')
    accepted_datetime = db.Column(db.DateTime, default=None, comment='受理时间')
    created_by_id = db.Column(db.String(20), nullable=False, comment='创建人')
    created_date = db.Column(db.DateTime, nullable=False, default=None, comment='创建时间')
    last_modified_by_id = db.Column(db.String(20), nullable=False, comment='最后修改人')
    last_modified_date = db.Column(db.DateTime, nullable=False, comment='最后修改时间')
    deleted_by_id = db.Column(db.String(20), default=None, comment='删除人')
    deleted_date = db.Column(db.DateTime, default=None, comment='删除时间')
    cancel_by_id = db.Column(db.String(20), default=None, comment='取消人')
    cancel_date = db.Column(db.DateTime, default=None, comment='取消时间')
    cancel_by_reason = db.Column(db.Text, comment='取消原因')
    actual_due_time = db.Column(db.DateTime, default=None, comment='实际交付时间')
    complete_date = db.Column(db.DateTime, default=None, comment='实际完成时间')
    functional_module_id = db.Column(db.String(20), primary_key=True, comment='ID')
    first_delivery_date = db.Column(db.DateTime, default=None, comment='实际交付时间')


class DICTicketTask(db.Model):
    __tablename__ = 'dic_ticket_task'

    id = db.Column(db.String(20), primary_key=True, comment='ID')
    ticket_id = db.Column(db.String(20), nullable=False, comment='工单ID')
    project_id = db.Column(db.String(20), nullable=False, comment='对应项目ID')
    milestone_id = db.Column(db.String(200), nullable=False, comment='里程碑id')
    handle_type = db.Column(db.String(200), nullable=False, comment='工单类型')
    assign_by_id = db.Column(db.String(20), nullable=False, comment='指派人')
    assign_date = db.Column(db.DateTime, default=None, comment='创建时间')
    created_by_id = db.Column(db.String(20), nullable=False, comment='创建人')
    created_date = db.Column(db.DateTime, default=None, comment='创建时间')
    assign_date = db.Column(db.DateTime, default=None, comment='指派时间')
    description = db.Column(db.Text, nullable=False, comment='描述')
    subject = db.Column(db.Text, nullable=False, comment='主题')


class DICTicketProject(db.Model):
    __tablename__ = 'dic_ticket_project'

    id = db.Column(db.String(20), primary_key=True, comment='项目ID')
    key = db.Column(db.String(100), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    project_path = db.Column(db.String(300), nullable=False)
    created_by_id = db.Column(db.String(20), nullable=False, comment='创建人')
    created_date = db.Column(db.DateTime, nullable=False, default=None, comment='创建时间')
    is_active = db.Column(db.Integer, nullable=False, comment='是否可用')

    def __repr__(self):
        return f"<DICTicketProject(id={self.id}, project_name={self.project_name})>"


class DICTicketMessage(db.Model):
    __tablename__ = 'dic_ticket_message'

    id = db.Column(db.String(20), primary_key=True, comment='id')
    parent_id = db.Column(db.String(20), default=None, comment='父级id')
    ticket_id = db.Column(db.String(20), nullable=False, comment='工单ID')
    content = db.Column(db.Text, nullable=False, comment='评论内容')
    created_by_id = db.Column(db.String(20), nullable=False, comment='评论人')
    created_username = db.Column(db.String(20), nullable=False, comment='评论人')
    to_user_id = db.Column(db.String(20), nullable=False, comment='被评论人')
    to_username = db.Column(db.String(20), nullable=False, comment='被评论人')
    created_date = db.Column(db.DateTime, nullable=False, default=None, comment='评论时间')
    need_reply = db.Column(db.Integer, nullable=False, comment='评论人')

    def __repr__(self):
        return f"<DICTicketMessage(id={self.id}, ticket_id={self.ticket_id})>"


class DICTicketFunctionalModule(db.Model):
    __tablename__ = 'dic_ticket_functional_module'

    id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Integer, nullable=False, comment='是否可用')
    def __repr__(self):
        return f"<DICTicketFunctionalModule(id={self.id}, name={self.name})>"
