from sqlalchemy import desc
from app.models import db
from app.utils.api_util import AppException
from app.models.techadmin import BusinessLead


class BusinessLeadDao:

    @staticmethod
    def queryBusinessLeadById(_id: str) -> BusinessLead:
        """
        :return:
        """
        res = BusinessLead.query.filter(BusinessLead.id == _id).one_or_none()
        return res

    @staticmethod
    def queryBusinessLeadByLeadCode(lead_code=None) -> [BusinessLead]:
        res = BusinessLead.query.filter(BusinessLead.lead_code == lead_code).all()
        return res

    @staticmethod
    def queryBusinessLeadByFilter(create_by=None, **kwargs) -> [int, BusinessLead]:
        """
        :param create_by:
        :param kwargs: 查询参数
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000
        temp_query = BusinessLead.query.filter()
        if create_by:
            temp_query = temp_query.filter(BusinessLead.create_by == create_by)

        for k, v in kwargs.items():
            if k not in BusinessLead.__dict__.keys() or not v:
                continue

            if isinstance(v, (bool, int)):
                temp_query = temp_query.filter(getattr(BusinessLead, k) == v)
            else:
                temp_query = temp_query.filter(getattr(BusinessLead, k).like(f"%{v}%"))

        res = temp_query.order_by(desc(BusinessLead.create_time)).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items

    @staticmethod
    def addBusinessLead(new_lead: BusinessLead) -> str:
        exist = BusinessLeadDao.queryBusinessLeadById(new_lead.id)
        if exist:
            raise AppException("创建失败，线索ID已创建")

        db.session.add(new_lead)
        db.session.commit()

        return new_lead.id

    @staticmethod
    def updateBusinessLeadById(_id, update_data: dict):
        BusinessLead.query.filter(BusinessLead.id == _id).update(update_data)
        db.session.commit()