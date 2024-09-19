import json

from flask import Blueprint, session, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.extensions import permission, redis_client
from app.utils.api_util import Api, AppResponse, AppException
from app.utils.func_util import prepare_args_for_parser

settings_app = Blueprint('settings', __name__, url_prefix='/api/settings')
settings_api = Api(settings_app)


get_properties_parser = RequestParser()
get_properties_parser.add_argument('page_key', location='args', type=str)

put_properties_parser = RequestParser()
put_properties_parser.add_argument('page_key', location='json', type=str)
put_properties_parser.add_argument('data', location='json', type=dict)


@settings_api.resource('', '/fields/properties')
class FieldsPropertiesAPI(Resource):

    def put(self):
        """
        设置字段显隐
        :return:
        """

        parser_args = prepare_args_for_parser(put_properties_parser.copy())
        params = parser_args.parse_args()

        user_id = session["user_id"]
        key = f'techadmin:settings:{user_id}:{params.get("page_key")}'
        redis_client.set(key, json.dumps(params.get("data")))

        return jsonify(AppResponse())

    def get(self):
        """
        获取字段显隐
        :return:
        """
        pass

        parser_args = prepare_args_for_parser(get_properties_parser.copy())
        params = parser_args.parse_args()

        user_id = session["user_id"]
        key = f'techadmin:settings:{user_id}:{params.get("page_key")}'
        data = redis_client.getValueToJson(key)
        if not data:
            data = {}

        return jsonify(AppResponse(data))

