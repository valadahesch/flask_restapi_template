import copy
import json
import time

from flask import Blueprint, session, jsonify, current_app
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from datetime import datetime
from app.extensions import executor, message_gw, logger
from app.utils.func_util import prepare_args_for_parser, validate_half_hour
from app.enums.eco_partner_template import ECOPARTNER_TEMPLATE, getSeEcoTaskType
from app.utils.http_api.msg_template import SeEcoTaskEmail, SeEcoSubTaskEmail, SeEcoAllTaskArchiveEmail, \
    SeEcoRecordPendingEmail, SeEcoRecordApprovedEmail, SeEcoRecordUnApprovedEmail
from app.enums.permission_enum import p_list
from app.extensions import permission
from app.controllers.elasticsearch_service import ESService
from app.controllers.dao import SysUserDao, SeEcoTaskDao, DataScopeDao, SeEcoRecordDao, SysAttachmentDao, \
    SeEcoApprovalDao, TblEmployeeDao
from app.controllers.schema import SeEcoTaskSchema, SeEcoRecordSchema, SeEcoApprovalRecordSchema
from app.controllers.response import marsh_response, SeEcoTaskDetail, SeEcoTaskList, SeEcoTaskPartnerList, \
    SeEcoRecordList, SeEcoRecordApprovalList
from app.utils.api_util import Api, AppResponse, AppException

ecopartner_app = Blueprint('eco_partner', __name__, url_prefix='/api/presales/eco_partner')
ecopartner_api = Api(ecopartner_app)


post_task_parser = RequestParser()
post_task_parser.add_argument('subject', location='json', type=str, required=True)
post_task_parser.add_argument('owner_id', location='json', type=str)
post_task_parser.add_argument('partner_id', location='json', type=str, required=True)
post_task_parser.add_argument('partner_name', location='json', type=str, required=True)
post_task_parser.add_argument('partner_status', location='json', type=str)
post_task_parser.add_argument('partner_industry', location='json', type=str)
post_task_parser.add_argument('partner_contact', location='json', type=str)
post_task_parser.add_argument('partner_contact_info', location='json', type=str)
post_task_parser.add_argument('created_by_id', location='json', type=str)
post_task_parser.add_argument('manager_id', location='json', type=str, required=True, dest='channel_manager_id')
post_task_parser.add_argument('support_mode', location='json', type=str, choices=["On-site", "Remote"],  required=True)
post_task_parser.add_argument('support_type_1st', location='json', type=str, required=True)
post_task_parser.add_argument('support_type_2nd', location='json', type=str, required=True)
post_task_parser.add_argument('start_date', location='json', type=str, required=True)
post_task_parser.add_argument('end_date', location='json', type=str, required=True)
post_task_parser.add_argument('duration', location='json', type=validate_half_hour, required=True)


@ecopartner_api.resource('/task')
class TaskAPI(Resource):

    @permission.check([p_list['p_sework_eco_task_add'], p_list['p_sework_eco_task_assgin_add']])
    def post(self):
        """
        创建主任务
        :return:
        """
        parser_args = prepare_args_for_parser(post_task_parser.copy())
        params = parser_args.parse_args()

        if not params.get("created_by_id"):
            params['created_by_id'] = session['user_id']
        if not params.get("owner_id"):
            params['owner_id'] = session['user_id']
        params['last_modified_by_id'] = session['user_id']
        schema = SeEcoTaskSchema()
        task = schema.load(params)

        _id, task_number = SeEcoTaskDao.addTask(task)
        task_com = SeEcoTaskDao.getTaskJoinSysUserById(_id)
        if not task_com:
            raise AppException("查询失败，任务不存在")
        data = {"id": _id, "task_number": task_number}
        create_user, owner_user = task_com[1], task_com[2]
        for _ in range(3):
            time.sleep(0.3)
            res = ESService.querySeEcoTaskById(_id)
            if res:
                break

        def notice(**kwargs):
            try:
                message_gw.push(**kwargs)
            except Exception as e:
                logger.error("ProjectTask Create Exception: {}".format(str(e)))

        site_domain = current_app.config["SITE_DOMAIN"]
        template = SeEcoTaskEmail()
        template.update({
            "id": task.id, "task_number": task.task_number, "subject": task.subject,
            "site_domain": site_domain, "owner_name": owner_user.display_name,
            "created_by_name": create_user.display_name,
            "created_date": task.created_date.strftime('%Y-%m-%d %H:%M:%S')
        })
        executor.submit(notice, target=owner_user.email, template=template)

        return AppResponse(data)


post_subtask_parser = RequestParser()
post_subtask_parser.add_argument('subject', location='json', type=str, required=True)
post_subtask_parser.add_argument('owner_ids', location='json', type=list, required=True)
post_subtask_parser.add_argument('partner_contact', location='json', type=str)
post_subtask_parser.add_argument('partner_contact_info', location='json', type=str)
post_subtask_parser.add_argument('support_mode', location='json', type=str, choices=["On-site", "Remote"], required=True)
post_subtask_parser.add_argument('start_date', location='json', type=str, required=True)
post_subtask_parser.add_argument('end_date', location='json', type=str, required=True)
post_subtask_parser.add_argument('duration', location='json', type=validate_half_hour, required=True)


