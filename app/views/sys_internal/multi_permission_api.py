import json
from flask import Blueprint, jsonify
from flask_restful import Resource
from werkzeug.datastructures import FileStorage
from flask_restful.reqparse import RequestParser
from app.utils.api_util import Api, AppResponse
from app.utils.func_util import prepare_args_for_parser
from app.controllers import ESService
from app.extensions import permission, apollo_util
from app.enums.permission_enum import p_list
from app.controllers.response import marsh_response, CrmSysCustomerList


multi_permission_app = Blueprint('multi_permission', __name__, url_prefix='/api/multi_permission')
multi_permission_api = Api(multi_permission_app)

post_common_parser = RequestParser()
post_common_parser.add_argument('meta', location='form', type=str)
post_common_parser.add_argument('file', location='files', type=FileStorage, required=True)


@multi_permission_api.resource("/district/list")
class ResourceAPI(Resource):

    @permission.check(p_list['p_common_district'])
    def get(self):
        """
        行政区域查询
        :return:
        """
        data = {"list": apollo_util.getValue("district")}

        return jsonify(AppResponse(data))


get_customer_parser = RequestParser()
get_customer_parser.add_argument('customer', location='args', type=str)


@multi_permission_api.resource("/crm/customer")
class ResourceDownloadAPI(Resource):

    @permission.check(p_list['p_common_customer'])
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
