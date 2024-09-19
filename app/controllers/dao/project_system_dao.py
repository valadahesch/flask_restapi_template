from app.models.project_system import MainInventory, MainCollectField, UserMain, ProjectMain, FieldCustomValue
from app.models import db


class MainInventoryDao:

    @staticmethod
    def queryInventoryBySN(SN: str) -> MainInventory:
        """
        :param issue_Id: issue ID
        :return:
        """
        res = MainInventory.query.filter(MainInventory.serial_number == SN).one_or_none()
        return res


class MainCollectFieldDao:

    @staticmethod
    def queryCollectFieldByIssueId(_id: str) -> MainCollectField:
        """
        :param _id:
        :return:
        """
        res = MainCollectField.query.filter(MainCollectField.issue_id == _id).one_or_none()
        return res

    @staticmethod
    def queryCollectFieldByFilter(uid=None, **kwargs) -> (int, [(MainCollectField, ProjectMain, UserMain)]):
        """
        获取所有负责人是uid的任务信息（巡检项目）
        task_id: 任务ID
        project_name: 项目名称
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000

        temp = db.session.query(MainCollectField, ProjectMain, UserMain).join(
            ProjectMain, ProjectMain.id == MainCollectField.project_id).join(
            UserMain, UserMain.uid == ProjectMain.lead
        ).filter(
            MainCollectField.project_tpl == '设备巡检'
        )

        if uid:
            temp = temp.filter(MainCollectField.uid == uid)

        if kwargs.get("task_id"):
            temp = temp.filter(MainCollectField.issue_id == kwargs.get("task_id"))

        if kwargs.get("project_subject"):
            temp = temp.filter(MainCollectField.project_name.like(f"%{kwargs.get('project_subject')}%"))

        res = temp.order_by(MainCollectField.start_date.desc()).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items


class ProjectMainDao:

    @staticmethod
    def getProjectByUser(_id: str) -> [ProjectMain, UserMain]:
        """
        获取项目信息与项目负责人信息
        """
        res = db.session.query(ProjectMain, UserMain).join(
            UserMain, ProjectMain.lead == UserMain.uid).filter(ProjectMain.id == _id).one_or_none()
        return res


class FieldCustomValueDao:

    @staticmethod
    def queryFieldCustomValueByIssueId(issue_id: str, custom_field_id: str) -> FieldCustomValue:
        """
        根据任务ID和字段ID获取字段内容
        """

        res = FieldCustomValue.query.filter(FieldCustomValue.issue_id == issue_id,
                                            FieldCustomValue.custom_field_id == custom_field_id).one_or_none()

        return res


class UserMainDao:

    @staticmethod
    def queryUserMainByUid(_id: str) -> UserMain:
        """
        查询用户信息
        """

        res = UserMain.query.filter(UserMain.uid == _id).one_or_none()
        return res
