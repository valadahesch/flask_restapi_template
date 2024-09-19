from app.models import db
from app.models.crm_views import t_GetLeadList, t_View_AssignablePerson, t_VIEW_ACCOUNT, t_VIEW_SE_PROJECT_OPPORTUNITY
from sqlalchemy.orm import sessionmaker, scoped_session


class CrmViewsDao:

    @staticmethod
    def getSession():
        engine = db.get_engine(bind="crm_views")
        session = scoped_session(sessionmaker(bind=engine))()
        return session

    @staticmethod
    def queryLeadListByLeadId(lead_id: str) -> t_GetLeadList:
        """
        根据线索ID查询线索
        :param lead_id: CRM线索ID
        :return:
        """
        res = None
        session = CrmViewsDao.getSession()
        try:
            res = session.query(t_GetLeadList).filter(t_GetLeadList.columns['leadid'] == lead_id).one_or_none()
        except Exception as e:
            session.rollback()
        finally:
            session.close()
        return res

    @staticmethod
    def queryAssignUserByEmail(email: str) -> [t_GetLeadList]:
        """
        SE 指派人员查询
        :param email: 分配人邮箱
        :return:
        """
        res = []
        session = CrmViewsDao.getSession()
        try:
            res = session.query(t_View_AssignablePerson).filter(
                t_View_AssignablePerson.columns['SE分派员邮箱地址'] == email
            ).all()
        except Exception as e:
            session.rollback()
        finally:
            session.close()
        return res

    @staticmethod
    def queryAssignerByEmail(email: str) -> [t_GetLeadList]:
        """
        我的分派员列表查询
        :param email: 分配人邮箱
        :return:
        """
        res = []
        session = CrmViewsDao.getSession()
        try:
            res = session.query(t_View_AssignablePerson).filter(
                t_View_AssignablePerson.columns['可分派用户邮箱地址'] == email
            ).all()
        except Exception as e:
            session.rollback()
        finally:
            session.close()
        return res

    @staticmethod
    def queryAccountByName(name: str) -> t_VIEW_ACCOUNT:
        """
        根据客户名称查询crm客户信息
        :param name: 客户名称
        :return:
        """
        res = None
        session = CrmViewsDao.getSession()
        try:
            res = session.query(t_VIEW_ACCOUNT).filter(t_VIEW_ACCOUNT.columns['name'] == name).first()
        except Exception as e:
            session.rollback()
        finally:
            session.close()
        return res

    @staticmethod
    def querySeProjectOpportunity(opportunity_numbers: list) -> [t_VIEW_ACCOUNT]:
        """
        根据商机编号查询CRM商机
        :param opportunity_numbers: 商机编号
        :return:
        """
        res = None
        session = CrmViewsDao.getSession()
        try:
            res = session.query(t_VIEW_SE_PROJECT_OPPORTUNITY).filter(
                t_VIEW_SE_PROJECT_OPPORTUNITY.columns['商机编号'].in_(opportunity_numbers)
            ).all()
        except Exception as e:
            session.rollback()
        finally:
            session.close()
        return res
