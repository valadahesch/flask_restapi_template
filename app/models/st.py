from . import db


class StSiteDepartment(db.Model):
    __tablename__ = 'st_site_department'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role = db.Column(db.String(30))
    site_id = db.Column(db.Integer, db.ForeignKey('st_site.id', ondelete='CASCADE', onupdate='CASCADE'))


class StSite(db.Model):
    __tablename__ = 'st_site'
    id = db.Column(db.Integer(), primary_key=True, comment='ID')
    site_name = db.Column(db.String(50), nullable=False, comment='站点名称')
    site_url = db.Column(db.String(300), comment='站点URL')
    parent_id = db.Column(db.Integer(), comment='父级ID, 关联于id')
    create_time = db.Column(db.String(20), comment='创建时间')
    update_time = db.Column(db.String(20), comment='更新时间')
    description = db.Column(db.String(500), comment='站点描述')
    image = db.Column(db.String(100), comment='站点运行图片')
    type = db.Column(db.String(40), comment='站点类型')
    zindex = db.Column(db.Integer(), comment='排序索引')
    accendant = db.Column(db.String(40), comment='维护人')
    is_hide = db.Column(db.String(10), comment='是否显示')

class StVisitHistory(db.Model):
    __tablename__ = 'st_visit_history'
    user_id = db.Column(db.String(20), primary_key=True)
    create_time = db.Column(db.DateTime)
    site_id = db.Column(db.Integer())
    search_info = db.Column(db.String(400))

