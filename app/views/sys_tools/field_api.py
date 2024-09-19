from marshmallow.schema import SchemaMeta
from flask import Blueprint, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.utils.api_util import Api, AppResponse
from app.controllers import response
from app.utils.func_util import prepare_args_for_parser

field_app = Blueprint('field', __name__, url_prefix='/api/tools/field')
field_api = Api(field_app)

field_attr_parser = RequestParser()
field_attr_parser.add_argument('subsystem', location='args', type=str, nullable=True, required=True)
field_attr_parser.add_argument('object', location='args', type=str, nullable=True, required=True)


@field_api.resource('', '/attributes')
class FieldListToolsAPI(Resource):

    def get(self):
        """
        获取左侧项目菜单列表权限， 一次返回权限下所有的菜单
        :return:
        """
        data = {"list": []}
        parser_args = prepare_args_for_parser(field_attr_parser.copy())
        field_attr_params = parser_args.parse_args()

        for k in dir(response):
            resp_class = getattr(response, k)

            if isinstance(resp_class, SchemaMeta):
                resp_class = resp_class()
                if hasattr(resp_class, '__subsystem__') and hasattr(resp_class, '__object__'):
                    subsystem = getattr(resp_class, '__subsystem__')
                    sub_object = getattr(resp_class, '__object__')
                    if field_attr_params['subsystem'] == subsystem and field_attr_params['object'] == sub_object:
                        data["list"] = resp_class.attributes()

        return jsonify(AppResponse(data))
