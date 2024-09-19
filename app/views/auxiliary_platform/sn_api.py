from flask import Blueprint, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.enums.permission_enum import p_list
from app.extensions import tac_api, permission
from app.utils.func_util import prepare_args_for_parser, extract_sn
from app.utils.api_util import Api, AppResponse

sn_app = Blueprint('sn', __name__, url_prefix='/api/auxiliary/sn')
sn_api = Api(sn_app)

get_extract_parser = RequestParser()
get_extract_parser.add_argument('text', location='json', type=str, required=True)


@sn_api.resource('/extract')
class ExtractSnAPI(Resource):

    @permission.check(p_list['p_auxiliary_sn_query'])
    def post(self):
        """
        提取SN
        :return:
        """
        data = {"list": []}

        parser_args = prepare_args_for_parser(get_extract_parser.copy())
        params = parser_args.parse_args()

        result = extract_sn(params.get("text"))
        if result:
            data["list"] = result

        return jsonify(AppResponse(data))


get_sn_parser = RequestParser()
get_sn_parser.add_argument('source', location='args', type=str, default="CRM")
get_sn_parser.add_argument('sn[]', location='args', type=str, required=True, action='append', dest='sn')
get_sn_parser.add_argument('page', location='args', type=int, default=1)
get_sn_parser.add_argument('size', location='args', type=int, default=10)


@sn_api.resource('/query')
class getSnAPI(Resource):

    @permission.check(p_list['p_auxiliary_sn_query'])
    def get(self):
        """
        提取SN
        :return:
        """
        data = {}

        parser_args = prepare_args_for_parser(get_sn_parser.copy())
        params = parser_args.parse_args()

        source, sn_list = params.get("source"), params.get("sn")
        page, size = params.get("page"), params.get("size")
        if source == 'CRM':
            for sn in sn_list:
                resp_json = tac_api.getCrmSN(sn, page, size)
                if resp_json:
                    if resp_json.get("code") != 0:
                        continue

                    data[sn] = resp_json.get("data")

        return jsonify(AppResponse(data))
