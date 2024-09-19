import json
from flask import request, session, Blueprint
from flask_restful import Resource
from app.controllers.response import marsh_response
from app.extensions import permission, redis_client
from app.enums.permission_enum import p_list
from app.utils.api_util import Api, AppException, AppResponse
from flask_restful.reqparse import RequestParser
from app.utils.func_util import getCurrentTime, getRandomString16, validate_input, str_to_bool, validate_null
from app.controllers.response.message_gateway_respone import AddMessageGatewayTemplateResponse, GetMessageGatewayTemplateResponse, \
                                                             ListMessageGatewayTemplateResponse, PutMessageGatewayTemplateResponse
from app.controllers.dao.message_gateway_dao import MessageGatewayTempalteDao
from app.utils.func_util import prepare_args_for_parser


message_gateway_app = Blueprint('message_gateway', __name__, url_prefix='/api/message_gateway')
message_gateway_api = Api(message_gateway_app)


message_gateway_parser = RequestParser()
message_gateway_parser.add_argument('template_number', location='json', type=validate_null)
message_gateway_parser.add_argument('subject', location='json', type=validate_null)
message_gateway_parser.add_argument('content', location='json', type=validate_null)
message_gateway_parser.add_argument('enable', location='json', type=bool)
message_gateway_parser.add_argument('media_type', location='json', type=validate_null)
message_gateway_parser.add_argument('language', location='json', type=validate_null)
message_gateway_parser.add_argument('remark', location='json', type=str)

list_message_gateway_parser = RequestParser()
list_message_gateway_parser.add_argument('language[]', location='args', type=str, action='append', dest='language')
list_message_gateway_parser.add_argument('enable[]', location='args', type=str_to_bool, action='append', dest='enable')
list_message_gateway_parser.add_argument('media_type[]', location='args', type=str, action='append', dest='media_type')
list_message_gateway_parser.add_argument('like', location='args', type=str)
list_message_gateway_parser.add_argument('page', location='args', type=int)
list_message_gateway_parser.add_argument('size', location='args', type=int)

@message_gateway_api.resource('/template')
class AddMessageGatewayTemplate(Resource):
    @permission.check(p_list['p_message_gateway_template_all'])
    @marsh_response(AddMessageGatewayTemplateResponse)
    def post(self):
        """
        function: 新增消息网关模版
        """
        parser_args = prepare_args_for_parser(message_gateway_parser.copy())
        params = parser_args.parse_args()
        current_time = getCurrentTime()
        template_id = getRandomString16()
        all_template_id = MessageGatewayTempalteDao.queryAllTemplateId()
        while template_id in all_template_id:
            template_id = getRandomString16()
        template_number = params.get("template_number")
        if not validate_input(template_number):
            raise AppException(message="模版编号要求长度不大于10位,并且仅包含数字和英文字母")
        params["created_by_id"] = session['user_id']
        params["last_modified_by_id"] = session['user_id']
        params["last_modified_date"] = current_time
        params["created_date"] = current_time
        params["id"] = template_id

        language = params.get("language")
        if language == "zh_cn":
            redis_key = f"message:template:{template_number}"
        elif language == "en_us":
            redis_key = f"message:template:{template_number}:en:us"
        else:
            raise AppException(message="请检查语种(language)参数是否正常")
         
        redis_data = {"subject": params.get("subject"), "content": params.get("content"), 
                      "enable": params.get("enable")}
        redis_client.set(name=redis_key, value=json.dumps(redis_data))
        MessageGatewayTempalteDao.addMessageTemplate(params)
        return {"id": template_id}


@message_gateway_api.resource('/template/<string:template_id>')
class MessageGatewayTemplate(Resource):

    @permission.check(p_list['p_message_gateway_template_all'])
    @marsh_response(GetMessageGatewayTemplateResponse)
    def get(self, template_id):
        """
        function: 获取某个消息网关模版详情
        """
        template_data = MessageGatewayTempalteDao.queryMessageTemplateById(template_id)
        return template_data
    
    @permission.check(p_list['p_message_gateway_template_all'])
    @marsh_response(PutMessageGatewayTemplateResponse)
    def put(self, template_id):
        """
        function: 修改某个消息网关模版
        """
        parser_args = prepare_args_for_parser(message_gateway_parser.copy())
        params = parser_args.parse_args()
        params["last_modified_by_id"] = session['user_id']
        params["last_modified_date"] = getCurrentTime()
        template_number = params.get("template_number")
        if template_number:
            if not validate_input(template_number):
                raise AppException(message="模版编号要求长度不大于10位,并且仅包含数字和英文字母")
        MessageGatewayTempalteDao.updateMessageTemplateById(template_id, params)
        template_data = MessageGatewayTempalteDao.queryMessageTemplateById(template_id)

        language = template_data.get("language")
        if language == "zh_cn":
            redis_key = f"message:template:{template_number}"
        elif language == "en_us":
            redis_key = f"message:template:{template_number}:en:us"
        else:
            raise AppException(message="请检查语种(language)参数是否正常")
        redis_data = {"subject":template_data.get("subject"), "content": template_data.get("content"), 
                      "enable": template_data.get("enable")}
        redis_client.set(name=redis_key, value=json.dumps(redis_data))

        return AppResponse()
    

@message_gateway_api.resource('/template/list')
class ListMessageGatewayTemplate(Resource):
    @permission.check(p_list['p_message_gateway_template_all'])
    @marsh_response(ListMessageGatewayTemplateResponse)
    def get(self):
        """
        function: 条件查询消息网关模版列表数据
        """
        parser_args = prepare_args_for_parser(list_message_gateway_parser.copy())
        params = parser_args.parse_args()
        data = MessageGatewayTempalteDao.queryMessageTemplateList(params)
        return data