from flask import request, session, Blueprint
from flask_restful import Resource
from app.controllers.response import marsh_response
from app.extensions import permission
from app.enums.permission_enum import p_list
from app.utils.api_util import Api, AppException
from flask_restful.reqparse import RequestParser
from app.utils.gitlab_util import GitLabDICTicket
from app.utils.func_util import prepare_args_for_parser, getDicTicketNumberID, getRandomString20, getCurrentTime
from app.controllers.response.dic_ticket_respone import CreateTicketResponse, UpdateTicketResponse, ListTicketResponse,\
                                                        GetTicketDetailPermissionResponse, GetTicketResponse, ListFunctionalModuleResponse, \
                                                        ListProjectsResponse, CreateTaskResponse, CreateMessageResponse, GetMessageResponse, \
                                                        DeleteTicketResponse, GetTaskResponse, GetMyTaskResponse
from app.controllers.dao.dic_ticket_dao import DICTicketsDao, DICTicketProjectDao, DICTicketTaskDao, SysUserDepartmet, DICTicketMessageDao, \
                                               DICTicketFunctionalModuleDao
from app.utils.gitlab_util import GitLabDICTicket
from app.utils.http_api.msg_template import DicTicketEmail, DicTicketMessageEmail, DicTicketTaskEmail
from app.extensions import message_gw
from app.config import EmailConfig
from app.enums.dic_tickets_enum import enums

dic_ticket_app = Blueprint('dic_ticket', __name__, url_prefix='/api/dic')
dic_ticket_api = Api(dic_ticket_app)
handle_reminders = EmailConfig['dic_ticket']['handle_reminders']
dicket_enums = enums['dic_tickets']

post_ticket_parser = RequestParser()
post_ticket_parser.add_argument('parent_id', location='json', type=str)
post_ticket_parser.add_argument('subject', location='json', type=str)
post_ticket_parser.add_argument('description', location='json', type=str)
post_ticket_parser.add_argument('support_type', location='json', type=str)
post_ticket_parser.add_argument('privacy', location='json', type=str)
post_ticket_parser.add_argument('functional_module_id', location='json', type=str)
post_ticket_parser.add_argument('priority', location='json', type=str)
post_ticket_parser.add_argument('action', location='json', type=str)
post_ticket_parser.add_argument('created_by_id', location='json', type=str)
post_ticket_parser.add_argument('commit_by_id', location='json', type=str)
post_ticket_parser.add_argument('to_user_id', location='json', type=str)
post_ticket_parser.add_argument('to_username', location='json', type=str)
post_ticket_parser.add_argument('handle_type', location='json', type=str)
post_ticket_parser.add_argument('milestone_title', location='json', type=str)
post_ticket_parser.add_argument('start_time', location='json', type=str)
post_ticket_parser.add_argument('end_time', location='json', type=str)
post_ticket_parser.add_argument('project_id', location='json', type=str)
post_ticket_parser.add_argument('assign_by_id', location='json', type=str)
post_ticket_parser.add_argument('content', location='json', type=str)
post_ticket_parser.add_argument('need_reply', location='json', type=bool)
post_ticket_parser.add_argument('data', location='json', type=list)

get_ticket_parser = RequestParser()
get_ticket_parser.add_argument('classification', location='args', type=str)
get_ticket_parser.add_argument('page', location='args', type=int)
get_ticket_parser.add_argument('size', location='args', type=int)
get_ticket_parser.add_argument('ticket_id', location='args', type=str)
get_ticket_parser.add_argument('like', location='args', type=str)

get_ticket_parser.add_argument('status[]', location='args', type=str, action='append', dest='status')
get_ticket_parser.add_argument('support_type[]', location='args', type=str, action='append', dest='support_type')
get_ticket_parser.add_argument('priority[]', location='args', type=str, action='append', dest='priority')
get_ticket_parser.add_argument('privacy[]', location='args', type=str, action='append', dest='privacy')

get_ticket_parser.add_argument('ticket_status[]', location='args', type=str, action='append', dest='ticket_status')
get_ticket_parser.add_argument('ticket_like', location='args', type=str)
get_ticket_parser.add_argument('task_subject', location='args', type=str)


