from . import db


class SeEcoRecord(db.Model):
    __tablename__ = 'se_eco_record'

    id = db.Column(db.String(20), primary_key=True)
    support_start_date = db.Column(db.DateTime)
    support_end_date = db.Column(db.DateTime)
    support_duration = db.Column(db.Integer)
    status = db.Column(db.String(20))
    published_date = db.Column(db.DateTime)
    task_id = db.Column(db.String(20))
    record_content = db.Column(db.Text)
    unapproval_reason = db.Column(db.String(100))
    created_by_id = db.Column(db.String(20))
    created_date = db.Column(db.DateTime)
    last_modified_by_id = db.Column(db.String(100))
    last_modified_date = db.Column(db.DateTime)
    deleted_by_id = db.Column(db.String(20))
    deleted_date = db.Column(db.DateTime)


class SeEcoTask(db.Model):
    __tablename__ = 'se_eco_task'

    id = db.Column(db.String(20), primary_key=True)
    parent_id = db.Column(db.String(20))
    task_number = db.Column(db.String(10))
    subject = db.Column(db.String(100))
    partner_id = db.Column(db.String(50))
    partner_name = db.Column(db.String(100))
    partner_status = db.Column(db.String(20))
    partner_industry = db.Column(db.String(100))
    partner_contact = db.Column(db.String(50))
    partner_contact_info = db.Column(db.String(50))
    channel_manager_id = db.Column(db.String(20))
    status = db.Column(db.String(20))
    owner_id = db.Column(db.String(20, 'utf8_general_ci'))
    support_mode = db.Column(db.String(20))
    support_type_1st = db.Column(db.String(50))
    support_type_2nd = db.Column(db.String(50))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    duration = db.Column(db.Integer)
    task_result = db.Column(db.String(100))
    task_incomplete_reason = db.Column(db.String(100))
    created_by_id = db.Column(db.String(20, 'utf8_general_ci'))
    created_date = db.Column(db.DateTime)
    last_modified_by_id = db.Column(db.String(20, 'utf8_general_ci'))
    last_modified_date = db.Column(db.DateTime)
    deleted_by_id = db.Column(db.String(20, 'utf8_general_ci'))
    deleted_date = db.Column(db.DateTime)


class SeEcoApprovalRecord(db.Model):
    __tablename__ = 'se_eco_approval_record'

    id = db.Column(db.String(20), primary_key=True)
    record_id = db.Column(db.String(20), nullable=False)
    main_task_id = db.Column(db.String(20), nullable=False)
    result = db.Column(db.String(100))
    incomplete_reason = db.Column(db.String(100, 'utf8_general_ci'))
    created_date = db.Column(db.DateTime)
    approval_date = db.Column(db.DateTime)
