import json

from datetime import datetime, timedelta
from flask import Blueprint, session, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.utils.func_util import prepare_args_for_parser
from app.utils.http_api.msg_template import SeWeeklyEmail
from app.enums.permission_enum import p_list
from app.extensions import permission, oss_util, executor, logger, message_gw
from app.controllers.schema import SeWeeklySchema
from app.controllers.dao import SeWeeklyDao, SysUserDao, DataScopeDao, TblDepartmentDao
from app.controllers.service import weekSummary, weekProjects, weekEcological, weekInternalWork, \
    weekWorkingStatistics, getLastWeeklyDate, queryWeeklyProject, queryWeeklyEcological, queryWeeklyInternalWork, \
    weekNeedProblem, weekWorkPlan
from app.controllers.response import marsh_response, SeWeekly, SeWeeklyList
from app.utils.api_util import Api, AppResponse, AppException

seweekly_app = Blueprint('seweekly', __name__, url_prefix='/api/presales/weekly')
seweekly_api = Api(seweekly_app)


post_weekly_parser = RequestParser()
post_weekly_parser.add_argument('subject', location='json', type=str, required=True)
post_weekly_parser.add_argument('cc', location='json', type=list)
post_weekly_parser.add_argument('receiver', location='json', type=list, required=True)
post_weekly_parser.add_argument('department_ids', location='json', type=list, required=True, default=[])
post_weekly_parser.add_argument('start_date', location='json', type=str, required=True)
post_weekly_parser.add_argument('end_date', location='json', type=str, required=True)
post_weekly_parser.add_argument('data', location='json', type=dict, required=True)


@seweekly_api.resource('')
class SeWeeklyNewAPI(Resource):

    @permission.check(p_list['p_se_weekly_list'])
    def post(self):
        """
        保存周报
        :return:
        """
        parser_args = prepare_args_for_parser(post_weekly_parser.copy())
        params = parser_args.parse_args()

        params["receiver"] = json.dumps(params["receiver"])
        params["cc"] = json.dumps(params["cc"])
        params["department_ids"] = json.dumps(sorted(params["department_ids"]))
        params["status"] = "Draft"
        params["template"] = "SeWeekly"
        params["created_by_id"] = session["user_id"]
        params["last_modified_by_id"] = session["user_id"]

        weekly_data = params.pop("data")
        params["version"] = weekly_data.get("version")
        schema = SeWeeklySchema()
        weekly = schema.load(params)
        weekly_id = SeWeeklyDao.addWeekly(weekly)

        oss_util.putObject('tech-template', f'SeWeekly_{weekly_id}.data', json.dumps(weekly_data.get("data")))

        data = {"id": weekly_id}
        return jsonify(AppResponse(data))


get_weekly_parser = RequestParser()
get_weekly_parser.add_argument('subject', location='args', type=str)
get_weekly_parser.add_argument('created_date_range[]', location='args', type=str, action='append', dest="receiver")
get_weekly_parser.add_argument('receiver[]', location='args', type=str, action='append', dest="receiver")
get_weekly_parser.add_argument('status[]', location='args', type=str, action='append', dest="status")
get_weekly_parser.add_argument('page', location='args', type=int, default=1)
get_weekly_parser.add_argument('size', location='args', type=int, default=1000)


@seweekly_api.resource('/list')
class SeWeeklyAPI(Resource):

    @permission.check(p_list['p_se_weekly_list'])
    @marsh_response(SeWeeklyList)
    def get(self):
        """
        周报列表
        :return:
        """
        parser_args = prepare_args_for_parser(get_weekly_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")), "size": int(params.get("size"))
        }

        user_id = session["user_id"]
        data["total"], weekly_list = SeWeeklyDao.getWeeklyByOwnerAndFilter(user_id, **params)
        for weekly_cm in weekly_list:
            weekly, c_user, m_user = weekly_cm
            schema = SeWeeklySchema()
            weekly = schema.dump(weekly)

            weekly["receiver"] = json.loads(weekly["receiver"])
            weekly["cc"] = json.loads(weekly["cc"])
            weekly["created_name"] = c_user.display_name
            weekly["department"] = []
            if weekly["department_ids"]:
                department_ids = json.loads(weekly["department_ids"])
                department_list = TblDepartmentDao.queryDepartmentByIds(department_ids)
                weekly["department"] = [
                    {"id": department.id, "name": department.name} for department in department_list
                ]

            data["list"].append(weekly)

        return data


