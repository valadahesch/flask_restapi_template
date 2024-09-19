import json
from datetime import datetime
from app.extensions import redis_client, jwt_util
from app.config import SessionConfig
from flask import Blueprint, jsonify, request, session
from flask_restful import Resource
from app.controllers.dao import DataScopeDao
from app.extensions import permission
from app.enums.permission_enum import p_list
from flask_restful.reqparse import RequestParser
from app.utils.api_util import Api, AppException, AppResponse
from app.utils.func_util import prepare_args_for_parser, to_bool_or_none
from app.controllers.dao import TblEmployeeDao, SysUserDao, SysRoleUserDao
from app.controllers.schema import TbEmployeeSchema, SysUserSchema, SysRoleSchema, SysRoleUserSchema
from app.controllers.response import SSOUser, marsh_response, EmployeeDetail, EmployeeInfoList, SysUserList, SysUserDetail, \
    SysRoleList, SysSimulationUser

user_app = Blueprint('user', __name__, url_prefix='/api/sys/user')
user_api = Api(user_app)


employee_parser = RequestParser()
employee_parser.add_argument('name', location='args', type=str, nullable=True, dest='E.name')
employee_parser.add_argument('department', location='args', type=str, nullable=True, dest='D.name')
employee_parser.add_argument('position', location='args', type=str, nullable=True)
employee_parser.add_argument('gender', location='args', type=int, choices=[1, 2], nullable=True)
employee_parser.add_argument('is_local', location='args', type=bool, choices=[True, False], nullable=True)
employee_parser.add_argument('page', location='args', type=int, default=1)
employee_parser.add_argument('size', location='args', type=int, default=1000)


@user_api.resource('', '/employee')
class EmployeeAPI(Resource):

    @permission.check(p_list['p_employee_list'])
    @marsh_response(EmployeeInfoList)
    def get(self):
        """
        人员列表-企业内部员工，获取所有人员（部门），分页
        :return:
        """
        parser_args = prepare_args_for_parser(employee_parser.copy())
        params = parser_args.parse_args()
        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")),
            "size": int(params.get("size"))
        }

        user_id = session['user_id']
        user_ids = DataScopeDao.getSysUserByRank(user_id, 'employee:list')
        if not user_ids:
            return data

        total, sysuser_employee_department = SysUserDao.getSysUserEDByIdsAndFilter(user_ids, **params)
        data["total"] = total

        for sed in sysuser_employee_department:
            sys_user, employee, department = sed

            employee_schema = TbEmployeeSchema()
            employee = employee_schema.dump(employee)
            employee['gender'] = int(employee['gender'])
            employee['department'] = department.name
            employee["sys_user_id"] = sys_user.id

            data["list"].append(employee)

        return data


@user_api.resource('', '/employee/list/<role_id>')
class EmployeeRoleAPI(Resource):

    @permission.check(p_list['p_employee_list'])
    @marsh_response(EmployeeInfoList)
    def get(self, role_id):
        """
        查询角色下，人员列表-企业内部员工
        :return:
        """
        parser_args = prepare_args_for_parser(employee_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")),
            "size": int(params.get("size"))
        }

        total, employee_department_user = TblEmployeeDao.getEDUByFilter(**params)
        data["total"] += total

        employee_schema = TbEmployeeSchema()
        for edu in employee_department_user:
            employee, department, sys_user = edu
            employee = employee_schema.dump(employee)
            employee['gender'] = int(employee['gender'])
            employee['department'] = department.name
            employee["sys_user_id"] = sys_user.id

            if sys_user:
                role_user = SysRoleUserDao.querySysRoleByRoleUserId(role_id, sys_user.id)
                if role_user:
                    employee["has_the_role"] = True

            data["list"].append(employee)

        return data


@user_api.resource('', '/employee/<user_id>')
class EmployeeByIdAPI(Resource):

    @permission.check(p_list['p_employee_list'])
    @marsh_response(EmployeeDetail)
    def get(self, user_id):
        """
        人员列表-企业用户
        :return:
        """
        data = {"user_detail": {}}

        params = {"E.id": user_id}
        total, employee_department_sysuser = TblEmployeeDao.getEDByFilter(**params)

        employee_schema = TbEmployeeSchema()
        for eds in employee_department_sysuser:
            employee, department = eds[0], eds[1]
            employee = employee_schema.dump(employee)
            employee['gender'] = int(employee['gender'])
            employee['department'] = department.name
            sys_user = SysUserDao.querySysUserByEmployeeId(employee['id'])
            if sys_user:
                employee['local_name'] = sys_user.display_name
            data["user_detail"] = employee

        return data


local_user_parser = RequestParser()
local_user_parser.add_argument('name', location='args', type=str, nullable=True, dest='display_name')
local_user_parser.add_argument('user_type', location='args', type=int, nullable=True)
local_user_parser.add_argument('is_employee', location='args', type=to_bool_or_none, nullable=True)
local_user_parser.add_argument('is_login', location='args', type=to_bool_or_none, nullable=True)
local_user_parser.add_argument('page', location='args', type=int, default=1)
local_user_parser.add_argument('size', location='args', type=int, default=1000)


put_local_parse = RequestParser()
put_local_parse.add_argument('extattr', location='json', type=str, nullable=True)


