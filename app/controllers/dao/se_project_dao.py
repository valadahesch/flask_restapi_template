from app.models import db
from datetime import datetime
from sqlalchemy.orm import aliased
from sqlalchemy import or_, desc, func, and_
from app.models.se_project import SeProjectProject, SeProjectTask, SeProjectRecord, SeProjectApprovalRecord, \
    SeProjectFocus, SeWeekly
from app.models.techadmin import SysUser
from app.utils.api_util import AppException


class SeProjectProjectDao:

    @staticmethod
    def queryProjectById(_id: str) -> SeProjectProject:
        """
        :param _id: 项目ID
        :return:
        """
        res = SeProjectProject.query.filter(SeProjectProject.id == _id).one_or_none()
        return res

    @staticmethod
    def querySubProjectByParentId(parent_project) -> [SeProjectProject]:
        """
        :param parent_project: 父项目ID
        :return:
        """
        res = SeProjectProject.query.filter(SeProjectProject.parent_project == parent_project).all()
        return res

    @staticmethod
    def queryProjectByIds(ids: list) -> [SeProjectProject]:
        """
        :param ids: 项目ID列表
        :return:
        """
        res = SeProjectProject.query.filter(SeProjectProject.id.in_(ids)).all()
        return res

    @staticmethod
    def queryProjectByNumber(number: str) -> SeProjectProject:
        """
        :param number: 项目编号
        :return:
        """
        res = SeProjectProject.query.filter(SeProjectProject.project_number == number).one_or_none()
        return res

    @staticmethod
    def queryProjectByOpportunityNumber(opportunity_number: str) -> SeProjectProject:
        """
        :param opportunity_number: 商机编号
        :return:
        """
        res = SeProjectProject.query.filter(SeProjectProject.opportunity_number == opportunity_number).one_or_none()
        return res

    @staticmethod
    def queryProjectByCreateById(user_id: str) -> [SeProjectProject]:
        """
        :param user_id 用户id
        :return:
        """
        res = SeProjectProject.query.filter(SeProjectProject.created_by_id == user_id).all()
        return res

    @staticmethod
    def addProject(new_project: SeProjectProject):
        exist = SeProjectProjectDao.queryProjectById(new_project.id)
        if exist:
            raise AppException("创建失败，项目ID已存在")

        exist = SeProjectProjectDao.queryProjectByNumber(new_project.project_number)
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
        SeProjectProject.query.filter(SeProjectProject.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def deleteProjectById(_id, delete_data):

        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if "last_modified_date" not in delete_data.keys():
            delete_data["last_modified_date"] = now_datetime

        if 'deleted_date' not in delete_data.keys():
            delete_data["deleted_date"] = now_datetime

        SeProjectProject.query.filter(SeProjectProject.id == _id).update(delete_data)
        db.session.commit()

    @staticmethod
    def getProjectByOwner(owner_id, start_date, endate_date=None) -> [SeProjectProject]:
        temp = SeProjectProject.query.filter(
            SeProjectProject.owner_id == owner_id,
            SeProjectProject.last_modified_date > start_date
        )
        if endate_date:
            temp = temp.filter(SeProjectProject.last_modified_date < endate_date)

        res = temp.order_by(SeProjectProject.last_modified_date.desc()).all()
        return res

    @staticmethod
    def getProjectByOwnerAndFilter(owner, **kwargs) -> (int, [(SeProjectProject, SysUser, SysUser, SysUser)]):
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
        temp = db.session.query(SeProjectProject, create_user, owner_user, modify_user).join(
            create_user, SeProjectProject.created_by_id == create_user.id).join(
            owner_user, SeProjectProject.owner_id == owner_user.id).join(
            modify_user, SeProjectProject.last_modified_by_id == modify_user.id
        ).filter(SeProjectProject.owner_id == owner, SeProjectProject.deleted_date == None)

        if kwargs.get("created_by_id"):
            temp = temp.filter(SeProjectProject.created_by_id.in_(kwargs.get("created_by_id")))

        if kwargs.get("status"):
            temp = temp.filter(SeProjectProject.status.in_(kwargs.get("status")))

        if kwargs.get("date_range"):
            temp = temp.filter(
                SeProjectProject.created_date >= kwargs.get("date_range")[0],
                SeProjectProject.created_date <= kwargs.get("date_range")[1]
            )

        if kwargs.get('date_order') == 'asc':
            order = SeProjectProject.created_date.asc()
        else:
            order = SeProjectProject.created_date.desc()

        res = temp.distinct(SeProjectProject.id).order_by(order).paginate(
            page=page, per_page=size, error_out=False
        )

        return res.total, res.items

    @staticmethod
    def getProjectJoinSysUserById(_id: str) -> (SeProjectProject, SysUser, SysUser):

        create_user = aliased(SysUser)
        owner_user = aliased(SysUser)
        res = db.session.query(SeProjectProject, create_user, owner_user).join(
            create_user, SeProjectProject.created_by_id == create_user.id).join(
            owner_user, SeProjectProject.owner_id == owner_user.id).filter(
            SeProjectProject.id == _id, SeProjectTask.deleted_date == None
        ).first()

        return res


class SeProjectTaskDao:

    @staticmethod
    def queryTaskById(_id: str) -> SeProjectTask:
        """
        :param _id: 任务ID
        :return:
        """
        res = SeProjectTask.query.filter(SeProjectTask.id == _id).one_or_none()
        return res

    @staticmethod
    def queryTaskByProjectId(project_id: str) -> [SeProjectTask]:
        """
        :param project_id: 任务ID
        :return:
        """
        res = SeProjectTask.query.filter(SeProjectTask.project_id == project_id).all()
        return res

    @staticmethod
    def queryLastTaskByProjectId(project_id: str) -> SeProjectTask:
        """
        :param project_id: 任务ID
        :return:
        """
        res = SeProjectTask.query.filter(
            SeProjectTask.project_id == project_id).order_by(
            SeProjectTask.created_date.desc()).first()
        return res

    @staticmethod
    def queryTaskByTaskNumber(number: str) -> SeProjectTask:
        """
        :param number: 任务编号
        :return:
        """
        res = SeProjectTask.query.filter(SeProjectTask.task_number == number).one_or_none()
        return res

    @staticmethod
    def queryTaskByTaskEventNumber(number: str) -> [SeProjectTask]:
        """
        :param number: 任务编号
        :return:
        """
        res = SeProjectTask.query.filter(SeProjectTask.event_number == number).all()
        return res

    @staticmethod
    def queryMainEventTaskByTaskEventNumber(event_number: str) -> SeProjectTask:
        """
        :param event_number: 任务编号
        :return:
        """
        res = SeProjectTask.query.filter(
            SeProjectTask.event_number == event_number, SeProjectTask.parent_id == None,
            SeProjectTask.deleted_date == None
        ).one_or_none()
        return res

    @staticmethod
    def queryTaskByTaskLineName(assign_number: str) -> SeProjectTask:
        """
        :param assign_number: 任务行
        :return:
        """
        res = SeProjectTask.query.filter(
            SeProjectTask.assign_number == assign_number, SeProjectTask.deleted_date == None
        ).one_or_none()
        return res

    @staticmethod
    def queryTaskByParentId(parent_id: str) -> [SeProjectTask]:
        """
        获取所有子任务
        :param parent_id: 父任务ID
        :return:
        """
        res = SeProjectTask.query.filter(
            SeProjectTask.parent_id == parent_id
        ).all()
        return res

    @staticmethod
    def queryUndoneTaskByParentId(parent_id: str) -> [SeProjectTask]:
        """
        未完成的子任务
        :param parent_id: 父任务ID
        :return:
        """
        res = SeProjectTask.query.filter(
            SeProjectTask.parent_id == parent_id, SeProjectTask.deleted_date == None,
            or_(SeProjectTask.task_result == None, SeProjectTask.status == 5)
        ).all()
        return res

    @staticmethod
    def queryUndoneMainTaskByProjectId(project_id: str) -> [SeProjectTask]:
        """
        未完成的主任务
        :param project_id: 父任务ID
        :return:
        """
        res = SeProjectTask.query.filter(
            SeProjectTask.project_id == project_id, SeProjectTask.task_result == None,
            SeProjectTask.parent_id, SeProjectTask.deleted_date == None
        ).all()
        return res

    @staticmethod
    def queryTaskBySysUserId(user_id: str) -> [SeProjectTask]:
        """
        查询所有创建人或者责任人是user_id的任务
        :param user_id: 父任务ID
        :return:
        """
        res = SeProjectTask.query.filter(
            or_(SeProjectTask.owner_id == user_id, SeProjectTask.created_by_id == user_id),
            SeProjectTask.deleted_date == None
        ).all()

        return res

    @staticmethod
    def queryTasksBySysUserId(user_id: str) -> [SeProjectTask]:
        """
        查询所有创建任务是user_id的主任务
        :param user_id 拆功能键人
        :return:
        """
        res = SeProjectTask.query.filter(
            SeProjectTask.created_by_id == user_id, SeProjectTask.parent_id == None,
            SeProjectTask.deleted_date == None
        ).all()
        return res

    @staticmethod
    def queryDoTaskByProjectId(project_id: str) -> [SeProjectTask]:
        """
        获取项目下所有任务
        :param project_id: 父任务ID
        :return:
        """
        res = SeProjectTask.query.filter(
            SeProjectTask.project_id == project_id, SeProjectTask.task_result == None,
            SeProjectTask.deleted_date == None
        ).all()
        return res

    @staticmethod
    def queryTaskBySysUserIds(user_ids: list) -> [SeProjectTask]:
        """
        查询所有创建人或者责任人是user_id的任务
        :param user_ids: 用户ID列表
        :return:
        """
        res = SeProjectTask.query.filter(
            or_(SeProjectTask.owner_id.in_(user_ids), SeProjectTask.created_by_id.in_(user_ids)),
            SeProjectTask.deleted_date == None
        ).all()

        return res

    @staticmethod
    def addTask(new_task: SeProjectTask):
        exist = SeProjectTaskDao.queryTaskById(new_task.id)
        if exist:
            raise AppException("创建失败，任务ID已存在")

        exist = SeProjectTaskDao.queryTaskByTaskNumber(new_task.task_number)
        if exist:
            raise AppException("创建失败，任务编号已存在")

        new_task.status = new_task.status if new_task.status else 1
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
        SeProjectTask.query.filter(SeProjectTask.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def updateTaskByIds(ids: list, update_data: dict):
        if "last_modified_date" not in update_data.keys():
            update_data["last_modified_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SeProjectTask.query.filter(SeProjectTask.id.in_(ids)).update(update_data)
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

        SeProjectTask.query.filter(SeProjectTask.id == _id).update(delete_data)
        db.session.commit()

    @staticmethod
    def queryTaskJoinSysUserByUserIds(user_ids: list) -> [(SeProjectTask, SysUser, SysUser)]:
        """
        查询所有创建人或者责任人是user_id的任务
        :param user_ids: 用户ID列表
        :return:
        """
        create_user = aliased(SysUser)
        owner_user = aliased(SysUser)
        temp = db.session.query(
            SeProjectTask, create_user, owner_user).join(
            create_user, SeProjectTask.created_by_id == create_user.id).join(
            owner_user, SeProjectTask.owner_id == owner_user.id).filter(
            SeProjectTask.deleted_date == None
        )
        if "*" in user_ids:
            res = temp.all()
        else:
            res = temp.filter(or_(SeProjectTask.owner_id.in_(user_ids), SeProjectTask.created_by_id.in_(user_ids))).all()
        return res

    @staticmethod
    def getTaskJoinProjectById(_id: str) -> (SeProjectTask, SeProjectProject):
        res = db.session.query(
            SeProjectTask, SeProjectProject).join(
            SeProjectProject, SeProjectTask.project_id == SeProjectProject.id).filter(
            SeProjectTask.id == _id, SeProjectTask.deleted_date == None
        ).first()

        return res

    @staticmethod
    def getTaskJoinSysUserById(_id: str) -> (SeProjectTask, SeProjectProject, SysUser, SysUser):
        create_user = aliased(SysUser)
        owner_user = aliased(SysUser)
        res = db.session.query(
            SeProjectTask, SeProjectProject, create_user, owner_user).join(
            SeProjectProject, SeProjectTask.project_id == SeProjectProject.id).join(
            create_user, SeProjectTask.created_by_id == create_user.id).join(
            owner_user, SeProjectTask.owner_id == owner_user.id).filter(
            SeProjectTask.id == _id, SeProjectTask.deleted_date == None
        ).first()

        return res

    @staticmethod
    def getTaskJoinSysUserByUserId(user_ids: list, project_id=None) -> [(SeProjectTask, SysUser, SysUser)]:
        """
        查询所有创建人或者责任人是user_id的任务
        :param project_id:  项目ID
        :param user_ids: 用户ID列表
        :return:
        """
        create_user, owner_user = aliased(SysUser), aliased(SysUser)
        temp = db.session.query(
            SeProjectTask, create_user, owner_user).join(
            create_user, SeProjectTask.created_by_id == create_user.id).join(
            owner_user, SeProjectTask.owner_id == owner_user.id).filter(
            SeProjectTask.project_id == project_id, SeProjectTask.deleted_date == None
        )

        if "*" in user_ids:
            res = temp.all()
        else:
            res = temp.filter(or_(SeProjectTask.owner_id.in_(user_ids), SeProjectTask.created_by_id.in_(user_ids))).all()

        return res

    @staticmethod
    def getTaskJoinSysUserByIds(ids: list) -> [(SeProjectTask, SysUser, SysUser)]:
        """
        查询所有创建人或者责任人是user_id的任务
        :param ids: 父任务ID列表
        :return:
        """
        create_user, owner_user = aliased(SysUser), aliased(SysUser)
        res = db.session.query(
            SeProjectTask, create_user, owner_user).join(
            create_user, SeProjectTask.created_by_id == create_user.id).join(
            owner_user, SeProjectTask.owner_id == owner_user.id).filter(
            SeProjectTask.id.in_(ids), SeProjectTask.deleted_date == None
        ).all()

        return res

    @staticmethod
    def getTaskJoinSysUserByProjectId(project_id: str) -> [(SeProjectTask, SysUser, SysUser)]:
        """
        获取项目下所有任务
        :param project_id: 父任务ID
        :return:
        """
        create_user, owner_user = aliased(SysUser), aliased(SysUser)
        res = db.session.query(
            SeProjectTask, create_user, owner_user).join(
            create_user, SeProjectTask.created_by_id == create_user.id).join(
            owner_user, SeProjectTask.owner_id == owner_user.id).filter(
            SeProjectTask.project_id == project_id, SeProjectTask.deleted_date == None
        ).all()
        return res

    @staticmethod
    def getTasksJoinSysUserByIds(ids: list) -> [(SeProjectTask, SeProjectProject, SysUser, SysUser)]:
        """
        根据任务Ids查询所有任务
        :param ids: 父任务ID
        :return:
        """
        create_user, owner_user, project = aliased(SysUser), aliased(SysUser), SeProjectProject
        res = db.session.query(
            SeProjectTask, SeProjectProject, create_user, owner_user).join(
            create_user, SeProjectTask.created_by_id == create_user.id).join(
            owner_user, SeProjectTask.owner_id == owner_user.id).join(
            SeProjectProject, SeProjectTask.project_id == SeProjectProject.id).filter(
            SeProjectTask.id.in_(ids), SeProjectTask.deleted_date == None
        ).all()
        return res

    @staticmethod
    def getApprovalTaskJoinSysUserByCreateId(
            created_by_id: str) -> [(SeProjectTask, SeProjectProject, SysUser, SysUser)]:
        """
        根据主任务创建人获取所有项目下待审批的任务
        :param created_by_id: 父任务ID
        :return:
        """
        create_user, owner_user, project = aliased(SysUser), aliased(SysUser), SeProjectProject
        res = db.session.query(
            SeProjectTask, SeProjectProject, create_user, owner_user).join(
            create_user, SeProjectTask.created_by_id == create_user.id).join(
            owner_user, SeProjectTask.owner_id == owner_user.id).join(
            SeProjectProject, SeProjectTask.project_id == SeProjectProject.id).filter(
            SeProjectTask.created_by_id == created_by_id, SeProjectTask.status == 5,
            SeProjectTask.deleted_date == None, SeProjectTask.parent_id is None
        ).all()
        return res

    @staticmethod
    def getPreEnableTaskJoinSysUserByCreateId(owner_id: str) -> [(SeProjectTask, SeProjectProject, SysUser, SysUser)]:
        """
        根据项目创建人获取所有项目下待审批的任务
        :param owner_id: 任务负责人ID
        :return:
        """
        create_user, owner_user, project = aliased(SysUser), aliased(SysUser), SeProjectProject
        res = db.session.query(
            SeProjectTask, SeProjectProject, create_user, owner_user).join(
            create_user, SeProjectTask.created_by_id == create_user.id).join(
            owner_user, SeProjectTask.owner_id == owner_user.id).join(
            SeProjectProject, SeProjectTask.project_id == SeProjectProject.id).filter(
            SeProjectTask.owner_id == owner_id, SeProjectTask.status == 4,
            SeProjectTask.deleted_date == None
        ).all()
        return res

    @staticmethod
    def getTaskProjectJoinSysUserByUserId(user_id: str, page: int, size: int, status: list, task_number: str, subject: str,
                                          project_number: str, project_subject: str, created_date_range: list, 
                                          support_mode: list, task_result: list):  
        """
        获取我负责的所有任务
        :param user_id: 用户
        :return: db.session.query
        """
        create_user, owner_user, last_modified_user = aliased(SysUser), aliased(SysUser), aliased(SysUser)
        query = db.session.query(SeProjectTask, SeProjectProject, create_user, owner_user, last_modified_user)
        query = query.outerjoin(create_user, SeProjectTask.created_by_id == create_user.id)
        query = query.outerjoin(owner_user, SeProjectTask.owner_id == owner_user.id)
        query = query.outerjoin(last_modified_user, SeProjectTask.last_modified_by_id == last_modified_user.id)
        query = query.outerjoin(SeProjectProject, SeProjectTask.project_id == SeProjectProject.id)
        query = query.filter(SeProjectTask.owner_id == user_id)
        if status:
            query = query.filter(SeProjectTask.status.in_(status))
        if support_mode:
            query = query.filter(SeProjectTask.support_mode.in_(support_mode))  
        if task_result:
            query = query.filter(SeProjectTask.task_result.in_(task_result))  
        if created_date_range:
            start_date = datetime.strptime(created_date_range[0], "%Y-%m-%d %H:%M:%S")
            end_date = datetime.strptime(created_date_range[1], "%Y-%m-%d %H:%M:%S")
            query = query.filter(SeProjectTask.created_date.between(start_date, end_date))
        if task_number:
            like_clause = f"%{task_number}%"
            query = query.filter(or_(SeProjectTask.event_number.ilike(like_clause), SeProjectTask.task_number.ilike(like_clause),
                                    and_(
                                        SeProjectTask.assign_number.ilike(like_clause),
                                        SeProjectTask.parent_id.isnot(None)
                                    )))
        if subject:
            like_clause = f"%{subject}%"
            query = query.filter(SeProjectTask.subject.ilike(like_clause))
        if project_number:
            like_clause = f"%{project_number}%"
            query = query.filter(or_(SeProjectProject.project_number.ilike(like_clause), SeProjectProject.opportunity_number.ilike(like_clause)))
        if project_subject:
            like_clause = f"%{project_number}%"
            query = query.filter(SeProjectProject.subject.ilike(like_clause))
        offset = (page - 1) * size
        total = query.count()
        query = query.order_by(SeProjectTask.created_date.desc()).offset(offset).limit(size)
        return query, total


class SeProjectRecordDao:

    @staticmethod
    def queryRecordById(_id: str) -> SeProjectRecord:
        """
        :param _id: 任务日志ID
        :return:
        """
        res = SeProjectRecord.query.filter(SeProjectRecord.id == _id).one_or_none()
        return res

    @staticmethod
    def queryRecordByStatus(task_id: str, status: str) -> [SeProjectRecord]:
        """
        :param task_id: 任务ID
        :param status: 任务日志ID
        :return:
        """
        res = SeProjectRecord.query.filter(SeProjectRecord.task_id == task_id, SeProjectRecord.status == status).all()
        return res

    @staticmethod
    def queryLastRecordByStatus(task_id: str) -> SeProjectRecord:
        """
        :param task_id: 任务ID
        :return:
        """
        res = SeProjectRecord.query.filter(
            SeProjectRecord.task_id == task_id, SeProjectRecord.status == "2").order_by(
            SeProjectRecord.created_date.desc()
        ).first()
        return res

    @staticmethod
    def queryApprovalRecordByTaskId(task_id: str) -> [SeProjectRecord]:
        """
        :param task_id: 任务ID
        :return:
        """
        res = SeProjectRecord.query.filter(SeProjectRecord.task_id == task_id, SeProjectRecord.status == "4").all()
        return res

    @staticmethod
    def addRecord(new_record: SeProjectRecord):
        exist = SeProjectRecordDao.queryRecordById(new_record.id)
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

        if update_data.get("status") == 2:
            update_data["published_date"] = now_date

        if "last_modified_date" not in update_data.keys():
            update_data["last_modified_date"] = now_date
        if "deleted_by_id" in update_data.keys():
            update_data["deleted_date"] = now_date

        SeProjectRecord.query.filter(SeProjectRecord.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def deleteRecordById(_id, delete_data):
        exist = SeProjectRecordDao.queryRecordById(_id)
        if exist:
            if exist.status == 2 or exist.status == 4:
                raise AppException("删除失败，只能删除草稿日志")

        if "last_modified_date" not in delete_data.keys():
            delete_data["last_modified_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if "deleted_date" not in delete_data.keys():
            delete_data["deleted_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        SeProjectRecord.query.filter(SeProjectRecord.id == _id).update(delete_data)
        db.session.commit()

    @staticmethod
    def getRecordJoinSysUserByStatus(task_id: str, status: str) -> [(SeProjectRecord, SysUser)]:
        res = db.session.query(
            SeProjectRecord, SysUser).join(
            SysUser, SeProjectRecord.created_by_id == SysUser.id).filter(
            SeProjectRecord.task_id == task_id, SeProjectRecord.status == status,
            SeProjectRecord.deleted_date == None
        ).order_by(SeProjectRecord.support_start_date.desc()).all()

        return res
    
    @staticmethod
    def getRecordJoinSeProjectTaskByStatus(task_id: str, status: list) -> [(SeProjectRecord, SeProjectTask)]:
        res = db.session.query(
            SeProjectRecord, SeProjectTask).join(
            SeProjectTask, SeProjectRecord.task_id == SeProjectTask.id).filter(
                or_(
                    SeProjectTask.id == task_id,
                    SeProjectTask.parent_id == task_id,
                ),
                SeProjectRecord.status.in_(status)
        ).order_by(SeProjectRecord.support_start_date.desc()).all()

        return res

    @staticmethod
    def getPublishProjectRecord(project_id: str) -> [(SeProjectRecord, SeProjectTask, SysUser)]:
        res = db.session.query(SeProjectRecord, SeProjectTask, SysUser).join(
            SysUser, SeProjectRecord.created_by_id == SysUser.id).join(
            SeProjectTask, SeProjectRecord.task_id == SeProjectTask.id).join(
            SeProjectProject, SeProjectTask.project_id == SeProjectProject.id).filter(
            SeProjectProject.id == project_id, SeProjectRecord.status == 2,
            SeProjectRecord.deleted_date == None
        ).order_by(SeProjectRecord.support_start_date.desc()).all()

        return res

    @staticmethod
    def getAllRecordJoinSysUserByStatus(task_ids: list, status: str) -> [(SeProjectRecord, SysUser)]:
        res = db.session.query(
            SeProjectRecord, SysUser).join(
            SysUser, SeProjectRecord.created_by_id == SysUser.id).filter(
            SeProjectRecord.task_id.in_(task_ids), SeProjectRecord.status == status,
            SeProjectRecord.deleted_date == None
        ).order_by(SeProjectRecord.support_start_date.desc()).all()

        return res

    @staticmethod
    def queryTotalRecordByIds(user_ids, start_date, endate_date=None) -> [SeProjectRecord]:
        """
        :param endate_date:
        :param start_date:
        :param user_ids: 创建人ID
        :return:
        """
        temp = SeProjectRecord.query.filter(
            SeProjectRecord.created_by_id.in_(user_ids), SeProjectRecord.status == 2,
            SeProjectRecord.last_modified_date > start_date
        )
        if endate_date:
            temp = temp.filter(SeProjectRecord.last_modified_date < endate_date)

        res = temp.order_by(SeProjectRecord.last_modified_date.desc()).all()
        return res

    @staticmethod
    def getAllRecordCountByTaskIds(task_ids: list) -> [(str, str)]:
        res = db.session.query(SeProjectRecord.task_id, func.count(SeProjectRecord.id).label('count')).filter(
            SeProjectRecord.task_id.in_(task_ids), SeProjectRecord.status == 2,
            SeProjectRecord.deleted_date == None
        ).group_by(SeProjectRecord.task_id).all()

        return res

    @staticmethod
    def getAllRecordByUserIdAndFilter(user_ids: list, **kwargs) -> [
        (SeProjectRecord, SeProjectTask, SeProjectProject, SysUser)
    ]:
        """
        查询所有创建人或者责任人是user_ids的任务
        :param kwargs:
        :param user_ids: 用户ID列表
        :return:
        """

        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 10

        temp = db.session.query(SeProjectRecord, SeProjectTask, SeProjectProject, SysUser).join(
            SeProjectTask, SeProjectRecord.task_id == SeProjectTask.id).join(
            SeProjectProject, SeProjectTask.project_id == SeProjectProject.id).join(
            SysUser, SeProjectRecord.created_by_id == SysUser.id).filter(
            SeProjectRecord.created_by_id.in_(user_ids)
        )
        if kwargs.get("status"):
            temp = temp.filter(SeProjectRecord.status.in_(kwargs.get("status")))

        if kwargs.get("adcodes"):
            temp = temp.filter(SeProjectRecord.support_location_adcode.in_(kwargs.get("adcodes")))

        if kwargs.get("task_number"):
            task_number = kwargs.get("task_number")
            temp = temp.filter(or_(
                SeProjectTask.task_number == task_number, SeProjectTask.event_number == task_number,
                SeProjectTask.assign_number == task_number
            ))

        if kwargs.get("task_subject"):
            temp = temp.filter(SeProjectTask.subject.like(f'%{kwargs.get("task_subject")}%'))

        if kwargs.get("project_number"):
            temp = temp.filter(or_(
                SeProjectProject.opportunity_number == kwargs.get("project_number")
            ))

        if kwargs.get("project_subject"):
            temp = temp.filter(or_(
                SeProjectProject.subject.like(f'%{kwargs.get("project_subject")}%')
            ))

        if kwargs.get("date_range"):
            start_date = kwargs.get("date_range")[0]
            end_data = kwargs.get("date_range")[1]
            temp = temp.filter(or_(
                and_(SeProjectRecord.support_start_date > start_date, SeProjectRecord.support_start_date < end_data),
                and_(SeProjectRecord.support_end_date > start_date, SeProjectRecord.support_end_date < end_data)
            ))

        res = temp.order_by(SeProjectRecord.support_start_date).paginate(
            page=page, per_page=size, error_out=False
        )

        return res.total, res.items
    
    @staticmethod
    def getRecordJoinSeProjectById(project_id: str) -> [(SeProjectRecord, SeProjectTask)]:
        res = db.session.query(SeProjectRecord, SeProjectTask).join(
            SeProjectTask, SeProjectRecord.task_id == SeProjectTask.id).join(
            SeProjectProject, SeProjectTask.project_id == SeProjectProject.id).filter(
            SeProjectProject.id == project_id, SeProjectRecord.deleted_date == None
        ).order_by(SeProjectRecord.support_start_date.desc()).all()

        return res

class SeProjectApprovalDao:

    @staticmethod
    def queryApprovalRecordById(_id: str) -> SeProjectApprovalRecord:
        """
        :param _id: 审批日志ID
        :return:
        """
        res = SeProjectApprovalRecord.query.filter(SeProjectApprovalRecord.id == _id).one_or_none()
        return res

    @staticmethod
    def queryApprovalRecordByRecordId(record_id: str) -> SeProjectApprovalRecord:
        """
        :param record_id: 任务日志ID
        :return:
        """
        res = SeProjectApprovalRecord.query.filter(SeProjectApprovalRecord.record_id == record_id).order_by(
            SeProjectApprovalRecord.created_date.desc()
        ).first()
        return res

    @staticmethod
    def queryApprovalRecordByTaskId(task_id: str) -> SeProjectApprovalRecord:
        """
        :param task_id: 任务ID
        :return:
        """
        res = SeProjectApprovalRecord.query.filter(SeProjectApprovalRecord.task_id == task_id).order_by(
            SeProjectApprovalRecord.created_date.desc()
        ).first()
        return res

    @staticmethod
    def queryApprovalingRecordByTaskId(task_id: str) -> SeProjectApprovalRecord:
        """
        :param task_id: 任务ID
        :return:
        """
        res = SeProjectApprovalRecord.query.filter(
            SeProjectApprovalRecord.task_id == task_id, SeProjectApprovalRecord.approval_date == None,
            SeProjectApprovalRecord.record_id == None
        ).order_by(
            SeProjectApprovalRecord.created_date.desc()
        ).first()
        return res

    @staticmethod
    def queryApprovalByRecordId(record_id: str) -> SeProjectApprovalRecord:
        """
        :param record_id: 任务日志ID
        :return:
        """
        res = SeProjectApprovalRecord.query.filter(
            SeProjectApprovalRecord.record_id == record_id, SeProjectApprovalRecord.approval_date == None
        ).order_by(
            SeProjectApprovalRecord.created_date.desc()
        ).first()
        return res

    @staticmethod
    def queryUnApprovalByRecordId(record_id: str) -> SeProjectApprovalRecord:
        """
        :param record_id: 任务日志ID
        :return:
        """
        res = SeProjectApprovalRecord.query.filter(
            SeProjectApprovalRecord.record_id == record_id, SeProjectApprovalRecord.result == "2"
        ).order_by(
            SeProjectApprovalRecord.created_date.desc()
        ).first()
        return res

    @staticmethod
    def addRecord(new_approval: SeProjectApprovalRecord):
        exist = SeProjectApprovalDao.queryApprovalRecordById(new_approval.id)
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
        exist = SeProjectApprovalDao.queryApprovalRecordById(_id)
        if not exist:
            return

        if "approval_date" not in update_data.keys():
            update_data["approval_date"] = now_date

        SeProjectApprovalRecord.query.filter(SeProjectApprovalRecord.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def getApprovalRecordByUserId(user_id: str) -> [(
            SeProjectApprovalRecord, SeProjectRecord, SeProjectTask, SeProjectProject, SysUser
    )]:
        """
        查询所有创建人或者责任人是user_ids的任务
        :param kwargs:
        :param user_id: 用户ID列表
        :return:
        """
        res = db.session.query(SeProjectApprovalRecord, SeProjectRecord, SeProjectTask, SeProjectProject, SysUser).join(
            SeProjectRecord, SeProjectApprovalRecord.record_id == SeProjectRecord.id).join(
            SeProjectTask, SeProjectApprovalRecord.main_task_id == SeProjectTask.id).join(
            SeProjectProject, SeProjectApprovalRecord.project_id == SeProjectProject.id).join(
            SysUser, SeProjectRecord.created_by_id == SysUser.id).filter(
            SeProjectApprovalRecord.approval_date == None, SeProjectTask.created_by_id == user_id,
            SeProjectRecord.deleted_date == None, SeProjectProject.deleted_date == None
        ).order_by(SeProjectApprovalRecord.created_date).all()
        return res

    @staticmethod
    def getApprovalTaskByUserId(created_by_id: str) -> [SeProjectApprovalRecord]:
        """
        根据主任务的创建人查询待审批任务
        :param created_by_id: 用户ID列表
        :return:
        """
        res = db.session.query(SeProjectApprovalRecord).join(
            SeProjectTask, SeProjectApprovalRecord.main_task_id == SeProjectTask.id).filter(
            SeProjectApprovalRecord.approval_date == None, SeProjectTask.created_by_id == created_by_id
        ).order_by(SeProjectApprovalRecord.created_date).all()
        return res


class SeProjectFocusDao:

    @staticmethod
    def queryFocusById(_id: str) -> SeProjectFocus:
        """
        :param _id: 关注项目ID
        :return:
        """
        res = SeProjectFocus.query.filter(SeProjectFocus.id == _id).one_or_none()
        return res

    @staticmethod
    def queryDoFocusByUserId(user_id: str) -> [SeProjectFocus]:
        """
        获取用户关注的所有项目
        :param user_id: 关注者ID
        :return:
        """
        res = SeProjectFocus.query.filter(
            SeProjectFocus.follower_id == user_id, SeProjectFocus.deleted_date == None
        ).all()
        return res

    @staticmethod
    def queryFocusByProject(project_id: str) -> [SeProjectFocus]:
        """
        获取项目的所有关注
        :param project_id: 项目ID
        :return:
        """
        res = SeProjectFocus.query.filter(
            SeProjectFocus.project_id == project_id,
            SeProjectFocus.deleted_date == None,
        ).all()
        return res

    @staticmethod
    def queryFocusByProjectId(user_id: str, project_id: str) -> SeProjectFocus:
        """
        获取用户关注过的项目信息
        :param user_id: 关注着ID
        :param project_id: 项目ID
        :return:
        """
        res = SeProjectFocus.query.filter(
            SeProjectFocus.follower_id == user_id, SeProjectFocus.project_id == project_id
        ).one_or_none()
        return res

    @staticmethod
    def addFocus(new_focus: SeProjectFocus):
        exist = SeProjectFocusDao.queryFocusById(new_focus.id)
        if exist:
            raise AppException("创建失败，关注项目ID已存在")

        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_focus.followed_date = now_date

        db.session.add(new_focus)
        db.session.commit()
        return new_focus.id

    @staticmethod
    def updateFocusById(_id, update_data: dict):
        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if "followed_date" not in update_data.keys():
            update_data["followed_date"] = now_date

        SeProjectFocus.query.filter(SeProjectFocus.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def deleteFocusById(_id, delete_data):

        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 'deleted_date' not in delete_data.keys():
            delete_data["deleted_date"] = now_datetime

        SeProjectFocus.query.filter(SeProjectFocus.id == _id).update(delete_data)
        db.session.commit()

    @staticmethod
    def getFocusJoinProjectByFollowerId(follower_id: str) -> [(SeProjectFocus, SeProjectProject)]:
        res = db.session.query(SeProjectFocus, SeProjectProject).join(
            SeProjectProject, SeProjectFocus.project_id == SeProjectProject.id).filter(
            SeProjectFocus.follower_id == follower_id, SeProjectFocus.deleted_date == None
        ).all()

        return res


class SeWeeklyDao:

    @staticmethod
    def queryWeeklyById(_id: str) -> SeWeekly:
        """
        :param _id: 周报ID
        :return:
        """
        res = SeWeekly.query.filter(SeWeekly.id == _id).one_or_none()
        return res

    @staticmethod
    def queryLastWeekly(created_by_id, department_ids=None) -> SeWeekly:
        """
        :param department_ids:
        :param created_by_id: 创建人ID
        :return:
        """
        temp = SeWeekly.query.filter(SeWeekly.created_by_id == created_by_id, SeWeekly.status == "Published")

        if department_ids:
            temp.filter(SeWeekly.department_ids == department_ids)

        res = temp.order_by(desc(SeWeekly.send_date)).first()
        return res

    @staticmethod
    def getWeeklyByOwnerAndFilter(owner, **kwargs) -> (int, [(SeWeekly, SysUser, SysUser)]):
        """
        查询责任人是owner_id的项目
        :param owner:
        :param kwargs: 用户ID列表
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 10

        create_user = aliased(SysUser)
        modify_user = aliased(SysUser)
        temp = db.session.query(SeWeekly, create_user, modify_user).join(
            create_user, SeWeekly.created_by_id == create_user.id).join(
            modify_user, SeWeekly.last_modified_by_id == modify_user.id
        ).filter(SeWeekly.created_by_id == owner)

        if kwargs.get("subject"):
            temp = temp.filter(SeWeekly.subject.like(f"%{kwargs.get('subject')}%"))

        if kwargs.get("status"):
            status_filter = []
            for s in kwargs.get("status"):
                status_filter.append(SeWeekly.status == s)
            temp = temp.filter(or_(*status_filter))

        if kwargs.get("created_date_range"):
            temp = temp.filter(
                SeWeekly.created_date >= kwargs.get("created_date_range")[0],
                SeWeekly.created_date <= kwargs.get("created_date_range")[1]
            )

        if kwargs.get('date_order') == 'asc':
            order = SeWeekly.created_date.asc()
        else:
            order = SeWeekly.created_date.desc()

        res = temp.distinct(SeWeekly.id).order_by(order).paginate(
            page=page, per_page=size, error_out=False
        )

        return res.total, res.items

    @staticmethod
    def addWeekly(new: SeWeekly):
        exist = SeWeeklyDao.queryWeeklyById(new.id)
        if exist:
            raise AppException("创建失败，模板ID")

        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        new.created_date = now_date
        new.last_modified_date = now_date

        db.session.add(new)
        db.session.commit()
        return new.id

    @staticmethod
    def updateWeeklyById(_id, update_data: dict):
        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        exist = SeWeeklyDao.queryWeeklyById(_id)
        if not exist:
            raise AppException("更新失败，周报不存在")

        if "last_modified_date" not in update_data.keys():
            update_data["last_modified_date"] = now_date

        SeWeekly.query.filter(SeWeekly.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def getSubWeekly(user_ids, start_date, endate_date=None) -> [SeWeekly]:
        """
        :param endate_date:
        :param start_date:
        :param user_ids: 创建人ID
        :return:
        """
        temp = SeWeekly.query.filter(
            SeWeekly.created_by_id.in_(user_ids), SeWeekly.status == "Published",
            SeWeekly.send_date > start_date
        )
        if endate_date:
            temp = temp.filter(SeWeekly.send_date < endate_date)

        res = temp.order_by(SeWeekly.send_date.desc()).all()
        return res