@seweekly_api.resource('/<weekly_id>')
class SeWeeklyDetailAPI(Resource):

    @permission.check(p_list['p_se_weekly_list'])
    @marsh_response(SeWeekly)
    def get(self, weekly_id):
        """
        周报详情
        :return:
        """

        weekly = SeWeeklyDao.queryWeeklyById(weekly_id)
        c_user = SysUserDao.querySysUserById(weekly.created_by_id)

        schema = SeWeeklySchema()
        weekly = schema.dump(weekly)
        weekly["receiver"] = json.loads(weekly["receiver"])
        weekly["cc"] = json.loads(weekly["cc"])
        weekly["created_name"] = c_user.display_name
        weekly["department"] = []
        if weekly["department_ids"]:
            department_ids = json.loads(weekly["department_ids"])
            department_list = TblDepartmentDao.queryDepartmentByIds(department_ids)
            weekly["department"] = [
                {"id": department.id, "name": department.name} for department in department_list
            ]

        if weekly["status"] == "Draft":
            template_data, _ = oss_util.getObject('tech-template', f'SeWeekly_{weekly_id}.data')
            weekly["data"] = {
                "data": json.loads(template_data)
            }
        else:
            template_html, _ = oss_util.getObject('tech-template', f'SeWeekly_{weekly_id}.html')
            weekly["data"] = {
                "html": template_html.decode('utf-8')
            }

        return weekly

    @permission.check(p_list['p_se_weekly_list'])
    def post(self, weekly_id):
        """
        发送周报
        :return:
        """
        parser_args = prepare_args_for_parser(post_weekly_parser.copy())
        params = parser_args.parse_args()

        weekly = SeWeeklyDao.queryWeeklyById(weekly_id)
        if weekly.status == "Published":
            raise AppException("发送失败，周报已发送")

        target_email, cc_email = [], []
        if params["receiver"]:
            target_email = [r["email"] for r in params["receiver"]]
        if params["cc"]:
            cc_email = [r["email"] for r in params["receiver"]]

        params["department_ids"] = json.dumps(sorted(params["department_ids"]))
        params["receiver"] = json.dumps(params["receiver"])
        params["cc"] = json.dumps(params["cc"])
        params["status"] = "Published"
        params["send_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        weekly_data = params.pop("data")
        params["version"] = weekly_data.get("version")

        SeWeeklyDao.updateWeeklyById(weekly_id, params)
        oss_util.putObject('tech-template', f'SeWeekly_{weekly_id}.html', weekly_data.get("html").encode('utf-8'))

        def notice(**kwargs):
            try:
                message_gw.push(**kwargs)
            except Exception as e:
                logger.error("SeWeeklyDetailAPI Exception: {}".format(str(e)))

        template = SeWeeklyEmail()
        template.update({
            "subject": params["subject"],
            "data": weekly_data.get("html")
        })
        executor.submit(notice, target=target_email,  template=template, cc=cc_email)

        return jsonify(AppResponse())

    @permission.check(p_list['p_se_weekly_list'])
    def put(self, weekly_id):
        """
        编辑周报
        :return:
        """
        parser_args = prepare_args_for_parser(post_weekly_parser.copy())
        params = parser_args.parse_args()

        weekly = SeWeeklyDao.queryWeeklyById(weekly_id)
        if weekly.status == "Published":
            raise AppException("编辑失败，已发送周报无法编辑")

        params["receiver"] = json.dumps(params["receiver"])
        params["cc"] = json.dumps(params["cc"])
        params["department_ids"] = json.dumps(sorted(params["department_ids"]))
        params["status"] = "Draft"
        params["last_modified_by_id"] = session["user_id"]

        weekly_data = params.pop("data")
        params["version"] = weekly_data.get("version")

        SeWeeklyDao.updateWeeklyById(weekly_id, params)
        oss_util.putObject('tech-template', f'SeWeekly_{weekly_id}.data', json.dumps(weekly_data.get("data")))

        return jsonify(AppResponse(weekly_id))

    @permission.check(p_list['p_se_weekly_list'])
    def delete(self, weekly_id):
        weekly = SeWeeklyDao.queryWeeklyById(weekly_id)
        if weekly.status == "Published":
            raise AppException("删除失败，已发送周报无法删除")

        update_data = {
            "status": "Deleted",
            "deleted_by_id": session["user_id"],
            "deleted_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        SeWeeklyDao.updateWeeklyById(weekly_id, update_data)

        return jsonify(AppResponse(weekly_id))


get_tpdata_parser = RequestParser()
get_tpdata_parser.add_argument('key', location='args', type=str, required=True)
get_tpdata_parser.add_argument('department_ids[]', location='args', type=str, action='append', dest="department_ids")


@seweekly_api.resource('/template/data')
class SeWeeklyTemplateDataAPI(Resource):

    @permission.check(p_list['p_se_weekly_list'])
    def get(self):
        """
        获取模板数据
        :return:
        """
        parser_args = prepare_args_for_parser(get_tpdata_parser.copy())
        params = parser_args.parse_args()

        user_id = session["user_id"]
        department_ids = sorted(params["department_ids"]) if params.get("department_ids") else []
        last_date = getLastWeeklyDate(user_id, json.dumps(department_ids)).strftime('%Y-%m-%d %H:%M:%S')
        sysuser_employee = DataScopeDao.getDirectlyReportingById(user_id, department_ids)
        subordinate_ids = [sysuser.id for sysuser, _ in sysuser_employee] if sysuser_employee else []

        data = {}
        tp_key = params.get("key")
        if tp_key == "base":
            data["base"] = {
                "obj": {
                    "start_date": last_date,
                    "end_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "receiver": [],
                    "cc": [],
                    "subject": "",
                    "department_ids": []
                }
            }

        elif tp_key == "summary":
            data["summary"] = weekSummary(user_id, subordinate_ids, last_date)

        elif tp_key == "projects":
            data["projects"] = weekProjects(user_id, subordinate_ids, last_date)

        elif tp_key == "ecological":
            data["ecological"] = weekEcological(user_id, subordinate_ids, last_date)

        elif tp_key == "internalwork":
            data["internalwork"] = weekInternalWork(user_id, subordinate_ids, last_date)

        elif tp_key == "summationproblem":
            data["summationproblem"] = weekNeedProblem(user_id, subordinate_ids, last_date)

        elif tp_key == "workplan":
            data["workplan"] = weekWorkPlan(user_id, subordinate_ids, last_date)

        elif tp_key == "workingstatistics":
            data["workingstatistics"] = weekWorkingStatistics(user_id, subordinate_ids, last_date)

        return jsonify(AppResponse(data))


get_newdata_parser = RequestParser()
get_newdata_parser.add_argument('key', location='args', type=str, required=True)
get_newdata_parser.add_argument('data', location='args', type=str, required=True)


@seweekly_api.resource('/template/new/data')
class SeWeeklyNewDataAPI(Resource):

    @permission.check(p_list['p_se_weekly_list'])
    def get(self):
        """
        获取模板数据
        :return:
        """
        parser_args = prepare_args_for_parser(get_newdata_parser.copy())
        params = parser_args.parse_args()

        data = {}
        tp_key = params.get("key")
        number = params.get("data")
        if tp_key == "projects":
            data["projects"] = queryWeeklyProject(number)

        elif tp_key == "ecological":
            data["ecological"] = queryWeeklyEcological(number)

        elif tp_key == "internalwork":
            data["internalwork"] = queryWeeklyInternalWork(number)

        return jsonify(AppResponse(data))


get_notsend_parser = RequestParser()
get_notsend_parser.add_argument('department_ids[]', location='args', type=str, action='append', dest="department_ids")


@seweekly_api.resource('/not_send')
class SeWeeklyNotSendAPI(Resource):

    @permission.check(p_list['p_se_weekly_list'])
    def get(self):
        """
        查询没有发周报的下属
        :return:
        """
        data = {"list": []}

        parser_args = prepare_args_for_parser(get_notsend_parser.copy())
        params = parser_args.parse_args()

        user_id = session["user_id"]
        department_ids = sorted(params["department_ids"]) if params.get("department_ids") else []
        last_date = getLastWeeklyDate(user_id, json.dumps(department_ids))
        sysuser_employee = DataScopeDao.getDirectlyReportingById(user_id, department_ids)
        subordinate_ids = [sysuser.id for sysuser, _ in sysuser_employee] if sysuser_employee else []

        for subordinate_id in subordinate_ids:
            subordinate_user = None
            sub_weekly = SeWeeklyDao.queryLastWeekly(subordinate_id)
            if sub_weekly:
                if sub_weekly.send_date < last_date:
                    subordinate_user = SysUserDao.querySysUserById(subordinate_id)
            else:
                subordinate_user = SysUserDao.querySysUserById(subordinate_id)
            if subordinate_user:
                data["list"].append({"id": subordinate_user.id, "name": subordinate_user.display_name})
        return jsonify(AppResponse(data))
