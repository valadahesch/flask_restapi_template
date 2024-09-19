from app.models import db
from datetime import datetime
from sqlalchemy.orm import aliased
from sqlalchemy import or_, func
from app.models.techadmin import SysUser
from app.models.eco_partner import SeEcoTask, SeEcoRecord, SeEcoApprovalRecord
from app.utils.api_util import AppException


class SeEcoTaskDao:

    @staticmethod
    def queryTaskById(_id: str) -> SeEcoTask:
        """
        :param _id: 任务ID
        :return:
        """
        res = SeEcoTask.query.filter(SeEcoTask.id == _id).one_or_none()
        return res

    @staticmethod
    def queryTaskByNumber(task_number: str) -> SeEcoTask:
        """
        :param task_number: 任务编号
        :return:
        """
        res = SeEcoTask.query.filter(SeEcoTask.task_number == task_number).one_or_none()
        return res

    @staticmethod
    def queryTaskByParentId(parent_id: str) -> [SeEcoTask]:
        """
        :param parent_id: 任务编号
        :return:
        """
        res = SeEcoTask.query.filter(SeEcoTask.parent_id == parent_id).all()
        return res

    @staticmethod
    def queryTaskByPartnerIds(partner_ids: list) -> [SeEcoTask]:
        """
        查询所有创建人或者责任人是user_ids的任务
        :param partner_ids: 用户ID列表
        :return:
        """
        res = db.session.query(SeEcoTask).filter(
            SeEcoTask.partner_id.in_(partner_ids), SeEcoTask.parent_id == None,
            SeEcoTask.deleted_date == None
        ).all()

        return res

    @staticmethod
    def queryUndoneTaskByParentId(parent_id: str) -> [SeEcoTask]:
        """
        未完成的子任务
        :param parent_id: 父任务ID
        :return:
        """
        res = SeEcoTask.query.filter(
            SeEcoTask.parent_id == parent_id, SeEcoTask.task_result == None,
            SeEcoTask.deleted_date == None
        ).all()
        return res

    @staticmethod
    def queryTaskPartnerByUserId(user_ids: list, **kwargs) -> (int, [str]):
        """
        查询所有创建人或者责任人是user_ids的任务
        :param kwargs:
        :param user_ids: 用户ID列表
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000

        temp_query = db.session.query(SeEcoTask.partner_id).filter(
            or_(SeEcoTask.owner_id.in_(user_ids), SeEcoTask.created_by_id.in_(user_ids)),
            SeEcoTask.parent_id == None, SeEcoTask.deleted_date == None
        )

        for k, v in kwargs.items():
            if k not in SeEcoTask.__dict__.keys() or not v:
                continue

            if isinstance(v, (bool, int)):
                temp_query = temp_query.filter(getattr(SeEcoTask, k) == v)
            else:
                temp_query = temp_query.filter(getattr(SeEcoTask, k).like(f"%{v}%"))

        res = temp_query.distinct().order_by(SeEcoTask.partner_id).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items

    @staticmethod
    def updateTaskById(_id, update_data: dict):
        if "last_modified_date" not in update_data.keys():
            update_data["last_modified_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SeEcoTask.query.filter(SeEcoTask.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def deleteTaskById(_id, delete_data):
        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if "last_modified_date" not in delete_data.keys():
            delete_data["last_modified_date"] = now_datetime

        if 'deleted_date' not in delete_data.keys():
            delete_data["deleted_date"] = now_datetime

        SeEcoTask.query.filter(SeEcoTask.id == _id).update(delete_data)
        db.session.commit()

    @staticmethod
    def addTask(new_task: SeEcoTask):
        exist = SeEcoTaskDao.queryTaskById(new_task.id)
        if exist:
            raise AppException("创建失败，任务ID已存在")

        exist = SeEcoTaskDao.queryTaskByNumber(new_task.task_number)
        if exist:
            raise AppException("创建失败，任务编号已存在")

        new_task.status = "UnStart"
        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_task.created_date = now_date
        new_task.last_modified_date = now_date

        db.session.add(new_task)
        db.session.commit()
        return new_task.id, new_task.task_number

    @staticmethod
    def getTaskJoinSysUserById(_id: str) -> (SeEcoTask, SysUser, SysUser, SysUser):
        create_user = aliased(SysUser)
        owner_user = aliased(SysUser)
        modified_user = aliased(SysUser)
        res = db.session.query(
            SeEcoTask, create_user, owner_user, modified_user).join(
            create_user, SeEcoTask.created_by_id == create_user.id).join(
            owner_user, SeEcoTask.owner_id == owner_user.id).join(
            modified_user, SeEcoTask.last_modified_by_id == modified_user.id).filter(
            SeEcoTask.id == _id, SeEcoTask.deleted_date == None
        ).first()

        return res

    @staticmethod
    def getTaskJoinSysUserByIds(ids: list) -> [(SeEcoTask, SysUser, SysUser)]:
        create_user = aliased(SysUser)
        owner_user = aliased(SysUser)
        res = db.session.query(
            SeEcoTask, create_user, owner_user).join(
            create_user, SeEcoTask.created_by_id == create_user.id).join(
            owner_user, SeEcoTask.owner_id == owner_user.id).filter(
            SeEcoTask.id.in_(ids), SeEcoTask.deleted_date == None
        ).all()

        return res

    @staticmethod
    def getTasksJoinSysUserByIds(user_ids: list, partner_id=None) -> [(SeEcoTask, SysUser, SysUser)]:
        """
        查询所有创建人或者责任人是user_ids的任务
        :param partner_id:
        :param user_ids: 用户ID列表
        :return:
        """
        create_user = aliased(SysUser)
        owner_user = aliased(SysUser)
        temp = db.session.query(SeEcoTask, create_user, owner_user).join(
            create_user, SeEcoTask.created_by_id == create_user.id).join(
            owner_user, SeEcoTask.owner_id == owner_user.id).filter(
            or_(SeEcoTask.owner_id.in_(user_ids), SeEcoTask.created_by_id.in_(user_ids)),
            SeEcoTask.deleted_date == None
        )

        if partner_id:
            temp = temp.filter(SeEcoTask.partner_id == partner_id)

        res = temp.order_by(SeEcoTask.created_date.desc()).all()
        return res

    @staticmethod
    def getCloseTasksByOwnerIds(owner_ids: list, start_date, endate_date=None) -> [SeEcoTask]:
        """
        获取一段时间内任务完成的数量
        :param start_date: 时间范围
        :param owner_ids: 用户ID列表
        :return:
        """
        temp = db.session.query(SeEcoTask).filter(
            SeEcoTask.owner_id.in_(owner_ids), SeEcoTask.status == "Closed",
            SeEcoTask.last_modified_date > start_date, SeEcoTask.deleted_date == None
        )

        if endate_date:
            temp = temp.filter(SeEcoTask.last_modified_date < endate_date)

        res = temp.order_by(SeEcoTask.created_date.desc()).all()
        return res

    @staticmethod
    def getOwnerTasksByOwnerId(owner_id: str, start_date, endate_date=None) -> [SeEcoTask]:
        """
        获取自己完成的任务
        :param start_date: 时间范围
        :param owner_id: 用户ID列表
        :return:
        """
        temp = db.session.query(SeEcoTask).filter(
            SeEcoTask.owner_id == owner_id, SeEcoTask.status == "Closed",
            SeEcoTask.last_modified_date > start_date, SeEcoTask.deleted_date == None
        )

        if endate_date:
            temp = temp.filter(SeEcoTask.last_modified_date < endate_date)

        res = temp.order_by(SeEcoTask.created_date.desc()).all()
        return res


class SeEcoRecordDao:

    @staticmethod
    def queryRecordById(_id: str) -> SeEcoRecord:
        """
        :param _id: 任务日志ID
        :return:
        """
        res = SeEcoRecord.query.filter(SeEcoRecord.id == _id).one_or_none()
        return res

    @staticmethod
    def queryRecordByStatus(task_id: str, status: str) -> [SeEcoRecord]:
        """
        :param task_id: 任务ID
        :param status: 任务日志ID
        :return:
        """
        res = SeEcoRecord.query.filter(
            SeEcoRecord.task_id == task_id, SeEcoRecord.status == status,
            SeEcoRecord.deleted_date == None
        ).all()
        return res

    @staticmethod
    def addRecord(new_record: SeEcoRecord):
        exist = SeEcoRecordDao.queryRecordById(new_record.id)
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
        exist = SeEcoRecordDao.queryRecordById(_id)
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

        SeEcoRecord.query.filter(SeEcoRecord.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def deleteRecordById(_id, delete_data):
        exist = SeEcoRecordDao.queryRecordById(_id)
        if exist:
            if exist.status == 2:
                raise AppException("删除失败，只能删除草稿日志")

        if "last_modified_date" not in delete_data.keys():
            delete_data["last_modified_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if "deleted_date" not in delete_data.keys():
            delete_data["deleted_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        SeEcoRecord.query.filter(SeEcoRecord.id == _id).update(delete_data)
        db.session.commit()

    @staticmethod
    def getRecordJoinSysUserByStatus(task_id: str, status: str) -> [(SeEcoRecord, SysUser)]:
        res = db.session.query(
            SeEcoRecord, SysUser).join(
            SysUser, SeEcoRecord.created_by_id == SysUser.id).filter(
            SeEcoRecord.task_id == task_id, SeEcoRecord.status == status,
            SeEcoRecord.deleted_date == None
        ).order_by(SeEcoRecord.created_date).all()

        return res

    @staticmethod
    def getPendingRecordJoinTaskByUserID(user_id: str, status: str) -> [(SeEcoRecord, SeEcoTask, SysUser)]:
        res = db.session.query(
            SeEcoRecord, SeEcoTask, SysUser).join(
            SeEcoTask, SeEcoRecord.task_id == SeEcoTask.id).join(
            SysUser, SeEcoRecord.created_by_id == SysUser.id).filter(
            SeEcoRecord.status == status, SeEcoTask.owner_id == user_id,
            SeEcoRecord.deleted_date == None
        ).order_by(SeEcoRecord.created_date).all()

        return res

    @staticmethod
    def queryTotalRecordByIds(user_ids, start_date, endate_date=None) -> [SeEcoRecord]:
        """
        :param endate_date:
        :param start_date:
        :param user_ids: 创建人ID
        :return:
        """
        temp = SeEcoRecord.query.filter(
            SeEcoRecord.created_by_id.in_(user_ids), SeEcoRecord.status == "Publish",
            SeEcoRecord.last_modified_date > start_date
        )
        if endate_date:
            temp = temp.filter(SeEcoRecord.last_modified_date < endate_date)

        res = temp.order_by(SeEcoRecord.last_modified_date.desc()).all()
        return res

    @staticmethod
    def queryTotalRecordByTaskId(task_id: str) -> [SeEcoRecord]:
        res = db.session.query(SeEcoRecord).filter(
            SeEcoRecord.task_id == task_id, SeEcoRecord.status == "Publish",
            SeEcoRecord.deleted_date == None
        ).order_by(SeEcoRecord.created_date).all()
        return res

    @staticmethod
    def queryLastRecordByTaskId(task_id: str) -> SeEcoRecord:
        res = db.session.query(SeEcoRecord).filter(
            SeEcoRecord.task_id == task_id, SeEcoRecord.status == "Publish",
            SeEcoRecord.deleted_date == None
        ).order_by(SeEcoRecord.published_date).first()
        return res


class SeEcoApprovalDao:

    @staticmethod
    def queryApprovalRecordById(_id: str) -> SeEcoApprovalRecord:
        """
        :param _id: 审批日志ID
        :return:
        """
        res = SeEcoApprovalRecord.query.filter(SeEcoApprovalRecord.id == _id).one_or_none()
        return res

    @staticmethod
    def queryApprovalRecordByRecordId(record_id: str) -> SeEcoApprovalRecord:
        """
        :param record_id: 任务日志ID
        :return:
        """
        res = SeEcoApprovalRecord.query.filter(SeEcoApprovalRecord.record_id == record_id).order_by(
            SeEcoApprovalRecord.created_date.desc()
        ).first()
        return res

    @staticmethod
    def addRecord(new_approval: SeEcoApprovalRecord):
        exist = SeEcoApprovalDao.queryApprovalRecordById(new_approval.id)
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
        exist = SeEcoApprovalDao.queryApprovalRecordById(_id)
        if not exist:
            return

        if "approval_date" not in update_data.keys():
            update_data["approval_date"] = now_date

        SeEcoApprovalRecord.query.filter(SeEcoApprovalRecord.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def getApprovalRecordByUserId(user_id: str) -> [(SeEcoApprovalRecord, SeEcoRecord, SeEcoTask, SysUser)]:
        """
        查询所有创建人或者责任人是user_ids的任务
        :param kwargs:
        :param user_id: 用户ID列表
        :return:
        """

        res = db.session.query(SeEcoApprovalRecord, SeEcoRecord, SeEcoTask, SysUser).join(
            SeEcoRecord, SeEcoApprovalRecord.record_id == SeEcoRecord.id).join(
            SeEcoTask, SeEcoApprovalRecord.main_task_id == SeEcoTask.id).join(
            SysUser, SeEcoRecord.created_by_id == SysUser.id).filter(
            SeEcoApprovalRecord.approval_date == None, SeEcoTask.created_by_id == user_id,
            SeEcoRecord.deleted_date == None, SeEcoTask.deleted_date == None
        ).order_by(SeEcoApprovalRecord.created_date).all()
        return res