from . import db

class AuxiliaryStamp(db.Model):
    __tablename__ = 'auxiliary_stamp_record'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='盖章记录ID')
    file_name = db.Column(db.String(200), nullable=False, comment='盖章材料文件名')
    request_by_id = db.Column(db.String(20), default=None, comment='请求盖章的人员')
    reason = db.Column(db.Text, comment='请求盖章原因')
    file_id = db.Column(db.String(40), nullable=False, comment='盖章材料ID（方便云平台获取文件）')
    stamp_by_id = db.Column(db.String(20), nullable=False, comment='执行盖章操作的人员')
    status = db.Column(db.Integer, nullable=False, comment='盖章状态: 1 盖章中, 2 盖章成功, 3 盖章失败')
    created_date = db.Column(db.DateTime, nullable=False, comment='盖章时间')
    stamp_date = db.Column(db.DateTime, nullable=False, comment='盖章时间')
    object_name = db.Column(db.String(200), nullable=False, comment='盖章后文件存储路径')