@user_api.resource('', '/local')
class SysUserAPI(Resource):

    @permission.check(p_list['p_user_list'])
    @marsh_response(SysUserList, p_list['p_user_list'])
    def get(self):
        """
        人员列表-系统用户，获取用户信息
        :return:
        """
        parser_args = prepare_args_for_parser(local_user_parser.copy())
        params = parser_args.parse_args()
        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")),
            "size": int(params.get("size"))
        }

        total, sys_users = SysUserDao.querySysUserByFilter(**params)
        data["total"] += total

        schema = SysUserSchema()
        sys_users = schema.dump(sys_users, many=True)
        for sys_user in sys_users:
            sys_user['extattr'] = json.loads(sys_user['extattr']) if sys_user['extattr'] else []
            sys_user['is_employee'] = True if sys_user['employee_id'] else False
            data["list"].append(sys_user)

        return data

    @permission.check(p_list['p_user_mutation'])
    def put(self):
        """
        人员列表-系统用户， 编辑用户信息
        :return:
        """
        parser_args = prepare_args_for_parser(local_user_parser.copy())
        params = parser_args.parse_args()

        if params.get('extattr'):
            params['extattr'] = json.dumps(params['extattr'], ensure_ascii=False)
        SysUserDao.updateSysUserById(session["user_id"], params)


@user_api.resource('', '/local/list/<role_id>')
class SysUserRoleAPI(Resource):

    @permission.check(p_list['p_user_list'])
    @marsh_response(SysUserList, p_list['p_user_list'])
    def get(self, role_id):
        """
        查询角色下，人员列表-系统用户
        :return:
        """
        parser_args = prepare_args_for_parser(local_user_parser.copy())
        params = parser_args.parse_args()
        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")),
            "size": int(params.get("size"))
        }

        total, sys_users = SysUserDao.querySysUserByFilter(**params)
        data["total"] += total

        schema = SysUserSchema()
        sys_users = schema.dump(sys_users, many=True)
        for sys_user in sys_users:
            sys_user['extattr'] = json.loads(sys_user['extattr']) if sys_user['extattr'] else []
            sys_user['is_employee'] = True if sys_user['employee_id'] else False

            role_user = SysRoleUserDao.querySysRoleByRoleUserId(role_id, sys_user["id"])
            if role_user:
                sys_user["has_the_role"] = True

            data["list"].append(sys_user)

        return data


@user_api.resource('', '/local/<user_id>')
class SysUserByIdAPI(Resource):

    @permission.check(p_list['p_user_list'])
    @marsh_response(SysUserDetail)
    def get(self, user_id):
        """
        人员列表-系统用户详细信息
        :return:
        """
        data = {"user_detail": {}}
        sys_user = SysUserDao.querySysUserById(user_id)

        schema = SysUserSchema()
        sys_user = schema.dump(sys_user)
        sys_user['is_employee'] = True if sys_user['employee_id'] else False
        sys_user['extattr'] = json.loads(sys_user['extattr']) if sys_user['extattr'] else []
        data["user_detail"] = sys_user

        return data


put_role_parser = RequestParser()
put_role_parser.add_argument('role_list', location='json', type=list, required=True)


@user_api.resource('', '/local/<user_id>/role')
class UserByIdAPI(Resource):

    @permission.check(p_list['p_role_list'])
    @marsh_response(SysRoleList, only=["list.id", "list.name"])
    def get(self, user_id):
        """
        查询系统用户绑定的角色
        :return:
        """
        data = {"list": []}
        sr_list = SysRoleUserDao.getSRByByUserId(user_id)
        for sr in sr_list:
            schema = SysRoleSchema()
            role = schema.dump(sr[1])
            data["list"].append(role)

        return data

    @permission.check(p_list['p_role_mutation'])
    def put(self, user_id):
        """
        系统人员绑定批量角色
        :return:
        """
        failed_list = []
        parser_args = prepare_args_for_parser(put_role_parser.copy())
        params = parser_args.parse_args()

        role_user_list = SysRoleUserDao.querySysRolesByUserId(user_id)
        role_ids = [role_user.role_id for role_user in role_user_list]

        for role_user in role_user_list:
            if role_user.role_id not in params['role_list']:
                try:
                    SysRoleUserDao.deleteRoleUser(role_user.id)
                except AppException as e:
                    failed_list.append({"id": role_user.role_id, "message": e.message})

        for role_id in params['role_list']:
            if role_id not in role_ids:
                role_user = {"role_id": role_id, "user_id": user_id}
                schema = SysRoleUserSchema()
                role_user = schema.load(role_user)
                try:
                    SysRoleUserDao.addRoleUser(role_user)
                except AppException as e:
                    failed_list.append({"id": role_user.role_id, "message": e.message})

        if failed_list:
            data = {"failed_list": failed_list}
            return jsonify(AppResponse(data))

        return jsonify(AppResponse())


@user_api.resource('', '/local/generate/<string:user_id>/token')
class SysSimulationUser(Resource):

    @permission.check(p_list['p_user_generate_token'])
    @marsh_response(SysSimulationUser)
    def get(self, user_id):
        """
        系统管理-系统用户管理，身份模拟功能
        :return:
        """
        if request.headers.get("X-Real-User-Id"):
            raise AppException(message="当前处于身份模拟状态, 请退出后再进行操作")
        sso_user = {}
        sso_user = SSOUser(**sso_user).to_dict()
        role_users = SysRoleUserDao.querySysRolesByUserId(user_id)
        roles = [role_user.role_id for role_user in role_users]
        sso_user['roles'] = roles
        timestamp = datetime.now().timestamp()
        sso_user['timestamp'] = timestamp
        token = jwt_util.createToken(user_id, timestamp)
        redis_client.updateSimulationOnlineUser(user_id, sso_user, SessionConfig.get('sess_expire'))
        return {"token": token}