put_ticket_parser = RequestParser()
put_ticket_parser.add_argument('feasibility', location='json', type=str)
put_ticket_parser.add_argument('cancel_by_reason', location='json', type=str)
put_ticket_parser.add_argument('status', location='json', type=str)
put_ticket_parser.add_argument('priority', location='json', type=str)
put_ticket_parser.add_argument('functional_module_id', location='json', type=str)
put_ticket_parser.add_argument('privacy', location='json', type=str)
put_ticket_parser.add_argument('support_type', location='json', type=str)
put_ticket_parser.add_argument('description', location='json', type=str)
put_ticket_parser.add_argument('subject', location='json', type=str)
put_ticket_parser.add_argument('parent_id', location='json', type=str)
put_ticket_parser.add_argument('due_time', location='json', type=str)
put_ticket_parser.add_argument('created_by_id', location='json', type=str)


@dic_ticket_api.resource('/ticket/functional_module/list')
class ListFunctionalModule(Resource):
    @permission.check([p_list['p_dic_ticket_manage_all'], p_list['p_dic_ticket_all']])
    @marsh_response(ListFunctionalModuleResponse)
    def get(self):
        """
        function: 全量获取功能模块信息
        role: 所有用户
        """
        return DICTicketFunctionalModuleDao.queryFunctionalModule()

    

@dic_ticket_api.resource('/ticket')
class CreateTicket(Resource):
    @permission.check([p_list['p_dic_ticket_manage_all'], p_list['p_dic_ticket_all']])
    @marsh_response(CreateTicketResponse)
    def post(self):
        """
        function: 提交工单功能
        role: 所有用户, 管理员可选created_by_id
        """
        parser_args = prepare_args_for_parser(post_ticket_parser.copy())
        params = parser_args.parse_args()
        ticket_id = getRandomString20()
        number_id = getDicTicketNumberID()
        all_ticket_id, all_ticket_number_id = DICTicketsDao.queryAllTicketIds()
        while ticket_id in all_ticket_id:
            ticket_id = getRandomString20()
        while number_id in all_ticket_number_id:
            number_id = getDicTicketNumberID()
        current_time = getCurrentTime()
        if params.get("commit_by_id"):
            params["commit_by_id"] = params.get("commit_by_id")
        else:
            params["commit_by_id"] = session["user_id"]
        params["created_date"] = current_time
        params["created_by_id"] = session["user_id"]
        params["last_modified_by_id"] = session["user_id"]
        params["last_modified_date"] = current_time
        params["id"] = ticket_id
        params["number"] = number_id
        DICTicketsDao.createTickets(params)
        if params.get("action") == "Commit":
            template = DicTicketEmail()
            commit_by_name = SysUserDepartmet.getUsernameById(session["user_id"])
            template.update({"commit": commit_by_name, "priority": dicket_enums['priority'][params.get("priority")], 
                             "status": "提交", "support_type": dicket_enums['support_type'][params.get("support_type")],
                             "number": number_id, "subject": params.get("subject")})
            target = SysUserDepartmet.getEmailById(session["user_id"])
            if target:
                message_gw.push(target=target, template=template, cc=handle_reminders)
            else:
                raise AppException(message="获取用户邮箱失败")
        DICTicketMessageDao.systemMessage(ticket_id, "工单已完成创建")
        return {"id": ticket_id}
    

