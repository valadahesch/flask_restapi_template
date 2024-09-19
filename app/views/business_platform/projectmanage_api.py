import copy
import json
import re
import time

from datetime import datetime
from flask import Blueprint, session, jsonify, current_app, request
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.controllers.response.se_project_response import UserTaskListAPIResponse
from app.enums.se_project_template import SEPROJECT_TEMPLATE, getSeProjectProjectType
from app.extensions import permission, message_gw, executor, logger, apollo_util
from app.enums.permission_enum import p_list
from app.utils.func_util import prepare_args_for_parser, validate_null, validate_half_hour, str_to_none, getNearestDatetime, \
    getNearestDatetimeAsia
from app.controllers import ESService
from app.controllers.service import SeProjectOS
from app.utils.http_api.msg_template import SeProjectProjectFirstEmail, SeProjectTaskSecondEmail, \
    SeProjectSubTaskEmail, SeProjectRecordPendingEmail, SeProjectRecordApprovedEmail, SeProjectRecordUnApprovedEmail, \
    SeProjectTaskArchiveEmail, SeProjectProjectArchiveEmail, SeProjectTaskApprovedEmail, \
    SeProjectTaskApprovedArchiveEmail, SeProjectTaskUnApprovedArchiveEmail, SeProjectRecordReturnEmail, \
    SeProjectTaskDispatchFailedEmail, SeProjectRecordApprovedDICAPP
from app.controllers.dao import SeProjectProjectDao, SeProjectTaskDao, SeProjectRecordDao, DataScopeDao, \
    SysAttachmentDao, SysUserDao, TblEmployeeDao, SeProjectApprovalDao, SeProjectFocusDao, CrmViewsDao, SysRoleUserDao, \
    OperateHistoryDao
from app.controllers.schema import SeProjectProjectSchema, SeProjectTaskSchema, SeProjectRecordSchema, \
    SeProjectApprovalRecordSchema, SeProjectFocusSchema, OperateHistorySchema
from app.controllers.response import marsh_response, SeProjectProjectDetail, SeProjectTaskDetail, SeProjectRecordList, \
    SeProjectTaskList, SeProjectProjectList, SeProjectParticipantList, SeProjectTaskApprovalList, SeProjectRecord, \
    SeSubProjectProjectDetailList, SeProjectRecordMineList, SeProjectOperateHistoryList
from app.utils.api_util import Api, AppResponse, AppException
from app.enums.se_project_enum import enums as project_enums

projectmanage_app = Blueprint('projectmanage', __name__, url_prefix='/api/presales/project_manage')
projectmanage_api = Api(projectmanage_app)

post_project_parser = RequestParser()
post_project_parser.add_argument('subject', location='json', type=str)
post_project_parser.add_argument('new_name', location='json', type=str)
post_project_parser.add_argument('new_type', location='json', type=str)
post_project_parser.add_argument('new_apply_for_key_customer_support', location='json', type=str)
post_project_parser.add_argument('new_opportunity_code', location='json', type=str)
post_project_parser.add_argument('new_opportunity_id', location='json', type=str)
post_project_parser.add_argument('opportunityratingcode', location='json', type=str)
post_project_parser.add_argument('new_account_name', location='json', type=str)
post_project_parser.add_argument('new_contact_id', location='json', type=str)
post_project_parser.add_argument('new_accountcontactnumber', location='json', type=str)
post_project_parser.add_argument('new_projectproducttioncause', location='json', type=str)
post_project_parser.add_argument('new_is_letter', location='json', type=str)
post_project_parser.add_argument('new_placeorderforecast', location='json', type=str)
post_project_parser.add_argument('new_business_stage', location='json', type=str)
post_project_parser.add_argument('new_predictenddate', location='json', type=str)
post_project_parser.add_argument('new_actualvalue', location='json', type=float)
post_project_parser.add_argument('new_salesengineer', location='json', type=str)
post_project_parser.add_argument('quotedetailproductlist', location='json', type=list)
post_project_parser.add_argument('saleemail', location='json', type=str)
post_project_parser.add_argument('topsaleemail', location='json', type=str)
post_project_parser.add_argument('semail', location='json', type=str)
post_project_parser.add_argument('linename', location='json', type=str, dest='assign_number')


