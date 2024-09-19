from app.models.tac_ods import OdsWecomUser, OdsWecomDepartment


class TacOdsWeComUserDao:

    @staticmethod
    def queryWecomUserByUserId(user_id: str) -> OdsWecomUser:
        """
        :param user_id: UserName ID
        :return:
        """
        res = OdsWecomUser.query.filter(OdsWecomUser.userid == user_id).one_or_none()
        return res

    @staticmethod
    def queryWecomUser() -> [OdsWecomUser]:
        """
        :return:
        """
        res = OdsWecomUser.query.all()
        return res


class TacOdsWeComDepartmentDao:

    @staticmethod
    def queryWecomDepartmentById(_id: str) -> OdsWecomDepartment:
        """
        :param _id:
        :return:
        """
        res = OdsWecomDepartment.query.filter(OdsWecomDepartment.id == _id).one_or_none()
        return res

    @staticmethod
    def queryWecomDepartment() -> [OdsWecomDepartment]:
        """
        :return:
        """
        res = OdsWecomDepartment.query.all()
        return res


# # from app.models.tac_ods import t_ods_wecom_user
#
# class TacOdsController:
#
#     @staticmethod
#     def queryOdsWecomUserByUserId(user_id: str) -> t_ods_wecom_user:
#         """
#         通过角色ID查询角色
#         :param user_id: 用户ID
#         :return:
#         """
#         # sql = t_ods_wecom_user.select(t_ods_wecom_user.columns['userid'] == user_id)
#         # wecom_user = db.get_engine('tac_ods').execute(sql).one_or_none()
#
#         with db.get_engine('tac_ods').connect() as db_session:
#             sql = t_ods_wecom_user.select(t_ods_wecom_user.columns['userid'] == user_id)
#             wecom_user = db_session.execute(sql).one_or_none()
#
#         return wecom_user