@dic_ticket_api.resource('/ticket/<string:ticket_id>')
class UpdateTicket(Resource):
    @permission.check([p_list['p_dic_ticket_manage_all'], p_list['p_dic_ticket_all']])
    @marsh_response(DeleteTicketResponse)
    def delete(self, ticket_id):
        ticket_status = DICTicketsDao.getTicketStatus(ticket_id=ticket_id)
        if ticket_status in ["Draft", "Cancel"]:
            update_data = {"status": "Deleted"}
            DICTicketsDao.updateTicket(ticket_id=ticket_id, update_data=update_data)
        else:
            raise AppException(message="此状态下工单无法删除")

    @permission.check([p_list['p_dic_ticket_manage_all'], p_list['p_dic_ticket_all']])
    @marsh_response(UpdateTicketResponse)
    def put(self, ticket_id):

        parser_args = prepare_args_for_parser(put_ticket_parser.copy())
        params = parser_args.parse_args()
        x_permission = request.headers.get('X-Permission')
        is_admin = SysUserDepartmet.isAdmin(session["user_id"])
        is_admin = True if x_permission == p_list['p_dic_ticket_manage_all'] and is_admin else False

        ticket = DICTicketsDao.getTicketById(ticket_id=ticket_id)
        ticket_status, current_time = ticket.get("status"), getCurrentTime()
        before_accept_status = ["Draft", "Commit"]
        after_accept_status = ["Accepting", "Doing", "Delivery", "Complete", "Cancel"]

        template = DicTicketEmail()
        target, commit_by_name = SysUserDepartmet.getEmailAndDisplaynameById(ticket.get("commit_by_id"))
        email_data = {"commit": commit_by_name, "priority": dicket_enums['priority'][ticket.get("priority")],
                       "status": "驳回", "support_type": dicket_enums['support_type'][ticket.get("support_type")],
                        "number": ticket.get("number"), "subject": ticket.get("subject")}

        if params.get("status") == "Cancel":
            update_data = {
                "feasibility": params.get("feasibility") or "",
                "cancel_by_reason": params.get("cancel_by_reason") or "",
                "status": params.get("status"),
                "last_modified_by_id": session["user_id"],
                "last_modified_date": current_time,
                "cancel_date": current_time,
                "cancel_by_id": session["user_id"]
            }
            if not is_admin:
                if ticket_status in before_accept_status:
                    DICTicketsDao.updateTicket(ticket_id=ticket_id, update_data=update_data)
                if ticket_status in after_accept_status:
                    raise AppException("工单已被受理或取消，无法被编辑，如有特殊修改请尝试联系管理员!")
            if is_admin:
                DICTicketsDao.updateTicket(ticket_id=ticket_id, update_data=update_data)
                email_data["status"] = f"驳回, 原因是:{params.get('feasibility')}"
                template.update(email_data)
                message_gw.push(target=target, template=template, cc=handle_reminders)


        else:
            update_data = {
                    "parent_id": params.get("parent_id"),
                    "subject": params.get("subject"),
                    "description": params.get("description"),
                    "support_type": params.get("support_type"),
                    "privacy": params.get("privacy"),
                    "functional_module_id": params.get("functional_module_id"),
                    "priority":  params.get("priority"),
                    "status": params.get("status")
            }

            if is_admin and params.get("created_by_id"):
                    update_data["created_by_id"] = params.get("created_by_id")
                    update_data["due_time"] = params.get("due_time")

            if len(ticket.get("first_delivery_date")) < 5 and params.get("status") == "Delivery":
                update_data["first_delivery_date"] = current_time

            if ticket_status != params.get("status") and params.get("status") == "Accepting":
                update_data["accepted_by_id"] = session["user_id"]
                update_data["accepted_datetime"] = current_time
                email_data["status"] = "受理"
                template.update(email_data)
                message_gw.push(target=target, template=template, cc=handle_reminders)

            if ticket_status != params.get("status") and params.get("status") == "Complete":
                update_data["actual_due_time"] = current_time
                update_data["complete_date"] = current_time
                email_data["status"] = "处理完成"
                template.update(email_data)
                participant = DICTicketsDao.queryTicketParticipant(ticket_id)
                message_gw.push(target=target, template=template, cc=list(set(handle_reminders+participant)))

            if ticket_status != params.get("status") and params.get("status") == "Delivery":
                email_data["status"] = "交付, 需要你确认需求是否已处理完成，如已完成,需及时将工单状态修改为【完成】"
                template.update(email_data)
                participant = DICTicketsDao.queryTicketParticipant(ticket_id)
                message_gw.push(target=target, template=template, cc=list(set(handle_reminders+participant)))

            DICTicketsDao.updateTicket(ticket_id=ticket_id, update_data=update_data)

        if ticket_status != params.get("status") and params.get("status"):
            DICTicketMessageDao.systemMessage(ticket_id, f"工单状态已更改为{params.get('status')}")
        return None
    