@ecopartner_api.resource('/task/<task_id>/sub_task')
class SubTaskAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    def post(self, task_id):
        """
        创建子任务
        :return:
        """
        parser_args = prepare_args_for_parser(post_subtask_parser.copy())
        params = parser_args.parse_args()

        data = {"list": []}

        parent_task = SeEcoTaskDao.queryTaskById(task_id)
        if not parent_task:
            raise AppException("操作失败，主任务不存在")
        params["parent_id"] = task_id
        params['created_by_id'] = session['user_id']
        params["partner_id"] = parent_task.partner_id
        params["partner_name"] = parent_task.partner_name
        params["partner_status"] = parent_task.partner_status
        params["partner_industry"] = parent_task.partner_industry
        params["support_type_1st"] = parent_task.support_type_1st
        params["support_type_2nd"] = parent_task.support_type_2nd
        params["channel_manager_id"] = parent_task.channel_manager_id
        params['last_modified_by_id'] = session['user_id']

        owner_list = params.pop("owner_ids")
        for owner_id in owner_list:
            params['owner_id'] = owner_id
            schema = SeEcoTaskSchema()
            task = schema.load(params)
            _id, task_number = SeEcoTaskDao.addTask(task)

            task_com = SeEcoTaskDao.getTaskJoinSysUserById(_id)
            if not task_com:
                raise AppException("查询失败，任务不存在")
            data["list"].append({"id": _id, "task_number": task_number})

            create_user, owner_user = task_com[1], task_com[2]
            for _ in range(3):
                time.sleep(0.3)
                res = ESService.querySeEcoSubTaskById(task_id, _id)
                if res:
                    break

            def notice(**kwargs):
                try:
                    message_gw.push(**kwargs)
                except Exception as e:
                    logger.error("ProjectTask Create Exception: {}".format(str(e)))

            site_domain = current_app.config["SITE_DOMAIN"]
            template = SeEcoSubTaskEmail()
            template.update({
                "id": task.id, "task_number": task.task_number, "subject": task.subject,
                "site_domain": site_domain, "owner_name": owner_user.display_name,
                "created_by_name": create_user.display_name,
                "created_date": task.created_date.strftime('%Y-%m-%d %H:%M:%S'),
                "parent_task_id": parent_task.id, "parent_task_number": parent_task.task_number,
                "parent_task_subject": parent_task.subject
            })
            executor.submit(notice, target=owner_user.email, template=template)

        if data["list"]:
            update_data = {
                "status": "InProgress",
                "last_modified_by_id": session['user_id']
            }
            SeEcoTaskDao.updateTaskById(task_id, update_data)

        return AppResponse(data)


@ecopartner_api.resource('/task/<task_id>')
class TaskIdAPI(Resource):

    @marsh_response(SeEcoTaskDetail)
    @permission.check(p_list['p_sework_eco_all'])
    def get(self, task_id):
        """
        任务详情
        :return:
        """
        user_id = session["user_id"]
        task_com = SeEcoTaskDao.getTaskJoinSysUserById(task_id)
        if not task_com:
            raise AppException("查询失败，任务不存在")

        task, create_user, owner_user, modified_user = task_com
        if not (user_id == create_user.id or user_id == owner_user.id):
            flag = False
            if not task.parent_id:
                sub_task_list = SeEcoTaskDao.queryTaskByParentId(task_id)
                if sub_task_list:
                    for sub_task in sub_task_list:
                        if sub_task.created_by_id == user_id or sub_task.owner_id == user_id:
                            flag = True
            if not flag:
                user_ids = DataScopeDao.getSysUserByRank(user_id, 'sework.internal:all')
                if not user_ids:
                    raise AppException("查询失败，没有权限")
                else:
                    if not (create_user.id in user_ids or owner_user.id in user_ids) and user_ids[0] != "*":
                        raise AppException("查询失败，没有权限")

        schema = SeEcoTaskSchema()
        data = schema.dump(task)
        data["created_by_name"] = create_user.display_name
        data["owner_name"] = owner_user.display_name
        data["last_modified_by_name"] = modified_user.display_name
        data["support_type_1st"] = getSeEcoTaskType(data["support_type_1st"])
        data["support_type_2nd"] = getSeEcoTaskType(data["support_type_2nd"])

        if task.parent_id:
            parent_task = SeEcoTaskDao.queryTaskById(task.parent_id)
            data["parent_task_number"] = parent_task.task_number

        if task.channel_manager_id:
            channel_user = SysUserDao.querySysUserById(task.channel_manager_id)
            if channel_user:
                data["channel_manager_name"] = channel_user.display_name

        return data

    @permission.check(p_list['p_sework_eco_all'])
    def delete(self, task_id):
        """
        任务删除
        :return:
        """
        task = SeEcoTaskDao.queryTaskById(task_id)
        if not task:
            raise AppException("删除失败，任务不存在")

        if not (task.status == "UnStart" and task.created_by_id == session['user_id']):
            raise AppException("删除失败，没有权限")

        delete_data = {
            "status": "Deleted",
            "deleted_by_id": session['user_id'],
            'last_modified_by_id': session['user_id']
        }
        SeEcoTaskDao.deleteTaskById(task_id, delete_data)

        for _ in range(3):
            time.sleep(0.3)
            res = ESService.querySeEcoTaskById(task_id)
            if res:
                if res.get("created_date"):
                    break

        ESService.deleteSeEcoTaskById(task_id)
        for _ in range(3):
            time.sleep(0.3)
            res = ESService.querySeWorkByProjectId(task_id)
            if not res:
                break

        return jsonify(AppResponse())


