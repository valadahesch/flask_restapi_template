from flask import Blueprint, session
from flask_restful import Resource
from app.extensions import permission
from app.enums.permission_enum import p_list
from app.controllers import ESService
from app.controllers.dao import SysUserDao, TblEmployeeDao, CrmViewsDao, DataScopeDao
from app.utils.func_util import prepare_args_for_parser, input_filter
from app.controllers.schema import SysUserSchema
from flask_restful.reqparse import RequestParser
from app.controllers.response import marsh_response, CrmSysCustomerList, CrmSysUserList, CrmSysCustomer, \
    CrmSysUser, SeWorkOwnerList
from app.utils.api_util import Api

crm_app = Blueprint('crm', __name__, url_prefix='/api/internal/crm')
crm_api = Api(crm_app)

get_customer_parser = RequestParser()
get_customer_parser.add_argument('customer', location='args', type=input_filter)


@crm_api.resource('/customer')
class CrmSysCustomerAPI(Resource):

    @permission.check(p_list['p_internal_api_list'])
    @marsh_response(CrmSysCustomerList)
    def get(self):
        """
        获取CRM系统客户
        :return:
        """
        parser_args = prepare_args_for_parser(get_customer_parser.copy())
        params = parser_args.parse_args()

        data = {"list": []}
        _, data["list"] = ESService.queryCrmAccountByAccountName(params.get('customer'))
        return data


@crm_api.resource('/customer/<customer_id>')
class CrmSysCustomerIdAPI(Resource):

    @permission.check(p_list['p_internal_api_list'])
    @marsh_response(CrmSysCustomer)
    def get(self, customer_id):
        """
        获取CRM系统客户
        :return:
        """
        data = ESService.queryCrmAccountByAccountId(customer_id)
        if data:
            if data.get("OwnerId"):
                owner = ESService.queryCrmSystemUserByUserId(data["OwnerId"])
                if owner:
                    if owner.get("internalemail"):
                        sys_user = SysUserDao.querySysUserByEmail(owner["internalemail"])
                        data["owner_id"] = sys_user.id
                        data["owner_name"] = sys_user.display_name
        return data


get_sysuser_parser = RequestParser()
get_sysuser_parser.add_argument('sysuser', location='args', type=str)


@crm_api.resource('/sysuser')
class CrmSysUserAPI(Resource):

    @permission.check(p_list['p_internal_api_list'])
    @marsh_response(CrmSysUserList)
    def get(self):
        """
        获取CRM系统用户
        :return:
        """
        parser_args = prepare_args_for_parser(get_sysuser_parser.copy())
        params = parser_args.parse_args()

        data = {"list": []}
        _, data["list"] = ESService.queryCrmSysUserByUserName(params['sysuser'])

        return data


@crm_api.resource('/sysuser/<user_id>')
class CrmSysUserIdAPI(Resource):

    @permission.check(p_list['p_internal_api_list'])
    @marsh_response(CrmSysUser)
    def get(self, user_id):
        """
        获取CRM系统用户
        :return:
        """

        data = ESService.queryCrmSystemUserByUserId(user_id)
        return data


@crm_api.resource('/my_assignable_se_staff')
class ProjectOwnerAPI(Resource):

    @permission.check(p_list['p_internal_api_list'])
    @marsh_response(SeWorkOwnerList)
    def get(self):
        """
        责任人，当前用户及下属列表
        :return:
        """
        data = {"list": []}
        user_id = session["user_id"]

        sysuser_employee = SysUserDao.getSysUserEmployeeById(user_id)
        if not sysuser_employee:
            return data

        sysuser, employee = sysuser_employee
        assign_list = CrmViewsDao.queryAssignUserByEmail(sysuser.email)
        for assign in assign_list:
            employee_department = TblEmployeeDao.getEmployeeJoinDepartmentDByEmail(assign[7])
            if not employee_department:
                continue

            employee, department = employee_department
            assign_sysuser = SysUserDao.querySysUserByEmail(assign[7])
            if not assign_sysuser:
                sys_user = SysUserDao.querySysUserByEmployeeId(employee.id)
                if sys_user:
                    user_id = sys_user.id
                else:
                    schema = SysUserSchema(only=['id', 'display_name', 'employee_id'])
                    sys_user = schema.load({"display_name": employee.name, "employee_id": employee.id})
                    user_id = SysUserDao.addSysUserByEmployee(sys_user)
            else:
                user_id = assign_sysuser.id

            user_name = f'{employee.name}-{department.name}-{employee.position}'
            owner = {
                "id": user_id,
                "internal_email": employee.email,
                "user_name": user_name,
            }
            data["list"].append(owner)

        if not assign_list and '数字化支持' in employee.position:
            employee_department_list = TblEmployeeDao.getEDByDepartmentId(1809)
            for employee_department in employee_department_list:
                employee, department = employee_department
                user_name = f'{employee.name}-{department.name}-{employee.position}'

                sys_user = SysUserDao.querySysUserByEmployeeId(employee.id)
                if sys_user:
                    owner = {
                        "id": sys_user.id,
                        "internal_email": employee.email,
                        "user_name": user_name,
                    }
                    data["list"].append(owner)

        return data


@crm_api.resource('/my_assigner')
class CrmMyAssignerAPI(Resource):

    @permission.check(p_list['p_internal_api_list'])
    @marsh_response(SeWorkOwnerList)
    def get(self):
        """
        我的直属分派员列表
        :return:
        """
        data = {"list": []}
        user_id = session["user_id"]

        sysuser_employee = SysUserDao.getSysUserEmployeeById(user_id)
        if not sysuser_employee:
            return data

        assigner_ids = []
        sysuser, employee = sysuser_employee
        crm_assigner_list = CrmViewsDao.queryAssignerByEmail(sysuser.email)
        for assigner in crm_assigner_list:
            employee_department = TblEmployeeDao.getEmployeeJoinDepartmentDByEmail(assigner[3])
            if not employee_department:
                continue

            employee, department = employee_department
            assign_sysuser = SysUserDao.querySysUserByEmployeeId(assigner[3])
            if not assign_sysuser:
                sys_user = SysUserDao.querySysUserByEmployeeId(employee.id)
                if sys_user:
                    assigner_user_id = sys_user.id
                else:
                    schema = SysUserSchema(only=['id', 'display_name', 'employee_id'])
                    sys_user = schema.load({"display_name": employee.name, "employee_id": employee.id})
                    assigner_user_id = SysUserDao.addSysUserByEmployee(sys_user)
            else:
                assigner_user_id = assign_sysuser.id

            user_name = f'{employee.name}-{department.name}-{employee.position}'
            owner = {
                "id": assigner_user_id,
                "internal_email": employee.email,
                "user_name": user_name,
            }
            assigner_ids.append(assigner_user_id)
            data["list"].append(owner)

        local_assigner_list = DataScopeDao.getAllSuperiorByUserId(user_id)
        for local_assigner in local_assigner_list:
            if local_assigner in assigner_ids:
                continue

            sysuser_ed = SysUserDao.getSysUserEDById(local_assigner)
            if sysuser_ed:
                sys_user, employee, department = sysuser_ed
                user_name = f'{employee.name}-{department.name}-{employee.position}'
                owner = {
                    "id": sys_user.id,
                    "internal_email": employee.email,
                    "user_name": user_name,
                }
                assigner_ids.append(sys_user.id)
                data["list"].append(owner)

        return data