@dic_ticket_api.resource('/ticket/list')
class ListTicket(Resource):
    @permission.check([p_list['p_dic_ticket_manage_all'], p_list['p_dic_ticket_all']])
    @marsh_response(ListTicketResponse) 
    def get(self):
        """
        获取工单列表
        """
        parser_args = prepare_args_for_parser(get_ticket_parser.copy())
        params = parser_args.parse_args()
        x_permission = request.headers.get('X-Permission')
        is_admin = SysUserDepartmet.isAdmin(session["user_id"])
        admin = True if x_permission == p_list['p_dic_ticket_manage_all'] and is_admin else False
        
        classification, status = params.get("classification"), params.get("status")
        page, size = params.get("page"), params.get("size")
        support_type, priority = params.get("support_type"), params.get("priority")
        privacy, like = params.get("privacy"), params.get("like")
        if classification == "draft":
            ticket_data = DICTicketsDao.queryDraftTickets(session["user_id"], classification, page, size, 
                                                          support_type, priority, privacy, like)
        else:
            ticket_data = DICTicketsDao.queryTickets(classification, status, page, size, support_type, priority, 
                                                     session["user_id"], admin, privacy, like)
        return ticket_data
    

@dic_ticket_api.resource('/ticket/<string:ticket_id>')
class GetTicket(Resource):
    @permission.check([p_list['p_dic_ticket_manage_all'], p_list['p_dic_ticket_all']])
    @marsh_response(GetTicketResponse)
    def get(self, ticket_id):
        """
        查看工单详情, 需要区分管理员和非管理员,管理员可以查看对应任务
        """
        if not DICTicketsDao.queryeTicketIsExist(ticket_id):
            raise AppException(message="工单不存在或者已经被删除")

        x_permission = request.headers.get('X-Permission')
        is_admin = SysUserDepartmet.isAdmin(session["user_id"])
        admin = True if x_permission == p_list['p_dic_ticket_manage_all'] and is_admin else False

        if not admin:
            ticket = DICTicketsDao.getTicketById(ticket_id)
            user = [ticket.get("commit_by_id"), ticket.get("created_by_id")]

            privacy = ticket.get("privacy")
            if privacy == "Private":
                if session["user_id"] not in user:
                    raise AppException(message="该工单并不被您拥有")
        
        return  DICTicketsDao.getTicketAndFunctionalModule(ticket_id)
    

@dic_ticket_api.resource('/ticket/permission/<string:page_title>')
class GetTicketDetailPermission(Resource):
    @permission.check([p_list['p_dic_ticket_manage_all'], p_list['p_dic_ticket_all']])
    @marsh_response(GetTicketDetailPermissionResponse)
    def get(self, page_title):
        parser_args = prepare_args_for_parser(get_ticket_parser.copy())
        params = parser_args.parse_args()
        ticket_id, permission = params.get("ticket_id"), []

        if ticket_id:
            if not DICTicketsDao.queryeTicketIsExist(ticket_id):
                raise AppException(message="工单不存在或者已经被删除")
            
            ticket = DICTicketsDao.getTicketById(ticket_id)
            created_by_id, ticket_status = ticket.get("created_by_id"), ticket.get("status")
            x_permission = request.headers.get('X-Permission')
            accepted_user = True if ticket.get("accepted_by_id") == session['user_id'] else False
            is_admin = SysUserDepartmet.isAdmin(session["user_id"])

            if x_permission == p_list['p_dic_ticket_manage_all'] and is_admin:
                if ticket_status == "Draft":
                    if created_by_id == session["user_id"]:
                        permission = ["edit","commit", "delete"]
                elif ticket_status == "Commit":
                    permission = ["edit","cancel","accepting"]
                elif ticket_status == "Cancel":
                    permission = ["edit","delete"]
                elif ticket_status == "Accepting":
                    permission = ["edit","cancel","doing", "add-task"]
                elif ticket_status == "Doing":
                    permission = ["edit","cancel","delivery", "add-task"]
                elif ticket_status == "Delivery":
                    permission = ["edit","cancel", "doing"]   
            else:
                if created_by_id == session["user_id"]:
                    if ticket_status == "Draft":
                        permission = ["edit", "commit", "delete"]
                    elif ticket_status == "Commit":
                        permission = ["cancel"]
                    elif ticket_status in ["Accepting", "Doing"]:
                        permission = ["cancel"]
                    elif ticket_status == "Delivery":
                        permission = ["cancel", "complete", "doing"]
            if accepted_user:
                permission.append("fs_mutation")
        return {"list": permission}
    