task_archive_parser = RequestParser()
task_archive_parser.add_argument('task_result', location='json', type=str, choices=["Complete", "Incomplete"], required=True)
task_archive_parser.add_argument('task_incomplete_reason', location='json', type=str)


@ecopartner_api.resource('/task/<task_id>/archive')
class TaskArchiveAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    def put(self, task_id):
        """
        任务归档
        :return:
        """
        parser_args = prepare_args_for_parser(task_archive_parser.copy())
        params = parser_args.parse_args()

        if params["task_result"] == "Incomplete" and not params.get("task_incomplete_reason"):
            raise AppException("归档失败，请填写未完成的原因")

        task = SeEcoTaskDao.queryTaskById(task_id)
        if not task:
            raise AppException("归档失败，任务不存在")

        pending_record_list = SeEcoRecordDao.queryRecordByStatus(task_id, "Pending")
        if pending_record_list:
            raise AppException(f"归档失败，存在未审批的日志")

        if not task.parent_id:
            undone_task_list = SeEcoTaskDao.queryUndoneTaskByParentId(task.id)
            if undone_task_list:
                undone_id = ','.join([undone_task.task_number for undone_task in undone_task_list])
                raise AppException(f"归档失败，任务{undone_id}未结束")

        else:
            # 子任务结束都结束通知子任务归档
            undone_task_list = SeEcoTaskDao.queryUndoneTaskByParentId(task.parent_id)
            if not undone_task_list:
                task_com = SeEcoTaskDao.getTaskJoinSysUserById(task.parent_id)
                if task_com:
                    main_task, owner_user = task_com[0], task_com[2]

                    def notice(**kwargs):
                        try:
                            message_gw.push(**kwargs)
                        except Exception as e:
                            logger.error("ProjectTask Create Exception: {}".format(str(e)))

                    site_domain = current_app.config["SITE_DOMAIN"]
                    template = SeEcoAllTaskArchiveEmail()
                    template.update({
                        "id": main_task.id, "task_number": main_task.task_number,
                        "subject": main_task.subject, "site_domain": site_domain
                    })
                    executor.submit(notice, target=owner_user.email, template=template)

        params['status'] = "Closed"
        params['last_modified_by_id'] = session['user_id']
        SeEcoTaskDao.updateTaskById(task_id, params)

        return jsonify(AppResponse())


tasks_parser = RequestParser()
tasks_parser.add_argument('partner_id', location='args', type=str)
tasks_parser.add_argument('query', location='args', type=str)
tasks_parser.add_argument('date_range[]', location='args', type=str, action='append', dest='date_range')
tasks_parser.add_argument('order_column', location='args', type=str, choices=["created_date", "last_modified_date"], default="created_date")
tasks_parser.add_argument('order_direct', location='args', type=str, choices=["asc", "desc"], default="desc")
tasks_parser.add_argument('update_date_range[]', location='args', type=str, action='append', dest='update_date_range')
tasks_parser.add_argument('owner_id[]', location='args', type=str, action='append', dest='owner_id')
tasks_parser.add_argument('created_by_id[]', location='args', type=str, action='append', dest='created_by_id')
tasks_parser.add_argument('status[]', location='args', type=str, action='append', dest='status')
tasks_parser.add_argument('participants[]', location='args', type=str, action='append', dest='participants')
tasks_parser.add_argument('page', location='args', type=int)
tasks_parser.add_argument('size', location='args', type=int)


