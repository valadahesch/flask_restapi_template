import json

from app.models import db
from app.enums.html_tag_enum import *
from app.controllers.dao import OperateHistoryDao
from app.controllers.schema import OperateHistorySchema
from datetime import datetime
from app.extensions import executor
from flask import request, session


class OperateService:

    def __init__(self, target, target_id, params=None, create_by_id=None):
        self.target = target
        self.target_id = target_id
        self.params_data = params
        self.action = request.method.lower()
        if params:
            self.params_data = json.dumps(params, ensure_ascii=False)
        if create_by_id:
            self.create_by_id = create_by_id
        elif session.get("user_id"):
            self.create_by_id = session["user_id"]
        else:
            self.create_by_id = 0

    def recordLog(self, log):
        db_app = db.get_app()

        def record():
            operate_log = {
                "action": self.action,
                "log": log,
                "created_by_id": self.create_by_id,
                "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "target": self.target,
                "target_id": self.target_id,
                "params_data": self.params_data
            }
            with db_app.app_context():
                schema = OperateHistorySchema()
                operate_history = schema.load(operate_log)
                OperateHistoryDao.addOperateHistory(operate_history)

        executor.submit(record)


class SeProjectOS(OperateService):

    def __init__(self, target_id, params=None, create_by_id=None):
        target = 'se_project_project'
        super().__init__(target, target_id, params, create_by_id)

    def logProjectCreate(
            self, project_id, project_number, project_subject,
            task_id, task_number, task_subject,
            assign_user, assign_user_name
    ):
        """
        创建并分派项目
        :return:
        """
        project = SeProjectHT(project_id, project_number, project_subject)
        task = SeProjectTaskHT(task_id, task_number, task_subject)
        user = UserInfoHT(assign_user, assign_user_name)

        log = f'创建了项目 {project} 并分派主任务 {task} 给 {user} 。'
        self.recordLog(log)

    def logProjectConfirm(self, project_id, project_number, project_subject):
        """
        确认项目
        :return:
        """
        project = SeProjectHT(project_id, project_number, project_subject)

        log = f'确认了项目 {project} 。'
        self.recordLog(log)

    def logProjectReturn(self, project_id, project_number, project_subject, task_list):
        """
        项目和任务的退
        :return:
        """
        project = SeProjectHT(project_id, project_number, project_subject)

        tasks = []
        for task in task_list:
            tasks.append(str(SeProjectTaskHT(task.get("id"), task.get("task_number"), task.get("subject"))))

        log = f'将项目 {project} 退回，并删除了 {",".join(tasks)} 任务。'
        self.recordLog(log)

    def logProjectAssign(
            self, project_id, project_number, project_subject,
            old_user_id, old_user_name,
            new_user_id, new_user_name,
    ):
        """
        重新指派项目负责人
        :return:
        """
        project = SeProjectHT(project_id, project_number, project_subject)
        old_user = UserInfoHT(old_user_id, old_user_name)
        new_user = UserInfoHT(new_user_id, new_user_name)

        log = f'将项目 {project} 负责人从 {old_user} 变更为 {new_user}。'
        self.recordLog(log)

    def logProjectArchive(self, project_id, project_number, project_subject, project_result):
        """
        项目归档
        :return:
        """
        project = SeProjectHT(project_id, project_number, project_subject)

        log = f'将项目 {project} 归档，项目结果：{project_result} 。'
        self.recordLog(log)

    def logProjectEdit(self, project_id, project_number, project_subject):
        """
        编辑项目
        :return:
        """
        project = SeProjectHT(project_id, project_number, project_subject)

        log = f'编辑了项目 {project}'
        self.recordLog(log)

    def logProjectCombine(
            self, src_project_id, src_project_number, src_project_subject,
            dst_project_id, dst_project_number, dst_project_subject
    ):
        """
        项目合并
        :return:
        """
        src_project = SeProjectHT(src_project_id, src_project_number, src_project_subject)
        dst_project = SeProjectHT(dst_project_id, dst_project_number, dst_project_subject)

        log = f'将项目 {src_project} 合并到 {dst_project} 。'
        self.recordLog(log)

    def logSubTaskCreate(self, task_id, task_number, task_subject, assign_user, assign_user_name):
        """
        创建子任务
        :return:
        """
        task = SeProjectTaskHT(task_id, task_number, task_subject)
        user = UserInfoHT(assign_user, assign_user_name)

        log = f'创建了子任务 {task} 分派给 {user} 。'
        self.recordLog(log)

    def logTaskEnable(self, task_id, task_number, task_subject):
        """
        任务确认
        :return:
        """
        task = SeProjectTaskHT(task_id, task_number, task_subject)

        log = f'确认了任务 {task} 。'
        self.recordLog(log)

    def logTaskDelete(self, task_id, task_number, task_subject):
        """
        任务删除
        :return:
        """
        task = SeProjectTaskHT(task_id, task_number, task_subject)

        log = f'删除了任务 {task} 。'
        self.recordLog(log)

    def logTaskReturn(self, task_id, task_number, task_subject):
        """
        主任务退回
        :return:
        """
        task = SeProjectTaskHT(task_id, task_number, task_subject)

        log = f'将主任务 {task} 退回。'
        self.recordLog(log)

    def logTaskArchiveSubmit(self, task_id, task_number, task_subject, approval_userid, approval_name):
        """
        任务归档提交
        :return:
        """
        task = SeProjectTaskHT(task_id, task_number, task_subject)
        approval = UserInfoHT(approval_userid, approval_name)

        log = f'提交了任务 {task} 归档申请，等待 {approval} 审批。'
        self.recordLog(log)

    def logTaskArchiveAuto(self, task_id, task_number, task_subject):
        """
        任务归档提交并自动审批通过
        :return:
        """
        task = SeProjectTaskHT(task_id, task_number, task_subject)

        log = f'提交了任务 {task} 归档申请，并自动审批通过。'
        self.recordLog(log)

    def logTaskArchiveApprove(self, task_id, task_number, task_subject, approval_result):
        """
        任务归档审批
        :return:
        """
        task = SeProjectTaskHT(task_id, task_number, task_subject)

        log = f'审批了任务 {task} 的归档申请，审批结果： {approval_result} 。'
        self.recordLog(log)

    def logRecordCreate(self, record_id):
        """
        创建日志
        :return:
        """
        record = SeProjectRecordHT(record_id)

        log = f'创建了日志 {record} 。'
        self.recordLog(log)

    def logRecordSubmit(self, record_id, approval_userid, approval_name):
        """
        提交日志
        :return:
        """
        record = SeProjectRecordHT(record_id)
        approval = UserInfoHT(approval_userid, approval_name)

        log = f'提交了日志 {record} ，等待 {approval} 审批。'
        self.recordLog(log)

    def logRecordPublish(self, record_id):
        """
        发布日志
        :return:
        """
        record = SeProjectRecordHT(record_id)

        log = f'发布了日志 {record} 。'
        self.recordLog(log)

    def logRecordApproval(self, record_id):
        """
        审批日志通过
        :return:
        """
        record = SeProjectRecordHT(record_id)

        log = f'审批日志 {record} 通过。'
        self.recordLog(log)

    def logRecordUnApproval(self, record_id, reason):
        """
        审批日志不通过
        :return:
        """
        task = SeProjectRecordHT(record_id)

        log = f'审批日志 {task} 不通过，原因：{reason} 。'
        self.recordLog(log)

    def logRecordReturn(self, record_id):
        """
        日志撤回
        :return:
        """
        record = SeProjectRecordHT(record_id)

        log = f'将日志 {record} 撤回。'
        self.recordLog(log)
