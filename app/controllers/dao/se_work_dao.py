from app.models import db
from datetime import datetime
from sqlalchemy.orm import aliased
from sqlalchemy import or_
from app.models.se_work import SeWorkProject, SeWorkTask, SeWorkRecord, SeWorkApprovalRecord
from app.models.techadmin import SysUser
from app.utils.api_util import AppException


class SeWorkProjectDao:

    @staticmethod
    def queryProjectById(_id: str) -> SeWorkProject:
        """
        :param _id: 项目ID
        :return:
        """
        res = SeWorkProject.query.filter(SeWorkProject.id == _id).one_or_none()
        return res

    @staticmethod
    def queryProjectByNumber(number: str) -> SeWorkProject:
        """
        :param number: 项目编号
        :return:
        """
        res = SeWorkProject.query.filter(SeWorkProject.project_number == number).one_or_none()
        return res

    @staticmethod
    def addProject(new_project: SeWorkProject):
        exist = SeWorkProjectDao.queryProjectById(new_project.id)
        if exist:
            raise AppException("创建失败，项目ID已存在")

        exist = SeWorkProjectDao.queryProjectByNumber(new_project.project_number)
        if exist:
            raise AppException("创建失败，项目Number已存在")

        new_project.status = 1
        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_project.created_date = now_date
        new_project.last_modified_date = now_date

        db.session.add(new_project)
        db.session.commit()
        return new_project.id, new_project.project_number

    @staticmethod
    def updateProjectById(_id, update_data: dict):
        if "last_modified_date" not in update_data.keys():
            update_data["last_modified_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SeWorkProject.query.filter(SeWorkProject.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def deleteProjectById(_id, delete_data):

        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if "last_modified_date" not in delete_data.keys():
            delete_data["last_modified_date"] = now_datetime

        if 'deleted_date' not in delete_data.keys():
            delete_data["deleted_date"] = now_datetime

        SeWorkProject.query.filter(SeWorkProject.id == _id).update(delete_data)
        db.session.commit()

    @staticmethod
    def getProjectByOwnerAndFilter(owner, **kwargs) -> (int, [(SeWorkProject, SysUser, SysUser, SysUser)]):
        """
        查询责任人是owner_id的项目
        :param owner:
        :param kwargs: 用户ID列表
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000

        create_user = aliased(SysUser)
        owner_user = aliased(SysUser)
        modify_user = aliased(SysUser)
        temp = db.session.query(SeWorkProject, create_user, owner_user, modify_user).join(
            create_user, SeWorkProject.created_by_id == create_user.id).join(
            owner_user, SeWorkProject.owner_id == owner_user.id).join(
            modify_user, SeWorkProject.last_modified_by_id == modify_user.id
        ).filter(SeWorkProject.owner_id == owner, SeWorkProject.deleted_date == None)

        if kwargs.get("created_by_id"):
            temp = temp.filter(SeWorkProject.created_by_id.in_(kwargs.get("created_by_id")))

        if kwargs.get("status"):
            temp = temp.filter(SeWorkProject.status.in_(kwargs.get("status")))

        if kwargs.get("date_range"):
            temp = temp.filter(
                SeWorkProject.created_date >= kwargs.get("date_range")[0],
                SeWorkProject.created_date <= kwargs.get("date_range")[1]
            )

        if kwargs.get('date_order') == 'asc':
            order = SeWorkProject.created_date.asc()
        else:
            order = SeWorkProject.created_date.desc()

        res = temp.distinct(SeWorkProject.id).order_by(order).paginate(
            page=page, per_page=size, error_out=False
        )

        return res.total, res.items

    @staticmethod
    def getProjectJoinSysUserById(_id: str) -> (SeWorkProject, SysUser, SysUser):

        create_user = aliased(SysUser)
        owner_user = aliased(SysUser)
        res = db.session.query(SeWorkProject, create_user, owner_user).join(
            create_user, SeWorkProject.created_by_id == create_user.id).join(
            owner_user, SeWorkProject.owner_id == owner_user.id).filter(
            SeWorkProject.id == _id, SeWorkTask.deleted_date == None
        ).first()

        return res


class SeWorkTaskDao:

    @staticmethod
    def queryTaskById(_id: str) -> SeWorkTask:
        """
        :param _id: 任务ID
        :return:
        """
        res = SeWorkTask.query.filter(SeWorkTask.id == _id).one_or_none()
        return res

    @staticmethod
    def queryTaskByNumber(task_number: str) -> SeWorkTask:
        """
        :param task_number: 任务编号
        :return:
        """
        res = SeWorkTask.query.filter(SeWorkTask.task_number == task_number).one_or_none()
        return res

    @staticmethod
    def queryTaskByProjectId(project_id: str) -> [SeWorkTask]:
        """
        :param project_id: 任务ID
        :return:
        """
        res = SeWorkTask.query.filter(SeWorkTask.project_id == project_id).all()
        return res

    @staticmethod
    def queryLastTaskByProjectId(project_id: str) -> [SeWorkTask]:
        """
        :param project_id: 任务ID
        :return:
        """
        res = SeWorkTask.query.filter(SeWorkTask.project_id == project_id).order_by(
            SeWorkTask.last_modified_date.desc()).first()
        return res

    @staticmethod
    def queryTaskByTaskNumber(number: str) -> SeWorkTask:
        """
        :param number: 任务编号
        :return:
        """
        res = SeWorkTask.query.filter(SeWorkTask.task_number == number).one_or_none()
        return res

    @staticmethod
    def queryTaskByParentId(parent_id: str) -> [SeWorkTask]:
        """
        获取所有子任务
        :param parent_id: 父任务ID
        :return:
        """
        res = SeWorkTask.query.filter(
            SeWorkTask.parent_id == parent_id
        ).all()
        return res

    @staticmethod
    def queryUndoneTaskByParentId(parent_id: str) -> [SeWorkTask]:
        """
        未完成的子任务
        :param parent_id: 父任务ID
        :return:
        """
        res = SeWorkTask.query.filter(
            SeWorkTask.parent_id == parent_id, SeWorkTask.task_result == None,
            SeWorkTask.deleted_date == None
        ).all()
        return res

    @staticmethod
    def queryTaskBySysUserId(user_id: str) -> [SeWorkTask]:
        """
        查询所有创建人或者责任人是user_id的任务
        :param user_id: 父任务ID
        :return:
        """
        res = SeWorkTask.query.filter(
            or_(SeWorkTask.owner_id == user_id, SeWorkTask.created_by_id == user_id),
            SeWorkTask.deleted_date == None
        ).all()

        return res

    @staticmethod
    def queryDoTaskByProjectId(project_id: str) -> [SeWorkTask]:
        """
        获取项目下所有任务
        :param project_id: 父任务ID
        :return:
        """
        res = SeWorkTask.query.filter(
            SeWorkTask.project_id == project_id, SeWorkTask.task_result == None,
            SeWorkTask.deleted_date == None
        ).all()
        return res

    @staticmethod
    def queryTaskBySysUserIds(user_ids: list) -> [SeWorkTask]:
        """
        查询所有创建人或者责任人是user_id的任务
        :param user_ids: 用户ID列表
        :return:
        """
        res = SeWorkTask.query.filter(
            or_(SeWorkTask.owner_id.in_(user_ids), SeWorkTask.created_by_id.in_(user_ids)),
            SeWorkTask.deleted_date == None
        ).all()

        return res

    @staticmethod
    def addTask(new_task: SeWorkTask):
        exist = SeWorkTaskDao.queryTaskById(new_task.id)
        if exist:
            raise AppException("创建失败，任务ID已存在")

        exist = SeWorkTaskDao.queryTaskByTaskNumber(new_task.task_number)
        if exist:
            raise AppException("创建失败，任务编号已存在")

        new_task.status = 1
        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_task.created_date = now_date
        new_task.last_modified_date = now_date

        db.session.add(new_task)
        db.session.commit()
        return new_task.id, new_task.task_number

    @staticmethod
    def updateTaskById(_id, update_data: dict):
        if "last_modified_date" not in update_data.keys():
            update_data["last_modified_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SeWorkTask.query.filter(SeWorkTask.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def deleteTaskById(_id, delete_data):

        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if "last_modified_date" not in delete_data.keys():
            delete_data["last_modified_date"] = now_datetime

        if 'deleted_date' not in delete_data.keys():
            delete_data["deleted_date"] = now_datetime

        if 'status' not in delete_data.keys():
            delete_data["status"] = 3

        SeWorkTask.query.filter(SeWorkTask.id == _id).update(delete_data)
        db.session.commit()

    @staticmethod
    def queryTaskJoinSysUserByUserIds(user_ids: list) -> [(SeWorkTask, SysUser, SysUser)]:
        """
        查询所有创建人或者责任人是user_id的任务
        :param user_ids: 用户ID列表
        :return:
        """
        create_user = aliased(SysUser)
        owner_user = aliased(SysUser)
        temp = db.session.query(
            SeWorkTask, create_user, owner_user).join(
            create_user, SeWorkTask.created_by_id == create_user.id).join(
            owner_user, SeWorkTask.owner_id == owner_user.id).filter(
            SeWorkTask.deleted_date == None
        )
        if "*" in user_ids:
            res = temp.all()
        else:
            res = temp.filter(or_(SeWorkTask.owner_id.in_(user_ids), SeWorkTask.created_by_id.in_(user_ids))).all()
        return res

    @staticmethod
    def getTaskJoinProjectById(_id: str) -> (SeWorkTask, SeWorkProject):
        res = db.session.query(
            SeWorkTask, SeWorkProject).join(
            SeWorkProject, SeWorkTask.project_id == SeWorkProject.id).filter(
            SeWorkTask.id == _id, SeWorkTask.deleted_date == None
        ).first()

        return res

    @staticmethod
    def getTaskJoinSysUserById(_id: str) -> (SeWorkTask, SeWorkProject, SysUser, SysUser):
        create_user = aliased(SysUser)
        owner_user = aliased(SysUser)
        res = db.session.query(
            SeWorkTask, SeWorkProject, create_user, owner_user).join(
            SeWorkProject, SeWorkTask.project_id == SeWorkProject.id).join(
            create_user, SeWorkTask.created_by_id == create_user.id).join(
            owner_user, SeWorkTask.owner_id == owner_user.id).filter(
            SeWorkTask.id == _id, SeWorkTask.deleted_date == None
        ).first()

        return res

    @staticmethod
    def getTaskJoinSysUserByUserId(user_ids: list, project_id=None) -> [(SeWorkTask, SysUser, SysUser)]:
        """
        查询所有创建人或者责任人是user_id的任务
        :param project_id:  项目ID
        :param user_ids: 用户ID列表
        :return:
        """
        create_user, owner_user = aliased(SysUser), aliased(SysUser)
        temp = db.session.query(
            SeWorkTask, create_user, owner_user).join(
            create_user, SeWorkTask.created_by_id == create_user.id).join(
            owner_user, SeWorkTask.owner_id == owner_user.id).filter(
            SeWorkTask.project_id == project_id, SeWorkTask.deleted_date == None
        )

        if "*" in user_ids:
            res = temp.all()
        else:
            res = temp.filter(or_(SeWorkTask.owner_id.in_(user_ids), SeWorkTask.created_by_id.in_(user_ids))).all()

        return res

    @staticmethod
    def getTaskJoinSysUserByIds(ids: list) -> [(SeWorkTask, SysUser, SysUser)]:
        """
        查询所有创建人或者责任人是user_id的任务
        :param ids: 父任务ID列表
        :return:
        """
        create_user, owner_user = aliased(SysUser), aliased(SysUser)
        res = db.session.query(
            SeWorkTask, create_user, owner_user).join(
            create_user, SeWorkTask.created_by_id == create_user.id).join(
            owner_user, SeWorkTask.owner_id == owner_user.id).filter(
            SeWorkTask.id.in_(ids), SeWorkTask.deleted_date == None
        ).all()

        return res

    @staticmethod
    def getTaskJoinSysUserByProjectId(project_id: str) -> [(SeWorkTask, SysUser, SysUser)]:
        """
        获取项目下所有任务
        :param project_id: 父任务ID
        :return:
        """
        create_user, owner_user = aliased(SysUser), aliased(SysUser)
        res = db.session.query(
            SeWorkTask, create_user, owner_user).join(
            create_user, SeWorkTask.created_by_id == create_user.id).join(
            owner_user, SeWorkTask.owner_id == owner_user.id).filter(
            SeWorkTask.project_id == project_id, SeWorkTask.deleted_date == None
        ).all()
        return res

    @staticmethod
    def getOwnerTasksByOwnerId(owner_id: str, start_date, endate_date=None) -> [SeWorkTask]:
        """
        获取所有已完成的自己的任务
        :param owner_id: 父任务ID
        :return:
        """
        temp = db.session.query(SeWorkTask).filter(
            SeWorkTask.owner_id == owner_id, SeWorkTask.status == 2,
            SeWorkTask.last_modified_date > start_date, SeWorkTask.deleted_date == None
        )

        if endate_date:
            temp = temp.filter(SeWorkTask.last_modified_date < endate_date)

        res = temp.order_by(SeWorkTask.created_date.desc()).all()
        return res


class SeWorkRecordDao:

    @staticmethod
    def queryRecordById(_id: str) -> SeWorkRecord:
        """
        :param _id: 任务日志ID
        :return:
        """
        res = SeWorkRecord.query.filter(SeWorkRecord.id == _id).one_or_none()
        return res

    @staticmethod
    def queryRecordByStatus(task_id: str, status: str) -> [SeWorkRecord]:
        """
        :param task_id: 任务ID
        :param status: 任务日志ID
        :return:
        """
        res = SeWorkRecord.query.filter(SeWorkRecord.task_id == task_id, SeWorkRecord.status == status).all()
        return res

    @staticmethod
    def addRecord(new_record: SeWorkRecord):
        exist = SeWorkRecordDao.queryRecordById(new_record.id)
        if exist:
            raise AppException("创建失败，日志ID已存在")

        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_record.created_date = now_date
        new_record.last_modified_date = now_date
        if new_record.status == 2:
            new_record.published_date = now_date

        db.session.add(new_record)
        db.session.commit()
        return new_record.id

    @staticmethod
    def updateRecordById(_id, update_data: dict):
        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        exist = SeWorkRecordDao.queryRecordById(_id)
        if exist:
            if exist.status == 2:
                raise AppException("更新失败，只能更新草稿日志")
            else:
                if update_data.get("status") == 2:
                    update_data["published_date"] = now_date

        if "last_modified_date" not in update_data.keys():
            update_data["last_modified_date"] = now_date
        if "deleted_by_id" in update_data.keys():
            update_data["deleted_date"] = now_date

        SeWorkRecord.query.filter(SeWorkRecord.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def deleteRecordById(_id, delete_data):
        exist = SeWorkRecordDao.queryRecordById(_id)
        if exist:
            if exist.status == 2:
                raise AppException("删除失败，只能删除草稿日志")

        if "last_modified_date" not in delete_data.keys():
            delete_data["last_modified_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if "deleted_date" not in delete_data.keys():
            delete_data["deleted_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        SeWorkRecord.query.filter(SeWorkRecord.id == _id).update(delete_data)
        db.session.commit()

    @staticmethod
    def getRecordJoinSysUserByStatus(task_id: str, status: str) -> [(SeWorkRecord, SysUser)]:
        res = db.session.query(
            SeWorkRecord, SysUser).join(
            SysUser, SeWorkRecord.created_by_id == SysUser.id).filter(
            SeWorkRecord.task_id == task_id, SeWorkRecord.status == status,
            SeWorkRecord.deleted_date == None
        ).order_by(SeWorkRecord.created_date).all()

        return res

    @staticmethod
    def queryTotalRecordByIds(user_ids, start_date, endate_date=None) -> [SeWorkRecord]:
        """
        :param endate_date:
        :param start_date:
        :param user_ids: 创建人ID
        :return:
        """
        temp = SeWorkRecord.query.filter(
            SeWorkRecord.created_by_id.in_(user_ids), SeWorkRecord.status == 2,
            SeWorkRecord.last_modified_date > start_date
        )
        if endate_date:
            temp = temp.filter(SeWorkRecord.last_modified_date < endate_date)

        res = temp.order_by(SeWorkRecord.last_modified_date.desc()).all()
        return res

    @staticmethod
    def queryTotalRecordByTaskId(task_id) -> [SeWorkRecord]:
        res = db.session.query(SeWorkRecord).filter(
            SeWorkRecord.task_id == task_id, SeWorkRecord.status == 2,
            SeWorkRecord.deleted_date == None
        ).order_by(SeWorkRecord.created_date).all()
        return res

    @staticmethod
    def queryLastRecordByTaskId(task_id) -> SeWorkRecord:
        res = db.session.query(SeWorkRecord).filter(
            SeWorkRecord.task_id == task_id, SeWorkRecord.status == 2,
            SeWorkRecord.deleted_date == None
        ).order_by(SeWorkRecord.published_date).first()
        return res


class SeWorkApprovalDao:

    @staticmethod
    def queryApprovalRecordById(_id: str) -> SeWorkApprovalRecord:
        """
        :param _id: 审批日志ID
        :return:
        """
        res = SeWorkApprovalRecord.query.filter(SeWorkApprovalRecord.id == _id).one_or_none()
        return res

    @staticmethod
    def queryApprovalRecordByRecordId(record_id: str) -> SeWorkApprovalRecord:
        """
        :param record_id: 任务日志ID
        :return:
        """
        res = SeWorkApprovalRecord.query.filter(SeWorkApprovalRecord.record_id == record_id).order_by(
            SeWorkApprovalRecord.created_date.desc()
        ).first()
        return res

    @staticmethod
    def queryUnApprovalByRecordId(record_id: str) -> SeWorkApprovalRecord:
        """
        :param record_id: 任务日志ID
        :return:
        """
        res = SeWorkApprovalRecord.query.filter(
            SeWorkApprovalRecord.record_id == record_id, SeWorkApprovalRecord.result == "2"
        ).order_by(
            SeWorkApprovalRecord.created_date.desc()
        ).first()
        return res

    @staticmethod
    def addRecord(new_approval: SeWorkApprovalRecord):
        exist = SeWorkApprovalDao.queryApprovalRecordById(new_approval.id)
        if exist:
            raise AppException("创建失败，日志ID已存在")

        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_approval.created_date = now_date

        db.session.add(new_approval)
        db.session.commit()
        return new_approval.id

    @staticmethod
    def updateApprovalById(_id, update_data: dict):
        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        exist = SeWorkApprovalDao.queryApprovalRecordById(_id)
        if not exist:
            return

        if "approval_date" not in update_data.keys():
            update_data["approval_date"] = now_date

        SeWorkApprovalRecord.query.filter(SeWorkApprovalRecord.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def getApprovalRecordByUserId(user_id: str) -> [(SeWorkApprovalRecord, SeWorkRecord, SeWorkProject, SysUser)]:
        """
        查询所有创建人或者责任人是user_ids的任务
        :param kwargs:
        :param user_id: 用户ID列表
        :return:
        """

        res = db.session.query(SeWorkApprovalRecord, SeWorkRecord, SeWorkProject, SysUser).join(
            SeWorkRecord, SeWorkApprovalRecord.record_id == SeWorkRecord.id).join(
            SeWorkProject, SeWorkApprovalRecord.project_id == SeWorkProject.id).join(
            SysUser, SeWorkRecord.created_by_id == SysUser.id).filter(
            SeWorkApprovalRecord.approval_date == None, SeWorkProject.created_by_id == user_id,
            SeWorkRecord.deleted_date == None, SeWorkProject.deleted_date == None
        ).order_by(SeWorkApprovalRecord.created_date).all()
        return res