@ecopartner_api.resource('/tasks')
class TasksAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    @marsh_response(SeEcoTaskList)
    def get(self):
        """
        查询任务列表
        :return:
        """
        parser_args = prepare_args_for_parser(tasks_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")), "size": int(params.get("size"))
        }

        user_id = session["user_id"]
        user_ids = DataScopeDao.getSysUserByRank(user_id, 'sework.internal:all')
        if not user_ids:
            return data

        for param_field in ["owner_id", "participants"]:
            if params.get(param_field):
                user_list = copy.copy(params.get(param_field))
                for _id in user_list:
                    if _id == "me":
                        params[param_field].remove("me")
                        params[param_field].append(user_id)
                    if _id == "my_subordinates":
                        params[param_field].remove("my_subordinates")
                        sysuser_list = DataScopeDao.getSubordinateIdById(user_id)
                        for sysuser in sysuser_list:
                            params[param_field].append(sysuser.id)

                params[param_field] = list(set(params.get(param_field)))

        total, es_res = ESService.querySeEcoPartnerByFilter(user_ids, **params)
        if es_res:
            for hit in es_res:
                main_task = hit["_source"]
                if main_task.get("deleted_date"):
                    continue

                sub_task_list = main_task["sub_tasks"]
                for sub_task in sub_task_list:
                    if ((sub_task.get("owner_id") not in user_ids and sub_task.get("created_by_id") not in user_ids) or
                            sub_task.get("deleted_date")):
                        continue
                    sub_task["support_type_1st"] = getSeEcoTaskType(sub_task["support_type_1st"])
                    sub_task["support_type_2nd"] = getSeEcoTaskType(sub_task["support_type_2nd"])
                    sub_task["created_date"] = datetime.strptime(
                        sub_task["created_date"], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
                    sub_task["last_modified_date"] = datetime.strptime(
                        sub_task["last_modified_date"], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
                    data["list"].append(sub_task)

                del main_task["sub_tasks"]
                main_task["support_type_1st"] = getSeEcoTaskType(main_task["support_type_1st"])
                main_task["support_type_2nd"] = getSeEcoTaskType(main_task["support_type_2nd"])
                main_task["created_date"] = datetime.strptime(
                    main_task["created_date"], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
                main_task["last_modified_date"] = datetime.strptime(
                    main_task["last_modified_date"], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
                data["list"].append(main_task)

        data["total"] = total
        return data


task_partners_parser = RequestParser()
task_partners_parser.add_argument('partner_name', location='args', type=str)
task_partners_parser.add_argument('page', location='args', type=int)
task_partners_parser.add_argument('size', location='args', type=int)


@ecopartner_api.resource('/tasks/partners')
class TasksPartnersAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    @marsh_response(SeEcoTaskPartnerList)
    def get(self):
        """
        所有任务的合作伙伴列表
        :return:
        """
        parser_args = prepare_args_for_parser(task_partners_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")), "size": int(params.get("size"))
        }

        user_id = session["user_id"]

        user_ids = DataScopeDao.getSysUserByRank(user_id, 'sework.internal:all')
        if not user_ids:
            return data

        total, partner_ids = SeEcoTaskDao.queryTaskPartnerByUserId(user_ids, **params)
        if partner_ids:
            partner_info = {}
            partner_ids = list(set([partner_id[0] for partner_id in partner_ids]))
            task_list = SeEcoTaskDao.queryTaskByPartnerIds(partner_ids)
            for task in task_list:
                if not task:
                    continue

                partner_id = task.partner_id
                created_date = task.created_date.strftime('%Y-%m-%d %H:%M:%S')
                last_modified_date = task.last_modified_date.strftime('%Y-%m-%d %H:%M:%S')
                if task.partner_id not in partner_info.keys():
                    info = {
                        "id": task.partner_id,
                        "partner_name": task.partner_name,
                        "first_support_date": created_date,
                        "last_support_date": last_modified_date,
                        "handing_number": 1 if task.status in ('UnStart', 'InProgress') else 0,
                        "all_number": 1 if task.status != 'Deleted' else 0,
                    }
                    partner_info[partner_id] = info

                else:
                    if partner_info.get(partner_id)["first_support_date"] > created_date:
                        partner_info[partner_id]["first_support_date"] = created_date
                    if partner_info.get(partner_id)["last_support_date"] < last_modified_date:
                        partner_info[partner_id]["last_support_date"] = last_modified_date
                    if task.status == 'InProgress':
                        partner_info[partner_id]["handing_number"] += 1
                    if task.status != 'Deleted':
                        partner_info[partner_id]["all_number"] += 1

            if partner_info.get("first_support_date"):
                partner_info["first_support_date"] = partner_info["first_support_date"].strftime('%Y-%m-%d %H:%M:%S')
            if partner_info.get("last_support_date"):
                partner_info["last_support_date"] = partner_info["last_support_date"].strftime('%Y-%m-%d %H:%M:%S')

            data["list"] = list(partner_info.values())
        data["total"] = total

        return data


@ecopartner_api.resource('/record/pending_approval')
class TaskPendingApprovalAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    @marsh_response(SeEcoRecordApprovalList)
    def get(self):
        """
        获取待审批日志列表
        :return:
        """

        user_id = session["user_id"]
        data = {"list": [], "total": 0, "page": 1, "size": 0}
        approval_rtc_list = SeEcoApprovalDao.getApprovalRecordByUserId(user_id)
        for approval_rtc in approval_rtc_list:
            approval, record, task, create_user = approval_rtc
            schema = SeEcoRecordSchema()
            record = schema.dump(record)

            record["record_content"] = json.loads(record["record_content"])
            record["created_by_name"] = create_user.display_name
            record["task_id"] = task.id
            record["task_number"] = task.task_number
            record["task_subject"] = task.subject
            record["attachments"] = []
            attachments = SysAttachmentDao.queryAttachmentByObjectId("se_eco_record", record["id"])
            for attachment in attachments:
                record["attachments"].append({
                    "id": attachment.id,
                    "filename": attachment.file_name,
                    "file_size": attachment.file_size,
                    "file_type": attachment.file_type
                })

            data["list"].append(record)

        return data


@ecopartner_api.resource('/task/support_type')
class TaskSupportTypeAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    def get(self):
        """
        任务支持项、支持方式列表
        :return:
        """
        data = {"list": ECOPARTNER_TEMPLATE}

        return jsonify(AppResponse(data))


page_permission_parser = RequestParser()
page_permission_parser.add_argument('task_id', location='args', type=str)


@ecopartner_api.resource('/permission/<page_title>')
class PagePermissionAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    def get(self, page_title):
        """
        任务详情，操作权限
        :return:
        """
        parser_args = prepare_args_for_parser(page_permission_parser.copy())
        params = parser_args.parse_args()

        data = {"list": []}
        if page_title == 'task_detail':
            if not params.get("task_id"):
                raise AppException("参数错误，任务ID不能为空")

            task = SeEcoTaskDao.queryTaskById(params['task_id'])
            if not task:
                raise AppException("获取失败，项目不存在")

            if task.owner_id == session['user_id'] and task.status in ("UnStart", "InProgress"):
                data["list"] = ["create_record", "task_archive"]

            if not task.parent_id and task.owner_id == session['user_id'] and task.status in ("UnStart", "InProgress"):
                data["list"] += ["create_sub_task"]

        return jsonify(AppResponse(data))


post_record_parser = RequestParser()
post_record_parser.add_argument('support_start_date', location='json', type=str, required=True)
post_record_parser.add_argument('support_end_date', location='json', type=str, required=True)
post_record_parser.add_argument('support_duration', location='json', type=validate_half_hour, required=True)
post_record_parser.add_argument('record_content', location='json', type=list, required=True)
post_record_parser.add_argument('attachments', location='json', type=list)
post_record_parser.add_argument('status', location='json', choices=["Draft", "Pending"], type=str, required=True)


@ecopartner_api.resource('/task/<task_id>/record')
class RecordAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    def post(self, task_id):
        """
        创建日志
        :return:
        """
        parser_args = prepare_args_for_parser(post_record_parser.copy())
        params = parser_args.parse_args()

        data = {"id": ""}
        params["task_id"] = task_id
        params["record_content"] = json.dumps(params["record_content"], ensure_ascii=False)
        params['created_by_id'] = session['user_id']
        params['last_modified_by_id'] = session['user_id']

        attachments = params.get("attachments")
        if 'attachments' in params.keys():
            params.pop('attachments')

        schema = SeEcoRecordSchema()
        record = schema.load(params)
        _id = SeEcoRecordDao.addRecord(record)
        if _id:
            data["id"] = _id
            if attachments:
                for attachment_id in attachments:
                    update_data = {"related_object_id": _id}
                    SysAttachmentDao.updateAttachmentById(attachment_id, update_data)

            update_data = {
                "status": "InProgress",
                "last_modified_by_id": session['user_id']
            }
            SeEcoTaskDao.updateTaskById(task_id, update_data)

            if params.get("status") == "Pending":
                task_com = SeEcoTaskDao.getTaskJoinSysUserById(record.task_id)
                if task_com:
                    task, create_user, owner_user = task_com[0], task_com[1], task_com[2]
                    task_subject = task.subject
                    partner_name = task.partner_name
                    main_task_id = task.parent_id if task.parent_id else task.id

                    if task.parent_id:
                        task_com = SeEcoTaskDao.getTaskJoinSysUserById(task.parent_id)
                        if task_com:
                            task, create_user, owner_user = task_com[0], task_com[1], task_com[2]

                    record_user = SysUserDao.querySysUserById(session['user_id'])
                    if not record_user:
                        return AppException("更新成功，邮件通知失败")

                    site_domain = current_app.config["SITE_DOMAIN"]
                    record_content = ""
                    record_content_load = json.loads(record.record_content)
                    for content in record_content_load:
                        if content.get("type") == "tip":
                            continue
                        record_content += f'{content.get("name")}: {content.get("content")}  <br/>'

                    target, cc, replay = [create_user.email], [], record_user.email
                    if task.created_by_id == session['user_id']:
                        update_data = {
                            "status": "Publish",
                            "published_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        SeEcoRecordDao.updateRecordById(_id, update_data)

                        channel_manager_name = ""
                        if task.channel_manager_id:
                            channel_user_employee = SysUserDao.getSysUserEmployeeById(task.channel_manager_id)
                            if channel_user_employee:
                                sys_user, employee = channel_user_employee[0], channel_user_employee[1]
                                channel_manager_name = sys_user.display_name
                                if employee:
                                    target.append(employee.email)
                                    leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                                    if leader_employee:
                                        cc.append(leader_employee.email)
                        if record_user.employee_id:
                            employee = TblEmployeeDao.queryEmployeeById(owner_user.employee_id)
                            if employee:
                                leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                                if leader_employee:
                                    cc.append(leader_employee.email)

                        record = SeEcoRecordDao.queryRecordById(_id)
                        template = SeEcoRecordApprovedEmail()
                        template.update({
                            "id": task.id, "task_number": task.task_number, "subject": task.subject,
                            "approver": create_user.display_name, "partner_name": task.partner_name,
                            "created_by_name": record_user.display_name, "site_domain": site_domain,
                            "support_type_2nd": getSeEcoTaskType(task.support_type_2nd)["name"],
                            "channel_manager_name": channel_manager_name,
                            "published_date": record.published_date.strftime('%Y-%m-%d %H:%M:%S'),
                            "support_start_date": record.support_start_date.strftime('%Y-%m-%d %H:%M:%S'),
                            "support_end_date": record.support_end_date.strftime('%Y-%m-%d %H:%M:%S'),
                            "support_duration": record.support_duration / 60,
                            "record_content": record_content
                        })

                    else:
                        approval_record = {
                            "record_id": _id,
                            "main_task_id": main_task_id
                        }
                        schema = SeEcoApprovalRecordSchema()
                        approval_record = schema.load(approval_record)
                        SeEcoApprovalDao.addRecord(approval_record)

                        template = SeEcoRecordPendingEmail()
                        template.update({
                            "task_number": task.task_number, "subject": task_subject,
                            "created_by_name": record_user.display_name, "partner_name": partner_name,
                            "site_domain": site_domain, "record_content": record_content,
                            "approver": create_user.display_name
                        })

                    def notice(**kwargs):
                        try:
                            message_gw.push(**kwargs)
                        except Exception as e:
                            logger.error("Record Pending Exception: {}".format(str(e)))
                    executor.submit(notice, target=target, template=template, reply_to=replay, cc=cc)

        return jsonify(AppResponse(data))


put_record_parser = RequestParser()
put_record_parser.add_argument('support_start_date', location='json', type=str)
put_record_parser.add_argument('support_end_date', location='json', type=str)
put_record_parser.add_argument('support_duration', location='json', type=validate_half_hour)
put_record_parser.add_argument('record_content', location='json', type=list)
put_record_parser.add_argument('attachments', location='json', type=list)
put_record_parser.add_argument('status', location='json', choices=["Draft", "Pending"], type=str)


@ecopartner_api.resource('/record/<record_id>')
class RecordIdAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    def put(self, record_id):
        """
        编辑日志(编辑草稿)
        :return:
        """
        parser_args = prepare_args_for_parser(put_record_parser.copy())
        params = parser_args.parse_args()

        if 'record_content' in params:
            params['record_content'] = json.dumps(params["record_content"], ensure_ascii=False)

        attachments = params.get("attachments")
        if 'attachments' in params.keys():
            params.pop('attachments')

        params['last_modified_by_id'] = session['user_id']
        SeEcoRecordDao.updateRecordById(record_id, params)
        if attachments:
            for attachment_id in attachments:
                update_data = {"related_object_id": record_id}
                SysAttachmentDao.updateAttachmentById(attachment_id, update_data)

        record = SeEcoRecordDao.queryRecordById(record_id)
        if params.get("status") == "Pending":
            task_com = SeEcoTaskDao.getTaskJoinSysUserById(record.task_id)
            if task_com:
                task, create_user, owner_user = task_com[0], task_com[1], task_com[2]
                task_subject = task.subject
                partner_name = task.partner_name
                main_task_id = task.parent_id if task.parent_id else task.id

                if task.parent_id:
                    task_com = SeEcoTaskDao.getTaskJoinSysUserById(task.parent_id)
                    if task_com:
                        task, create_user, owner_user = task_com[0], task_com[1], task_com[2]

                record_user = SysUserDao.querySysUserById(session['user_id'])
                if not record_user:
                    return AppException("更新成功，邮件通知失败")

                site_domain = current_app.config["SITE_DOMAIN"]
                record_content = ""
                record_content_load = json.loads(record.record_content)
                for content in record_content_load:
                    if content.get("type") == "tip":
                        continue
                    record_content += f'{content.get("name")}: {content.get("content")}  <br/>'

                target, cc, replay = [create_user.email], [], record_user.email
                if task.created_by_id == session['user_id']:
                    update_data = {
                        "status": "Publish",
                        "last_modified_by_id": session['user_id'],
                        "published_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    SeEcoRecordDao.updateRecordById(record_id, update_data)

                    channel_manager_name = ""
                    if task.channel_manager_id:
                        channel_user_employee = SysUserDao.getSysUserEmployeeById(task.channel_manager_id)
                        if channel_user_employee:
                            sys_user, employee = channel_user_employee[0], channel_user_employee[1]
                            channel_manager_name = sys_user.display_name
                            if employee:
                                target.append(employee.email)
                                leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                                if leader_employee:
                                    cc.append(leader_employee.email)
                    if record_user.employee_id:
                        employee = TblEmployeeDao.queryEmployeeById(owner_user.employee_id)
                        if employee:
                            leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                            if leader_employee:
                                cc.append(leader_employee.email)

                    template = SeEcoRecordApprovedEmail()
                    template.update({
                        "id": task.id, "task_number": task.task_number, "subject": task.subject,
                        "approver": create_user.display_name, "partner_name": task.partner_name,
                        "created_by_name": record_user.display_name, "site_domain": site_domain,
                        "support_type_2nd": getSeEcoTaskType(task.support_type_2nd)["name"],
                        "channel_manager_name": channel_manager_name,
                        "published_date": record.published_date.strftime('%Y-%m-%d %H:%M:%S'),
                        "support_start_date": record.support_start_date.strftime('%Y-%m-%d %H:%M:%S'),
                        "support_end_date": record.support_end_date.strftime('%Y-%m-%d %H:%M:%S'),
                        "support_duration": record.support_duration / 60,
                        "record_content": record_content
                    })

                else:
                    approval_record = {
                        "record_id": record_id,
                        "main_task_id": main_task_id
                    }
                    schema = SeEcoApprovalRecordSchema()
                    approval_record = schema.load(approval_record)
                    SeEcoApprovalDao.addRecord(approval_record)

                    template = SeEcoRecordPendingEmail()
                    template.update({
                        "task_number": task.task_number, "subject": task_subject,
                        "created_by_name": record_user.display_name, "partner_name": partner_name,
                        "site_domain": site_domain, "record_content": record_content,
                        "approver": create_user.display_name
                    })

                def notice(**kwargs):
                    try:
                        message_gw.push(**kwargs)
                    except Exception as e:
                        logger.error("Record Pending Exception: {}".format(str(e)))
                executor.submit(notice, target=target, template=template, cc=cc, reply_to=replay)

        return jsonify(AppResponse())

    @permission.check(p_list['p_sework_eco_all'])
    def delete(self, record_id):
        """
        删除日志
        :return:
        """
        delete_data = {"deleted_by_id": session['user_id'], 'last_modified_by_id': session['user_id']}
        SeEcoRecordDao.deleteRecordById(record_id, delete_data)

        return jsonify(AppResponse())


get_record_parser = RequestParser()
get_record_parser.add_argument('status', location='args', type=str, choices=["Draft", "Publish", "Pending"], required=True)


@ecopartner_api.resource('/task/<task_id>/record/list')
class RecordListAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    @marsh_response(SeEcoRecordList)
    def get(self, task_id):
        """
        查看任务日志列表
        :return:
        """
        parser_args = prepare_args_for_parser(get_record_parser.copy())
        params = parser_args.parse_args()

        data = {"list": [], "total": 0, "page": 1, "size": 0}

        task_com = SeEcoTaskDao.getTaskJoinSysUserById(task_id)
        if not task_com:
            raise AppException("查询失败，任务不存在")
        task, create_user, owner_user, modified_user = task_com

        user_id = session["user_id"]
        if params["status"] == "Draft" and task.owner_id != user_id:
            return data

        if not (user_id == create_user.id or user_id == owner_user.id):
            flag = False
            if not task.parent_id:
                sub_task_list = SeEcoTaskDao.queryTaskByParentId(task_id)
                if sub_task_list:
                    for sub_task in sub_task_list:
                        if sub_task.created_by_id == user_id or sub_task.owner_id == user_id:
                            flag = True
            if not flag:
                user_ids = DataScopeDao.getSysUserByRank(user_id, 'sework.internal:all')
                if not user_ids:
                    raise AppException("查询失败，没有权限")
                else:
                    if not (create_user.id in user_ids or owner_user.id in user_ids) and user_ids[0] != "*":
                        raise AppException("查询失败，没有权限")

        approval_id = create_user.id
        approval_name = create_user.display_name
        if not task.parent_id:
            main_task_com = SeEcoTaskDao.getTaskJoinSysUserById(task.parent_id)
            if main_task_com:
                create_user = task_com[1]
                approval_id = create_user.id
                approval_name = create_user.display_name

        record_create_list = SeEcoRecordDao.getRecordJoinSysUserByStatus(task_id, params["status"])
        if not record_create_list:
            return data

        for record_c in record_create_list:
            record, create_user = record_c
            schema = SeEcoRecordSchema()
            record = schema.dump(record)

            record["approval_id"] = approval_id
            record["approval_name"] = approval_name
            record["record_content"] = json.loads(record["record_content"])
            record["created_by_name"] = create_user.display_name
            record["attachments"] = []
            attachments = SysAttachmentDao.queryAttachmentByObjectId("se_eco_record", record["id"])
            for attachment in attachments:
                record["attachments"].append({
                    "id": attachment.id,
                    "filename": attachment.file_name,
                    "file_size": attachment.file_size,
                    "file_type": attachment.file_type
                })
            data["list"].append(record)

        data["total"] = len(record_create_list)
        data["size"] = len(record_create_list)

        return data


approval_record_parser = RequestParser()
approval_record_parser.add_argument('approval', location='json', choices=[1, 2], type=int, required=True)
approval_record_parser.add_argument('unapproval_reason', location='json', type=str)


@ecopartner_api.resource('/record/<record_id>/approval')
class RecordApprovalAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    def put(self, record_id):
        """
        日志审批，审批通过设置为发布状态
        :return:
        """
        parser_args = prepare_args_for_parser(approval_record_parser.copy())
        params = parser_args.parse_args()

        if params["approval"] == 2 and not params.get("unapproval_reason"):
            raise AppException("操作失败，请填写原因")

        approval_record = SeEcoApprovalDao.queryApprovalRecordByRecordId(record_id)
        update_data = {
            "result": params["approval"],
            "incomplete_reason": params.get("unapproval_reason")
        }
        SeEcoApprovalDao.updateApprovalById(approval_record.id, update_data)

        update_data = {
            "status": "Publish" if params.get("approval") == 1 else "Draft",
            "unapproval_reason": params.get("unapproval_reason"),
            "last_modified_by_id": session['user_id'],
            "published_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        SeEcoRecordDao.updateRecordById(record_id, update_data)

        record = SeEcoRecordDao.queryRecordById(record_id)
        task_com = SeEcoTaskDao.getTaskJoinSysUserById(record.task_id)
        if task_com:
            task, create_user, owner_user = task_com[0], task_com[1], task_com[2]
            if task.parent_id:
                task_com = SeEcoTaskDao.getTaskJoinSysUserById(task.parent_id)
                if task_com:
                    create_user = task_com[1]

            record_user = SysUserDao.querySysUserById(record.created_by_id)
            if not record:
                return AppException("审批成功，邮件通知失败")

            site_domain = current_app.config["SITE_DOMAIN"]
            record_content = ""
            record_content_load = json.loads(record.record_content)
            for content in record_content_load:
                if content.get("type") == "tip":
                    continue
                record_content += f'{content.get("name")}: {content.get("content")}  <br/>'

            target, cc, replay = [record_user.email], [], ""
            if params["approval"] == 1:
                target.append(create_user.email)
                replay = record_user.email
                channel_manager_name = ""
                if task.channel_manager_id:
                    channel_user_employee = SysUserDao.getSysUserEmployeeById(task.channel_manager_id)
                    if channel_user_employee:
                        sys_user, employee = channel_user_employee[0], channel_user_employee[1]
                        channel_manager_name = sys_user.display_name
                        if employee:
                            target.append(employee.email)
                            leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                            if leader_employee:
                                cc.append(leader_employee.email)
                if record_user.employee_id:
                    employee = TblEmployeeDao.queryEmployeeById(owner_user.employee_id)
                    if employee:
                        leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                        if leader_employee:
                            cc.append(leader_employee.email)

                template = SeEcoRecordApprovedEmail()
                template.update({
                    "id": task.id, "task_number": task.task_number, "subject": task.subject,
                    "approver": create_user.display_name, "partner_name": task.partner_name,
                    "created_by_name": record_user.display_name, "site_domain": site_domain,
                    "support_type_2nd": getSeEcoTaskType(task.support_type_2nd)["name"],
                    "channel_manager_name": channel_manager_name,
                    "published_date": record.published_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_start_date": record.support_start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_end_date": record.support_end_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_duration": record.support_duration / 60,
                    "record_content": record_content
                })

            else:
                replay = create_user.email
                template = SeEcoRecordUnApprovedEmail()
                template.update({
                    "id": task.id, "task_number": task.task_number, "subject": task.subject,
                    "approver": create_user.display_name, "reject_reason": params.get("unapproval_reason"),
                    "site_domain": site_domain, "record_content": record_content
                })
                cc.append(create_user.email)

            def notice(**kwargs):
                try:
                    message_gw.push(**kwargs)
                except Exception as e:
                    logger.error("ProjectTask Create Exception: {}".format(str(e)))
            executor.submit(notice, target=target, template=template, cc=cc, reply_to=replay)

        return jsonify(AppResponse())
