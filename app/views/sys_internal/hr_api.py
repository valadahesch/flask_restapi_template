from flask import Blueprint
from flask_restful import Resource
from app.extensions import permission
from app.enums.permission_enum import p_list
from app.utils.func_util import prepare_args_for_parser
from app.controllers.dao import SysUserDao
from flask_restful.reqparse import RequestParser
from app.controllers.response import marsh_response, SeWorkOwnerList
from app.utils.api_util import Api

hr_app = Blueprint('hr', __name__, url_prefix='/api/internal/hr')
hr_api = Api(hr_app)


get_employee_parser = RequestParser()
get_employee_parser.add_argument('keyword', location='args', type=str, dest='employee_name')


@hr_api.resource('/staff/list')
class TaskOwnerAPI(Resource):

    @permission.check(p_list['p_internal_api_list'])
    @marsh_response(SeWorkOwnerList)
    def get(self):
        """
        任务责任人，当前用户及下属列表
        :return:
        """
        data = {"list": []}

        parser_args = prepare_args_for_parser(get_employee_parser.copy())
        params = parser_args.parse_args()

        if not params.get("employee_name"):
            return data

        sysuser_ed_list = SysUserDao.getSysUserEDByEmployeeName(params["employee_name"])
        for sysuser_employee_department in sysuser_ed_list:
            sysuser, employee, department = sysuser_employee_department
            user_name = f'{employee.name}-{department.name}-{employee.position}'
            owner = {
                "id": sysuser.id,
                "internal_email": employee.email,
                "user_name": user_name,
            }
            data["list"].append(owner)

        return data