@projectmanage_api.resource('/crm_async')
class ProjectAPI(Resource):

    def post(self):
        """
        接受CRM推送数据：创建项目、主任务
        :return:
        """
        parser_args = prepare_args_for_parser(post_project_parser.copy())
        params = parser_args.parse_args()
        logger.info(f'received crm se request:{request.json}')
        owner = SysUserDao.querySysUserByEmail(params["new_salesengineer"])
        create_user = SysUserDao.querySysUserByEmail(params['semail'])
        sale_user = SysUserDao.querySysUserByEmail(params['saleemail'])
        top_sale_user = SysUserDao.querySysUserByEmail(params['topsaleemail'])
        account = CrmViewsDao.queryAccountByName(params['new_account_name'])

        template = None
        account_id = ''
        if account:
            account_id = account[1] if account[1] else account[0].lower()

        def notice(**kwargs):
            try:
                message_gw.push(**kwargs)
            except Exception as e:
                logger.error("ProjectTask Create Exception: {}".format(str(e)))

        project = SeProjectProjectDao.queryProjectByOpportunityNumber(params['new_opportunity_code'])
        if not project:
            """
            商机项目不存在创建项目与主任务
            """
            project_owner = owner
            project_info = {
                'project_type': '商机管理',
                'opportunity_number': params['new_opportunity_code'],
                'opportunity_name': params['new_opportunity_id'],
                'subject': params['new_opportunity_id'],
                'created_by_id': create_user.id if create_user is not None else "",
                'sale_by_id': sale_user.id if sale_user is not None else "",
                'owner_id': owner.id if owner is not None else "",
                'account_id': account_id,
                'account_name': params['new_account_name'],
                'contact_name': params['new_contact_id'],
                'contact_info': params['new_accountcontactnumber'],
                'opportunity_value': params['new_actualvalue'],
                'customer_requirement': params['new_projectproducttioncause'],
                'last_modified_by_id': create_user.id if create_user is not None else "",
                'crm_raw_data': json.dumps(request.json),
                'application_type': params['new_type'],
                'is_big_project_support': params['new_apply_for_key_customer_support'],
                'opportunity_level': params['opportunityratingcode'],
                'is_itai_project': params['new_is_letter'],
                'order_prediction': params['new_placeorderforecast'],
                'expected_order_completion_date': params['new_predictenddate'],
                'sales_leader_id': top_sale_user.id if top_sale_user is not None else "",
                "business_stage": params["new_business_stage"]
            }

            schema = SeProjectProjectSchema()
            project = schema.load(project_info)
            _id, _ = SeProjectProjectDao.addProject(project)

            template = SeProjectProjectFirstEmail()
            template.update({
                "project_id": project.id, "project_number": project.opportunity_number, "subject": project.subject,
                "owner_name": owner.display_name if owner is not None else "",
                "created_by_name": create_user.display_name if create_user is not None else "",
                "created_date": project.created_date.strftime('%Y-%m-%d %H:%M:%S')
            })

            project = SeProjectProjectDao.queryProjectByOpportunityNumber(params['new_opportunity_code'])
            for _ in range(3):
                time.sleep(0.5)
                res = ESService.querySeProjectByProjectId(project.id)
                if res:
                    break

        else:
            project_owner = SysUserDao.querySysUserById(project.owner_id)
            update_data = {
                'sale_by_id': sale_user.id if sale_user is not None else "",
                'sales_leader_id': top_sale_user.id if top_sale_user is not None else "",
                'deleted_by_id': None, 'deleted_date': None,
                'business_stage': params["new_business_stage"]
            }
            if project.status != 4:
                SeProjectProjectDao.updateProjectById(project.id, update_data)

        if project.status in [3, 4]:
            reason = ''
            if project.status == 3:
                reason = "项目已完成不允许分派"
                logger.info(f'ProjectAPI new_opportunity_code:{params["new_opportunity_code"]}, 项目已完成不允许再分配')
            elif project.status == 4:
                reason = "项目已删除不允许再分派"
                logger.info(f'ProjectAPI new_opportunity_code:{params["new_opportunity_code"]}, 项目已删除不允许再分配')

            target = []
            if owner:
                target.append(owner.email)
            if create_user:
                target.append(create_user.email)
            if target:
                template = SeProjectTaskDispatchFailedEmail()
                template.update({
                    "line_name": params.get("assign_number") if params.get("assign_number") else params['new_name'],
                    "reason": reason
                })
                executor.submit(notice, target=target, template=template)

            raise AppException(f"创建任务失败，{reason}")

        task_info = {
            'event_number': params['new_name'],
            'subject': params['subject'],
            'created_by_id': create_user.id if create_user is not None else "",
            'owner_id': owner.id if owner is not None else "",
            'status': 4,
            'account_id': account_id.lower(),
            'account_name': params['new_account_name'],
            'contact_name': params['new_contact_id'],
            'contact_info': params['new_accountcontactnumber'],
            'last_modified_by_id': create_user.id if create_user is not None else "",
            'project_id': project.id,
            'crm_raw_data': json.dumps(request.json),
            "assign_number": params.get("assign_number")
        }
        if project.status == 5 and project.parent_project:
            task_info["project_id"] = project.parent_project

        main_event_task = SeProjectTaskDao.queryMainEventTaskByTaskEventNumber(params['new_name'])
        if main_event_task:
            if main_event_task.status != 1:
                logger.info(f'ProjectAPI event_number:{params["new_name"]}, 只允许进行中任务再次分派')

                target = []
                if owner:
                    target.append(owner.email)
                if create_user:
                    target.append(create_user.email)

                if target:
                    template = SeProjectTaskDispatchFailedEmail()
                    template.update({
                        "line_name": params.get("assign_number") if params.get("assign_number") else params['new_name'],
                        "reason": "只允许进行中任务再分配"
                    })
                    executor.submit(notice, target=target, template=template)
                raise AppException("创建任务失败，只允许进行中任务再分配")

            line_task = SeProjectTaskDao.queryTaskByTaskLineName(params['assign_number'])
            if not line_task:
                # 创建子任务
                task_info["parent_id"] = main_event_task.id
                task_info["support_type_1st"] = main_event_task.support_type_1st
                task_info["support_type_2nd"] = main_event_task.support_type_2nd
                task_info["contact_position"] = main_event_task.contact_position

            else:
                # 任务已存在
                logger.info(f'ProjectAPI event_number:{params["new_name"]}, 工单已存在')
                raise AppException("创建任务失败，该工单已存在")

        schema = SeProjectTaskSchema()
        task = schema.load(task_info)
        _id, task_number = SeProjectTaskDao.addTask(task)
        data = {"id": _id, "task_number": task_number}

        if not template:
            template = SeProjectTaskSecondEmail()
            template.update({
                "project_id": project.id, "project_number": project.opportunity_number,
                "task_id": task.id, "task_number": params.get('new_name'),
                "subject": project.subject, "task_subject": task.subject,
                "owner_name": project_owner.display_name if project_owner is not None else "",
                "task_owner_name": owner.display_name if owner is not None else "",
                "created_by_name": create_user.display_name if create_user is not None else "",
                "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

        cc = [create_user.email]
        if owner:
            directly_leader_list = SysUserDao.getDirectlyLeaderByUserId(owner.id)
            for directly_leader in directly_leader_list:
                cc.append(directly_leader.email)

        executor.submit(notice, target=owner.email, template=template, cc=cc)

        SeProjectOS(project.id, params, create_user.id).logProjectCreate(
            project.id, project.opportunity_number, project.subject,
            task.id, params.get('new_name'), task.subject,
            owner.id, owner.display_name
        )
        return AppResponse(data)


get_project_parser = RequestParser()
get_project_parser.add_argument('query', location='args', type=str)
get_project_parser.add_argument('date_range[]', location='args', type=str, action='append', dest='date_range')
get_project_parser.add_argument('order_column', location='args', type=str, choices=["created_date", "last_modified_date", "last_record_created_date",
                                                                                    "last_record_support_start_date"], default="created_date")
get_project_parser.add_argument('order_direct', location='args', type=str, choices=["asc", "desc"], default="desc")
get_project_parser.add_argument('update_date_range[]', location='args', type=str, action='append', dest='update_date_range')
get_project_parser.add_argument('owner_id[]', location='args', type=str, action='append', dest='owner_id')
get_project_parser.add_argument('created_by_id[]', location='args', type=str, action='append', dest='created_by_id')
get_project_parser.add_argument('status[]', location='args', type=int, action='append', dest='status')
get_project_parser.add_argument('participants[]', location='args', type=str, action='append', dest='participants')
get_project_parser.add_argument('task_result[]', location='args', type=str, action='append', dest='task_result')
get_project_parser.add_argument('classification', location='args', type=str)
get_project_parser.add_argument('page', location='args', type=int, default=1)
get_project_parser.add_argument('size', location='args', type=int, default=1000)
get_project_parser.add_argument('last_record_created_date_range[]', location='args', type=str, action='append', dest='last_record_created_date_range')
get_project_parser.add_argument('last_record_support_start_date_range[]', location='args', type=str, action='append', dest='last_record_support_start_date_range')


@projectmanage_api.resource('/project')
class ProjectListAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectProjectList)
    def get(self):
        """
        查询所有项目列表，字段排序，筛选（责任人、参与人；我的，下属，具体用户名，关键词（所有字段）搜索，分页
        :return:
        ES数据库调整，权限标识调整
        """
        parser_args = prepare_args_for_parser(get_project_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")), "size": int(params.get("size"))
        }
        user_id = session["user_id"]
        params['user_id'] = user_id

        permission_mark = p_list['p_se_project_manage_list']
        if params.get("classification") == "support":
            permission_mark = p_list['p_se_project_manage_support']
        user_ids = DataScopeDao.getSysUserByRank(user_id, permission_mark)
        if not user_ids:
            return data

        for param_field in ["owner_id", "created_by_id", "participants"]:
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

        if params.get("owner_id") and not params.get("query") and not params.get("participants"):
            if params["owner_id"][0] == user_id and len(params.get("owner_id")) == 1:
                project_ids, participants_map = [], {}
                task_co_list = SeProjectTaskDao.queryTaskJoinSysUserByUserIds(user_ids)
                for task_co in task_co_list:
                    task, create_user, owner_user = task_co
                    project_ids.append(task.project_id)
                    participant = {"id": task.owner_id, "display_name": owner_user.display_name}
                    if task.project_id in participants_map and participant not in participants_map.get(task.project_id):
                        participants_map[task.project_id].append(participant)
                    else:
                        participants_map[task.project_id] = [participant]

        if params.get("classification") == 'favor' or params.get("classification") == 'all':
            focus_list = SeProjectFocusDao.queryDoFocusByUserId(user_id)
            params["project_ids"] = [focus.project_id for focus in focus_list]
        elif params.get("classification") == 'subordinate':
            subordinate_list = DataScopeDao.getSubordinateIdById(user_id)
            params["subordinate_uid"] = [sysuser.id for sysuser in subordinate_list]

        total, es_res = ESService.querySeProjectByFilter(user_ids, **params)
        if es_res:
            for hit in es_res:
                project = hit["_source"]
                project["taken_hours"]= 0
                if project.get("tasks"):
                    for task in project.get("tasks"):
                        if task.get("record"):
                            for record in task.get("record"):
                                if record["status"] == 2:
                                    project["taken_hours"] += round(record["support_duration"]/60, 1)
                del project["tasks"]
                project["project_phase"] = getSeProjectProjectType(project.get("project_phase"))
                project["created_date"] = datetime.strptime(
                    project["created_date"], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
                project["last_modified_date"] = datetime.strptime(
                    project["last_modified_date"], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
                project["permission"] = []
                if (project['owner_id'] == user_id or project['created_by_id'] == user_id) and project['status'] != 3:
                    project["permission"].append("project_archive")
                data["list"].append(project)
            data["total"] = total
        if params.get("classification") == 'mine' and params.get("status") == [1]:
            logger.info(f"ProjectListAPI Get ResponseData: {data}")

        return data


get_record_pending_parser = RequestParser()
get_record_pending_parser.add_argument('page', location='args', type=int, default=1, required=True)
get_record_pending_parser.add_argument('size', location='args', type=int, default=1000, required=True)


@projectmanage_api.resource('/record/pending')
class RecordPendingAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectRecordList)
    def get(self):
        """
        获取待审批日志列表
        :return:
        """
        parser_args = prepare_args_for_parser(get_record_pending_parser.copy())
        params = parser_args.parse_args()

        page, size = params["page"], params["size"]
        data = {"list": [], "total": 0, "page": page, "size": size}
        approval_rtpc_list = SeProjectApprovalDao.getApprovalRecordByUserId(session['user_id'])
        for approval_rtpc in approval_rtpc_list:
            approval, record, main_task, project, create_user = approval_rtpc

            if record.task_id == main_task.id:
                task = main_task
            else:
                task = SeProjectTaskDao.queryTaskById(record.task_id)

            schema = SeProjectRecordSchema()
            record = schema.dump(record)
            record["task_number"] = task.task_number
            record["task_subject"] = task.subject
            record["task_parent_id"] = task.parent_id
            record["task_event_number"] = task.event_number
            record["assign_number"] = task.assign_number
            record["record_content"] = json.loads(record["record_content"])
            record["created_by_name"] = create_user.display_name
            record["account_name"] = project.account_name
            record["customer_requirement"] = project.customer_requirement
            record["support_type_1st"] = getSeProjectProjectType(task.support_type_1st)
            record["support_type_2nd"] = getSeProjectProjectType(task.support_type_2nd)
            record["attachments"] = []
            attachments = SysAttachmentDao.queryAttachmentByObjectId("se_project_record", record["id"])
            for attachment in attachments:
                record["attachments"].append({
                    "id": attachment.id,
                    "filename": attachment.file_name,
                    "file_size": attachment.file_size,
                    "file_type": attachment.file_type
                })
            data["list"].append(record)

        data["total"] = len(data["list"])
        data["list"] = data["list"][(page - 1) * size:((page - 1) * size + size)]
        return data


@projectmanage_api.resource('/record/<record_id>')
class RecordDetailAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectRecord)
    def get(self, record_id):
        """
        日志详情
        :return:
        """
        record = SeProjectRecordDao.queryRecordById(record_id)
        if not record:
            raise AppException("查询失败，日志不存在")

        task = SeProjectTaskDao.queryTaskById(record.task_id)
        if not task:
            return AppException("查询失败，任务不存在")

        project = SeProjectProjectDao.queryProjectById(task.project_id)
        if not project:
            return AppException("查询失败，项目不存在")

        schema = SeProjectRecordSchema()
        data = schema.dump(record)
        data["task_event_number"] = task.event_number
        if task.parent_id:
            if task.assign_number:
                data["task_event_number"] = task.assign_number
            else:
                data["task_event_number"] = task.task_number
        data["task_number"] = task.task_number
        data["task_subject"] = task.subject
        data["parent_id"] = task.parent_id
        data["event_number"] = task.event_number
        data["assign_number "] = task.assign_number
        data["record_content"] = json.loads(data["record_content"])
        data["support_type_1st"] = getSeProjectProjectType(task.support_type_1st)
        data["support_type_2nd"] = getSeProjectProjectType(task.support_type_2nd)
        data["project"] = {
            "id": project.id,
            "project_number": project.project_number,
            "subject": project.subject,
            "opportunity_number": project.opportunity_number
        }

        if task.parent_id:
            parent_task = SeProjectTaskDao.queryTaskById(task.parent_id)
            if parent_task:
                data["parent_task"] = {
                    "id": parent_task.id,
                    "task_number": parent_task.task_number,
                    "subject": parent_task.subject
                }

        data["attachments"] = []
        attachments = SysAttachmentDao.queryAttachmentByObjectId("se_project_record", record_id)
        for attachment in attachments:
            data["attachments"].append({
                "id": attachment.id,
                "filename": attachment.file_name,
                "file_size": attachment.file_size,
                "file_type": attachment.file_type
            })

        record_user = SysUserDao.querySysUserById(record.created_by_id)
        if not record:
            return AppException("审批成功，邮件通知失败")

        data["created_by_name"] = record_user.display_name
        data["account_name"] = project.account_name
        data["customer_requirement"] = project.customer_requirement

        return data


approval_record_parser = RequestParser()
approval_record_parser.add_argument('approval', location='json', choices=[1, 2], type=int, required=True)
approval_record_parser.add_argument('unapproval_reason', location='json', type=str)


@projectmanage_api.resource('/record/<record_id>/approval')
class RecordApprovalAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def put(self, record_id):
        """
        日志审批
        :return:
        """
        parser_args = prepare_args_for_parser(approval_record_parser.copy())
        params = parser_args.parse_args()

        if params["approval"] == 2 and not params.get("unapproval_reason"):
            raise AppException("操作失败，请填写原因")

        approval_record = SeProjectApprovalDao.queryApprovalRecordByRecordId(record_id)
        update_data = {
            "result": params["approval"],
            "incomplete_reason": params.get("unapproval_reason")
        }
        SeProjectApprovalDao.updateApprovalById(approval_record.id, update_data)

        update_data = {
            "status": 2 if params.get("approval") == 1 else 1,
            "last_modified_by_id": session['user_id']
        }
        SeProjectRecordDao.updateRecordById(record_id, update_data)

        record = SeProjectRecordDao.queryRecordById(record_id)
        if not record:
            return AppException("审批成功，邮件通知失败")
        record_user = SysUserDao.querySysUserById(record.created_by_id)
        if not record_user:
            return AppException("审批成功，邮件通知失败")
        task = SeProjectTaskDao.queryTaskById(record.task_id)
        if not task:
            return AppException("审批成功，邮件通知失败")
        task_co = SeProjectTaskDao.getTaskJoinSysUserById(approval_record.main_task_id)
        if not task_co:
            return AppException("审批成功，邮件通知失败")
        main_task, project, create_user, owner_user = task_co
        project_owner = SysUserDao.querySysUserById(project.owner_id)
        if not project_owner:
            return AppException("审批成功，邮件通知失败")
        project_sales = SysUserDao.querySysUserById(project.sale_by_id)
        project_sales = project_sales.display_name if project_sales else ""

        update_data = {"last_modified_by_id": session['user_id']}
        if params["approval"] == 1:
            task_taken_hours = 0
            all_record = SeProjectRecordDao.queryRecordByStatus(task.id, '2')
            for publish_record in all_record:
                task_taken_hours += round(publish_record.support_duration / 60, 1)
            update_data["taken_hours"] = task_taken_hours
        SeProjectTaskDao.updateTaskById(record.task_id, update_data)

        update_data = {"last_modified_by_id": session['user_id']}
        SeProjectProjectDao.updateProjectById(task.project_id, update_data)

        site_domain = current_app.config["SITE_DOMAIN"]
        record_content = ""
        record_content_load = json.loads(record.record_content)
        for content in record_content_load:
            if content.get("type") == "tip":
                continue
            record_content += f'{content.get("name")}: {content.get("content")}  <br/>'

        target, cc, cc_reason = [record_user.email], [], ""
        if params["approval"] == 1:
            replay = record_user.email
            target.append(create_user.email)
            if record_user.employee_id:
                employee = TblEmployeeDao.queryEmployeeById(record_user.employee_id)
                if employee:
                    leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                    if leader_employee:
                        cc.append(leader_employee.email)
                        cc_reason += f'{leader_employee.email}: 任务创建人EHR上级 <br/>'

                    department_manage = apollo_util.getValue("se_project_department_manage")
                    if employee.department in department_manage:
                        department_employee_id = department_manage.get(employee.department)
                        department_employee = TblEmployeeDao.queryEmployeeByUserId(department_employee_id)
                        if department_employee:
                            cc.append(department_employee.email)
                        if leader_employee:
                            if leader_employee.email:
                                cc_reason += f'{leader_employee.email}: 日志创建人部门领导 <br/>'

            cc_user_list = []
            if project.sale_by_id:
                cc_user_list.append(project.sale_by_id)
                cc_reason += f'{project.sale_by_id}(sale_by_id): 项目销售 <br/>'
            if project.sales_leader_id:
                cc_user_list.append(project.sales_leader_id)
                cc_reason += f'{project.sales_leader_id}(sales_leader_id): 项目销售上级 <br/>'
            if project.owner_id:
                cc_user_list.append(project.owner_id)
                cc_reason += f'{project.owner_id}(owner_id): 项目负责人 <br/>'
            if record_user.manage_id:
                cc_user_list.append(record_user.manage_id)
                cc_reason += f'{record_user.manage_id}(manage_id): 日志创建人站点上级 <br/>'
            focus = SeProjectFocusDao.queryFocusByProject(project.id)
            for f in focus:
                cc_user_list.append(f.follower_id)
                cc_reason += f'{f.follower_id}(follower_id): 项目关注人 <br/>'

            if cc_user_list:
                cc_user_list = SysUserDao.querySysUserByIds(list(set(cc_user_list)))
                for cc_user in cc_user_list:
                    cc.append(cc_user.email)
            cc = list(set(cc))
            es_res = ESService.querySeProjectByProjectId(project.id)
            project_taken_hours = 0
            if es_res.get("tasks"):
                for es_res_task in es_res.get("tasks"):
                    if es_res_task.get("record"):
                        for es_res_record in es_res_task.get("record"):
                            if es_res_record.get("status") == 2:
                                project_taken_hours+= round(es_res_record["support_duration"]/60, 1)
            template = SeProjectRecordApprovedEmail()
            template.update({
                "task_id": task.id, "task_number": task.task_number if task.parent_id else task.event_number,
                "subject": task.subject,
                "created_by_name": record_user.display_name, "approver": create_user.display_name,
                "site_domain": site_domain,
                "support_type_1st": getSeProjectProjectType(task.support_type_1st)["name"],
                "support_type_2nd": getSeProjectProjectType(task.support_type_2nd)["name"],
                "published_date": record.published_date.strftime('%Y-%m-%d %H:%M:%S'),
                "support_start_date": record.support_start_date.strftime('%Y-%m-%d %H:%M:%S'),
                "support_end_date": record.support_end_date.strftime('%Y-%m-%d %H:%M:%S'),
                "support_duration": record.support_duration/60,
                "record_content": record_content,
                "account_name": project.account_name,
                "project_name": project.subject,
                "record_data": json.loads(record.record_content),
                "project_owner_name": project_owner.display_name,
                "project_sales_by_name": project_sales,
                "project_opportunity_number": project.opportunity_number,
                "project_opportunity_name": project.opportunity_name,
                "project_subject": project.subject,
                "cc_reason": cc_reason,
                "project_customer_requirement": project.customer_requirement,
                "project_total_support_duration": project_taken_hours
            })

            SeProjectOS(task.project_id, params).logRecordApproval(record_id)

        else:
            replay = create_user.email
            template = SeProjectRecordUnApprovedEmail()
            template.update({
                "task_id": task.id, "task_number": task.task_number if task.parent_id else task.event_number,
                "subject": task.subject,
                "approver": create_user.display_name, "reject_reason": params.get("unapproval_reason"),
                "site_domain": site_domain, "record_content": record_content
            })
            cc.append(create_user.email)

            SeProjectOS(task.project_id, params).logRecordUnApproval(record_id, params.get("unapproval_reason"))

        def notice(**kwargs):
            try:
                message_gw.push(**kwargs)
            except Exception as e:
                logger.error("RecordApprovalAPI Exception: {}".format(str(e)))

        executor.submit(notice, target=target, template=template, cc=cc, reply_to=replay)
        return jsonify(AppResponse())


@projectmanage_api.resource('/record/<record_id>/return')
class RecordReturnAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def put(self, record_id):
        """
        日志撤回
        :return:
        """

        user_id = session["user_id"]
        record = SeProjectRecordDao.queryRecordById(record_id)
        task_project = SeProjectTaskDao.getTaskJoinProjectById(record.task_id)
        if not task_project:
            raise AppException("撤回失败，任务不存在")

        task, project = task_project
        if user_id == record.created_by_id and record.status == 4:
            update_data = {"status": 1, "last_modified_by_id": session['user_id']}
            SeProjectRecordDao.updateRecordById(record_id, update_data)
            approval = SeProjectApprovalDao.queryApprovalByRecordId(record_id)
            if approval:
                update_data = {"result": 2, "incomplete_reason": '日志提交人撤回'}
                SeProjectApprovalDao.updateApprovalById(approval.id, update_data)

        elif user_id == project.created_by_id and record.status == 2:
            update_data = {"status": 1, "last_modified_by_id": session['user_id']}
            SeProjectRecordDao.updateRecordById(record_id, update_data)

            approval = SeProjectApprovalDao.queryApprovalByRecordId(record_id)
            if approval:
                update_data = {"result": 2, "incomplete_reason": '项目创建人撤回'}
                SeProjectApprovalDao.updateApprovalById(approval.id, update_data)

            if record.created_by_id != user_id:
                record_user = SysUserDao.querySysUserById(record.created_by_id)
                if not record_user:
                    return AppException("撤回失败，查询失败")
                current_user = SysUserDao.querySysUserById(user_id)
                if not current_user:
                    return AppException("撤回失败，查询失败")

                record_content = ""
                record_content_load = json.loads(record.record_content)
                for content in record_content_load:
                    if content.get("type") == "tip":
                        continue
                    record_content += f'{content.get("name")}: {content.get("content")}  <br/>'

                target, cc = [record_user.email], [current_user.email]
                template = SeProjectRecordReturnEmail()
                template.update({
                    "task_number": task.task_number if task.parent_id else task.event_number,
                    "subject": task.subject,
                    "site_domain": current_app.config["SITE_DOMAIN"],
                    "task_id": task.id,
                    "approver": current_user.display_name,
                    "record_content": record_content
                })

                def notice(**kwargs):
                    try:
                        message_gw.push(**kwargs)
                    except Exception as e:
                        logger.error("RecordReturnAPI Exception: {}".format(str(e)))

                executor.submit(notice, target=target, template=template, cc=cc)

        else:
            raise AppException("撤回失败，没有权限")

        task_taken_hours = 0
        update_data = {"last_modified_by_id": session['user_id']}
        all_record = SeProjectRecordDao.queryRecordByStatus(task.id, '2')
        for publish_record in all_record:
            task_taken_hours += round(publish_record.support_duration / 60, 1)
        update_data["taken_hours"] = task_taken_hours
        SeProjectTaskDao.updateTaskById(record.task_id, update_data)

        SeProjectOS(task.project_id).logRecordReturn(record_id)

        return jsonify(AppResponse())


put_project_parser = RequestParser()
put_project_parser.add_argument('action', location='json', type=str, required=True)
put_project_parser.add_argument('subject', location='json', type=str)
put_project_parser.add_argument('competitors', location='json', type=str)
put_project_parser.add_argument('pre_bidding_date', location='json', type=str)
put_project_parser.add_argument('opportunity_level', location='json', type=str)
put_project_parser.add_argument('account_id', location='json', type=str)
put_project_parser.add_argument('account_name', location='json', type=str)
put_project_parser.add_argument('contact_name', location='json', type=str)
put_project_parser.add_argument('contact_info', location='json', type=str)
put_project_parser.add_argument('business_stage', location='json', type=str)
put_project_parser.add_argument('contact_position', location='json', type=str)
put_project_parser.add_argument('deploy_core', location='json', choices=["是", "否", ""], type=str)
put_project_parser.add_argument('is_big_project_support', location='json', choices=["是", "否", ""], type=str)
put_project_parser.add_argument('customer_requirement', location='json', type=str)
put_project_parser.add_argument('project_background_description', location='json', type=str, dest='background_description')
put_project_parser.add_argument("return_reason", location='json', type=str)
put_project_parser.add_argument("owner_id", location='json', type=str)


@projectmanage_api.resource('/project/<project_id>')
class ProjectDetailAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectProjectDetail)
    def get(self, project_id):
        """
        查看项目详情
        :return:
        """
        project_co = SeProjectProjectDao.getProjectJoinSysUserById(project_id)
        if not project_co:
            raise AppException("查询失败，项目不存在")

        project, create_user, owner_user = project_co
        user_id = session["user_id"]
        if not (user_id == create_user.id or user_id == owner_user.id):
            def has_permission():
                if project.is_big_project_support == '是':
                    permission_list = permission.getPermissionByUserId(user_id)
                    if p_list['p_se_project_manage_support'] in permission_list:
                        return True

                user_ids = DataScopeDao.getSysUserByRank(user_id, 'se.project_manage:list')
                if not user_ids:
                    return False

                if user_ids == ['*'] or (create_user.id in user_ids or owner_user.id in user_ids):
                    return True

                task_co_list = SeProjectTaskDao.getTaskJoinSysUserByProjectId(project_id)
                if not task_co_list:
                    return False

                for task_co in task_co_list:
                    if (task_co[0].owner_id == user_id or task_co[0].created_by_id == user_id
                            or task_co[0].owner_id in user_ids or task_co[0].created_by_id in user_ids):
                        return True
                return False

            if not has_permission:
                raise AppException("查询失败，没有权限")

        project, create_user, owner_user = project_co
        sale_user = SysUserDao.querySysUserById(project.sale_by_id)

        schema = SeProjectProjectSchema()
        data = schema.dump(project)
        focus = SeProjectFocusDao.queryFocusByProjectId(user_id, project_id)
        data["focused"] = True if focus and not focus.deleted_date else False
        if project.parent_project:
            parent_project = SeProjectProjectDao.queryProjectById(project.parent_project)
            data["parent_opportunity_number"] = parent_project.opportunity_number

        data["project_phase"] = getSeProjectProjectType(data["project_phase"])
        data['sale_by_name'] = sale_user.display_name if sale_user else ''
        data["created_by_name"] = create_user.display_name
        data["owner_name"] = owner_user.display_name

        records = SeProjectRecordDao.getRecordJoinSeProjectById(project_id)
        created_date_list = []
        support_start_date_list = []
        if records:
            for record, task in records:
                created_date_list.append(record.created_date)
                support_start_date_list.append(record.support_start_date)
            data["last_record_created_date"] = str(max(created_date_list))
            data["last_record_support_start_date"] = str(max(support_start_date_list))
        return data

    @permission.check(p_list['p_se_project_manage_list'])
    def put(self, project_id):
        """
        项目确认/编辑接口
        :return:
        """
        parser_args = prepare_args_for_parser(put_project_parser.copy())
        params = parser_args.parse_args()

        project = SeProjectProjectDao.queryProjectById(project_id)
        if not project:
            raise AppException("查询失败，项目不存在")

        subordinate_list = DataScopeDao.getSuperiorsIdById(project.created_by_id)
        superiors_ids = [sysuser.id for sysuser, employee in subordinate_list] + [project.created_by_id]
        if project.owner_id != session["user_id"]:
            if session["user_id"] not in superiors_ids or params["action"] != "assign_owner":
                raise AppException("操作失败，没有权限")

        action = params.get("action")
        if action == 'edit':
            #  只修改项目负责人，跳过字段验证
            if not (session['user_id'] in superiors_ids and len(params) <= 2):
                # 字段验证不可为空
                if "subject" not in params.keys():
                    raise AppException("Message: `subject` Error: Missing required parameter in the JSON body. Field description: None.")

                if "competitors" not in params.keys():
                    raise AppException("Message: `competitors` Error: Missing required parameter in the JSON body. Field description: None.")

                if "opportunity_level" not in params.keys():
                    raise AppException("Message: `opportunity_level` Error: Missing required parameter in the JSON body. Field description: None.")

                if "account_id" not in params.keys():
                    raise AppException("Message: `account_id` Error: Missing required parameter in the JSON body. Field description: None.")

                if "account_name" not in params.keys():
                    raise AppException("Message: `account_name` Error: Missing required parameter in the JSON body. Field description: None.")

                if "business_stage" not in params.keys():
                    raise AppException("Message: `business_stage` Error: Missing required parameter in the JSON body. Field description: None.")

                if "customer_requirement" not in params.keys():
                    raise AppException("Message: `customer_requirement` Error: Missing required parameter in the JSON body. Field description: None.")

                if "background_description" not in params.keys():
                    raise AppException("Message: `background_description` Error: Missing required parameter in the JSON body. Field description: None.")

            params.pop("action")
            if "return_reason" in params.keys():
                params.pop("return_reason")
            if "pre_bidding_date" in params.keys() and not params.get("pre_bidding_date"):
                params.pop("pre_bidding_date")

            params["status"] = 2
            SeProjectProjectDao.updateProjectById(project_id, params)

            SeProjectOS(project.id, params).logProjectEdit(project.id, project.opportunity_number, project.subject)

        elif action == 'confirm':
            update_data = {
                "status": 2,
                "deploy_core": params.get("deploy_core"),
                "subject": params.get("subject"),
                "opportunity_level": params.get("opportunity_level"),
                "business_stage": params.get("business_stage"),
                "account_name": params.get("account_name"),
                "account_id": params.get("account_id"),
                "contact_name": params.get("contact_name"),
                "contact_info": params.get("contact_info"),
                "contact_position": params.get("contact_position"),
                "background_description": params.get("background_description"),
                "customer_requirement": params.get("customer_requirement"),
                "competitors": params.get("competitors"),
                "pre_bidding_date": params.get("pre_bidding_date")
            }
            if params.get("is_big_project_support"):
                update_data["is_big_project_support"] = params.get("is_big_project_support")
            SeProjectProjectDao.updateProjectById(project_id, update_data)

            SeProjectOS(project.id, params).logProjectConfirm(project.id, project.opportunity_number, project.subject)

        elif action == 'assign_owner':
            if "owner_id" not in params.keys():
                raise AppException(
                    "Message: `owner_id` Error: Missing required parameter in the JSON body. Field description: None.")

            if session['user_id'] not in superiors_ids:
                raise AppException("操作失败，您没有操作权限")

            old_user = SysUserDao.querySysUserById(project.owner_id)
            new_user = SysUserDao.querySysUserById(params.get("owner_id"))

            update_data = {"owner_id": params.get("owner_id")}
            SeProjectProjectDao.updateProjectById(project_id, update_data)

            SeProjectOS(project.id, params).logProjectAssign(
                project.id, project.opportunity_number, project.subject,
                old_user.id, old_user.display_name, new_user.id, new_user.display_name
            )

        elif action == 'return':
            if "return_reason" in params.keys() and not params.get("return_reason"):
                raise AppException("Message: `return_reason` Error: Missing required parameter in the JSON body. Field description: None.")
            update_data = {"status": 4, "return_reason": params.get("return_reason")}
            SeProjectProjectDao.updateProjectById(project_id, update_data)

            # 查询所有任务未开始改为删除
            task_list = []
            task_co = SeProjectTaskDao.queryTaskByProjectId(project_id)
            for task in task_co:
                if task.status == 4:
                    SeProjectTaskDao.updateTaskById(task.id, {"status": 3})
                    task_list.append({"id": task.id, "task_number": "", "subject": task.subject})

            SeProjectOS(project.id, params).logProjectReturn(
                project.id, project.opportunity_number, project.subject, task_list
            )

        return jsonify(AppResponse())


