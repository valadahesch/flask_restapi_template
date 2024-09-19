import copy
import json
import time

from datetime import datetime
from flask import Blueprint, session, jsonify, current_app
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.extensions import permission, message_gw, executor, logger
from app.enums.permission_enum import p_list
from app.enums.se_work_template import getSeWorkProjectType, SEWORK_TEMPLATE
from app.utils.func_util import prepare_args_for_parser, validate_null, validate_half_hour
from app.controllers import ESService
from app.utils.http_api.msg_template import SeWorkProjectEmail, SeWorkTaskEmail, SeWorkSubTaskEmail, \
    SeWorkTaskArchiveEmail, SeWorkProjectArchiveEmail, SeWorkRecordUnApprovedEmail, SeWorkRecordPendingEmail, \
    SeWorkRecordApprovedEmail
from app.controllers.dao import SeWorkProjectDao, SeWorkTaskDao, SeWorkRecordDao, DataScopeDao, SysAttachmentDao, \
    SysUserDao, TblEmployeeDao, SeWorkApprovalDao
from app.controllers.schema import SeWorkProjectSchema, SeWorkTaskSchema, SeWorkRecordSchema, SeWorkApprovalRecordSchema
from app.controllers.response import marsh_response, SeWorkProjectDetail, SeWorkTaskDetail, SeWorkRecordList, \
    SeWorkTaskList, SeWorkProjectList, SeWorkParticipantList
from app.utils.api_util import Api, AppResponse, AppException

internalwork_app = Blueprint('internalwork', __name__, url_prefix='/api/presales/internal_work')
internalwork_api = Api(internalwork_app)


@internalwork_api.resource('/project/support_type')
class ProjectSupportTypeAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    def get(self):
        """
        获取项目类型，确定日志模板
        :return:
        """
        data = {"list": SEWORK_TEMPLATE}

        return jsonify(AppResponse(data))


post_project_parser = RequestParser()
post_project_parser.add_argument('subject', location='json', type=validate_null, required=True)
post_project_parser.add_argument('owner_id', location='json', type=validate_null, required=True)
post_project_parser.add_argument('account_id', location='json', type=str)
post_project_parser.add_argument('account_name', location='json', type=str)
post_project_parser.add_argument('contact_name', location='json', type=str)
post_project_parser.add_argument('contact_info', location='json', type=str)
post_project_parser.add_argument('support_type_1st', location='json', type=validate_null, required=True)
post_project_parser.add_argument('support_type_2nd', location='json', type=validate_null, required=True)


@internalwork_api.resource('/project')
class ProjectAPI(Resource):

    @permission.check(p_list['p_sework_internel_project_add'])
    def post(self):
        """
        创建项目
        :return:
        """
        parser_args = prepare_args_for_parser(post_project_parser.copy())
        params = parser_args.parse_args()

        owner = SysUserDao.querySysUserById(params["owner_id"])
        create_user = SysUserDao.querySysUserById(session['user_id'])

        params['created_by_id'] = session['user_id']
        params['last_modified_by_id'] = session['user_id']
        params['project_type'] = '售前内部事务'
        schema = SeWorkProjectSchema()
        project = schema.load(params)

        _id, project_number = SeWorkProjectDao.addProject(project)

        for _ in range(3):
            time.sleep(0.5)
            res = ESService.querySeWorkByProjectId(_id)
            if res:
                break

        def notice(**kwargs):
            try:
                message_gw.push(**kwargs)
            except Exception as e:
                logger.error("ProjectTask Create Exception: {}".format(str(e)))

        template = SeWorkProjectEmail()
        template.update({
            "id": project.id, "project_number": project.project_number, "subject": project.subject,
            "owner_name": owner.display_name, "created_by_name": create_user.display_name,
            "created_date": project.created_date.strftime('%Y-%m-%d %H:%M:%S')
        })
        executor.submit(notice, target=owner.email, template=template)

        data = {"id": _id, "project_number": project_number}
        return AppResponse(data)


get_project_parser = RequestParser()
get_project_parser.add_argument('query', location='args', type=str)
get_project_parser.add_argument('date_range[]', location='args', type=str, action='append', dest='date_range')
get_project_parser.add_argument('order_column', location='args', type=str, choices=["created_date", "last_modified_date"], default="created_date")
get_project_parser.add_argument('order_direct', location='args', type=str, choices=["asc", "desc"], default="desc")
get_project_parser.add_argument('update_date_range[]', location='args', type=str, action='append', dest='update_date_range')
get_project_parser.add_argument('owner_id[]', location='args', type=str, action='append', dest='owner_id')
get_project_parser.add_argument('created_by_id[]', location='args', type=str, action='append', dest='created_by_id')
get_project_parser.add_argument('status[]', location='args', type=int, action='append', dest='status')
get_project_parser.add_argument('participants[]', location='args', type=str, action='append', dest='participants')
get_project_parser.add_argument('page', location='args', type=int, default=1)
get_project_parser.add_argument('size', location='args', type=int, default=1000)


