from . import db


class SeWorkProject(db.Model):
    __tablename__ = 'se_work_project'

    id = db.Column(db.String(20), primary_key=True)
    project_type = db.Column(db.String(30), nullable=False)
    project_number = db.Column(db.String(10), nullable=False, unique=True)
    subject = db.Column(db.String(200))
    owner_id = db.Column(db.String(20))
    account_id = db.Column(db.String(50))
    account_name = db.Column(db.String(100))
    contact_name = db.Column(db.String(20))
    contact_info = db.Column(db.String(50))
    status = db.Column(db.SmallInteger)
    support_type_1st = db.Column(db.String(50))
    support_type_2nd = db.Column(db.String(50))
    created_by_id = db.Column(db.String(20))
    created_date = db.Column(db.DateTime)
    last_modified_by_id = db.Column(db.String(20))
    last_modified_date = db.Column(db.DateTime)
    deleted_by_id = db.Column(db.String(20))
    deleted_date = db.Column(db.DateTime)


class SeWorkRecord(db.Model):
    __tablename__ = 'se_work_record'

    id = db.Column(db.String(20), primary_key=True)
    support_start_date = db.Column(db.DateTime)
    support_end_date = db.Column(db.DateTime)
    support_duration = db.Column(db.Integer)
    published_date = db.Column(db.DateTime)
    status = db.Column(db.SmallInteger)
    task_id = db.Column(db.String(20))
    record_content = db.Column(db.Text)
    last_modified_by_id = db.Column(db.String(100))
    last_modified_date = db.Column(db.DateTime)
    deleted_by_id = db.Column(db.String(20))
    deleted_date = db.Column(db.DateTime)
    created_by_id = db.Column(db.String(20))
    created_date = db.Column(db.DateTime)


class SeWorkTask(db.Model):
    __tablename__ = 'se_work_task'

    id = db.Column(db.String(20), primary_key=True)
    parent_id = db.Column(db.String(20))
    project_id = db.Column(db.String(100))
    task_number = db.Column(db.String(10), nullable=False)
    subject = db.Column(db.String(200))
    owner_id = db.Column(db.String(20))
    account_id = db.Column(db.String(50))
    account_name = db.Column(db.String(100))
    contact_name = db.Column(db.String(20))
    contact_info = db.Column(db.String(50))
    status = db.Column(db.SmallInteger)
    support_mode = db.Column(db.SmallInteger)
    support_type_1st = db.Column(db.String(50))
    support_type_2nd = db.Column(db.String(50))
    task_start_date = db.Column(db.DateTime)
    task_end_date = db.Column(db.DateTime)
    task_result = db.Column(db.SmallInteger)
    task_incomplete_reason = db.Column(db.String(100))
    created_date = db.Column(db.DateTime)
    created_by_id = db.Column(db.String(20))
    last_modified_by_id = db.Column(db.String(20))
    last_modified_date = db.Column(db.DateTime)
    deleted_by_id = db.Column(db.String(20))
    deleted_date = db.Column(db.DateTime)


class SeWorkApprovalRecord(db.Model):
    __tablename__ = 'se_work_approval_record'

    id = db.Column(db.String(20), primary_key=True)
    record_id = db.Column(db.String(20), nullable=False)
    project_id = db.Column(db.String(20), nullable=False)
    result = db.Column(db.String(5))
    incomplete_reason = db.Column(db.String(100))
    created_date = db.Column(db.DateTime)
    approval_date = db.Column(db.DateTime)