@projectmanage_api.resource('/project/<project_id>/task_statistics')
class ProjectTaskStatisticsAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def get(self, project_id):
        """
        获取任务列表统计（统计各状态的主任务个数）
        :return:
        """
        data = {"task_total": 0, "total_in_progress": 0, "closed_total": 0, "pending_total": 0, "unrecognized_total": 0}
        if not project_id:
            raise AppException("参数错误，项目ID不能为空")

        project = SeProjectProjectDao.queryProjectById(project_id)
        if not project:
            raise AppException("获取失败，项目不存在")

        task_co_list = SeProjectTaskDao.getTaskJoinSysUserByProjectId(project_id)

        # count = len(task_co_list)
        # data["task_total"] = len(task_co_list)
        if task_co_list:
            for task_co in task_co_list:
                if task_co[0].parent_id:
                    continue
                data["task_total"] += 1
                if task_co[0].status == 1:
                    data["total_in_progress"] += 1
                elif task_co[0].status == 2:
                    data["closed_total"] += 1
                elif task_co[0].status == 4:
                    data["unrecognized_total"] += 1
                elif task_co[0].status == 5:
                    data["pending_total"] += 1

        return jsonify(AppResponse(data))


get_task_parser = RequestParser()
# get_task_parser.add_argument('project_id', location='args', type=validate_null, required=True)
get_task_parser.add_argument('page', location='args', type=int, default=1)
get_task_parser.add_argument('size', location='args', type=int, default=1000)


@projectmanage_api.resource('/project/<project_id>/task')
class ProjectTaskListAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectTaskList)
    def get(self, project_id):
        """
        查询项目任务列表 编号、主题、责任人、支持方式(现场/远程)、状态(进行中、已结束和已删除)、创建时间和操作等列
        :return:
        """
        parser_args = prepare_args_for_parser(get_task_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0, "totality": 0,
            "page": int(params.get("page")), "size": int(params.get("size"))
        }

        parent_task_taken = {}
        user_id = session["user_id"]
        task_ids, parent_ids = [], []
        project = SeProjectProjectDao.queryProjectById(project_id)
        if project:
            task_co_list = []
            all_task_co = SeProjectTaskDao.getTaskJoinSysUserByProjectId(project_id)
            if all_task_co:
                user_ids = DataScopeDao.getSysUserByRank(user_id, 'se.project_manage:list')
                role_user = SysRoleUserDao.querySysRoleByRoleUserId("0pvzutpcrqs5v0y", user_id)
                if project.created_by_id == user_id or project.owner_id == user_id or user_ids == ['*'] or (project.is_big_project_support == '是' and role_user):
                    task_co_list = all_task_co
                    for task_co in all_task_co:
                        task, create_user, owner_user = task_co
                        task_ids.append(task.id)
                        if task.parent_id and task.parent_id not in parent_ids:
                            parent_ids.append(task.parent_id)

                else:
                    for task_co in all_task_co:
                        task, create_user, owner_user = task_co
                        if task.owner_id in user_ids or task.created_by_id in user_ids:
                            task_ids.append(task.id)
                            task_co_list.append(task_co)
                            if task.parent_id and task.parent_id not in parent_ids:
                                parent_ids.append(task.parent_id)

                    for task_co in all_task_co:
                        task, create_user, owner_user = task_co
                        if task.id not in task_ids and task.id in parent_ids:
                            task_ids.append(task.id)
                            task_co_list.append(task_co)

                for task_co in all_task_co:
                    task, create_user, owner_user = task_co
                    if not task.taken_hours:
                        continue

                    def spend(task_id: str):
                        cost = 0
                        record_create_list = SeProjectRecordDao.getRecordJoinSysUserByStatus(task_id=task_id, status=2)
                        if record_create_list:
                            for record_c in record_create_list:
                                record, create_user = record_c
                                cost += record.support_duration
                        return cost

                    if task.parent_id in parent_ids:
                        if parent_task_taken.get(task.parent_id):
                            parent_task_taken[task.parent_id] += spend(task.id)
                        else:
                            parent_task_taken[task.parent_id] = spend(task.id)
                    elif task.id in parent_ids:
                        if parent_task_taken.get(task.id):
                            parent_task_taken[task.id] += spend(task.id)
                        else:
                            parent_task_taken[task.id] = spend(task.id)

            task_record_count = {}
            all_record_count = SeProjectRecordDao.getAllRecordCountByTaskIds(task_ids)
            for record_count in all_record_count:
                task_record_count[record_count[0]] = record_count[1]

            for task_co in task_co_list:
                task, create_user, owner_user = task_co
                if task.parent_id and task.parent_id not in task_ids:
                    continue

                schema = SeProjectTaskSchema()
                task = schema.dump(task)
                task["taken_hours"] = 0
                record_create_list = SeProjectRecordDao.getRecordJoinSysUserByStatus(task_id=task["id"], status=2)
                if record_create_list:
                    for record_c in record_create_list:
                        record, create_user = record_c
                        task["taken_hours"] += record.support_duration
                task["taken_hours"] = round(float(task["taken_hours"] / 60 ), 1)
                task["record_count"] = task_record_count.get(task["id"])
                task["support_type_1st"] = getSeProjectProjectType(task["support_type_1st"])
                task["support_type_2nd"] = getSeProjectProjectType(task["support_type_2nd"])
                task["created_by_name"] = create_user.display_name
                task["owner_name"] = owner_user.display_name
                task["application_type"] = project.application_type
                if task.get("assign_number") and task.get("parent_id"):
                    task["task_number"] = task.get("assign_number")
                if task["last_modified_by_id"] == task["owner_id"]:
                    task["last_modified_by_name"] = owner_user.display_name
                elif task["last_modified_by_id"] == task["created_by_id"]:
                    task["last_modified_by_name"] = create_user.display_name
                else:
                    modified_user = SysUserDao.querySysUserById(task["last_modified_by_id"])
                    task["last_modified_by_name"] = modified_user.display_name

                if parent_task_taken.get(task["id"]):
                    task["all_taken_hours"] = parent_task_taken.get(task["id"])
                    task["all_taken_hours"] = round(float(task["all_taken_hours"] / 60 ), 1)
                else:
                    task["all_taken_hours"] = task["taken_hours"]

                operate_permission = []
                if task["owner_id"] == session["user_id"] and task["status"] in [1, 4]:
                    if task["status"] == 1:
                        operate_permission.append("create_record")
                        operate_permission.append("task_archive")

                    if task["parent_id"]:
                        if task["status"] == 4:
                            operate_permission.append("delete_subtask")
                    else:
                        if task["status"] == 1:
                            operate_permission.append("create_subtask")

                task["permission"] = operate_permission
                data["list"].append(task)

            data["total"] = len(data["list"]) - len(parent_ids)
            data["totality"] = len(data["list"])
        return data


task_approval_parser = RequestParser()
# task_approval_parser.add_argument('project_id', location='args', type=validate_null, required=True)
task_approval_parser.add_argument('page', location='args', type=int, default=1)
task_approval_parser.add_argument('size', location='args', type=int, default=1000)


@projectmanage_api.resource('/project/<project_id>/task/approval')
class ProjectTaskApprovalListAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectTaskList)
    def get(self, project_id):
        """
        查询项目待审批的主任务列表 编号、主题、责任人、支持方式(现场/远程)、状态(进行中、已结束和已删除)、创建时间和操作等列
        :return:
        """
        parser_args = prepare_args_for_parser(task_approval_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")), "size": int(params.get("size"))
        }

        task_ids, parent_ids = [], []
        user_id = session["user_id"]
        project = SeProjectProjectDao.queryProjectById(project_id)
        if project:
            if project.created_by_id == user_id:
                task_co_list = SeProjectTaskDao.getTaskJoinSysUserByProjectId(project_id)

            else:
                user_ids = DataScopeDao.getSysUserByRank(user_id, 'se.project_manage:list')
                task_co_list = SeProjectTaskDao.getTaskJoinSysUserByUserId(user_ids, project_id)

            for task_co in task_co_list:
                task = task_co[0]
                task_ids.append(task.id)
                if task.parent_id:
                    parent_ids.append(task.parent_id)

            parent_tasks = [x for x in parent_ids if x not in task_ids]
            if parent_tasks:
                parent_task = SeProjectTaskDao.getTaskJoinSysUserByIds(parent_tasks)
                task_co_list += parent_task
                task_ids += [task_c0[0].id for task_c0 in parent_task]

            for task_co in task_co_list:
                task, create_user, owner_user = task_co
                if task.parent_id and task.parent_id not in task_ids:
                    continue
                if task.status != 5:
                    continue

                schema = SeProjectTaskSchema()
                task = schema.dump(task)
                task["support_type_1st"] = getSeProjectProjectType(task["support_type_1st"])
                task["support_type_2nd"] = getSeProjectProjectType(task["support_type_2nd"])
                task["created_by_name"] = create_user.display_name
                task["owner_name"] = owner_user.display_name
                task["application_type"] = project.application_type
                if task.get("assign_number") and task.get("parent_id"):
                    task["task_number"] = task.get("assign_number")
                if task["last_modified_by_id"] == task["owner_id"]:
                    task["last_modified_by_name"] = owner_user.display_name
                elif task["last_modified_by_id"] == task["created_by_id"]:
                    task["last_modified_by_name"] = create_user.display_name
                else:
                    modified_user = SysUserDao.querySysUserById(task["last_modified_by_id"])
                    task["last_modified_by_name"] = modified_user.display_name

                operate_permission = []
                if task["owner_id"] == session["user_id"]:
                    if not task["deleted_date"]:
                        operate_permission.append("delete")
                    if not task["task_result"]:
                        operate_permission.append("archive")
                        operate_permission.append("create_record")

                elif task["parent_id"]:
                    for task_co2 in task_co_list:
                        task2 = task_co2[0]
                        if task2.id == task["parent_id"] and task2.owner_id == session["user_id"]:
                            operate_permission += ["delete"]

                if not task["parent_id"] and task["owner_id"] == session["user_id"] and task["status"] != 2:
                    operate_permission += ["create_subtask"]

                task["permission"] = operate_permission
                data["list"].append(task)

        data["total"] = len(data["list"])
        data["totality"] = len(data["list"])
        return data


