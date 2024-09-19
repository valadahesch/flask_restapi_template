from flask import Blueprint
from app.enums.permission_enum import p_list
from app.extensions import permission
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.utils.api_util import Api
from app.utils.func_util import prepare_args_for_parser
from app.controllers.dao import TblDepartmentDao, TblEmployeeDao
from app.controllers.schema import TblDepartmentSchema, TbEmployeeSchema
from app.controllers.response import marsh_response, EmployeeSimpleList, DepartmentList

department_app = Blueprint('department', __name__, url_prefix='/api/sys/department')
department_api = Api(department_app)

department_parser = RequestParser()
department_parser.add_argument('name', location='args', type=str, nullable=True)
department_parser.add_argument('name_en', location='args', type=str, nullable=True)


@department_api.resource('')
class UserAPI(Resource):

    @permission.check(p_list['p_department_list'])
    @marsh_response(DepartmentList)
    def get(self):
        """
        部门管理，获取所有部门
        :return:
        """
        parser_args = prepare_args_for_parser(department_parser.copy())
        department_params = parser_args.parse_args()

        data = {"list": []}
        if 'name' in department_params.keys() or 'name_en' in department_params.keys():
            department_ids = []
            departments = []
            _, department_list = TblDepartmentDao.queryDepartmentByFilter(**department_params)
            for department in department_list:
                if department.id in department_ids:
                    continue
                departments.append(department)
                department_ids.append(department.id)
                parent_menus = TblDepartmentDao.queryParentDepartmentById(department.id)
                for parent_menu in parent_menus:
                    if parent_menu.id in department_ids:
                        continue
                    department_ids.append(parent_menu.id)
                    departments.append(parent_menu)

        else:
            departments = TblDepartmentDao.queryDepartment()

        department_schema = TblDepartmentSchema()
        departments = department_schema.dump(departments, many=True)

        data["list"] = departments
        return data


department_user_parser = RequestParser()
department_user_parser.add_argument('department_ids[]', location='args', type=int, action='append', required=True)


@department_api.resource('/user')
class DepartmentUserAPI(Resource):

    @permission.check(p_list['p_employee_list'])
    @marsh_response(EmployeeSimpleList)
    def get(self):
        """
        部门下的员工
        :return:
        """
        data = {"list": []}
        parser_args = prepare_args_for_parser(department_user_parser.copy())
        params = parser_args.parse_args()

        schema = TbEmployeeSchema(only=['id', 'name', 'main_department'])
        for department_id in params['department_ids[]']:
            employee_department_user_list = TblEmployeeDao.getEDUByDepartmentId(department_id)
            for employee_department_user in employee_department_user_list:
                employee, department, sys_user = employee_department_user
                employee = schema.dump(employee)
                if department:
                    employee['main_department'] = department.name
                    employee['sys_user_id'] = sys_user.id

                data["list"].append(employee)

        return data
