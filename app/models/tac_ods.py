from . import db


class OdsWecomDepartment(db.Model):
    __tablename__ = 'ods_wecom_department'
    __bind_key__ = 'tac_ods'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    name_en = db.Column(db.String(100))
    department_leader = db.Column(db.String(32))
    parentid = db.Column(db.Integer)
    order = db.Column(db.BigInteger)
    last_sync_time = db.Column(db.DateTime, nullable=False)
    is_deleted = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    deleted_time = db.Column(db.DateTime)


class OdsWecomUser(db.Model):
    __tablename__ = 'ods_wecom_user'
    __bind_key__ = 'tac_ods'

    userid = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(100))
    mobile = db.Column(db.String(15))
    department = db.Column(db.String(200))
    main_department = db.Column(db.Integer)
    order = db.Column(db.String(200))
    position = db.Column(db.String(50))
    gender = db.Column(db.String(1))
    email = db.Column(db.String(200))
    is_leader_in_dept = db.Column(db.String(200))
    direct_leader = db.Column(db.String(200))
    avatar = db.Column(db.String(200))
    thumb_avatar = db.Column(db.String(200))
    telephone = db.Column(db.String(20))
    alias = db.Column(db.String(100))
    extattr = db.Column(db.String(1000, 'utf8_general_ci'))
    status = db.Column(db.Integer)
    qr_code = db.Column(db.String(200))
    external_profile = db.Column(db.String(500))
    external_position = db.Column(db.String(500))
    address = db.Column(db.String(100))
    last_sync_time = db.Column(db.DateTime, nullable=False)
    is_deleted = db.Column(db.Integer, nullable=False, server_default=db.FetchedValue())
    deleted_time = db.Column(db.DateTime)