approval_task_parser = RequestParser()
approval_task_parser.add_argument('approval', location='json', choices=[1, 2], type=int, required=True)
approval_task_parser.add_argument('unapproval_reason', location='json', type=str)


@projectmanage_api.resource('/task/<task_id>/approval')
class TaskApprovalAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def put(self, task_id):
        """
        任务归档审批
        :return:
        """
        parser_args = prepare_args_for_parser(approval_task_parser.copy())
        params = parser_args.parse_args()

        if params["approval"] == 2 and not params.get("unapproval_reason"):
            raise AppException("操作失败，请填写原因")

        approval_record = SeProjectApprovalDao.queryApprovalRecordByTaskId(task_id)
        update_data = {
            "result": params["approval"],
            "incomplete_reason": params.get("unapproval_reason")
        }
        SeProjectApprovalDao.updateApprovalById(approval_record.id, update_data)

        update_data = {
            "status": 2 if params.get("approval") == 1 else 1,
            "last_modified_by_id": session['user_id']
        }
        SeProjectTaskDao.updateTaskById(task_id, update_data)

        task = SeProjectTaskDao.queryTaskById(task_id)
        if not task:
            return AppException("审批成功，邮件通知失败")

        if task.parent_id:
            update_data = {"last_modified_by_id": session['user_id']}
            SeProjectTaskDao.updateTaskById(task.parent_id, update_data)

        project_co = SeProjectProjectDao.getProjectJoinSysUserById(task.project_id)
        if not project_co:
            return AppException("审批成功，邮件通知失败")
        project, create_user, owner_user = project_co[0], project_co[1], project_co[2]

        record_user = SysUserDao.querySysUserById(task.created_by_id)
        if not task:
            return AppException("审批成功，邮件通知失败")

        def notice(**kwargs):
            try:
                message_gw.push(**kwargs)
            except Exception as e:
                logger.error("RecordApprovalAPI Exception: {}".format(str(e)))

        site_domain = current_app.config["SITE_DOMAIN"]
        target, cc, replay = [record_user.email], [], ""
        approval_result = "未通过"
        if params["approval"] == 1:
            approval_result = "通过"
            target.append(create_user.email)
            if record_user.employee_id:
                employee = TblEmployeeDao.queryEmployeeById(record_user.employee_id)
                if employee:
                    leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                    if leader_employee:
                        cc.append(leader_employee.email)

            task_user = SysUserDao.querySysUserById(task.owner_id)
            template = SeProjectTaskApprovedArchiveEmail()
            template.update({
                "task_id": task.id, "task_number": task.task_number if task.parent_id else task.event_number,
                "subject": task.subject, "site_domain": site_domain
            })
            executor.submit(notice, target=task_user.email, template=template)

            if task.parent_id:
                undone_task_list = SeProjectTaskDao.queryUndoneTaskByParentId(task.parent_id)
                if not undone_task_list:
                    main_task = SeProjectTaskDao.queryTaskById(task.parent_id)
                    if main_task:
                        template = SeProjectTaskArchiveEmail()
                        main_task_user = SysUserDao.querySysUserById(main_task.owner_id)
                        if main_task and main_task_user:
                            template.update({
                                "task_id": task.parent_id,
                                "task_number": main_task.task_number if main_task.parent_id else main_task.event_number,
                                "subject": main_task.subject, "site_domain": site_domain
                            })
                            executor.submit(notice, target=main_task_user.email, template=template)
            elif not task.parent_id:
                undone_main_task_list = SeProjectTaskDao.queryUndoneMainTaskByProjectId(task.project_id)
                if not undone_main_task_list:
                    template = SeProjectProjectArchiveEmail()
                    template.update({
                        "project_id": project.id, "project_number": project.opportunity_number,
                        "subject": project.subject, "site_domain": site_domain
                    })
                    executor.submit(notice, target=create_user.email, template=template)

        else:
            task_user = SysUserDao.querySysUserById(task.owner_id)
            template = SeProjectTaskUnApprovedArchiveEmail()
            template.update({
                "task_id": task.id, "task_number": task.task_number if task.parent_id else task.event_number,
                "subject": task.subject, "site_domain": site_domain,
                "approver": create_user.display_name, "reject_reason": params.get("unapproval_reason")
            })
            executor.submit(notice, target=task_user.email, template=template)

        SeProjectOS(project.id, params).logTaskArchiveApprove(
            task.id, task.task_number if task.parent_id else task.event_number, task.subject, approval_result
        )

        return jsonify(AppResponse())


return_task_parser = RequestParser()
return_task_parser.add_argument('task_incomplete_reason', location='json', type=str)


@projectmanage_api.resource('/task/<task_id>/return')
class MainTaskReturnAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def put(self, task_id):
        """
        主任务退回
        """
        parser_args = prepare_args_for_parser(return_task_parser.copy())
        params = parser_args.parse_args()

        task = SeProjectTaskDao.queryTaskById(task_id)
        if not task:
            raise AppException("任务退回失败，任务不存在")

        if task.owner_id != session['user_id']:
            raise AppException("任务退回失败，您不是任务负责人")

        update_data = {
            "status": 3,
            "last_modified_by_id": session['user_id'],
            "deleted_by_id":  session['user_id'],
            "deleted_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "task_incomplete_reason":  params.get("task_incomplete_reason")
        }
        SeProjectTaskDao.updateTaskById(task_id, update_data)
        
        project = SeProjectProjectDao.queryProjectById(task.project_id)
        SeProjectOS(project.id, params).logTaskReturn(
            task.id, task.task_number if task.parent_id else task.event_number, task.subject
        )
        return jsonify(AppResponse())


receive_task_parser = RequestParser()
receive_task_parser.add_argument('subject', location='json', type=str)
receive_task_parser.add_argument('contact_position', location='json', type=str)
receive_task_parser.add_argument('support_type_1st', location='json', type=str)
receive_task_parser.add_argument('support_type_2nd', location='json', type=str)
receive_task_parser.add_argument('support_mode', location='json', type=int)
receive_task_parser.add_argument('start_time', location='json', type=str_to_none, dest='task_start_date')
receive_task_parser.add_argument('end_date', location='json', type=str_to_none, dest='task_end_date')
receive_task_parser.add_argument('account_id', location='json', type=str)
receive_task_parser.add_argument('account_name', location='json', type=str)
receive_task_parser.add_argument('contact_name', location='json', type=str)
receive_task_parser.add_argument('contact_info', location='json', type=str)


@projectmanage_api.resource('/task/<task_id>/receive')
class TaskReceiveAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def put(self, task_id):
        """
        任务确认启用
        """
        parser_args = prepare_args_for_parser(receive_task_parser.copy())
        params = parser_args.parse_args()

        task = SeProjectTaskDao.queryTaskById(task_id)
        if not task:
            raise AppException("任务启用失败，任务不存在")

        if task.owner_id != session['user_id']:
            raise AppException("任务启用失败，您不是任务负责人")

        project = SeProjectProjectDao.queryProjectById(task.project_id)
        if not project:
            raise AppException("任务启用失败，所属项目不存在")

        if project.status == 1:
            owner_user = SysUserDao.querySysUserById(project.owner_id)
            if owner_user:
                owner_name = owner_user.display_name
                raise AppException(f"对应的项目未确认，需要{owner_name}对项目先进行确认")
            else:
                raise AppException(f"对应的项目未确认，请先对项目先进行确认")

        if task.parent_id:
            # 子任务时检查主任务是否启用或者结束
            main_task = SeProjectTaskDao.queryTaskById(task.parent_id)
            if main_task.status == 4:
                raise AppException("任务启用失败，请先对主任务先进行确认")
            if main_task.status == 2:
                raise AppException("任务启用失败，主任务已结束")

        params["status"] = 1
        SeProjectTaskDao.updateTaskById(task_id, params)

        task = SeProjectTaskDao.queryTaskById(task_id)
        if not task.parent_id:
            # 主任务确认，更新子任务支持类型和支持项
            sub_task_list = SeProjectTaskDao.queryTaskByParentId(task.id)
            for sub_task in sub_task_list:
                if not sub_task.support_type_1st or not sub_task.support_type_2nd:
                    update_data = {
                        "support_type_1st": task.support_type_1st,
                        "support_type_2nd": task.support_type_2nd,
                        "contact_position": task.contact_position
                    }
                    SeProjectTaskDao.updateTaskById(sub_task.id, update_data)

            update_data = {
                "last_modified_by_id": session['user_id']
            }
            SeProjectTaskDao.updateTaskById(task.id, update_data)

        update_data = {
            "last_modified_by_id": session['user_id'],
            "project_phase": params.get("support_type_1st")
        }
        SeProjectProjectDao.updateProjectById(task.project_id, update_data)

        SeProjectOS(project.id, params).logTaskEnable(
            task.id, task.task_number if task.parent_id else task.event_number, task.subject
        )

        return jsonify(AppResponse())


@projectmanage_api.resource('/task/support_type')
class ProjectSupportTypeAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def get(self):
        """
        获取任务类型，确定日志模板
        :return:
        """
        data = {"list": SEPROJECT_TEMPLATE}

        return jsonify(AppResponse(data))


post_subtask_parser = RequestParser()
post_subtask_parser.add_argument('subject', location='json', type=validate_null, required=True)
post_subtask_parser.add_argument('support_mode', location='json', type=validate_null, required=True)
post_subtask_parser.add_argument('account_id', location='json', type=str)
post_subtask_parser.add_argument('account_name', location='json', type=str)
post_subtask_parser.add_argument('contact_name', location='json', type=str)
post_subtask_parser.add_argument('contact_info', location='json', type=str)
post_subtask_parser.add_argument('contact_position', location='json', type=str)
post_subtask_parser.add_argument('task_start_date', location='json', type=str, dest='task_start_date')
post_subtask_parser.add_argument('task_end_date', location='json', type=str, dest='task_end_date')
post_subtask_parser.add_argument('owner_id', location='json', type=list, required=True)
post_subtask_parser.add_argument('support_type_2nd', location='json', type=str, required=True)


@projectmanage_api.resource('/task/<main_task_id>/subtask')
class SubTaskAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def post(self, main_task_id):
        """
        创建子任务
        :return:
        """
        parser_args = prepare_args_for_parser(post_subtask_parser.copy())
        params = parser_args.parse_args()

        data = {"list": []}
        task_p = SeProjectTaskDao.getTaskJoinProjectById(main_task_id)
        if not task_p:
            raise AppException("操作失败，任务不存在")

        main_task, project = task_p
        if main_task.owner_id != session['user_id']:
            raise AppException("操作失败，只有任务负责人可以创建")

        if main_task.status == 2:
            raise AppException("操作失败，任务已归档")
        if main_task.status == 4:
            raise AppException("操作失败，任务未启用")

        params["project_id"] = main_task.project_id
        params["parent_id"] = main_task.id
        params['event_number'] = main_task.event_number
        params["support_type_1st"] = main_task.support_type_1st
        params['created_by_id'] = session['user_id']
        params['last_modified_by_id'] = session['user_id']
        params['status'] = 4

        site_domain = current_app.config["SITE_DOMAIN"]
        create_user = SysUserDao.querySysUserById(session['user_id'])
        owner_list = copy.copy(params["owner_id"])
        for owner_id in owner_list:
            params['owner_id'] = owner_id
            owner = SysUserDao.querySysUserById(owner_id)
            schema = SeProjectTaskSchema()
            task = schema.load(params)
            _id, task_number = SeProjectTaskDao.addTask(task)

            def notice(**kwargs):
                try:
                    message_gw.push(**kwargs)
                except Exception as e:
                    logger.error("SubTask Create Exception: {}".format(str(e)))

            template = SeProjectSubTaskEmail()
            template.update({
                "site_domain": site_domain,
                "task_id": task.id, "task_number": task.task_number if task.parent_id else task.event_number,
                "subject": task.subject,
                "owner_name": owner.display_name, "created_by_name": create_user.display_name,
                "created_date": task.created_date.strftime('%Y-%m-%d %H:%M:%S'), "parent_task_id": main_task.id,
                "parent_task_number": main_task.task_number, "parent_task_subject": main_task.subject,
                "project_id": project.id, "project_number": project.opportunity_number,
                "project_subject": project.subject
            })
            executor.submit(notice, target=owner.email, template=template, cc=create_user.email)

            data["list"].append({"id": _id, "task_number": task_number})

            update_data = {"last_modified_by_id": session['user_id']}
            SeProjectProjectDao.updateProjectById(main_task.project_id, update_data)
            SeProjectOS(project.id, params).logSubTaskCreate(
                task.id, task.task_number if task.parent_id else task.event_number, task.subject,
                owner.id, owner.display_name
            )

        return jsonify(AppResponse(data))


@projectmanage_api.resource('/task/<task_id>')
class ProjectTaskIdAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectTaskDetail)
    def get(self, task_id):
        """
        任务详情
        :return:
        """
        task_pco = SeProjectTaskDao.getTaskJoinSysUserById(task_id)
        if not task_pco:
            raise AppException("查询失败，任务不存在")

        task, project, create_user, owner_user = task_pco
        user_id = session["user_id"]
        if not (user_id == create_user.id or user_id == owner_user.id
                or user_id == project.created_by_id or user_id == project.owner_id):
            def has_permission():
                if project.is_big_project_support == '是':
                    permission_list = permission.getPermissionByUserId(user_id)
                    if p_list['p_se_project_manage_support'] in permission_list:
                        return True

                user_ids = DataScopeDao.getSysUserByRank(user_id, 'se.project_manage:list')
                if not user_ids:
                    return False

                if user_ids == ['*'] or (create_user.id in user_ids or owner_user.id in user_ids):
                    return True

                sub_task_list = SeProjectTaskDao.queryTaskByParentId(task_id)
                if not sub_task_list:
                    return False

                for sub_task in sub_task_list:
                    if (sub_task.created_by_id == user_id or sub_task.owner_id == user_id
                            or sub_task.created_by_id in user_ids or sub_task.owner_id in user_ids):
                        return True
                return False

            if not has_permission:
                raise AppException("查询失败，没有权限")

        schema = SeProjectTaskSchema()
        data = schema.dump(task)
        data["project_number"] = project.project_number
        data["project_subject"] = project.subject
        data["opportunity_number"] = project.opportunity_number
        data["created_by_name"] = create_user.display_name
        data["owner_name"] = owner_user.display_name
        data["support_type_1st"] = getSeProjectProjectType(data["support_type_1st"])
        data["support_type_2nd"] = getSeProjectProjectType(data["support_type_2nd"])
        data["application_type"] = project.application_type
        if data.get("assign_number") and data.get("parent_id"):
            data["task_number"] = data.get("assign_number")
        if task.owner_id == task.last_modified_by_id:
            data["last_modified_by_name"] = owner_user.display_name
        else:
            modified_user = SysUserDao.querySysUserById(task.last_modified_by_id)
            if modified_user:
                data["last_modified_by_name"] = modified_user.display_name

        return data

    @permission.check(p_list['p_se_project_manage_list'])
    def delete(self, task_id):
        """
        子任务删除
        :return:
        """
        task = SeProjectTaskDao.queryTaskById(task_id)
        if not task:
            return jsonify(AppResponse())

        if not (task.created_by_id == session['user_id'] or task.owner_id == session['user_id']):
            raise AppException("删除失败，没有权限")

        if task.status == 4:
            delete_data = {"last_modified_by_id": session["user_id"], "deleted_by_id": session["user_id"]}
            SeProjectTaskDao.deleteTaskById(task_id, delete_data)
        else:
            raise AppException("删除失败，任务进行中无法删除")

        SeProjectOS(task.project_id).logTaskDelete(
            task.id, task.task_number if task.parent_id else task.event_number, task.subject
        )

        return jsonify(AppResponse())


