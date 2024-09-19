from flask import Blueprint, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.utils.api_util import Api, AppResponse
from app.extensions import logger
from app.controllers.dao import TblEmployeeDao, TblDepartmentDao, SysUserDao, SysRoleUserDao, SysRoleDao
from app.controllers.schema import TbEmployeeSchema, TblDepartmentSchema, SysUserSchema, SysRoleUserSchema
from app.utils.func_util import prepare_args_for_parser
from app.controllers.response import SSOUser

sync_app = Blueprint('sync', __name__, url_prefix='/api/tools/sync')
sync_api = Api(sync_app)

put_employee_parser = RequestParser()
put_employee_parser.add_argument('update', location='json', type=list)


@sync_api.resource('', '/employee')
class SyncEmployeeAPI(Resource):

    def put(self):
        """
        同步人员信息
        :return:
        """
        parser_args = prepare_args_for_parser(put_employee_parser.copy())
        params = parser_args.parse_args()

        failed_list = []
        if params.get('update'):
            for employee_info in params['update']:
                try:
                    schema = TbEmployeeSchema()
                    employee = schema.load(employee_info)
                    employee_id = TblEmployeeDao.addEmployee(employee)
                    sys_user = SysUserDao.querySysUserByEmail(employee.email)
                    if sys_user:
                        if sys_user.employee_id:
                            continue
                        update_data = {"employee_id": employee_id}
                        SysUserDao.updateSysUserById(sys_user.id, update_data)

                except Exception as e:
                    failed_list.append({"id": employee_info["userid"], "error": str(e)})

        if failed_list:
            if failed_list:
                data = {"failed_list": failed_list}
                return jsonify(AppResponse(data))

        return jsonify(AppResponse())


put_department_parser = RequestParser()
put_department_parser.add_argument('update', location='json', type=list)


@sync_api.resource('', '/department')
class SyncDepartmentAPI(Resource):

    def put(self):
        """
        同步人员信息
        :return:
        """
        parser_args = prepare_args_for_parser(put_department_parser.copy())
        params = parser_args.parse_args()

        failed_list = []
        if params.get('update'):
            for department_info in params['update']:
                try:
                    schema = TblDepartmentSchema()
                    department = schema.load(department_info)
                    TblDepartmentDao.addDepartment(department)
                except Exception as e:
                    failed_list.append({"id": department_info["id"], "error": str(e)})

            if failed_list:
                if failed_list:
                    data = {"failed_list": failed_list}
                    return jsonify(AppResponse(data))

        return jsonify(AppResponse())


put_passport_parser = RequestParser()
put_passport_parser.add_argument('update', location='json', type=list)


@sync_api.resource('', '/passport/user')
class SyncPasswordUserAPI(Resource):

    def put(self):
        """
        更新系统人员
        :return:
        """
        parser_args = prepare_args_for_parser(put_passport_parser.copy())
        params = parser_args.parse_args()

        failed_list = []
        if params.get('update'):
            for sso_user in params['update']:
                try:
                    only = [
                        'id', 'user_id', 'user_name', 'dp_name', 'first_name', 'last_name', 'nick_name',
                        'birthday', 'user_type', 'company_name', 'mobile', 'email'
                    ]
                    sso_user = SSOUser(**sso_user).to_dict()
                    if "hillstonenet.com" in sso_user.get("email").lower():
                        employee = TblEmployeeDao.queryEmployeeByEmail(sso_user["email"])
                        if employee:
                            sso_user["employee_id"] = employee.id
                            only.append('employee_id')

                    user_schema = SysUserSchema(only=only)
                    sys_user = user_schema.load(sso_user, unknown='exclude')
                    user_id = SysUserDao.addSysUserBySSO(sys_user, login_time=False)
                    if not user_id:
                        logger.error(f"用户创建失败，userId: {sso_user['user_id']}")
                        failed_list.append({"id": sso_user["user_id"], "error": "用户创建失败"})

                    # 获取角色，没有角色创建默认角色
                    role_users = SysRoleUserDao.querySysRolesByUserId(user_id)
                    if not role_users:
                        role_type = 1 if 'employee_id' in sso_user.keys() else 2
                        role = SysRoleDao.querySysRoleByType(role_type)
                        role_user = {"role_id": role.id, "user_id": user_id}
                        schema = SysRoleUserSchema()
                        role_user = schema.load(role_user)
                        SysRoleUserDao.addRoleUser(role_user)

                except Exception as e:
                    failed_list.append({"id": sso_user["user_id"], "error": str(e)})

            if failed_list:
                if failed_list:
                    data = {"failed_list": failed_list}
                    return jsonify(AppResponse(data))

        return jsonify(AppResponse())