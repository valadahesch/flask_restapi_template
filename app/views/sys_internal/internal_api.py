import json

from flask import Blueprint, session, jsonify
from flask_restful import Resource
from app.extensions import permission, apollo_util
from app.enums.permission_enum import p_list
from app.controllers.dao import SysUserDao, TblDepartmentDao, DataScopeDao, TblEmployeeDao
from app.controllers.dao.techadmin_dao import SysUserRedisDao
from flask_restful.reqparse import RequestParser
from app.controllers.response import marsh_response, SeWorkOwner, PersonInfo, SysUserInfoResponse
from app.utils.api_util import Api, AppResponse
from app.utils.func_util import prepare_args_for_parser

internal_app = Blueprint('internal', __name__, url_prefix='/api')
internal_api = Api(internal_app)


@internal_api.resource('/internal/user/<user_id>/department')
class SysUserEmployeeAPI(Resource):

    @permission.check(p_list['p_internal_api_list'])
    @marsh_response(SeWorkOwner)
    def get(self, user_id):
        """
        根据系统用户ID，查询用户的部门信息
        :return:
        """
        data = {}
        sysuser_employee = SysUserDao.getSysUserEmployeeById(user_id)
        if not sysuser_employee:
            return data

        sysuser, employee = sysuser_employee
        if not employee:
            return data

        department = TblDepartmentDao.queryDepartmentById(employee.department)
        if not department:
            return data

        user_name = f'{employee.name}-{department.name}-{employee.position}'
        data = {
            "id": user_id,
            "internal_email": employee.email,
            "user_name": user_name,
        }
        return data


@internal_api.resource('/internal/manage/department')
class ManageDepartmentAPI(Resource):

    @permission.check(p_list['p_internal_api_list'])
    def get(self):
        """
        根据系统用户ID，查询用户的部门信息
        :return:
        """
        data = {"list": []}
        department_list = []
        user_id = session["user_id"]
        user_employee = SysUserDao.getSysUserEmployeeById(user_id)
        if user_employee:
            employee = user_employee[1]
            department = TblDepartmentDao.queryDepartmentById(employee.department)
            if department:
                department_list.append({"id": department.id, "name": department.name})

        sysuser_employee = DataScopeDao.getDirectlyReportingById(user_id)
        for sys_user, employee in sysuser_employee:
            department = TblDepartmentDao.queryDepartmentById(employee.department)
            if department:
                res = {"id": department.id, "name": department.name}
                if res not in department_list:
                    department_list.append(res)

        data["list"] = department_list
        return jsonify(AppResponse(data))


put_person_parser = RequestParser()
put_person_parser.add_argument('manage_id', location='json', type=str)
put_person_parser.add_argument('work_city_adcode', location='json', type=str)
put_person_parser.add_argument('work_city', location='json', type=str)


@internal_api.resource('/internal/person/info')
class PersonInfo(Resource):

    @permission.check(p_list['p_internal_api_list'])
    @marsh_response(PersonInfo)
    def get(self):
        """
        内部人员获取个人信息
        :return:
        """
        data = {}
        user_id = session["user_id"]
        sysuser_employee_department = SysUserDao.getSysUserEDById(user_id)
        if sysuser_employee_department:
            sys_user, employee, department = sysuser_employee_department

            manage_name = ""
            if sys_user.manage_id:
                manage_sysuser_employee = SysUserDao.getSysUserEmployeeById(sys_user.manage_id)
                if manage_sysuser_employee:
                    manage_sysuser, manage_employee = manage_sysuser_employee
                    manage_name = manage_employee.name

            manage_ehr_name = ""
            if employee.leader:
                employee_leader = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                if employee_leader:
                    manage_ehr_name = employee_leader.name

            def get_extattr(name):
                value = ""
                if employee.extattr:
                    extattr = json.loads(employee.extattr)
                    for ext in extattr["attrs"]:
                        if ext["name"] == name:
                            value = ext["value"]
                return value

            data = {
                "id": sys_user.id,
                "display_name": sys_user.display_name,
                "employee_name": employee.name,
                "mobile": employee.mobile,
                "email": employee.email,
                "employee_number": employee.employee_number,
                "company": get_extattr("隶属公司"),
                "rank": get_extattr("职级"),
                "manage_id": sys_user.manage_id,
                "manage_name": manage_name,
                "manage_ehr_name": manage_ehr_name,
                "entry_time": get_extattr("入职时间"),
                "department": department.name,
                "position": employee.position,
                "work_city_adcode": sys_user.work_city_adcode,
                "work_city": sys_user.work_city,
            }

        return data

    @permission.check(p_list['p_internal_api_list'])
    def put(self):
        """
        内部人员编辑个人信息
        :return:
        """

        parser_args = prepare_args_for_parser(put_person_parser.copy())
        params = parser_args.parse_args()

        user_id = session["user_id"]
        SysUserDao.updateSysUserById(user_id, params)

        return jsonify(AppResponse())