post_record_parser = RequestParser()
post_record_parser.add_argument('support_start_date', location='json', type=validate_null, required=True)
post_record_parser.add_argument('support_end_date', location='json', type=validate_null, required=True)
post_record_parser.add_argument('support_duration', location='json', type=validate_half_hour, required=True)
post_record_parser.add_argument('support_location', location='json', type=str, required=True)
post_record_parser.add_argument('support_location_adcode', location='json', type=str, required=True)
post_record_parser.add_argument('record_content', location='json', type=list, required=True)
post_record_parser.add_argument('status', location='json', type=validate_null, choices=[1, 4], required=True)
post_record_parser.add_argument('attachments', location='json', type=list)


@projectmanage_api.resource('/task/<task_id>/record')
class RecordAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def post(self, task_id):
        """
        创建日志, 支持日期、所用工时、一些动态字段、附件、草稿、发布
        :return:
        """
        parser_args = prepare_args_for_parser(post_record_parser.copy())
        params = parser_args.parse_args()

        task = SeProjectTaskDao.queryTaskById(task_id)
        if not task.parent_id and task.status == 4:
            raise AppException("创建失败，任务未启用")

        if task.status == 2:
            raise AppException("任务已归档，无法提交日志")

        data = {"id": ""}
        params["task_id"] = task_id
        params["record_content"] = json.dumps(params["record_content"], ensure_ascii=False)
        params['created_by_id'] = session['user_id']
        params['last_modified_by_id'] = session['user_id']

        attachments = params.get("attachments")
        if 'attachments' in params.keys():
            params.pop('attachments')

        schema = SeProjectRecordSchema()
        record = schema.load(params)
        _id = SeProjectRecordDao.addRecord(record)
        data["id"] = _id

        if attachments:
            for attachment_id in attachments:
                update_data = {"related_object_id": _id}
                SysAttachmentDao.updateAttachmentById(attachment_id, update_data)

        if task.parent_id and task.status == 4:
            update_data = {"status": 1, "last_modified_by_id": session['user_id']}
            SeProjectTaskDao.updateTaskById(task_id, update_data)

        if params["status"] == 4:
            task = SeProjectTaskDao.queryTaskById(task_id)
            if not task:
                return AppException("创建成功，审批流程创建失败")

            main_task_id = task.parent_id if task.parent_id else task_id
            main_task_pco = SeProjectTaskDao.getTaskJoinSysUserById(main_task_id)
            if not main_task_pco:
                return AppException("创建成功，审批流程创建失败")
            main_task, project, main_task_cu, main_task_ou = main_task_pco
            main_task_user = SysUserDao.querySysUserById(main_task.created_by_id)
            record_user = SysUserDao.querySysUserById(record.created_by_id)
            if not record:
                return AppException("创建成功，邮件通知失败")
            project_owner = SysUserDao.querySysUserById(project.owner_id)
            if not project_owner:
                return AppException("审批成功，邮件通知失败")
            project_sales = SysUserDao.querySysUserById(project.sale_by_id)
            project_sales = project_sales.display_name if project_sales else ""

            site_domain = current_app.config["SITE_DOMAIN"]
            record_content = ""
            record_content_load = json.loads(record.record_content)
            for content in record_content_load:
                if content.get("type") == "tip":
                    continue
                record_content += f'{content.get("name")}: {content.get("content")}  <br/>'

            target, cc, replay, cc_reason = [record_user.email], [], record_user.email, ""

            def notice(**kwargs):
                try:
                    message_gw.push(**kwargs)
                except Exception as e:
                    logger.error("RecordAPI Exception: {}".format(str(e)))
                    
            if main_task.created_by_id == session['user_id']:
                update_record = {"status": 2}
                SeProjectRecordDao.updateRecordById(_id, update_record)

                task_taken_hours = 0
                all_record = SeProjectRecordDao.queryRecordByStatus(task.id, '2')
                for publish_record in all_record:
                    task_taken_hours += round(publish_record.support_duration / 60, 1)
                update_data = {"last_modified_by_id": session['user_id'], "taken_hours": task_taken_hours}
                SeProjectTaskDao.updateTaskById(record.task_id, update_data)

                update_data = {"last_modified_by_id": session['user_id']}
                SeProjectProjectDao.updateProjectById(task.project_id, update_data)

                record = SeProjectRecordDao.queryRecordById(_id)
                if not record:
                    return AppException("创建成功，邮件通知失败")

                if record_user.employee_id:
                    employee = TblEmployeeDao.queryEmployeeById(record_user.employee_id)
                    if employee:
                        leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                        if leader_employee:
                            cc.append(leader_employee.email)
                            cc_reason += f'{leader_employee.email}: 任务创建人EHR上级 <br/>'

                        department_manage = apollo_util.getValue("se_project_department_manage")
                        if employee.department in department_manage:
                            department_employee_id = department_manage.get(employee.department)
                            department_employee = TblEmployeeDao.queryEmployeeByUserId(department_employee_id)
                            if department_employee:
                                cc.append(department_employee.email)
                                cc_reason += f'{leader_employee.email}: 日志创建人部门领导 <br/>'

                cc_user_list = []
                if project.sale_by_id:
                    cc_user_list.append(project.sale_by_id)
                    cc_reason += f'{project.sale_by_id}(sale_by_id): 项目销售 <br/>'
                if project.sales_leader_id:
                    cc_user_list.append(project.sales_leader_id)
                    cc_reason += f'{project.sales_leader_id}(sales_leader_id): 项目销售上级 <br/>'
                if project.owner_id:
                    cc_user_list.append(project.owner_id)
                    cc_reason += f'{project.owner_id}(owner_id): 项目负责人 <br/>'
                if record_user.manage_id:
                    cc_user_list.append(record_user.manage_id)
                    cc_reason += f'{record_user.manage_id}(manage_id): 日志创建人站点上级 <br/>'
                focus = SeProjectFocusDao.queryFocusByProject(project.id)
                for f in focus:
                    cc_user_list.append(f.follower_id)
                    cc_reason += f'{f.follower_id}(follower_id): 项目关注人 <br/>'

                if cc_user_list:
                    cc_user_list = SysUserDao.querySysUserByIds(list(set(cc_user_list)))
                    for cc_user in cc_user_list:
                        cc.append(cc_user.email)
                cc = list(set(cc))
                es_res = ESService.querySeProjectByProjectId(project.id)
                project_taken_hours = 0
                if es_res.get("tasks"):
                    for es_res_task in es_res.get("tasks"):
                        if es_res_task.get("record"):
                            for es_res_record in es_res_task.get("record"):
                                if es_res_record.get("status") == 2:
                                    project_taken_hours+= round(es_res_record["support_duration"]/60, 1)
                template = SeProjectRecordApprovedEmail()
                template.update({
                    "task_id": task.id, "task_number": task.task_number if task.parent_id else task.event_number,
                    "subject": task.subject,
                    "created_by_name": record_user.display_name, "approver": main_task_cu.display_name,
                    "site_domain": site_domain,
                    "support_type_1st": getSeProjectProjectType(task.support_type_1st)["name"],
                    "support_type_2nd": getSeProjectProjectType(task.support_type_2nd)["name"],
                    "published_date": record.published_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_start_date": record.support_start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_end_date": record.support_end_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_duration": record.support_duration / 60,
                    "record_content": record_content,
                    "account_name": project.account_name,
                    "project_name": project.subject,
                    "record_data": json.loads(record.record_content),
                    "project_owner_name": project_owner.display_name,
                    "project_sales_by_name": project_sales,
                    "project_opportunity_number": project.opportunity_number,
                    "project_opportunity_name": project.opportunity_name,
                    "project_subject": project.subject,
                    "cc_reason": cc_reason,
                    "project_customer_requirement": project.customer_requirement,
                    "project_total_support_duration": project_taken_hours
                })
                SeProjectOS(task.project_id, params).logRecordPublish(_id)

            else:
                approval_record = {"record_id": _id, "project_id": project.id, "main_task_id": main_task.id}
                schema = SeProjectApprovalRecordSchema()
                approval_record = schema.load(approval_record)
                SeProjectApprovalDao.addRecord(approval_record)

                template = SeProjectRecordPendingEmail()
                template.update({
                    "task_number": task.task_number if task.parent_id else task.event_number,
                    "subject": task.subject,
                    "created_by_name": record_user.display_name,
                    "site_domain": site_domain, "record_content": record_content
                })
                target = [main_task_user.email]

                app_template = SeProjectRecordApprovedDICAPP()
                app_template.update({
                    "record_id": record.id,
                    "task_name": task.subject,
                    "account_name": project.account_name,
                    "support_type_1st": getSeProjectProjectType(task.support_type_1st)["name"],
                    "support_type_2nd": getSeProjectProjectType(task.support_type_2nd)["name"],
                    "support_start_date": record.support_start_date.strftime('%Y-%m-%d %H:%M'),
                    "support_duration": str(round(float(record.support_duration/60), 1)),
                    "record_creator": record_user.display_name,
                    "support_location": record.support_location
                })
                try:
                    app_template_target = main_task_user.email
                    match = re.match(r"^(.*?)@", app_template_target)
                    app_template_target = match.group(1)
                except:
                    raise AppException(message="小程序通知人获取失败")
                executor.submit(notice, target=app_template_target, template=app_template, source="dic_app")
                SeProjectOS(task.project_id, params).logRecordSubmit(
                    _id, main_task_user.id, main_task_user.display_name
                )

            executor.submit(notice, target=target, template=template, reply_to=replay, cc=cc)

        return jsonify(AppResponse(data))


put_record_parser = RequestParser()
put_record_parser.add_argument('support_start_date', location='json', type=validate_null)
put_record_parser.add_argument('support_end_date', location='json', type=validate_null)
put_record_parser.add_argument('support_duration', location='json', type=int)
put_record_parser.add_argument('support_location', location='json', type=str, required=True)
put_record_parser.add_argument('support_location_adcode', location='json', type=str, required=True)
put_record_parser.add_argument('record_content', location='json', type=list)
put_record_parser.add_argument('status', location='json', type=validate_null, choices=[1, 4])
put_record_parser.add_argument('attachments', location='json', type=list)