@dic_ticket_api.resource('/ticket/<string:ticket_id>/task')
class CreateTask(Resource):
    @permission.check(p_list['p_dic_ticket_manage_all'])
    @marsh_response(CreateTaskResponse)
    def post(self, ticket_id):
        """
        issue不要本系统建, 然后系统新建里程碑, 然后再人工到gitlab上建issue, 最好系统自带一个issue
        """
        parser_args = prepare_args_for_parser(post_ticket_parser.copy())
        params = parser_args.parse_args()
        empty_string, task_id = "", getRandomString20()
        all_task_id = DICTicketTaskDao.queryAllTaskIds()
        while task_id in all_task_id:
            task_id = getRandomString20()
        params = params.get("data")[0]
        handle_type = params.get("handle_type")
        description = params.get("description")
        subject = params.get("subject")
        milestone_title = params.get("milestone_title") or empty_string
        start_time = params.get("start_time") or empty_string
        end_time = params.get("end_time") or empty_string
        project_id = params.get("project_id") or empty_string
        assign_by_id = params.get("assign_by_id") or empty_string
        milestone_id = empty_string

        if handle_type == "develop":
            content = f"已添加开发类任务: {subject}"
            description = f"""<a href="{request.referrer}business_platform/dic/ticket_manage/detail/{ticket_id}">{milestone_title}</a>""" + description
            milestone_id = GitLabDICTicket().createTask(milestone_title, description, project_id, start_time, end_time)
            DICTicketTaskDao.createTask(task_id, ticket_id, handle_type, project_id, assign_by_id, 
                                        milestone_id, session["user_id"], getCurrentTime(), subject, '')
        if handle_type == "non_develop":
            DICTicketTaskDao.createTask(task_id, ticket_id, handle_type, '', assign_by_id, '', session["user_id"],
                                        getCurrentTime(), subject, description)
            content = f"已添加非开发类任务: {subject}"

        ticket, template = DICTicketsDao.getTicketById(ticket_id), DicTicketTaskEmail()
        target, assign_by_name = SysUserDepartmet.getEmailAndDisplaynameById(assign_by_id)
        template.update({"number": ticket.get("number"), "subject": ticket.get("subject"), 
                         "priority": dicket_enums['priority'][ticket.get("priority")],
                         "support_type": dicket_enums['support_type'][ticket.get("support_type")], 
                         "task_subject": subject, "task_support_type": handle_type, "assign_by_name": assign_by_name})
        message_gw.push(target=target, template=template)

        DICTicketsDao.updateTicketStatus(ticket_id=ticket_id, status="Doing")
        DICTicketMessageDao.systemMessage(ticket_id, content)
        return {"id": task_id}
    
    @permission.check(p_list['p_dic_ticket_manage_all'])
    @marsh_response(GetTaskResponse)
    def get(self, ticket_id):
        """
        获取任务
        """
        parser_args = prepare_args_for_parser(get_ticket_parser.copy())
        params = parser_args.parse_args()
        page = params.get("page")
        size = params.get("size")
        data = GitLabDICTicket().getTaskInfoById(ticket_id)
        return data
    


