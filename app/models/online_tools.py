from . import db


class AuxiliaryConf2Hs(db.Model):
    __tablename__ = 'auxiliary_conf2hs'

    id = db.Column(db.String(20), primary_key=True)
    file_name = db.Column(db.String(100))
    brand_name = db.Column(db.String(20))
    brand_version = db.Column(db.String(20))
    models = db.Column(db.String(200))
    export = db.Column(db.String(100))
    description = db.Column(db.String(200))
    result = db.Column(db.String(20))
    failed_reason = db.Column(db.String(200))
    created_by_id = db.Column(db.String(20, 'utf8_general_ci'), index=True)
    created_date = db.Column(db.DateTime)