@projectmanage_api.resource('/record/<record_id>')
class RecordEditAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def put(self, record_id):
        """
        编辑日志，判断是否草稿、只能草稿改发布
        :return:
        """
        parser_args = prepare_args_for_parser(put_record_parser.copy())
        params = parser_args.parse_args()
        user_id = session['user_id']
        record = SeProjectRecordDao.queryRecordById(record_id)
        if not record:
            raise AppException("编辑失败，日志不存在")

        task = SeProjectTaskDao.queryTaskById(record.task_id)
        # # 将字符串转换为datetime对象
        # time1 = datetime.strptime("2024-07-01 00:00:00", '%Y-%m-%d %H:%M:%S')
        # time2 = datetime.strptime("2024-07-13 00:00:00", '%Y-%m-%d %H:%M:%S')
        # if task.status == 2 and (record.created_date > time2 or record.created_date < time1):
        #    raise AppException("任务已归档，无法提交日志")

        if 'record_content' in params:
            params['record_content'] = json.dumps(params["record_content"], ensure_ascii=False)

        attachments = params.get("attachments")
        if 'attachments' in params.keys():
            params.pop('attachments')

        params['last_modified_by_id'] = user_id
        SeProjectRecordDao.updateRecordById(record_id, params)
        if attachments:
            old_attachments = SysAttachmentDao.queryAttachmentByObjectId("se_project_record", record_id)
            old_attachments_id = [attachment.id for attachment in old_attachments] if old_attachments else []
            for old_attachment_id in old_attachments_id:
                if old_attachment_id not in  attachments:
                    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    update_data = {"deleted_by_id": user_id, "related_object_id": "", "deleted_date": date}
                    SysAttachmentDao.updateAttachmentById(old_attachment_id, update_data)
            for attachment_id in attachments:
                update_data = {"related_object_id": record_id}
                SysAttachmentDao.updateAttachmentById(attachment_id, update_data)

        if params.get("status") == 4:
            record = SeProjectRecordDao.queryRecordById(record_id)
            if not record:
                return AppException("创建成功，邮件通知失败")
            record_user = SysUserDao.querySysUserById(record.created_by_id)
            if not record_user:
                return AppException("创建成功，邮件通知失败")
            task = SeProjectTaskDao.queryTaskById(record.task_id)
            if not task:
                return AppException("日志更新成功，审批流程创建失败")
            main_task_id = task.parent_id if task.parent_id else task.id
            main_task_pco = SeProjectTaskDao.getTaskJoinSysUserById(main_task_id)
            if not main_task_pco:
                return AppException("创建成功，审批流程创建失败")
            main_task, project, main_task_cu, main_task_ou = main_task_pco
            main_task_user = SysUserDao.querySysUserById(main_task.created_by_id)
            project_owner = SysUserDao.querySysUserById(project.owner_id)
            if not project_owner:
                return AppException("审批成功，邮件通知失败")
            project_sales = SysUserDao.querySysUserById(project.sale_by_id)
            project_sales = project_sales.display_name if project_sales else ""

            site_domain = current_app.config["SITE_DOMAIN"]
            record_content = ""
            record_content_load = json.loads(record.record_content)
            for content in record_content_load:
                if content.get("type") == "tip":
                    continue
                record_content += f'{content.get("name")}: {content.get("content")}  <br/>'
            target, cc, replay, cc_reason = [record_user.email], [], record_user.email, ""

            def notice(**kwargs):
                try:
                    message_gw.push(**kwargs)
                except Exception as e:
                    logger.error("RecordEditAPI Exception: {}".format(str(e)))

            if main_task.created_by_id == user_id:
                update_record = {"status": 2}
                SeProjectRecordDao.updateRecordById(record_id, update_record)

                task_taken_hours = 0
                all_record = SeProjectRecordDao.queryRecordByStatus(task.id, '2')
                for publish_record in all_record:
                    task_taken_hours += round(publish_record.support_duration/60, 1)
                update_data = {"last_modified_by_id": user_id, 'taken_hours': task_taken_hours}
                SeProjectTaskDao.updateTaskById(task.id, update_data)

                update_data = {"last_modified_by_id": user_id}
                SeProjectProjectDao.updateProjectById(task.project_id, update_data)

                if record_user.employee_id:
                    employee = TblEmployeeDao.queryEmployeeById(record_user.employee_id)
                    if employee:
                        leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                        if leader_employee:
                            cc.append(leader_employee.email)
                            cc_reason += f'{leader_employee.email}: 任务创建人EHR上级 <br/>'

                        department_manage = apollo_util.getValue("se_project_department_manage")
                        if employee.department in department_manage:
                            department_employee_id = department_manage.get(employee.department)
                            department_employee = TblEmployeeDao.queryEmployeeByUserId(department_employee_id)
                            if department_employee:
                                cc.append(department_employee.email)
                                cc_reason += f'{leader_employee.email}: 日志创建人部门领导 <br/>'

                cc_user_list = []
                if project.sale_by_id:
                    cc_user_list.append(project.sale_by_id)
                    cc_reason += f'{project.sale_by_id}(sale_by_id): 项目销售 <br/>'
                if project.sales_leader_id:
                    cc_user_list.append(project.sales_leader_id)
                    cc_reason += f'{project.sales_leader_id}(sales_leader_id): 项目销售上级 <br/>'
                if project.owner_id:
                    cc_user_list.append(project.owner_id)
                    cc_reason += f'{project.owner_id}(owner_id): 项目负责人 <br/>'
                if record_user.manage_id:
                    cc_user_list.append(record_user.manage_id)
                    cc_reason += f'{record_user.manage_id}(manage_id): 日志创建人站点上级 <br/>'
                focus = SeProjectFocusDao.queryFocusByProject(project.id)
                for f in focus:
                    cc_user_list.append(f.follower_id)
                    cc_reason += f'{f.follower_id}(follower_id): 项目关注人 <br/>'
                cc = list(set(cc))
                es_res = ESService.querySeProjectByProjectId(project.id)
                project_taken_hours = 0
                if es_res.get("tasks"):
                    for es_res_task in es_res.get("tasks"):
                        if es_res_task.get("record"):
                            for es_res_record in es_res_task.get("record"):
                                if es_res_record.get("status") == 2:
                                    project_taken_hours+= round(es_res_record["support_duration"]/60, 1)
                template = SeProjectRecordApprovedEmail()
                template.update({
                    "task_id": task.id, "task_number": task.task_number if task.parent_id else task.event_number,
                    "subject": task.subject,
                    "created_by_name": record_user.display_name, "approver": main_task_cu.display_name,
                    "site_domain": site_domain,
                    "support_type_1st": getSeProjectProjectType(task.support_type_1st)["name"],
                    "support_type_2nd": getSeProjectProjectType(task.support_type_2nd)["name"],
                    "published_date": record.published_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_start_date": record.support_start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_end_date": record.support_end_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_duration": record.support_duration / 60,
                    "record_content": record_content,
                    "account_name": project.account_name,
                    "project_name": project.subject,
                    "record_data": json.loads(record.record_content),
                    "project_owner_name": project_owner.display_name,
                    "project_sales_by_name": project_sales,
                    "project_opportunity_number": project.opportunity_number,
                    "project_opportunity_name": project.opportunity_name,
                    "project_subject": project.subject,
                    "cc_reason": cc_reason,
                    "project_customer_requirement": project.customer_requirement,
                    "project_total_support_duration": project_taken_hours
                })
                SeProjectOS(task.project_id, params).logRecordPublish(record_id)

            else:
                approval_record = {"record_id": record_id, "project_id": project.id, "main_task_id": main_task.id}
                schema = SeProjectApprovalRecordSchema()
                approval_record = schema.load(approval_record)
                SeProjectApprovalDao.addRecord(approval_record)

                template = SeProjectRecordPendingEmail()
                template.update({
                    "task_number": task.task_number if task.parent_id else task.event_number,
                    "subject": task.subject,
                    "created_by_name": record_user.display_name,
                    "site_domain": site_domain, "record_content": record_content
                })
                target = [main_task_user.email]

                app_template = SeProjectRecordApprovedDICAPP()
                app_template.update({
                    "record_id": record.id,
                    "task_name": task.subject,
                    "account_name": project.account_name,
                    "support_type_1st": getSeProjectProjectType(task.support_type_1st)["name"],
                    "support_type_2nd": getSeProjectProjectType(task.support_type_2nd)["name"],
                    "support_start_date": record.support_start_date.strftime('%Y-%m-%d %H:%M'),
                    "support_duration": str(round(float(record.support_duration/60), 1)),
                    "record_creator": record_user.display_name,
                    "support_location": record.support_location
                })
                try:
                    app_template_target = main_task_user.email
                    match = re.match(r"^(.*?)@", app_template_target)
                    app_template_target = match.group(1)
                except:
                    raise AppException(message="小程序通知人获取失败")
                executor.submit(notice, target=app_template_target, template=app_template, source="dic_app")
                SeProjectOS(task.project_id, params).logRecordSubmit(
                    record_id, main_task_user.id, main_task_user.display_name
                )

            executor.submit(notice, target=target, template=template, reply_to=replay, cc=cc)

        return jsonify(AppResponse())

    @permission.check(p_list['p_se_project_manage_list'])
    def delete(self, record_id):
        """
        删除草稿日志
        :return:
        """
        record = SeProjectRecordDao.queryRecordById(record_id)
        if not record:
            raise AppException("查询失败，日志不存在")

        delete_data = {"deleted_by_id": session['user_id'], "status": 3, 'last_modified_by_id': session['user_id']}
        SeProjectRecordDao.deleteRecordById(record_id, delete_data)

        return jsonify(AppResponse())


get_record_parser = RequestParser()
get_record_parser.add_argument('status', location='args', type=int, choices=[1, 2, 4], required=True)
get_record_parser.add_argument('page', location='args', type=int, default=1, required=True)
get_record_parser.add_argument('size', location='args', type=int, default=1000, required=True)


@projectmanage_api.resource('/task/<task_id>/record')
class RecordListAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectRecordList)
    def get(self, task_id):
        """
        日志列表（草稿、审批中、发布列表）
        :return:
        """
        parser_args = prepare_args_for_parser(get_record_parser.copy())
        params = parser_args.parse_args()

        data = {"list": [], "total": 0, "page": 1, "size": 0}

        task_pco = SeProjectTaskDao.getTaskJoinSysUserById(task_id)
        if not task_pco:
            raise AppException("查询失败，任务不存在")

        task, project, create_user, owner_user = task_pco
        user_id = session["user_id"]
        if not (user_id == create_user.id or user_id == owner_user.id or
                user_id == project.created_by_id or user_id == project.owner_id):
            def has_permission():
                if project.is_big_project_support == '是':
                    permission_list = permission.getPermissionByUserId(user_id)
                    if p_list['p_se_project_manage_support'] in permission_list:
                        return True

                user_ids = DataScopeDao.getSysUserByRank(user_id, 'se.project_manage:list')
                if not user_ids:
                    return False

                if user_ids == ['*'] or (create_user.id in user_ids or owner_user.id in user_ids):
                    return True

                if not task.parent_id:
                    sub_task_list = SeProjectTaskDao.queryTaskByParentId(task_id)
                    if not sub_task_list:
                        return False

                    for sub_task in sub_task_list:
                        if (sub_task.created_by_id == user_id or sub_task.owner_id == user_id
                                or sub_task.created_by_id in user_ids or sub_task.owner_id in user_ids):
                            return True
                return False

            if not has_permission:
                raise AppException("查询失败，没有权限")

        if params["status"] == 1:
            task = SeProjectTaskDao.queryTaskById(task_id)
            if task.owner_id != session["user_id"]:
                return data

        record_create_list = SeProjectRecordDao.getRecordJoinSysUserByStatus(task_id, params["status"])
        if not record_create_list:
            return data

        for record_c in record_create_list:
            record, create_user = record_c
            schema = SeProjectRecordSchema()
            record = schema.dump(record)

            record["task_number"] = task.task_number
            record["task_subject"] = task.subject
            record["task_parent_id"] = task.parent_id
            record["task_event_number"] = task.event_number

            record["record_content"] = json.loads(record["record_content"])
            record["created_by_name"] = create_user.display_name
            record["support_type_1st"] = getSeProjectProjectType(task.support_type_1st)
            record["support_type_2nd"] = getSeProjectProjectType(task.support_type_2nd)
            record["attachments"] = []
            attachments = SysAttachmentDao.queryAttachmentByObjectId("se_project_record", record["id"])
            for attachment in attachments:
                record["attachments"].append({
                    "id": attachment.id,
                    "filename": attachment.file_name,
                    "file_size": attachment.file_size,
                    "file_type": attachment.file_type
                })

            if record["status"] == 4:
                approval_record = SeProjectApprovalDao.queryApprovalRecordByRecordId(record["id"])
                if approval_record:
                    task_co = SeProjectTaskDao.getTaskJoinSysUserById(approval_record.main_task_id)
                    if task_co:
                        task, project, create_user, owner_user = task_co
                        record["approval_id"] = create_user.id
                        record["approval_name"] = create_user.display_name
                        if task.status == 1:
                            record["permission"] = ["return"]

            if record["status"] == 1:
                approval_record = SeProjectApprovalDao.queryUnApprovalByRecordId(record["id"])
                if approval_record:
                    record["unapproval_reason"] = approval_record.incomplete_reason

            if record["status"] == 2 and project.created_by_id == user_id:
                record["permission"] = ["return"]

            data["list"].append(record)

        data["total"] = len(record_create_list)
        data["size"] = len(record_create_list)

        return data


all_record_parser = RequestParser()
all_record_parser.add_argument('status', location='args', type=int, choices=[2], required=True)


@projectmanage_api.resource('/main_task/<main_task>/all_record')
class TaskAllRecordListAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectRecordList)
    def get(self, main_task):
        """
        查询主任务下所有子任务以及自身的日志列表
        :return:
        """
        parser_args = prepare_args_for_parser(all_record_parser.copy())
        params = parser_args.parse_args()

        data = {"list": []}

        task_pco = SeProjectTaskDao.getTaskJoinSysUserById(main_task)
        if not task_pco:
            raise AppException("查询失败，任务不存在")

        task, project, create_user, owner_user = task_pco
        if task.parent_id:
            raise AppException("查询失败，非主任务不允许查询")

        sub_task_list = SeProjectTaskDao.queryTaskByParentId(main_task)

        user_id = session["user_id"]
        if not (user_id == create_user.id or user_id == owner_user.id or
                user_id == project.created_by_id or user_id == project.owner_id):
            def has_permission():
                if project.is_big_project_support == '是':
                    permission_list = permission.getPermissionByUserId(user_id)
                    if p_list['p_se_project_manage_support'] in permission_list:
                        return True

                user_ids = DataScopeDao.getSysUserByRank(user_id, 'se.project_manage:list')
                if not user_ids:
                    return False

                if user_ids == ['*'] or (create_user.id in user_ids or owner_user.id in user_ids):
                    return True

                if not sub_task_list:
                    return False

                for sub_task in sub_task_list:
                    if (sub_task.created_by_id == user_id or sub_task.owner_id == user_id
                            or sub_task.created_by_id in user_ids or sub_task.owner_id in user_ids):
                        return True
                return False

            if not has_permission:
                raise AppException("查询失败，没有权限")

        task_ids = [main_task]
        for sub_task in sub_task_list:
            task_ids.append(sub_task.id)

        record_create_list = SeProjectRecordDao.getAllRecordJoinSysUserByStatus(task_ids, params["status"])
        if not record_create_list:
            return data

        for record_c in record_create_list:
            record, create_user = record_c
            schema = SeProjectRecordSchema()
            record = schema.dump(record)

            record["task_number"] = task.task_number
            record["task_subject"] = task.subject
            record["task_parent_id"] = task.parent_id
            record["task_event_number"] = task.event_number

            record["record_content"] = json.loads(record["record_content"])
            record["created_by_name"] = create_user.display_name
            record["support_type_1st"] = getSeProjectProjectType(task.support_type_1st)
            record["support_type_2nd"] = getSeProjectProjectType(task.support_type_2nd)
            record["attachments"] = []
            attachments = SysAttachmentDao.queryAttachmentByObjectId("se_project_record", record["id"])
            for attachment in attachments:
                record["attachments"].append({
                    "id": attachment.id,
                    "filename": attachment.file_name,
                    "file_size": attachment.file_size,
                    "file_type": attachment.file_type
                })

            if record["status"] == 2 and project.created_by_id == user_id:
                record["permission"] = ["return"]

            data["list"].append(record)

        return data


get_permission_parser = RequestParser()
get_permission_parser.add_argument('task_id', location='args', type=str)
get_permission_parser.add_argument('project_id', location='args', type=str)


@projectmanage_api.resource('/permission/<page_title>')
class PagePermissionAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def get(self, page_title):
        """
        操作权限查询
        :return:
        """
        parser_args = prepare_args_for_parser(get_permission_parser.copy())
        params = parser_args.parse_args()

        data = {"list": []}
        if page_title == 'project_detail':
            if not params.get("project_id"):
                raise AppException("参数错误，项目ID不能为空")

            project = SeProjectProjectDao.queryProjectById(params['project_id'])
            if not project:
                raise AppException("获取失败，项目不存在")

            if (project.owner_id == session['user_id'] or project.created_by_id == session['user_id'])\
                    and project.status != 3:
                task_co = SeProjectTaskDao.queryTaskByProjectId(params['project_id'])
                task_status = [task.status for task in task_co]
                if 1 not in task_status:
                    data["list"] = ["project_archive"]

            subordinate_list = DataScopeDao.getSuperiorsIdById(project.created_by_id)
            superiors_ids = [sysuser.id for sysuser, employee in subordinate_list] + [project.created_by_id]
            if (project.owner_id == session['user_id']) and project.status != 3:
                data["list"].append("project_mutation")

            if session['user_id'] in superiors_ids and project.status != 3:
                data["list"].append("project_leader_editor")

            if project.status == 1 and project.owner_id == session['user_id']:
                data["list"].append("project_enable")
                data["list"].append("project_return")

            if (project.status in [1, 2]
                    and (project.owner_id == session['user_id'] or project.created_by_id == session['user_id'])
                    and permission.userPermission(session['user_id'], p_list['p_se_project_manage_combine'])):
                data["list"].append("project_combine")

            owner_subordinate_list = DataScopeDao.getSuperiorsIdById(project.owner_id)
            superiors_ids += [project.owner_id]
            superiors_ids += [sysuser.id for sysuser, employee in owner_subordinate_list]
            if session['user_id'] in superiors_ids:
                data["list"].append("project_record")

        elif page_title == 'project':
            project_so = SeProjectProjectDao.queryProjectByCreateById(session['user_id'])
            if project_so:
                data["list"] = ["record_approval", "task_approval"]

        elif page_title == 'record_detail':
            project_so = SeProjectProjectDao.queryProjectByCreateById(session['user_id'])
            if project_so:
                data["list"] = ["record_approval"]

        elif page_title == 'task_detail':
            if not params.get("task_id"):
                raise AppException("参数错误，任务ID不能为空")

            task = SeProjectTaskDao.queryTaskById(params.get("task_id"))
            if not task:
                raise AppException("获取失败，任务不存在")

            if task.owner_id == session['user_id'] and task.status == 1:
                data["list"] = ["create_record"]
                if not task.parent_id:
                    data["list"] += ["create_subtask"]

                record = SeProjectRecordDao.queryRecordByStatus(task.id, '4')
                if not record and task.parent_id:
                    data["list"] += ["task_archive"]
                elif not task.parent_id and not record:
                    task_co = SeProjectTaskDao.queryTaskByParentId(task.id)
                    task_status = [task_.status for task_ in task_co]
                    if 1 not in task_status or 5 not in task_status:
                        data["list"] += ["task_archive"]
            elif task.owner_id == session['user_id'] and task.status == 4:
                data["list"] = ["task_enable"]
                if not task.parent_id or (task.parent_id and task.assign_number):
                    data["list"] += ["task_return"]

        return jsonify(AppResponse(data))


task_archive_parser = RequestParser()
task_archive_parser.add_argument('task_result', location='json', type=int, choices=[1, 2], required=True)
task_archive_parser.add_argument('task_incomplete_reason', location='json', type=str)


