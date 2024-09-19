from flask import Blueprint
from flask_restful import Resource
from app.enums.permission_enum import p_list
from app.extensions import aliyun_util, permission
from app.utils.func_util import prepare_args_for_parser
from flask_restful.reqparse import RequestParser
from app.controllers.response import marsh_response, AliyunUserList
from app.utils.api_util import Api

agent_app = Blueprint('agent', __name__, url_prefix='/api/support/aliyun_ccc/agent')
agent_api = Api(agent_app)

get_user_parser = RequestParser()
get_user_parser.add_argument('name_pattern', location='args', type=str)
get_user_parser.add_argument('page', location='args', type=int, default=1)
get_user_parser.add_argument('size', location='args', type=int, default=1000)


@agent_api.resource('')
class AliyunUserListAPI(Resource):

    @permission.check(p_list['p_support_call_record_list'])
    @marsh_response(AliyunUserList, p_list['p_support_call_record_list'])
    def get(self):
        """
        获取通话记录接口
        :return:
        """
        parser_args = prepare_args_for_parser(get_user_parser.copy())
        params = parser_args.parse_args()

        user_list = aliyun_util.listUsers(**params)
        return user_list