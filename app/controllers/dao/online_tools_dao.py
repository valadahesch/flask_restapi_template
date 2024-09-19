from app.models import db
from app.utils.api_util import AppException
from app.models.online_tools import AuxiliaryConf2Hs


class AuxiliaryConf2HSDao:

    @staticmethod
    def queryConf2HsById(_id: str) -> AuxiliaryConf2Hs:
        """
        :return:
        """
        res = AuxiliaryConf2Hs.query.filter(AuxiliaryConf2Hs.id == _id).one_or_none()
        return res

    @staticmethod
    def addConf2Hs(new_lead: AuxiliaryConf2Hs) -> str:
        exist = AuxiliaryConf2HSDao.queryConf2HsById(new_lead.id)
        if exist:
            raise AppException("创建失败，系统ID重复")

        db.session.add(new_lead)
        db.session.commit()

        return new_lead.id

    @staticmethod
    def updateConf2HsById(_id, update_data: dict):
        AuxiliaryConf2Hs.query.filter(AuxiliaryConf2Hs.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def queryConf2HsByFilter(create_by, **kwargs) -> [int, AuxiliaryConf2Hs]:
        """
        :param create_by:
        :param kwargs: 查询参数
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 10
        temp_query = AuxiliaryConf2Hs.query.filter(AuxiliaryConf2Hs.created_by_id == create_by)

        for k, v in kwargs.items():
            if k not in AuxiliaryConf2Hs.__dict__.keys() or not v:
                continue

            if isinstance(v, (bool, int)):
                temp_query = temp_query.filter(getattr(AuxiliaryConf2Hs, k) == v)
            else:
                temp_query = temp_query.filter(getattr(AuxiliaryConf2Hs, k).like(f"%{v}%"))

        res = temp_query.order_by(AuxiliaryConf2Hs.created_date.desc()).paginate(
            page=page, per_page=size, error_out=False)
        return res.total, res.items