@projectmanage_api.resource('/task/<task_id>/archive')
class TaskAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def put(self, task_id):
        """
        任务归档提交
        :return:
        """
        parser_args = prepare_args_for_parser(task_archive_parser.copy())
        params = parser_args.parse_args()

        record_list = SeProjectRecordDao.getRecordJoinSeProjectTaskByStatus(task_id=task_id, status=[1, 4])
        if record_list:
            draft_record_count, approval_record_count = 0, 0
            for record_c in record_list:
                record, task = record_c
                if record.status == 1:
                    draft_record_count += 1
                elif record.status == 4:
                     approval_record_count += 1
            raise AppException(message=f"任务当前存在{draft_record_count}个草稿, {approval_record_count}个待审批状态日志, 无法进行归档")
        
        if params["task_result"] == 2 and not params.get("task_incomplete_reason"):
            raise AppException("归档失败，请填写未完成的原因")

        task = SeProjectTaskDao.queryTaskById(task_id)
        if not task:
            raise AppException("归档失败，任务不存在")

        if task.owner_id != session['user_id']:
            raise AppException("归档失败，只可任务负责人提交归档")

        if task.status == 2:
            raise AppException("归档失败，任务已归档")

        approvaling_task = SeProjectApprovalDao.queryApprovalingRecordByTaskId(task_id)
        if approvaling_task and task.status == 5:
            raise AppException("提交失败，归档请求已提交")

        if not task.parent_id:
            undone_task_list = SeProjectTaskDao.queryUndoneTaskByParentId(task.id)
            if undone_task_list:
                undone_id = ','.join([undone_task.task_number for undone_task in undone_task_list])
                raise AppException(f"归档失败，任务{undone_id}未结束")

        approval_record_list = SeProjectRecordDao.queryApprovalRecordByTaskId(task.id)
        if approval_record_list:
            raise AppException(f"当前任务有{len(approval_record_list)}个日志正在审批，无法进行归档操作")

        def notice(**kwargs):
            try:
                message_gw.push(**kwargs)
            except Exception as e:
                logger.error("Task Archive Exception: {}".format(str(e)))

        params['last_modified_by_id'] = session['user_id']
        params['status'] = 5
        SeProjectTaskDao.updateTaskById(task_id, params)

        site_domain = current_app.config["SITE_DOMAIN"]
        main_task = task
        if task.parent_id:
            main_task = SeProjectTaskDao.queryTaskById(task.parent_id)
        project = SeProjectProjectDao.queryProjectById(task.project_id)

        if main_task.created_by_id == session['user_id']:
            update_data = {"status": 2, "last_modified_by_id": session['user_id']}
            SeProjectTaskDao.updateTaskById(task_id, update_data)

            update_data = {"last_modified_by_id": session['user_id']}
            SeProjectProjectDao.updateProjectById(task.project_id, update_data)

            if task.parent_id:
                undone_task_list = SeProjectTaskDao.queryUndoneTaskByParentId(task.parent_id)
                if not undone_task_list:
                    owner_user = SysUserDao.querySysUserById(main_task.owner_id)
                    if main_task and owner_user:
                        template = SeProjectTaskArchiveEmail()
                        template.update({
                            "task_id": task.parent_id,
                            "task_number": main_task.task_number if main_task.parent_id else main_task.event_number,
                            "subject": main_task.subject, "site_domain": site_domain
                        })
                        executor.submit(notice, target=owner_user.email, template=template)

            elif not task.parent_id:
                undone_main_task_list = SeProjectTaskDao.queryUndoneMainTaskByProjectId(task.project_id)
                if not undone_main_task_list:
                    create_user = SysUserDao.querySysUserById(project.created_by_id)
                    if create_user:
                        template = SeProjectProjectArchiveEmail()
                        template.update({
                            "project_id": project.id, "project_number": project.opportunity_number,
                            "subject": project.subject, "site_domain": site_domain
                        })
                        executor.submit(notice, target=create_user.email, template=template)

            SeProjectOS(project.id, params).logTaskArchiveAuto(
                task.id, task.task_number if task.parent_id else task.event_number, task.subject
            )

        else:
            approval_record = {"task_id": task_id, "project_id": project.id, "main_task_id": main_task.id}
            schema = SeProjectApprovalRecordSchema()
            approval_record = schema.load(approval_record)
            SeProjectApprovalDao.addRecord(approval_record)

            owner_user = SysUserDao.querySysUserById(task.owner_id)
            main_task_create_user = SysUserDao.querySysUserById(main_task.created_by_id)
            if owner_user:
                template = SeProjectTaskApprovedEmail()
                template.update({
                    "task_number": task.task_number if task.parent_id else task.parent_id,
                    "created_by_name": owner_user.display_name,
                    "subject": project.subject, "site_domain": site_domain, "project_id": project.id,
                    "task_result": "完成" if params["task_result"] == 1 else "未完成",
                    "task_incomplete_reason": params.get("task_incomplete_reason")
                })
                executor.submit(notice, target=main_task_create_user.email, template=template, cc=owner_user.email)
            else:
                SeProjectOS(project.id, params).logTaskArchiveSubmit(
                    task.id, task.task_number if task.parent_id else task.event_number, task.subject,
                    main_task_create_user.id, main_task_create_user.display_name
                )

        update_data = {"last_modified_by_id": session['user_id']}
        SeProjectProjectDao.updateProjectById(task.project_id, update_data)

        return jsonify(AppResponse())


archive_project_parser = RequestParser()
archive_project_parser.add_argument('task_result', location='json', type=int, choices=[1, 2, 3, 4, 5], required=True)
archive_project_parser.add_argument('task_incomplete_reason', location='json', type=str)


@projectmanage_api.resource('/project/<project_id>/archive')
class ProjectArchiveAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def put(self, project_id):
        """
        项目归档
        :return:
        """
        parser_args = prepare_args_for_parser(archive_project_parser.copy())
        params = parser_args.parse_args()

        if params.get("task_result") in [2, 3, 4, 5] and not params.get("task_incomplete_reason"):
            raise AppException("操作失败，请填写未完成的原因")

        project = SeProjectProjectDao.queryProjectById(project_id)
        if not project:
            raise AppException("操作失败，项目不存在")

        if project.owner_id != session['user_id']:
            raise AppException("操作失败，只有项目负责人可以操作")

        undone_task_list = []
        task_list = SeProjectTaskDao.queryDoTaskByProjectId(project_id)
        for task in task_list:
            if task.status == 1 and not task.parent_id:
                undone_task_list.append(task)

        if undone_task_list:
            undone_id = ','.join([undone_task.task_number for undone_task in undone_task_list])
            raise AppException(f"归档失败，任务{undone_id}未结束")

        params["status"] = 3
        params['last_modified_by_id'] = session['user_id']
        SeProjectProjectDao.updateProjectById(project_id, params)
        project_result = project_enums["project_manage"]["project_result"][params.get("task_result")]
        SeProjectOS(project.id, params).logProjectArchive(
            project.id, project.opportunity_number, project.subject, project_result
        )

        return jsonify(AppResponse())


focus_project_parser = RequestParser()
# focus_project_parser.add_argument('project_id', location='json', type=validate_null, required=True)
focus_project_parser.add_argument('action', location='json', type=validate_null, choices=["Concern", "Unfollow"], required=True)


@projectmanage_api.resource('/project/<project_id>/focus')
class ProjectFocusAPI(Resource):

    # @permission.check("p_se_project_manage_list")
    def post(self, project_id):
        """
        关注项目
        :return:
        """
        parser_args = prepare_args_for_parser(focus_project_parser.copy())
        params = parser_args.parse_args()

        project = SeProjectProjectDao.queryProjectById(project_id)
        if not project:
            raise AppException("操作失败，项目不存在")

        params["follower_id"] = session['user_id']
        params["project_id"] = project_id

        action = params.get("action")
        if 'action' in params.keys():
            params.pop('action')

        schema = SeProjectFocusSchema()
        focus = schema.load(params)
        focus_ = SeProjectFocusDao.queryFocusByProjectId(session['user_id'], project_id)

        if action == 'Unfollow':
            if not focus_:
                raise AppException("取消关注失败，未关注该项目")

            SeProjectFocusDao.deleteFocusById(focus_.id, {})

            return jsonify(AppResponse())
        else:
            if focus_:
                update_data = {"deleted_date": None}
                SeProjectFocusDao.updateFocusById(focus_.id, update_data)
                _id = focus_.id
            else:
                _id = SeProjectFocusDao.addFocus(focus)
            data = {"id": _id}

        return jsonify(AppResponse(data))


@projectmanage_api.resource('/project/owner/list')
class ProjectOwnerAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def get(self):
        """
        项目负责人列表查询
        :return:
        """
        userid_list = []
        data = {"list": [{"id": "me", "display_name": "我"}, {"id": "my_subordinates", "display_name": "我的下属"}]}
        user_id, user_roles = session["user_id"], session['roles']
        user_ids = DataScopeDao.getSysUserByRank(user_id, 'se.project_manage:list')
        total, res = ESService.querySeProjectByFilter(user_ids)
        if res:
            for hit in res:
                project = hit["_source"]
                del project["tasks"]

                if project["owner_id"] not in userid_list and project["owner_id"]:
                    data["list"].append({"id": project["owner_id"], "display_name": project["owner_name"]})
                    userid_list.append(project["owner_id"])

        return jsonify(AppResponse(data))


@projectmanage_api.resource('/project/create_by/list')
class ProjectCreateAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def get(self):
        """
        项目创建人列表查询
        :return:
        """
        userid_list = []
        data = {"list": [{"id": "me", "display_name": "我"}, {"id": "my_subordinates", "display_name": "我的下属"}]}
        user_id, user_roles = session["user_id"], session['roles']
        user_ids = DataScopeDao.getSysUserByRank(user_id, 'se.project_manage:list')
        total, res = ESService.querySeProjectByFilter(user_ids)
        if res:
            for hit in res:
                project = hit["_source"]
                del project["tasks"]

                if project["created_by_id"] not in userid_list and project["created_by_id"]:
                    data["list"].append({"id": project["created_by_id"], "display_name": project["created_by_name"]})
                    userid_list.append(project["created_by_id"])

        return jsonify(AppResponse(data))


@projectmanage_api.resource('/project/participants/list')
class ProjectParticipantsAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def get(self):
        """
        项目参与人列表查询
        :return:
        """
        userid_list = []
        data = {"list": [{"id": "me", "display_name": "我"}, {"id": "my_subordinates", "display_name": "我的下属"}]}
        user_id, user_roles = session["user_id"], session['roles']
        user_ids = DataScopeDao.getSysUserByRank(user_id, 'se.project_manage:list')
        total, res = ESService.querySeProjectByFilter(user_ids)
        if res:
            for hit in res:
                project = hit["_source"]
                del project["tasks"]

                for participant in project["participants"]:
                    if participant["id"] not in userid_list and participant["id"]:
                        data["list"].append(participant)
                        userid_list.append(participant["id"])

        return jsonify(AppResponse(data))


@projectmanage_api.resource('/project/<project_id>/participants/list')
class ProjectParticipantsListAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectParticipantList)
    def get(self, project_id):
        """
        项目参与人列表
        :return:
        """
        participants = []
        data = {"list": participants}

        def get_participant(owner_id):
            sysuser, employee, department = SysUserDao.getSysUserEDById(owner_id)
            result = {
                "id": owner_id,
                "display_name": sysuser.display_name,
                "name": employee.name,
                "department": department.name,
                "position": employee.position
            }
            leader_data = TblEmployeeDao.getESByEmployeeId(employee.leader)
            if leader_data:
                leader, leader_sysuser = leader_data[0], leader_data[1]
                if leader:
                    result["leader"] = leader.name
                if leader_sysuser:
                    result["leader_id"] = leader_sysuser.id
            return result

        project = SeProjectProjectDao.queryProjectById(project_id)
        if project:
            participant = get_participant(project.owner_id)
            participant["role"] = "项目负责人"
            participants.append(participant)

        task_list = SeProjectTaskDao.queryTaskByProjectId(project_id)
        for task in task_list:
            exist = False
            for p in participants:
                if p["id"] == task.owner_id:
                    if task.parent_id and '负责人' not in p["role"]:
                        p["role"] += ", 子任务负责人"
                    elif task.parent_id and '主任务负责人' not in p["role"]:
                        p["role"] += ", 主任务负责人"
                    exist = True

            if not exist:
                participant = get_participant(task.owner_id)
                participant["role"] = "子任务负责人" if task.parent_id else "主任务负责人"
                participants.append(participant)

        return data


get_products_parser = RequestParser()
get_products_parser.add_argument('page', location='args', type=int, default=1, required=True)
get_products_parser.add_argument('size', location='args', type=int, default=1000, required=True)


@projectmanage_api.resource('/project/<project_id>/products')
class ProjectProductsAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def get(self, project_id):
        """
        查询项目报价产品的接口
        :return:
        """
        parser_args = prepare_args_for_parser(get_products_parser.copy())
        params = parser_args.parse_args()

        page, size = params["page"], params["size"]
        data = {"list": [], "total": 0, "page": page, "size": size}
        project = SeProjectProjectDao.queryProjectById(project_id)
        if not project:
            raise AppException("查询失败，项目不存在")

        crm_raw_data = json.loads(project.crm_raw_data)
        quote_products = crm_raw_data.get("quotedetailproductlist")

        if quote_products:
            data["list"] = quote_products[(page-1)*size:((page-1)*size+size)]
            data["total"] = len(quote_products)

        return jsonify(AppResponse(data))


get_task_archive_parser = RequestParser()
get_task_archive_parser.add_argument('page', location='args', type=int, default=1, required=True)
get_task_archive_parser.add_argument('size', location='args', type=int, default=1000, required=True)


@projectmanage_api.resource('/archive/task/list')
class ApprovalTaskListAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectTaskApprovalList)
    def get(self):
        """
        获取我的待审批归档任务列表
        :return:
        """
        parser_args = prepare_args_for_parser(get_task_archive_parser.copy())
        params = parser_args.parse_args()

        page, size = params["page"], params["size"]
        data = {"list": [], "total": 0, "page": page, "size": size}

        user_id = session["user_id"]
        approval_list = SeProjectApprovalDao.getApprovalTaskByUserId(user_id)
        if not approval_list:
            return data

        task_ids = [approval.task_id for approval in approval_list]
        task_pco_list = SeProjectTaskDao.getTasksJoinSysUserByIds(task_ids)
        if task_pco_list:
            for task_pco in task_pco_list:
                task, project, create_user, owner_user = task_pco

                schema = SeProjectTaskSchema()
                task = schema.dump(task)
                task["support_type_1st"] = getSeProjectProjectType(task["support_type_1st"])
                task["support_type_2nd"] = getSeProjectProjectType(task["support_type_2nd"])
                task["created_by_name"] = create_user.display_name
                task["owner_name"] = owner_user.display_name
                if task.get("assign_number") and task.get("parent_id"):
                    task["task_number"] = task.get("assign_number")
                if task["last_modified_by_id"] == owner_user.id:
                    task["last_modified_name"] = owner_user.display_name
                else:
                    modified_user = SysUserDao.querySysUserById(task["last_modified_by_id"])
                    task["last_modified_name"] = modified_user.display_name

                task["project_subject"] = project.subject
                data["list"].append(task)
            data["total"] = len(data["list"])
            data["list"] = data["list"][(page - 1) * size:((page - 1) * size + size)]
        return data


get_enable_task_parser = RequestParser()
get_enable_task_parser.add_argument('page', location='args', type=int, default=1, required=True)
get_enable_task_parser.add_argument('size', location='args', type=int, default=1000, required=True)