@dic_ticket_api.resource('/ticket/project/list')
class ListProjects(Resource):

    @permission.check([p_list['p_dic_ticket_manage_all'], p_list['p_dic_ticket_all']])
    @marsh_response(ListProjectsResponse)
    def get(self):
        """
        获取项目列表
        """
        return DICTicketProjectDao.queryAllProject()
    

@dic_ticket_api.resource('/ticket/<string:ticket_id>/message')
class CreateMessage(Resource):
    @permission.check([p_list['p_dic_ticket_manage_all'], p_list['p_dic_ticket_all']])
    @marsh_response(CreateMessageResponse)
    def post(self, ticket_id):
        """
        添加留言, 是否需要@根据父级ID查评论人ID和评论人名称, 然后添加@前缀
        """
        parser_args = prepare_args_for_parser(post_ticket_parser.copy())
        params = parser_args.parse_args()
        content, parent_id, need_reply = params.get("content"), params.get("parent_id") or "", params.get("need_reply")
        to_user_id, to_username = params.get("to_user_id") or "", params.get("to_username") or ""
        message_id = getRandomString20()
        all_message_id = DICTicketMessageDao.queryAllMessageID()
        while message_id in all_message_id:
            message_id = getRandomString20()
        created_username = SysUserDepartmet.getUsernameById(user_id=session["user_id"])
        created_date = getCurrentTime()
        # if need_reply and DICTicketsDao.getTicketStatus(ticket_id) == "Delivery":
        #     DICTicketsDao.updateTicketStatus(ticket_id=ticket_id, status="Doing")
        # if parent_id:
        #     DICTicketMessageDao.updateMessageNeedReply(message_id=parent_id, need_reply=False)
        if to_user_id:
            to_username = SysUserDepartmet.getUsernameById(user_id=to_user_id)
        DICTicketMessageDao.createMessage(message_id, parent_id, ticket_id, content, need_reply,session["user_id"], 
                                          created_date, created_username, to_user_id, to_username)
        
        x_permission = request.headers.get('X-Permission')
        is_admin = SysUserDepartmet.isAdmin(session["user_id"])
        admin = True if x_permission == p_list['p_dic_ticket_manage_all'] and is_admin else False
        if admin:
            ticket, template = DICTicketsDao.getTicketById(ticket_id), DicTicketMessageEmail()
            target, commit_by_name = SysUserDepartmet.getEmailAndDisplaynameById(ticket.get("commit_by_id"))
            template.update({"commit": commit_by_name, "number": ticket.get("number"), "subject": ticket.get("subject"), "content": content})
            message_gw.push(target=target, template=template)

        return {"id": message_id}
    

    @permission.check([p_list['p_dic_ticket_manage_all'], p_list['p_dic_ticket_all']])
    @marsh_response(GetMessageResponse)
    def get(self, ticket_id):
        """
        获取留言
        """
        parser_args = prepare_args_for_parser(get_ticket_parser.copy())
        params = parser_args.parse_args()
        page = params.get("page")
        size = params.get("size")
        return DICTicketMessageDao.getMessageByTicketId(ticket_id=ticket_id, page=page, size=size)
    

@dic_ticket_api.resource('/ticket/tasks')
class GetTask(Resource):
    @permission.check(p_list['p_dic_ticket_manage_all'])
    @marsh_response(GetMyTaskResponse)
    def get(self):
        """
        获取我的任务
        """
        parser_args = prepare_args_for_parser(get_ticket_parser.copy())
        params = parser_args.parse_args()
        ticket_like = params.get("ticket_like")
        page, size = params.get("page"), params.get("size")
        ticket_status, task_subject = params.get("ticket_status"), params.get("task_subject")

        x_permission = request.headers.get('X-Permission')
        is_admin = SysUserDepartmet.isAdmin(session["user_id"])
        if x_permission == p_list['p_dic_ticket_manage_all'] and is_admin:
            data = DICTicketTaskDao.getTaskByUserId(user_id=session["user_id"], page=page, size=size, ticket_status=ticket_status,
                                                    task_subject=task_subject, ticket_like=ticket_like)
            return data            
        else:
            raise AppException(message="对不起, 暂未查到您的对应权限")