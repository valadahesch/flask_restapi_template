from . import db


class MessageTemplate(db.Model):
    __tablename__ = 'message_template'
    
    id = db.Column(db.String(16), primary_key=True, nullable=False)
    template_number = db.Column(db.String(10), nullable=False, comment='模板编号不唯一、可重复')
    subject = db.Column(db.String(200), nullable=False, comment='模版主题')
    content = db.Column(db.Text, nullable=False, comment='模版内容')
    created_by_id = db.Column(db.String(100), nullable=False, comment='创建人')
    created_date = db.Column(db.DateTime, nullable=False, comment='创建时间')
    last_modified_by_id = db.Column(db.String(100), nullable=False, comment='最后修改人')
    last_modified_date = db.Column(db.DateTime, nullable=False, comment='最后修改时间')
    enable = db.Column(db.Boolean, nullable=False, comment='是否可用')
    media_type = db.Column(db.String(30), nullable=False, comment='模版类型,邮件，短信，企业微信')
    language = db.Column(db.String(6), nullable=False, comment='语种, 可选值有：简体中文(zh_cn) 、English-United States(en_us)')
    remark = db.Column(db.String(200), nullable=False, comment='备注')

    def __init__(self, dictionary):
        for key, value in dictionary.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"<MessageTemplate(id={self.id}, subject={self.subject}, media_type={self.media_type})>"