@projectmanage_api.resource('/enable/task/list')
class EnableTaskListAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectTaskApprovalList)
    def get(self):
        """
        待确认任务列表
        :return:
        """
        parser_args = prepare_args_for_parser(get_enable_task_parser.copy())
        params = parser_args.parse_args()

        page, size = params["page"], params["size"]
        data = {"list": [], "total": 0, "page": page, "size": size}
        user_id = session["user_id"]
        task_pco_list = SeProjectTaskDao.getPreEnableTaskJoinSysUserByCreateId(user_id)
        if task_pco_list:
            for task_pco in task_pco_list:
                task, project, create_user, owner_user = task_pco

                schema = SeProjectTaskSchema()
                task = schema.dump(task)
                task["support_type_1st"] = getSeProjectProjectType(task["support_type_1st"])
                task["support_type_2nd"] = getSeProjectProjectType(task["support_type_2nd"])
                task["created_by_name"] = create_user.display_name
                task["owner_name"] = owner_user.display_name
                if task.get("assign_number") and task.get("parent_id"):
                    task["task_number"] = task.get("assign_number")
                if task["last_modified_by_id"] == owner_user.id:
                    task["last_modified_name"] = owner_user.display_name
                else:
                    modified_user = SysUserDao.querySysUserById(task["last_modified_by_id"])
                    task["last_modified_name"] = modified_user.display_name

                task["project_subject"] = project.subject
                data["list"].append(task)
            data["total"] = len(data["list"])
            data["list"] = data["list"][(page - 1) * size:((page - 1) * size + size)]

        return data


get_opportunity_status_parser = RequestParser()
get_opportunity_status_parser.add_argument('project_ids[]', location='args', type=str, action='append', dest='project_ids')


@projectmanage_api.resource('/opportunity/status')
class OpportunityStatusAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def get(self):
        """
        获取项目商机状态
        :return:
        """
        data = {"list": []}

        parser_args = prepare_args_for_parser(get_opportunity_status_parser.copy())
        params = parser_args.parse_args()

        project_ids = params.get("project_ids")
        project_list = SeProjectProjectDao.queryProjectByIds(project_ids)
        opportunity_numbers, opportunity_map = [], {}
        for project in project_list:
            if project.opportunity_number:
                opportunity_numbers.append(project.opportunity_number)

        opportunity_list = CrmViewsDao.querySeProjectOpportunity(opportunity_numbers)
        for opportunity in opportunity_list:
            if opportunity[2] in opportunity_map:
                continue
            opportunity_map[opportunity[2]] = opportunity

        for project in project_list:
            if project.opportunity_number:
                if project.opportunity_number not in opportunity_map:
                    continue
                data["list"].append(
                    {"project_id": project.id, "status": opportunity_map[project.opportunity_number][3]}
                )

        return jsonify(AppResponse(data))


post_combine_parser = RequestParser()
post_combine_parser.add_argument('parent_project_id', location='json', type=str)


@projectmanage_api.resource('/project/<project_id>/combine')
class ProjectCombineAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    def post(self, project_id):
        """
        项目合并(子项目和父项目都未关闭)
        :return:
        """
        parser_args = prepare_args_for_parser(post_combine_parser.copy())
        params = parser_args.parse_args()

        parent_project_id = params.get("parent_project_id")

        parent_project = SeProjectProjectDao.queryProjectById(parent_project_id)
        if not parent_project:
            raise AppException("合并失败，父项目不存在")
        sub_project = SeProjectProjectDao.queryProjectById(project_id)
        if not sub_project:
            raise AppException("合并失败，子项目不存在")

        if parent_project.status == 1:
            raise AppException("合并失败，父项目未确认")
        if parent_project.status == 3:
            raise AppException("合并失败，父项目已归档")
        if parent_project.status == 4:
            raise AppException("合并失败，父项目已删除")
        if sub_project.status == 3:
            raise AppException("合并失败，子项目已归档")

        parent_project_id = parent_project.id
        log_params = {
            "src_project_id": sub_project.id, "src_project_number": sub_project.opportunity_number,
            "src_project_subject": sub_project.subject, "dst_project_id": parent_project_id,
            "dst_project_number": parent_project.opportunity_number, "dst_project_subject": parent_project.subject
        }
        update_sub_project = {
            "parent_project": parent_project_id,
            "status": 5
        }
        SeProjectProjectDao.updateProjectById(project_id, update_sub_project)

        project_task_list = SeProjectTaskDao.queryTaskByProjectId(project_id)
        task_ids = [task.id for task in project_task_list]
        update_task = {
            "project_id": parent_project_id,
            "origin_project": project_id
        }
        SeProjectTaskDao.updateTaskByIds(task_ids, update_task)

        SeProjectOS(parent_project_id, params).logProjectCombine(**log_params)

        data = {"id": parent_project_id}
        return jsonify(AppResponse(data))


@projectmanage_api.resource('/project/<project_id>/sub_project/list')
class SubProjectListAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeSubProjectProjectDetailList)
    def get(self, project_id):
        """
        查询本项目下子项目列表
        :return:
        """
        data = {"list": []}
        project_co = SeProjectProjectDao.getProjectJoinSysUserById(project_id)
        if not project_co:
            raise AppException("查询失败，项目不存在")

        project, create_user, owner_user = project_co
        user_id = session["user_id"]
        if not (user_id == create_user.id or user_id == owner_user.id):
            def has_permission():
                if project.is_big_project_support == '是':
                    permission_list = permission.getPermissionByUserId(user_id)
                    if p_list['p_se_project_manage_support'] in permission_list:
                        return True

                user_ids = DataScopeDao.getSysUserByRank(user_id, 'se.project_manage:list')
                if not user_ids:
                    return False

                if user_ids == ['*'] or (create_user.id in user_ids or owner_user.id in user_ids):
                    return True

                task_co_list = SeProjectTaskDao.getTaskJoinSysUserByProjectId(project_id)
                if not task_co_list:
                    return False

                for task_co in task_co_list:
                    if (task_co[0].owner_id == user_id or task_co[0].created_by_id == user_id
                            or task_co[0].owner_id in user_ids or task_co[0].created_by_id in user_ids):
                        return True
                return False

            if not has_permission:
                raise AppException("查询失败，没有权限")

        sub_project_list = SeProjectProjectDao.querySubProjectByParentId(project_id)
        if sub_project_list:
            for sub_project in sub_project_list:
                project_co = SeProjectProjectDao.getProjectJoinSysUserById(sub_project.id)
                project, create_user, owner_user = project_co
                sale_user = SysUserDao.querySysUserById(sub_project.sale_by_id)
                schema = SeProjectProjectSchema()
                sub_project_data = schema.dump(project)
                focus = SeProjectFocusDao.queryFocusByProjectId(user_id, sub_project.id)
                sub_project_data["focused"] = True if focus and not focus.deleted_date else False
                sub_project_data["project_phase"] = getSeProjectProjectType(sub_project_data['project_phase'])
                sub_project_data['sale_by_name'] = sale_user.display_name if sale_user else ''
                sub_project_data["created_by_name"] = create_user.display_name
                sub_project_data["owner_name"] = owner_user.display_name
                data["list"].append(sub_project_data)

        return data


get_user_task_parser = RequestParser()
get_user_task_parser.add_argument('page', location='args', type=int, default=1, required=True)
get_user_task_parser.add_argument('size', location='args', type=int, default=15, required=True)
get_user_task_parser.add_argument('status[]', location='args', type=int, action='append', dest='status')
get_user_task_parser.add_argument('task_number', location='args', type=str)
get_user_task_parser.add_argument('subject', location='args', type=str)
get_user_task_parser.add_argument('project_number', location='args', type=str)
get_user_task_parser.add_argument('project_subject', location='args', type=str)
get_user_task_parser.add_argument('created_date_range[]', location='args', type=str, action='append', dest='created_date_range')
get_user_task_parser.add_argument('support_mode[]', location='args', type=int, action='append', dest='support_mode')
get_user_task_parser.add_argument('task_result[]', location='args', type=int, action='append', dest='task_result')


@projectmanage_api.resource('/task/list/mine')
class UserTaskListAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(UserTaskListAPIResponse)
    def get(self):
        """
        项目管理-获取我的任务列表
        :return:
        """
        parser_args = prepare_args_for_parser(get_user_task_parser.copy())
        params = parser_args.parse_args()

        page, size = params["page"], params["size"]
        data = {"list": [], "total": 0, "page": page, "size": size}
        user_id = session["user_id"]

        status,subject = params.get('status'), params.get('subject')
        task_number = params.get('task_number')
        project_number = params.get('project_number')
        project_subject = params.get('project_subject')
        created_date_range = params.get('created_date_range')
        support_mode = params.get('support_mode')
        task_result = params.get('task_result')
        try:
            task_query, total = SeProjectTaskDao.getTaskProjectJoinSysUserByUserId(user_id, page, size, status, task_number,
                                     subject, project_number, project_subject, created_date_range, support_mode, task_result)
            task_set_list = task_query.all()
            if task_set_list:
                for task_set in task_set_list:
                    task, project, create_user, owner_user, last_modified_user = task_set
                    schema = SeProjectTaskSchema()
                    task = schema.dump(task)
                    task["taken_hours"] = 0
                    record_create_list = SeProjectRecordDao.getRecordJoinSysUserByStatus(task_id=task["id"], status=2)
                    if record_create_list:
                        for record_c in record_create_list:
                            record, create_user = record_c
                            task["taken_hours"] += record.support_duration
                    task["taken_hours"] = round(float(task["taken_hours"] / 60 ), 1)
                    operate_permission = []
                    if task["owner_id"] == user_id and task["status"] in [1, 4]:
                        if task["status"] == 1:
                            operate_permission.append("create_record")
                            operate_permission.append("task_archive")
                        if task["parent_id"]:
                            if task["status"] == 4:
                                operate_permission.append("delete_subtask")
                        else:
                            if task["status"] == 1:
                                operate_permission.append("create_subtask")
                    if task.get("assign_number") and task.get("parent_id"):
                        task["task_number"] = task.get("assign_number")
                    task["permission"] = operate_permission
                    task["support_type_1st"] = getSeProjectProjectType(task["support_type_1st"])
                    task["support_type_2nd"] = getSeProjectProjectType(task["support_type_2nd"])
                    task["created_by_name"] = create_user.display_name
                    task["owner_name"] = owner_user.display_name
                    task["last_modified_name"] = last_modified_user.display_name
                    task["project_id"] = project.id
                    task["project_number"] = project.project_number
                    task["project_subject"] = project.subject
                    task["opportunity_number"] = project.opportunity_number
                    data["list"].append(task)
                data["total"] = total
        except Exception as error:
            logger.error(f"获取任务列表数据失败{error}")
        return data


record_mine_parser = RequestParser()
record_mine_parser.add_argument('page', location='args', type=int, default=1, required=True)
record_mine_parser.add_argument('size', location='args', type=int, default=10, required=True)
record_mine_parser.add_argument('status[]', location='args', type=int, action='append', dest='status')
record_mine_parser.add_argument('support_location_adcodes[]', location='args', type=str, dest='adcodes')
record_mine_parser.add_argument('task_number', location='args', type=str)
record_mine_parser.add_argument('task_subject', location='args', type=str)
record_mine_parser.add_argument('project_number', location='args', type=str)
record_mine_parser.add_argument('project_subject', location='args', type=str)
record_mine_parser.add_argument('date_range[]', location='args', type=str, action='append', dest='date_range')


@projectmanage_api.resource('/record/mine/list')
class SeProjectRecordMineAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectRecordMineList)
    def get(self):
        """
        项目管理-获取我的任务列表
        :return:
        """
        parser_args = prepare_args_for_parser(record_mine_parser.copy())
        params = parser_args.parse_args()

        user_id = session["user_id"]

        page, size = params["page"], params["size"]
        data = {"list": [], "total": 0, "page": page, "size": size}

        total, record_tpu_list = SeProjectRecordDao.getAllRecordByUserIdAndFilter([user_id], **params)
        if record_tpu_list:
            for record_tpu in record_tpu_list:
                record, task, project, create_user = record_tpu

                schema = SeProjectRecordSchema()
                record = schema.dump(record)
                record["task_number"] = task.task_number
                record["assign_number"] = task.assign_number
                record["task_parent_id"] = task.parent_id
                record["task_event_number"] = task.event_number
                record["support_mode"] = task.support_mode
                record["task_subject"] = task.subject
                record["support_type_1st"] = getSeProjectProjectType(task.support_type_1st)
                record["support_type_2nd"] = getSeProjectProjectType(task.support_type_2nd)
                record["project_id"] = project.id
                record["project_number"] = project.project_number
                record["opportunity_number"] = project.opportunity_number
                record["project_subject"] = project.subject

                attachments = SysAttachmentDao.queryAttachmentByObjectId("se_project_record", record["id"])
                record["attachments_count"] = len(attachments)
                data["list"].append(record)

        data["total"] = total

        return data


@projectmanage_api.resource('/project/<project_id>/all_record')
class SeProjectAllRecordAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectRecordList)
    def get(self, project_id):
        """
        项目所有日志列表功能
        :return:
        """

        user_id = session["user_id"]
        data = {"list": [], "total": 0, "page": 1, "size": 10}

        project = SeProjectProjectDao.queryProjectById(project_id)
        if not (user_id == project.owner_id or user_id == project.created_by_id):
            superiors_ids = []
            superiors_ids += DataScopeDao.getAllSuperiorsByUserId(project.created_by_id)
            superiors_ids += DataScopeDao.getAllSuperiorsByUserId(project.owner_id)

            if user_id not in superiors_ids:
                raise AppException("查询失败，没有权限")

        record_tu_list = SeProjectRecordDao.getPublishProjectRecord(project_id)
        if not record_tu_list:
            return data

        for record_tu in record_tu_list:
            record, task,  create_user = record_tu
            schema = SeProjectRecordSchema()
            record = schema.dump(record)
            record["task_number"] = task.task_number
            record["task_subject"] = task.subject
            record["task_parent_id"] = task.parent_id
            record["task_event_number"] = task.event_number
            record["assign_number"] = task.assign_number
            record["record_content"] = json.loads(record["record_content"])
            record["created_by_name"] = create_user.display_name
            record["support_type_1st"] = getSeProjectProjectType(task.support_type_1st)
            record["support_type_2nd"] = getSeProjectProjectType(task.support_type_2nd)
            record["attachments"] = []
            attachments = SysAttachmentDao.queryAttachmentByObjectId("se_project_record", record["id"])
            for attachment in attachments:
                record["attachments"].append({
                    "id": attachment.id,
                    "filename": attachment.file_name,
                    "file_size": attachment.file_size,
                    "file_type": attachment.file_type
                })

            if record["status"] == 4:
                approval_record = SeProjectApprovalDao.queryApprovalRecordByRecordId(record["id"])
                if approval_record:
                    task_co = SeProjectTaskDao.getTaskJoinSysUserById(approval_record.main_task_id)
                    if task_co:
                        task, project, create_user, owner_user = task_co
                        record["approval_id"] = create_user.id
                        record["approval_name"] = create_user.display_name
                        if task.status == 1:
                            record["permission"] = ["return"]

            if record["status"] == 1:
                approval_record = SeProjectApprovalDao.queryUnApprovalByRecordId(record["id"])
                if approval_record:
                    record["unapproval_reason"] = approval_record.incomplete_reason

            if record["status"] == 2 and project.created_by_id == user_id:
                record["permission"] = ["return"]

            data["list"].append(record)

        data["total"] = len(record_tu_list)
        data["size"] = len(record_tu_list)
        return data


op_history_parser = RequestParser()
op_history_parser.add_argument('page', location='args', type=int, default=1, required=True)
op_history_parser.add_argument('size', location='args', type=int, default=10, required=True)


@projectmanage_api.resource('/project/<project_id>/history')
class SeProjectHistoryAPI(Resource):

    @permission.check(p_list['p_se_project_manage_list'])
    @marsh_response(SeProjectOperateHistoryList)
    def get(self, project_id):
        """
        项目所有日志列表功能
        :return:
        """

        parser_args = prepare_args_for_parser(op_history_parser.copy())
        params = parser_args.parse_args()

        data = {"list": [], "total": 0, "page": params.get("page"), "size": params.get("size")}

        total, op_history_list = OperateHistoryDao.getOperateHistoryJoinUser('se_project_project', project_id, **params)
        for op_user in op_history_list:
            op_history, user = op_user

            schema = OperateHistorySchema()
            op_history = schema.dump(op_history)
            op_history["created_by_name"] = user.display_name
            data["list"].append(op_history)

        data["total"] = total
        return data