@internalwork_api.resource('/project/list')
class ProjectListAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    @marsh_response(SeWorkProjectList)
    def get(self):
        """
        查询所有项目列表，字段排序，筛选（责任人、参与人；我的，下属，具体用户名，关键词（所有字段）搜索，分页
        :return:
        """
        parser_args = prepare_args_for_parser(get_project_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")), "size": int(params.get("size"))
        }
        user_id = session["user_id"]
        user_ids = DataScopeDao.getSysUserByRank(user_id, 'sework.internal:all')
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
                task_co_list = SeWorkTaskDao.queryTaskJoinSysUserByUserIds(user_ids)
                for task_co in task_co_list:
                    task, create_user, owner_user = task_co
                    project_ids.append(task.project_id)
                    participant = {"id": task.owner_id, "display_name": owner_user.display_name}
                    if task.project_id in participants_map and participant not in participants_map.get(task.project_id):
                        participants_map[task.project_id].append(participant)
                    else:
                        participants_map[task.project_id] = [participant]

                data["total"], project_list = SeWorkProjectDao.getProjectByOwnerAndFilter(user_id, **params)
                for project in project_list:
                    project, c_user, o_user, m_user = project
                    schema = SeWorkProjectSchema()
                    project = schema.dump(project)

                    project["support_type_1st"] = getSeWorkProjectType(project["support_type_1st"])
                    project["support_type_2nd"] = getSeWorkProjectType(project["support_type_2nd"])
                    project["created_by_name"] = c_user.display_name
                    project["last_modified_by_name"] = m_user.display_name
                    project["owner_name"] = o_user.display_name
                    project["participants"] = participants_map.get(project["id"])
                    data["list"].append(project)

                return data

        total, es_res = ESService.querySeWorkByFilter(user_ids, **params)
        if es_res:
            for hit in es_res:
                project = hit["_source"]
                del project["tasks"]

                if project["deleted_date"]:
                    continue
                project["support_type_1st"] = getSeWorkProjectType(project["support_type_1st"])
                project["support_type_2nd"] = getSeWorkProjectType(project["support_type_2nd"])
                project["created_date"] = datetime.strptime(
                    project["created_date"], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
                project["last_modified_date"] = datetime.strptime(
                    project["last_modified_date"], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
                data["list"].append(project)
            data["total"] = total
            return data

        return data


@internalwork_api.resource('/project/<project_id>')
class ProjectDetailAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    @marsh_response(SeWorkProjectDetail)
    def get(self, project_id):
        """
        查看项目详情
        :return:
        """
        project_co = SeWorkProjectDao.getProjectJoinSysUserById(project_id)
        if not project_co:
            raise AppException("查询失败，项目不存在")

        project, create_user, owner_user = project_co
        user_id = session["user_id"]
        if not (user_id == create_user.id or user_id == owner_user.id):
            flag = False
            task_co_list = SeWorkTaskDao.getTaskJoinSysUserByProjectId(project_id)
            if task_co_list:
                for task_co in task_co_list:
                    if task_co[0].owner_id == user_id or task_co[0].created_by_id == user_id:
                        flag = True

            if not flag:
                user_ids = DataScopeDao.getSysUserByRank(user_id, 'sework.internal:all')
                if not user_ids:
                    raise AppException("查询失败，没有权限")
                else:
                    if not (create_user.id in user_ids or owner_user.id in user_ids) and user_ids[0] != "*":
                        raise AppException("查询失败，没有权限")

        project, create_user, owner_user = project_co
        schema = SeWorkProjectSchema()
        data = schema.dump(project)
        data["support_type_1st"] = getSeWorkProjectType(data["support_type_1st"])
        data["support_type_2nd"] = getSeWorkProjectType(data["support_type_2nd"])
        data["created_by_name"] = create_user.display_name
        data["owner_name"] = owner_user.display_name
        return data

    @permission.check(p_list['p_sework_internel_all'])
    def delete(self, project_id):
        """
        任务删除
        :return:
        """
        project = SeWorkProjectDao.queryProjectById(project_id)
        if not project:
            return jsonify(AppResponse())

        if not project.created_by_id == session['user_id']:
            raise AppException("删除失败，没有权限")

        if project.status == 1 or project.status == 4:
            delete_data = {"deleted_by_id": session["user_id"], "status": 4}
            SeWorkProjectDao.deleteProjectById(project_id, delete_data)
        else:
            raise AppException("删除失败，项目进行中无法删除")

        for _ in range(3):
            time.sleep(0.5)
            res = ESService.querySeWorkByProjectId(project_id)
            if res:
                if res.get("created_date"):
                    break

        ESService.deleteSeWorkProjectById(project_id)
        for _ in range(3):
            time.sleep(0.5)
            res = ESService.querySeWorkByProjectId(project_id)
            if not res:
                break

        return jsonify(AppResponse())


@internalwork_api.resource('/project/owner/list')
class ProjectOwnerAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    def get(self):
        """
        项目负责人列表查询
        :return:
        """
        userid_list = []
        data = {"list": [{"id": "me", "display_name": "我"}, {"id": "my_subordinates", "display_name": "我的下属"}]}
        user_id, user_roles = session["user_id"], session['roles']
        user_ids = DataScopeDao.getSysUserByRank(user_id, 'sework.internal:all')
        total, res = ESService.querySeWorkByFilter(user_ids)
        if res:
            for hit in res:
                project = hit["_source"]
                del project["tasks"]

                if project["owner_id"] not in userid_list and project["owner_id"]:
                    data["list"].append({"id": project["owner_id"], "display_name": project["owner_name"]})
                    userid_list.append(project["owner_id"])

        return jsonify(AppResponse(data))


@internalwork_api.resource('/project/create_by/list')
class ProjectCreateAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    def get(self):
        """
        项目创建人列表查询
        :return:
        """
        userid_list = []
        data = {"list": [{"id": "me", "display_name": "我"}, {"id": "my_subordinates", "display_name": "我的下属"}]}
        user_id, user_roles = session["user_id"], session['roles']
        user_ids = DataScopeDao.getSysUserByRank(user_id, 'sework.internal:all')
        total, res = ESService.querySeWorkByFilter(user_ids)
        if res:
            for hit in res:
                project = hit["_source"]
                del project["tasks"]

                if project["created_by_id"] not in userid_list and project["created_by_id"]:
                    data["list"].append({"id": project["created_by_id"], "display_name": project["created_by_name"]})
                    userid_list.append(project["created_by_id"])

        return jsonify(AppResponse(data))


@internalwork_api.resource('/project/participants/list')
class ProjectParticipantsAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    def get(self):
        """
        项目参与人列表查询
        :return:
        """
        userid_list = []
        data = {"list": [{"id": "me", "display_name": "我"}, {"id": "my_subordinates", "display_name": "我的下属"}]}
        user_id, user_roles = session["user_id"], session['roles']
        user_ids = DataScopeDao.getSysUserByRank(user_id, 'sework.internal:all')
        total, res = ESService.querySeWorkByFilter(user_ids)
        if res:
            for hit in res:
                project = hit["_source"]
                del project["tasks"]

                for participant in project["participants"]:
                    if participant["id"] not in userid_list and participant["id"]:
                        data["list"].append(participant)
                        userid_list.append(participant["id"])

        return jsonify(AppResponse(data))


@internalwork_api.resource('/project/<project_id>/participants/list')
class ProjectParticipantsListAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    @marsh_response(SeWorkParticipantList)
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

        project = SeWorkProjectDao.queryProjectById(project_id)
        if project:
            participant = get_participant(project.owner_id)
            participant["role"] = "项目负责人"
            participants.append(participant)

        task_list = SeWorkTaskDao.queryTaskByProjectId(project_id)
        for task in task_list:
            exist = False
            for p in participants:
                if p["id"] == task.owner_id:
                    if task.parent_id and '子任务负责人' not in p["role"]:
                        p["role"] += ", 子任务负责人"
                    elif task.parent_id and '主任务负责人' not in p["role"]:
                        p["role"] += ", 主任务负责人"
                    exist = True

            if not exist:
                participant = get_participant(task.owner_id)
                participant["role"] = "子任务负责人" if task.parent_id else "主任务负责人"
                participants.append(participant)

        return data


archive_project_parser = RequestParser()
archive_project_parser.add_argument('status', location='json', type=validate_null, choices=[3], required=True)


@internalwork_api.resource('/project/<project_id>/archive')
class ProjectArchiveAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    def put(self, project_id):
        """
        项目归档
        :return:
        """
        parser_args = prepare_args_for_parser(archive_project_parser.copy())
        params = parser_args.parse_args()

        project = SeWorkProjectDao.queryProjectById(project_id)
        if not project:
            raise AppException("操作失败，项目不存在")

        if project.owner_id != session['user_id']:
            raise AppException("操作失败，只有项目负责人可以操作")

        undone_task_list = []
        task_list = SeWorkTaskDao.queryDoTaskByProjectId(project_id)
        for task in task_list:
            if task.status == 1 and not task.parent_id:
                undone_task_list.append(task)

        if undone_task_list:
            undone_id = ','.join([undone_task.task_number for undone_task in undone_task_list])
            raise AppException(f"归档失败，任务{undone_id}未结束")

        params["status"] = 3
        params['last_modified_by_id'] = session['user_id']
        SeWorkProjectDao.updateProjectById(project_id, params)

        return jsonify(AppResponse())


post_task_parser = RequestParser()
post_task_parser.add_argument('project_id', location='json', type=validate_null, required=True)
post_task_parser.add_argument('subject', location='json', type=validate_null, required=True)
post_task_parser.add_argument('support_mode', location='json', type=validate_null, required=True)
post_task_parser.add_argument('account_id', location='json', type=str)
post_task_parser.add_argument('account_name', location='json', type=str)
post_task_parser.add_argument('contact_name', location='json', type=str)
post_task_parser.add_argument('contact_info', location='json', type=str)
post_task_parser.add_argument('start_time', location='json', type=str, dest='task_start_date')
post_task_parser.add_argument('end_date', location='json', type=str, dest='task_end_date')


@internalwork_api.resource('/task')
class ProjectTaskAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    def post(self):
        """
        创建主任务
        :return:
        """
        parser_args = prepare_args_for_parser(post_task_parser.copy())
        params = parser_args.parse_args()

        project = SeWorkProjectDao.queryProjectById(params['project_id'])
        if not project:
            raise AppException("操作失败，项目不存在")

        if project.owner_id != session['user_id']:
            raise AppException("操作失败，只有项目负责人可以操作")

        create_user = SysUserDao.querySysUserById(session['user_id'])

        params["support_type_1st"] = project.support_type_1st
        params["support_type_2nd"] = project.support_type_2nd
        params['owner_id'] = session['user_id']
        params['created_by_id'] = session['user_id']
        params['last_modified_by_id'] = session['user_id']
        schema = SeWorkTaskSchema()
        task = schema.load(params)

        _id, task_number = SeWorkTaskDao.addTask(task)

        update_project = {"last_modified_by_id": session['user_id'], "status": 2}
        SeWorkProjectDao.updateProjectById(params["project_id"], update_project)

        def notice(**kwargs):
            try:
                message_gw.push(**kwargs)
            except Exception as e:
                logger.error("ProjectTask Create Exception: {}".format(str(e)))

        template = SeWorkTaskEmail()
        template.update({
            "id": task.id, "task_number": task.task_number, "subject": task.subject,
            "owner_name": create_user.display_name, "created_by_name": create_user.display_name,
            "created_date": task.created_date.strftime('%Y-%m-%d %H:%M:%S'), "project_id": project.id,
            "project_number": project.project_number, "project_subject": project.subject
        })
        executor.submit(notice, target=create_user.email, template=template)

        data = {"id": _id, "task_number": task_number}
        return AppResponse(data)


get_task_parser = RequestParser()
get_task_parser.add_argument('project_id', location='args', type=validate_null, required=True)
get_task_parser.add_argument('page', location='args', type=int, default=1)
get_task_parser.add_argument('size', location='args', type=int, default=1000)


@internalwork_api.resource('/task/list')
class ProjectTaskListAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    @marsh_response(SeWorkTaskList)
    def get(self):
        """
        查询项目任务列表 编号、主题、责任人、支持方式(现场/远程)、状态(进行中、已结束和已删除)、创建时间和操作等列
        :return:
        """
        parser_args = prepare_args_for_parser(get_task_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")), "size": int(params.get("size"))
        }

        task_ids, parent_ids = [], []
        user_id = session["user_id"]
        project = SeWorkProjectDao.queryProjectById(params["project_id"])
        if project:
            if project.created_by_id == user_id:
                task_co_list = SeWorkTaskDao.getTaskJoinSysUserByProjectId(params["project_id"])

            else:
                user_ids = DataScopeDao.getSysUserByRank(user_id, 'sework.internal:all')
                task_co_list = SeWorkTaskDao.getTaskJoinSysUserByUserId(user_ids, params["project_id"])

            for task_co in task_co_list:
                task = task_co[0]
                task_ids.append(task.id)
                if task.parent_id:
                    parent_ids.append(task.parent_id)

            parent_tasks = [x for x in parent_ids if x not in task_ids]
            if parent_tasks:
                parent_task = SeWorkTaskDao.getTaskJoinSysUserByIds(parent_tasks)
                task_co_list += parent_task
                task_ids += [task_c0[0].id for task_c0 in parent_task]

            for task_co in task_co_list:
                task, create_user, owner_user = task_co
                if task.parent_id and task.parent_id not in task_ids:
                    continue

                schema = SeWorkTaskSchema()
                task = schema.dump(task)
                task["support_type_1st"] = getSeWorkProjectType(task["support_type_1st"])
                task["support_type_2nd"] = getSeWorkProjectType(task["support_type_2nd"])
                task["created_by_name"] = create_user.display_name
                task["owner_name"] = owner_user.display_name
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
        return data


@internalwork_api.resource('/task/<task_id>')
class ProjectTaskIdAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    @marsh_response(SeWorkTaskDetail)
    def get(self, task_id):
        """
        任务详情
        :return:
        """
        task_pco = SeWorkTaskDao.getTaskJoinSysUserById(task_id)
        if not task_pco:
            raise AppException("查询失败，任务不存在")

        task, project, create_user, owner_user = task_pco
        user_id = session["user_id"]
        if not (user_id == create_user.id or user_id == owner_user.id or user_id == project.created_by_id):
            flag = False
            if not task.parent_id:
                sub_task_list = SeWorkTaskDao.queryTaskByParentId(task_id)
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

        schema = SeWorkTaskSchema()
        data = schema.dump(task)
        data["project_number"] = project.project_number
        data["project_subject"] = project.subject
        data["created_by_name"] = create_user.display_name
        data["owner_name"] = owner_user.display_name
        if task.last_modified_by_id == task.created_by_id:
            data["last_modified_by_name"] = create_user.display_name
        elif task.last_modified_by_id == task.owner_id:
            data["last_modified_by_name"] = owner_user.display_name
        else:
            modified_user = SysUserDao.querySysUserById(task.last_modified_by_id)
            if modified_user:
                data["last_modified_by_name"] = modified_user.display_name

        data["support_type_1st"] = getSeWorkProjectType(data["support_type_1st"])
        data["support_type_2nd"] = getSeWorkProjectType(data["support_type_2nd"])

        return data

    @permission.check(p_list['p_sework_internel_all'])
    def delete(self, task_id):
        """
        任务删除
        :return:
        """
        delete_data = {"last_modified_by_id": session["user_id"], "deleted_by_id": session["user_id"]}
        SeWorkTaskDao.deleteTaskById(task_id, delete_data)

        return jsonify(AppResponse())


post_subtask_parser = RequestParser()
post_subtask_parser.add_argument('project_id', location='json', type=validate_null, required=True)
post_subtask_parser.add_argument('subject', location='json', type=validate_null, required=True)
post_subtask_parser.add_argument('support_mode', location='json', type=validate_null, required=True)
post_subtask_parser.add_argument('account_id', location='json', type=str)
post_subtask_parser.add_argument('account_name', location='json', type=str)
post_subtask_parser.add_argument('contact_name', location='json', type=str)
post_subtask_parser.add_argument('contact_info', location='json', type=str)
post_subtask_parser.add_argument('start_time', location='json', type=str, dest='task_start_date')
post_subtask_parser.add_argument('end_date', location='json', type=str, dest='task_end_date')
post_subtask_parser.add_argument('owner_id', location='json', type=list, required=True)


@internalwork_api.resource('/task/<task_id>/subtask')
class SubTaskAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    def post(self, task_id):
        """
        创建子任务
        :return:
        """
        parser_args = prepare_args_for_parser(post_subtask_parser.copy())
        params = parser_args.parse_args()

        data = {"list": []}
        task_p = SeWorkTaskDao.getTaskJoinProjectById(task_id)
        if not task_p:
            raise AppException("操作失败，任务不存在")

        main_task, project = task_p
        if main_task.owner_id != session['user_id']:
            raise AppException("操作失败，只有任务负责人可以创建")

        if main_task.status == 2:
            raise AppException("操作失败，任务已归档")

        params["project_id"] = main_task.project_id
        params["parent_id"] = main_task.id
        params["support_type_1st"] = main_task.support_type_1st
        params["support_type_2nd"] = main_task.support_type_2nd
        params['created_by_id'] = session['user_id']
        params['last_modified_by_id'] = session['user_id']

        create_user = SysUserDao.querySysUserById(session['user_id'])
        owner_list = copy.copy(params["owner_id"])
        for owner_id in owner_list:
            params['owner_id'] = owner_id
            owner = SysUserDao.querySysUserById(owner_id)
            schema = SeWorkTaskSchema()
            task = schema.load(params)
            _id, task_number = SeWorkTaskDao.addTask(task)

            def notice(**kwargs):
                try:
                    message_gw.push(**kwargs)
                except Exception as e:
                    logger.error("SubTask Create Exception: {}".format(str(e)))

            template = SeWorkSubTaskEmail()
            template.update({
                "id": task.id, "task_number": task.task_number, "subject": task.subject,
                "owner_name": owner.display_name, "created_by_name": create_user.display_name,
                "created_date": task.created_date.strftime('%Y-%m-%d %H:%M:%S'), "parent_task_id": main_task.id,
                "parent_task_number": main_task.task_number, "parent_task_subject": main_task.subject,
                "project_id": project.id, "project_number": project.project_number,
                "project_subject": project.subject
            })
            executor.submit(notice, target=owner.email, template=template)

            data["list"].append({"id": _id, "task_number": task_number})

        update_data = {"last_modified_by_id": session['user_id']}
        SeWorkProjectDao.updateProjectById(main_task.project_id, update_data)

        return jsonify(AppResponse(data))


task_archive_parser = RequestParser()
task_archive_parser.add_argument('task_result', location='json', type=int, choices=[1, 2], required=True)
task_archive_parser.add_argument('remark', location='json', type=str, dest="task_incomplete_reason")


@internalwork_api.resource('/task/<task_id>/archive')
class TaskAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    def put(self, task_id):
        """
        任务归档
        :return:
        """
        parser_args = prepare_args_for_parser(task_archive_parser.copy())
        params = parser_args.parse_args()

        if params["task_result"] == 2 and not params.get("task_incomplete_reason"):
            raise AppException("归档失败，请填写未完成的原因")

        task = SeWorkTaskDao.queryTaskById(task_id)
        if not task:
            raise AppException("归档失败，任务不存在")

        def notice(**kwargs):
            try:
                message_gw.push(**kwargs)
            except Exception as e:
                logger.error("Task Archive Exception: {}".format(str(e)))

        if not task.parent_id:
            undone_task_list = SeWorkTaskDao.queryUndoneTaskByParentId(task.id)
            if undone_task_list:
                undone_id = ','.join([undone_task.task_number for undone_task in undone_task_list])
                raise AppException(f"归档失败，任务{undone_id}未结束")
            else:
                project_co = SeWorkProjectDao.getProjectJoinSysUserById(task.project_id)
                if project_co:
                    project, project_create, project_owner = project_co
                    template = SeWorkProjectArchiveEmail()
                    template.update({
                        "id": project.id, "project_number": project.project_number, "subject": project.subject
                    })
                    executor.submit(notice, target=project_owner.email, template=template)

        params['last_modified_by_id'] = session['user_id']
        params['status'] = 2
        SeWorkTaskDao.updateTaskById(task_id, params)

        if task.parent_id:
            undone_task_list = SeWorkTaskDao.queryUndoneTaskByParentId(task.parent_id)
            if not undone_task_list:
                task_pco = SeWorkTaskDao.getTaskJoinSysUserById(task.parent_id)
                if task_pco:
                    task, project, task_create, task_owner = task_pco
                    template = SeWorkTaskArchiveEmail()
                    template.update({
                        "id": task.id, "task_number": task.task_number, "subject": task.subject
                    })
                    executor.submit(notice, target=task_owner.email, template=template)

        update_data = {"last_modified_by_id": session['user_id']}
        SeWorkProjectDao.updateProjectById(task.project_id, update_data)

        return jsonify(AppResponse())


post_record_parser = RequestParser()
post_record_parser.add_argument('support_start_date', location='json', type=validate_null, required=True)
post_record_parser.add_argument('support_end_date', location='json', type=validate_null, required=True)
post_record_parser.add_argument('support_duration', location='json', type=validate_half_hour, required=True)
post_record_parser.add_argument('record_content', location='json', type=list, required=True)
post_record_parser.add_argument('status', location='json', type=validate_null, choices=[1, 4], required=True)
post_record_parser.add_argument('attachments', location='json', type=list)


@internalwork_api.resource('/task/<task_id>/record')
class RecordAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    def post(self, task_id):
        """
        创建日志, 支持日期、所用工时、一些动态字段、附件、草稿、发布
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

        schema = SeWorkRecordSchema()
        record = schema.load(params)
        _id = SeWorkRecordDao.addRecord(record)
        data["id"] = _id

        if attachments:
            for attachment_id in attachments:
                update_data = {"related_object_id": _id}
                SysAttachmentDao.updateAttachmentById(attachment_id, update_data)

        if params["status"] == 4:
            task = SeWorkTaskDao.queryTaskById(task_id)
            if not task:
                return AppException("创建成功，审批流程创建失败")

            project_co = SeWorkProjectDao.getProjectJoinSysUserById(task.project_id)
            if not project_co:
                return AppException("创建成功，审批流程创建失败")
            project, create_user, owner_user = project_co[0], project_co[1], project_co[2]
            record_user = SysUserDao.querySysUserById(record.created_by_id)
            if not record:
                return AppException("创建成功，邮件通知失败")

            site_domain = current_app.config["SITE_DOMAIN"]
            record_content = ""
            record_content_load = json.loads(record.record_content)
            for content in record_content_load:
                if content.get("type") == "tip":
                    continue
                record_content += f'{content.get("name")}: {content.get("content")}  <br/>'

            target, cc, replay = [create_user.email], [], record_user.email
            if project.created_by_id == session['user_id']:
                update_record = {"status": 2}
                SeWorkRecordDao.updateRecordById(_id, update_record)
                update_data = {"last_modified_by_id": session['user_id']}
                SeWorkTaskDao.updateTaskById(task_id, update_data)
                SeWorkProjectDao.updateProjectById(task.project_id, update_data)

                record = SeWorkRecordDao.queryRecordById(_id)
                if not record:
                    return AppException("创建成功，邮件通知失败")

                if record_user.employee_id:
                    employee = TblEmployeeDao.queryEmployeeById(record_user.employee_id)
                    if employee:
                        leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                        if leader_employee:
                            cc.append(leader_employee.email)
                template = SeWorkRecordApprovedEmail()
                template.update({
                    "task_id": task.id, "task_number": task.task_number, "subject": task.subject,
                    "created_by_name": record_user.display_name, "approver": create_user.display_name,
                    "site_domain": site_domain,
                    "support_type_1st": getSeWorkProjectType(task.support_type_1st)["name"],
                    "support_type_2nd": getSeWorkProjectType(task.support_type_2nd)["name"],
                    "published_date": record.published_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_start_date": record.support_start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_end_date": record.support_end_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_duration": record.support_duration / 60,
                    "record_content": record_content
                })

            else:
                approval_record = {"record_id": _id, "project_id": project.id}
                schema = SeWorkApprovalRecordSchema()
                approval_record = schema.load(approval_record)
                SeWorkApprovalDao.addRecord(approval_record)

                template = SeWorkRecordPendingEmail()
                template.update({
                    "task_number": task.task_number, "subject": task.subject,
                    "created_by_name": record_user.display_name,
                    "site_domain": site_domain, "record_content": record_content,
                    "apporver": create_user.display_name
                })

            def notice(**kwargs):
                try:
                    message_gw.push(**kwargs)
                except Exception as e:
                    logger.error("RecordAPI Exception: {}".format(str(e)))
            executor.submit(notice, target=target, template=template, reply_to=replay, cc=cc)

        return jsonify(AppResponse(data))


put_record_parser = RequestParser()
put_record_parser.add_argument('support_start_date', location='json', type=validate_null)
put_record_parser.add_argument('support_end_date', location='json', type=validate_null)
put_record_parser.add_argument('support_duration', location='json', type=int)
put_record_parser.add_argument('record_content', location='json', type=list)
put_record_parser.add_argument('status', location='json', type=validate_null, choices=[1, 4])
put_record_parser.add_argument('attachments', location='json', type=list)


@internalwork_api.resource('/task/<task_id>/record/<record_id>')
class RecordEditAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    def put(self, task_id, record_id):
        """
        更新日志，判断是否草稿、只能草稿改发布
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
        SeWorkRecordDao.updateRecordById(record_id, params)

        if attachments:
            for attachment_id in attachments:
                update_data = {"related_object_id": record_id}
                SysAttachmentDao.updateAttachmentById(attachment_id, update_data)

        if params.get("status") == 4:
            task = SeWorkTaskDao.queryTaskById(task_id)
            if not task:
                return AppException("日志更新成功，审批流程创建失败")

            project_co = SeWorkProjectDao.getProjectJoinSysUserById(task.project_id)
            if not project_co:
                return AppException("日志更新成功，审批流程创建失败")
            project, create_user, owner_user = project_co[0], project_co[1], project_co[2]

            record = SeWorkRecordDao.queryRecordById(record_id)
            if not record:
                return AppException("创建成功，邮件通知失败")
            record_user = SysUserDao.querySysUserById(record.created_by_id)
            if not record:
                return AppException("创建成功，邮件通知失败")

            site_domain = current_app.config["SITE_DOMAIN"]
            record_content = ""
            record_content_load = json.loads(record.record_content)
            for content in record_content_load:
                if content.get("type") == "tip":
                    continue
                record_content += f'{content.get("name")}: {content.get("content")}  <br/>'

            target, cc, replay = [create_user.email], [], record_user.email
            if project.created_by_id == session['user_id']:
                update_record = {"status": 2}
                SeWorkRecordDao.updateRecordById(record_id, update_record)
                update_data = {"last_modified_by_id": session['user_id']}
                SeWorkTaskDao.updateTaskById(task_id, update_data)
                SeWorkProjectDao.updateProjectById(task.project_id, update_data)

                if record_user.employee_id:
                    employee = TblEmployeeDao.queryEmployeeById(record_user.employee_id)
                    if employee:
                        leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                        if leader_employee:
                            cc.append(leader_employee.email)
                template = SeWorkRecordApprovedEmail()
                template.update({
                    "task_id": task.id, "task_number": task.task_number, "subject": task.subject,
                    "created_by_name": record_user.display_name, "approver": create_user.display_name,
                    "site_domain": site_domain,
                    "support_type_1st": getSeWorkProjectType(task.support_type_1st)["name"],
                    "support_type_2nd": getSeWorkProjectType(task.support_type_2nd)["name"],
                    "published_date": record.published_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_start_date": record.support_start_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_end_date": record.support_end_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "support_duration": record.support_duration / 60,
                    "record_content": record_content
                })

            else:
                approval_record = {"record_id": record_id, "project_id": project.id}
                schema = SeWorkApprovalRecordSchema()
                approval_record = schema.load(approval_record)
                SeWorkApprovalDao.addRecord(approval_record)

                template = SeWorkRecordPendingEmail()
                template.update({
                    "task_number": task.task_number, "subject": task.subject,
                    "created_by_name": record_user.display_name,
                    "site_domain": site_domain, "record_content": record_content,
                    "apporver": create_user.display_name
                })

            def notice(**kwargs):
                try:
                    message_gw.push(**kwargs)
                except Exception as e:
                    logger.error("RecordEditAPI Exception: {}".format(str(e)))

            executor.submit(notice, target=target, template=template, reply_to=replay, cc=cc)

        return jsonify(AppResponse())

    def delete(self, task_id, record_id):
        """
        删除草稿日志
        :return:
        """

        delete_data = {"deleted_by_id": session['user_id'], 'last_modified_by_id': session['user_id']}
        SeWorkRecordDao.deleteRecordById(record_id, delete_data)

        return jsonify(AppResponse())


get_record_parser = RequestParser()
get_record_parser.add_argument('status', location='args', type=int, choices=[1, 2, 4], required=True)


@internalwork_api.resource('/task/<task_id>/record/list')
class RecordListAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
    @marsh_response(SeWorkRecordList)
    def get(self, task_id):
        """
        日志列表（或草稿列表）
        :return:
        """
        parser_args = prepare_args_for_parser(get_record_parser.copy())
        params = parser_args.parse_args()

        data = {"list": [], "total": 0, "page": 1, "size": 0}

        task_pco = SeWorkTaskDao.getTaskJoinSysUserById(task_id)
        if not task_pco:
            raise AppException("查询失败，任务不存在")

        task, project, create_user, owner_user = task_pco
        user_id = session["user_id"]
        if not (user_id == create_user.id or user_id == owner_user.id or user_id == project.created_by_id):
            flag = False
            if not task.parent_id:
                sub_task_list = SeWorkTaskDao.queryTaskByParentId(task_id)
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

        if params["status"] == 1:
            task = SeWorkTaskDao.queryTaskById(task_id)
            if task.owner_id != session["user_id"]:
                return data

        record_create_list = SeWorkRecordDao.getRecordJoinSysUserByStatus(task_id, params["status"])
        if not record_create_list:
            return data

        for record_c in record_create_list:
            record, create_user = record_c
            schema = SeWorkRecordSchema()
            record = schema.dump(record)

            record["record_content"] = json.loads(record["record_content"])
            record["created_by_name"] = create_user.display_name
            record["attachments"] = []
            attachments = SysAttachmentDao.queryAttachmentByObjectId("se_work_record", record["id"])
            for attachment in attachments:
                record["attachments"].append({
                    "id": attachment.id,
                    "filename": attachment.file_name,
                    "file_size": attachment.file_size,
                    "file_type": attachment.file_type
                })

            if record["status"] == 4:
                approval_record = SeWorkApprovalDao.queryApprovalRecordByRecordId(record["id"])
                if approval_record:
                    project_co = SeWorkProjectDao.getProjectJoinSysUserById(approval_record.project_id)
                    if project_co:
                        project, create_user, owner_user = project_co[0], project_co[1], project_co[2]
                        record["approval_id"] = create_user.id
                        record["approval_name"] = create_user.display_name

            if record["status"] == 1:
                approval_record = SeWorkApprovalDao.queryUnApprovalByRecordId(record["id"])
                if approval_record:
                    record["unapproval_reason"] = approval_record.incomplete_reason

            data["list"].append(record)

        data["total"] = len(record_create_list)
        data["size"] = len(record_create_list)

        return data


get_permission_parser = RequestParser()
get_permission_parser.add_argument('task_id', location='args', type=str)
get_permission_parser.add_argument('project_id', location='args', type=str)


@internalwork_api.resource('/permission/<page_title>')
class PagePermissionAPI(Resource):

    @permission.check(p_list['p_sework_internel_all'])
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

            project = SeWorkProjectDao.queryProjectById(params['project_id'])
            if not project:
                raise AppException("获取失败，项目不存在")

            if (project.owner_id == session['user_id'] or project.created_by_id == session['user_id'])\
                    and project.status != 3:
                data["list"] = ["create_task", "project_archive"]

            if project.status == 1 and project.created_by_id == session['user_id']:
                data["list"] += ["project_delete"]

        elif page_title == 'task_detail':
            if not params.get("task_id"):
                raise AppException("参数错误，任务ID不能为空")

            task = SeWorkTaskDao.queryTaskById(params.get("task_id"))
            if not task:
                raise AppException("获取失败，任务不存在")

            if task.owner_id == session['user_id'] and task.status == 1:
                data["list"] = ["create_record", "task_archive"]
                if not task.parent_id:
                    data["list"] += ["create_subtask"]

        return jsonify(AppResponse(data))


@internalwork_api.resource('/record/pending')
class RecordPendingAPI(Resource):

    @permission.check(p_list['p_sework_internel_project_add'])
    @marsh_response(SeWorkRecordList)
    def get(self):
        """
        获取待审批日志列表
        :return:
        """
        data = {"list": [], "total": 0, "page": 1, "size": 0}
        approval_rtc_list = SeWorkApprovalDao.getApprovalRecordByUserId(session['user_id'])
        for approval_rtc in approval_rtc_list:
            approval, record, project, create_user = approval_rtc
            task = SeWorkTaskDao.queryTaskById(record.task_id)
            if not task:
                raise AppException("查询失败，任务不存在")

            schema = SeWorkRecordSchema()
            record = schema.dump(record)
            record["task_number"] = task.task_number
            record["task_subject"] = task.subject
            record["record_content"] = json.loads(record["record_content"])
            record["created_by_name"] = create_user.display_name
            record["attachments"] = []
            attachments = SysAttachmentDao.queryAttachmentByObjectId("se_work_record", record["id"])
            for attachment in attachments:
                record["attachments"].append({
                    "id": attachment.id,
                    "filename": attachment.file_name,
                    "file_size": attachment.file_size,
                    "file_type": attachment.file_type
                })
            data["list"].append(record)

        data["total"] = len(data["list"])
        data["size"] = len(data["list"])
        return data


@internalwork_api.resource('/record/<record_id>')
class RecordDetailAPI(Resource):

    @permission.check(p_list['p_sework_internel_project_add'])
    def get(self, record_id):
        """
        日志详情
        :return:
        """
        record = SeWorkRecordDao.queryRecordById(record_id)
        if not record:
            raise AppException("查询失败，日志不存在")

        task = SeWorkTaskDao.queryTaskById(record.task_id)
        if not task:
            return AppException("查询失败，任务不存在")

        project = SeWorkProjectDao.queryProjectById(task.project_id)
        if not project:
            return AppException("查询失败，项目不存在")

        schema = SeWorkRecordSchema()
        data = schema.dump(record)
        data["task_number"] = task.task_number
        data["task_subject"] = task.subject
        data["record_content"] = json.loads(data["record_content"])
        data["project"] = {
            "id": project.id,
            "project_number": project.project_number,
            "subject": project.subject
        }

        if task.parent_id:
            parent_task = SeWorkTaskDao.queryTaskById(task.parent_id)
            if parent_task:
                data["parent_task"] = {
                    "id": parent_task.id,
                    "task_number": parent_task.task_number,
                    "subject": parent_task.subject
                }

        data["attachments"] = []
        attachments = SysAttachmentDao.queryAttachmentByObjectId("se_work_record", record_id)
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
        if "published_date" in data.keys():
            data.pop("published_date")

        return jsonify(AppResponse(data))


approval_record_parser = RequestParser()
approval_record_parser.add_argument('approval', location='json', choices=[1, 2], type=int, required=True)
approval_record_parser.add_argument('unapproval_reason', location='json', type=str)


@internalwork_api.resource('/record/<record_id>/approval')
class RecordApprovalAPI(Resource):

    @permission.check(p_list['p_sework_internel_project_add'])
    def put(self, record_id):
        """
        日志审批
        :return:
        """
        parser_args = prepare_args_for_parser(approval_record_parser.copy())
        params = parser_args.parse_args()

        if params["approval"] == 2 and not params.get("unapproval_reason"):
            raise AppException("操作失败，请填写原因")

        approval_record = SeWorkApprovalDao.queryApprovalRecordByRecordId(record_id)
        update_data = {
            "result": params["approval"],
            "incomplete_reason": params.get("unapproval_reason")
        }
        SeWorkApprovalDao.updateApprovalById(approval_record.id, update_data)

        update_data = {
            "status": 2 if params.get("approval") == 1 else 1,
            "last_modified_by_id": session['user_id']
        }
        SeWorkRecordDao.updateRecordById(record_id, update_data)

        record = SeWorkRecordDao.queryRecordById(record_id)
        if not record:
            return AppException("审批成功，邮件通知失败")

        update_data = {"last_modified_by_id": session['user_id']}
        SeWorkTaskDao.updateTaskById(record.task_id, update_data)

        task = SeWorkTaskDao.queryTaskById(record.task_id)
        if not task:
            return AppException("审批成功，邮件通知失败")
        project_co = SeWorkProjectDao.getProjectJoinSysUserById(task.project_id)
        if not project_co:
            return AppException("审批成功，邮件通知失败")
        project, create_user, owner_user = project_co[0], project_co[1], project_co[2]
        SeWorkProjectDao.updateProjectById(task.project_id, update_data)

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
            replay = record_user.email
            target.append(create_user.email)
            if record_user.employee_id:
                employee = TblEmployeeDao.queryEmployeeById(record_user.employee_id)
                if employee:
                    leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                    if leader_employee:
                        cc.append(leader_employee.email)

            template = SeWorkRecordApprovedEmail()
            template.update({
                "task_id": task.id, "task_number": task.task_number, "subject": task.subject,
                "created_by_name": record_user.display_name, "approver": create_user.display_name,
                "site_domain": site_domain,
                "support_type_1st": getSeWorkProjectType(task.support_type_1st)["name"],
                "support_type_2nd": getSeWorkProjectType(task.support_type_2nd)["name"],
                "published_date": record.published_date.strftime('%Y-%m-%d %H:%M:%S'),
                "support_start_date": record.support_start_date.strftime('%Y-%m-%d %H:%M:%S'),
                "support_end_date": record.support_end_date.strftime('%Y-%m-%d %H:%M:%S'),
                "support_duration": record.support_duration/60,
                "record_content": record_content
            })

        else:
            replay = create_user.email
            template = SeWorkRecordUnApprovedEmail()
            template.update({
                "task_id": task.id, "task_number": task.task_number, "subject": task.subject,
                "approver": create_user.display_name, "reject_reason": params.get("unapproval_reason"),
                "site_domain": site_domain, "record_content": record_content
            })
            cc.append(create_user.email)

        def notice(**kwargs):
            try:
                message_gw.push(**kwargs)
            except Exception as e:
                logger.error("RecordApprovalAPI Exception: {}".format(str(e)))

        executor.submit(notice, target=target, template=template, cc=cc, reply_to=replay)
        return jsonify(AppResponse())