@internal_api.resource('/internal/district/list')
class DistrictList(Resource):

    @permission.check(p_list['p_internal_api_list'])
    def get(self):
        """
        行政区域查询
        :return:
        """
        data = {"list": []}
        data["list"] = apollo_util.getValue("district")

        return jsonify(AppResponse(data))


@internal_api.resource('/internal/person/subordinate')
class PersonSubordinate(Resource):

    # @permission.check(p_list['p_internal_api_list'])
    def get(self):
        """
        获取系统个人下属
        :return:
        """
        data = {"list": []}
        user_id = session["user_id"]
        sysuser_list = SysUserDao.getSysPersonSubordinateIdById(user_id)
        for sys_user in sysuser_list:
            data["list"].append({"id": sys_user.id, "name": sys_user.display_name, "manage_id": sys_user.manage_id})

        return jsonify(AppResponse(data))
    

@internal_api.resource('/public/user/info/<user_id>')
class SysUserInfo(Resource):

    @permission.check(p_list['p_internal_api_list'])
    @marsh_response(SysUserInfoResponse)
    def get(self, user_id):
        """
        根据系统用户ID, 查询系统用户详细信息
        """
        data = SysUserRedisDao.querySysUserInfo(user_id)
        if not data:
            SysUserInfo = SysUserDao.querySysUserInfoById(user_id)
            user, employee = SysUserInfo.get("user"), SysUserInfo.get("employee")
            company, rank, manage_ehr_id, manage_ehr_name, entry_time = "", "", "", "", ""
            if employee:
                if employee.is_deleted == 1:
                    status = "leave"
                elif employee.is_deleted == 0:
                    status = "on"
                else:
                    status = "unkown"

                if employee.extattr:
                    extattr = json.loads(employee.extattr)
                    for attr in extattr["attrs"]:
                        if attr.get("name") == "隶属公司":
                            company = attr.get("value")
                        if attr.get("name") == "职级":
                            rank = attr.get("value")
                        if attr.get("name") == "入职时间":
                            entry_time = attr.get("value")
                        if attr.get("name") == "直接经理":
                            try:
                                avatar_user_id = attr.get("value")
                                avatar_user, avatar_employee = SysUserDao.querySysUserByEmployeeUserId(avatar_user_id)
                                manage_ehr_id = avatar_user.id
                                manage_ehr_name = avatar_employee.name
                            except:
                                manage_ehr_id, manage_ehr_name = "", ""

                department = TblDepartmentDao.queryAllHigherDepartment(user_id)
                department = department[::-1]
                data = {
                        "id": user.id,
                        "display_name": employee.name if employee.name else user.display_name,
                        "mobile": employee.mobile if employee.mobile else user.mobile, 
                        "email": employee.email if employee.email else user.email,
                        "status": status,
                        "avatar": employee.avatar,
                        "employee_number": employee.employee_number,
                        "company": company,
                        "rank": rank,
                        "manage_ehr_id": manage_ehr_id,
                        "manage_ehr_name": manage_ehr_name,
                        "entry_time": entry_time,
                        "departments": department,
                        "position": employee.position,
                        "gender": employee.gender,
                        "work_city_adcode": user.work_city_adcode,
                        "work_city": user.work_city
                    }
            else:
                data = {
                        "id": user.id,
                        "display_name": user.display_name,
                        "mobile": user.mobile, 
                        "email": user.email,
                        "status": "",
                        "avatar": "",
                        "employee_number": "",
                        "company": user.company_name,
                        "rank": "",
                        "manage_ehr_id": "",
                        "manage_ehr_name": "",
                        "entry_time": "",
                        "departments": [],
                        "position":"",
                        "gender": "",
                        "work_city_adcode": user.work_city_adcode,
                        "work_city": user.work_city
                    }      
            SysUserRedisDao.setSysUserInfo(user_id, data)
        return data