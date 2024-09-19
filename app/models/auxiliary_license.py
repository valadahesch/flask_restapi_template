from . import db

class AuxiliaryApplyLicenseRecord(db.Model):
    __tablename__ = 'auxiliary_apply_license_record'

    id = db.Column(db.String(20), primary_key=True, comment='ID')
    account_id = db.Column(db.String(80), nullable=False, comment='设备所有客户名称')
    sn = db.Column(db.String(2000), nullable=False, comment='申请许可的设备序列号')
    product_name = db.Column(db.String(40), nullable=False, comment='设备名称')
    lic_params = db.Column(db.String(2000), nullable=False, comment='申请的许可类型')
    created_date = db.Column(db.DateTime, nullable=False, comment='申请许可时间')
    end_time = db.Column(db.DateTime, nullable=False, comment='许可有效期截止时间')
    created_by_id = db.Column(db.String(20), nullable=False, comment='执行申请许可操作的用户')
    email = db.Column(db.String(40), comment='申请人邮箱')
    status = db.Column(db.String(40), comment='申请状态')
    order_id = db.Column(db.String(40), nullable=False, comment='许可文件下载id')
    error_msg = db.Column(db.String(2000), nullable=False, comment='失败原因')
    object_name = db.Column(db.String(200), nullable=False, comment='oss路径')

    def __repr__(self):
        return f'<AuxiliaryApplyLicenseRecord {self.id}>'
