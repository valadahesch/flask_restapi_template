from . import db

class SysFileManage(db.Model):
    __tablename__ = 'sys_file_manage'
    
    id = db.Column(db.String(20), primary_key=True, nullable=False, comment='文件、目录ID')
    parent_id = db.Column(db.String(20), nullable=True, comment='父级ID')
    obj_type = db.Column(db.String(20), nullable=False, comment='对象类型，文件/目录')
    obj_name = db.Column(db.String(200), nullable=False, comment='对象名，文件或者目录名')
    file_type = db.Column(db.String(20), nullable=False, comment='文件类型')
    file_size = db.Column(db.Integer, nullable=False, comment='文件大小（字节为单位）')
    created_by_id = db.Column(db.String(20), nullable=False, comment='创建人')
    created_date = db.Column(db.DateTime, nullable=False, comment='创建时间')
    deleted_date = db.Column(db.DateTime, nullable=True, comment='删除时间')
    related_object_type = db.Column(db.String(20), nullable=False, comment='关联对象（工单、项目）')
    related_object_id = db.Column(db.String(20), nullable=False, comment='关联ID （工单ID，项目ID）')
    deleted_by_id = db.Column(db.String(20), nullable=True, comment='删除人')

    def __repr__(self):
        return f"<SysFileManage(id={self.id}, obj_name={self.obj_name}, file_type={self.file_type})>"
