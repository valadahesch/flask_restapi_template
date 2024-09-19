from datetime import datetime
from app.models import db
from app.models.ps_inspection import PsTask, PsTaskUploadHistory, PsUserMapping, PsCustomerArchives


class PsTaskDao:

    @staticmethod
    def queryTaskById(_id: str) -> PsTask:
        """
        :param _id: task ID
        :return:
        """
        res = PsTask.query.filter(PsTask.id == _id).one_or_none()
        return res

    @staticmethod
    def queryTaskByTaskId(task_id: str) -> PsTask:
        """
        通过任务id（项目管理系统），获取任务列表中的信息
        """
        res = PsTask.query.filter(PsTask.task_id == task_id).one_or_none()
        return res

    @staticmethod
    def queryTaskGroupByInspection(year: str):
        """
        获取所有派单类型时间节点
        """
        res = PsTask.query.with_entities(PsTask.inspection_type).filter(
            year <= db.func.substring(PsTask.inspection_type, 3, 4), PsTask.is_pass == 'True').group_by(PsTask.inspection_type).order_by(
            PsTask.inspection_type.desc()).all()
        return res

    @staticmethod
    def addTask(task: PsTask):
        ps_task = PsTaskDao.queryTaskByTaskId(task.task_id)
        if ps_task:
            return ps_task.id

        db.session.add(task)
        db.session.commit()
        return task.id

    @staticmethod
    def updateTaskById(_id, update_data: dict):
        """
        _id: 任务id
        update_data: 更新内容
        """

        PsTask.query.filter(PsTask.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def getTaskJoinHistoryByTaskId(task_id: str) -> [(PsTask, PsTaskUploadHistory)]:
        """
        task: 系统ID
        """
        res = db.session.query(PsTask, PsTaskUploadHistory).join(
            PsTaskUploadHistory, PsTaskUploadHistory.task_id == PsTask.id).filter(
            PsTask.id == task_id
        ).all()
        return res


class PsTaskUploadHistoryDao:

    @staticmethod
    def queryTaskUploadHistoryById(_id: str) -> PsTaskUploadHistory:
        """
        :param _id: task ID
        :return:
        """
        res = PsTaskUploadHistory.query.filter(PsTaskUploadHistory.id == _id).one_or_none()
        return res

    @staticmethod
    def getTaskUploadHistoryByTaskId(task_id: str) -> [PsTaskUploadHistory]:
        """
        task_id：任务列表ID
        """
        res = PsTaskUploadHistory.query.filter(PsTaskUploadHistory.task_id == task_id).all()
        return res

    @staticmethod
    def addTaskUploadHistory(history: PsTaskUploadHistory):
        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        history.created_by_date = now_date

        db.session.add(history)
        db.session.commit()
        return history.id

    @staticmethod
    def updateTaskUploadHistoryById(_id, update_data: dict):
        PsTaskUploadHistory.query.filter(PsTaskUploadHistory.id == _id).update(update_data)
        db.session.commit()


class PsUserMappingDao:

    @staticmethod
    def queryUserMappingById(_id: str) -> PsUserMapping:
        """
        :param _id: task ID
        :return:
        """
        res = PsUserMapping.query.filter(PsUserMapping.technical_department_site_id == _id).one_or_none()
        return res


class PsCustomerArchivesDao:

    @staticmethod
    def queryCustomerArchivesById(_id: str) -> PsCustomerArchives:
        """
        _id: 系统ID
        """
        res = PsCustomerArchives.query.filter(PsCustomerArchives.id == _id).one_or_none()
        return res

    @staticmethod
    def queryCustomerArchivesByTaskId(_id: str, status: str) -> [PsCustomerArchives]:
        """
        :param _id: task ID
        :return:
        """
        res = PsCustomerArchives.query.filter(PsCustomerArchives.task_id == _id,
                                              PsCustomerArchives.status == status).all()
        return res

    @staticmethod
    def queryCustomerArchivesByTaskIdNotOrigin(_id: str) :
        """
        _id: task_id
        """
        res = PsCustomerArchives.query.filter(PsCustomerArchives.task_id == _id, PsCustomerArchives.status != 'origin').all()
        data = {}
        for customer in res:
            if customer.device_sn not in data:
                data[customer.device_sn] = customer

        return data

    @staticmethod
    def queryCustomerArchivesByTaskIdOrigin(_id: str) -> [PsCustomerArchives]:
        """
        _id: task_id
        """
        res = PsCustomerArchives.query.filter(PsCustomerArchives.task_id == _id, PsCustomerArchives.status == 'origin').all()

        return res

    @staticmethod
    def queryCustomerArchivesBySN(task_id: str, sn: str, status: str) -> PsCustomerArchives:
        """
        task_id: 上传文件记录id
        sn： 设备序列号
        status： 档案记录状态
        """

        res = PsCustomerArchives.query.filter(PsCustomerArchives.task_id == task_id, PsCustomerArchives.device_sn == sn,
                                              PsCustomerArchives.status == status).one_or_none()
        return res

    @staticmethod
    def queryCustomerArchivesByInspectionBySn(date_tag: str, sn_ids: list) -> [PsCustomerArchives]:
        """
        查询所属季度下对应SN的客户档案信息
        """
        if not date_tag or not sn_ids:
            return []

        res = PsCustomerArchives.query.filter(PsCustomerArchives.inspection_type == date_tag,
                                              PsCustomerArchives.device_sn.in_(sn_ids),
                                              PsCustomerArchives.status == 'edit').order_by(PsCustomerArchives.created_by_date.desc()).all()
        return res

    @staticmethod
    def queryCustomerArchivesBySnFirst(date_tag: str, sn_ids: list) -> PsCustomerArchives:
        """
        查询所属季度对应的设备信息的第一条数据
        """
        res = PsCustomerArchives.query.filter(PsCustomerArchives.inspection_type == date_tag,
                                              PsCustomerArchives.device_sn.in_(sn_ids),
                                              PsCustomerArchives.status == 'edit').order_by(
            PsCustomerArchives.created_by_date.desc()).first()
        return res

    @staticmethod
    def addCustomerArchives(customer: PsCustomerArchives):
        """
        写入客户档案
        """
        customer_archives = PsCustomerArchivesDao.queryCustomerArchivesBySN(customer.task_id, customer.device_sn,
                                                                            customer.status)
        if customer_archives:
            return customer_archives.id

        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        customer.created_by_date = now_date

        db.session.add(customer)
        db.session.commit()
        return customer.id

    @staticmethod
    def updateCustomerArchivesById(_id, update_data: dict):
        """
        更新数据
        """
        exist = PsCustomerArchivesDao.queryCustomerArchivesById(_id)
        if not exist or update_data['status'] == 'origin':
            return

        PsCustomerArchives.query.filter(PsCustomerArchives.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def getTaskJoinHistoryJoinCustomerByTaskId(task_id: str, status: str = '') -> [PsCustomerArchives]:
        """
        task_id: 任务列表系统ID
        """
        history_list = PsTaskDao.getTaskJoinHistoryByTaskId(task_id)

        data = []
        for history_dic in history_list:
            task, history = history_dic
            customer_origin = PsCustomerArchivesDao.queryCustomerArchivesByTaskIdOrigin(history.id)
            customer_list = PsCustomerArchivesDao.queryCustomerArchivesByTaskIdNotOrigin(history.id)
            for customer in customer_origin:
                if customer.device_sn in customer_list:
                    if status == 'all' or (status == 'edit' and customer_list[customer.device_sn].status == 'edit'):
                        data.append(customer_list[customer.device_sn])
                else:
                    if status == 'all':
                        data.append(customer)

        return data

    @staticmethod
    def queryCustomerArchivesByDeviceSN(sn: str) -> PsCustomerArchives:
        """
        sn 设备序列号获取设备历史记录信息中的部署区域信息
        """
        res = PsCustomerArchives.query.filter(
            PsCustomerArchives.device_sn == sn, PsCustomerArchives.is_publish == 'True',
            PsCustomerArchives.area != None
        ).first()
        return res

    @staticmethod
    def deleteCustomerArchivesByTaskId(task_id: str):
        """
        task_id 客户档案数据id
        删除数据
        """

        PsCustomerArchives.query.filter(PsCustomerArchives.status != 'origin',
                                        PsCustomerArchives.task_id == task_id).delete()
        db.session.commit()

