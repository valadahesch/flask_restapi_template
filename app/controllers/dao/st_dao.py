from app.models import db
from app.enums.st_enum import enums
from app.extensions import logger
from app.models.techadmin import SysUser, TblEmployee, TblDepartment
from app.models.st import StSiteDepartment, StSite, StVisitHistory

class SysSearchController:

    @staticmethod
    def addVisitHistoryBySearch(user_id: str, create_time, site_id, search_info):
        visit_history = StVisitHistory()
        visit_history.user_id = user_id,
        visit_history.create_time = create_time,
        visit_history.site_id = site_id,
        visit_history.search_info = search_info,
        db.session.add(visit_history)
        db.session.commit()
        return True

    @staticmethod
    def queryRoleByUserid(user_id):
        result = {}
        try:
            user = db.session.query(SysUser).filter_by(id=user_id).first()
            if user:
                result['user_type'] = user.user_type
                result['email'] = user.email
            if 'email' in result:
                employee = db.session.query(TblEmployee).filter_by(email=result['email']).first()
                if employee:
                    result['main_department'] = employee.main_department
                    department = db.session.query(TblDepartment).filter_by(id=employee.main_department).first()
                    while department.parentid != 1:
                        if department.name == '技术支持中心':
                            result['role_department'] = enums["st_content_role"][1]
                        elif department.name == '数字化支持中心':
                            result['role_department'] = enums["st_content_role"][2]
                            break
                        department = db.session.query(TblDepartment).filter_by(id=department.parentid).first()
                    else:
                        result['role_department'] = enums["st_content_role"][3]
                else:
                    result['main_department'] = None
                    result['role_department'] = enums["st_content_role"][3]
        except Exception as error:
            logger.info(error)
        return result

    @staticmethod
    def querySiteByRole(role):
        query = db.session.query(StSite).join(StSiteDepartment, StSite.id == StSiteDepartment.site_id).filter(
            StSiteDepartment.role == role).all()
        sites = []
        for site in query:
            site_dict = {
                'id': site.id,
                'site_name': site.site_name,
                'site_url': site.site_url or '',
                'parent_id': site.parent_id,
                'create_time': site.create_time,
                'description': site.description or '',
                'type': site.type,
                'zindex': site.zindex or 0,
                'accendant': site.accendant or ''
            }
            sites.append(site_dict)
        return {"list": sites}
