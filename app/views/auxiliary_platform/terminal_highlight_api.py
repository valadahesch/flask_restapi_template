from datetime import datetime
import json
from flask import Blueprint, jsonify, session
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.enums.permission_enum import p_list
from app.extensions import permission, redis_client
from app.utils.func_util import prepare_args_for_parser
from app.utils.api_util import Api, AppResponse, AppException



terminal_highlight_app = Blueprint('highlight', __name__, url_prefix='/api/auxiliary/terminal_highlight')
terminal_highlight_api = Api(terminal_highlight_app)


parser = RequestParser()
parser.add_argument('init_reg', location='json', type=str)
parser.add_argument('terminal_str', location='json', type=str)


@terminal_highlight_api.resource('')
class TerminalHighlight(Resource):

    @permission.check(p_list['p_auxiliary_terminal_highlight'])
    def get(self):
        """
        function: 获取高亮正则和终端命令数据
        """
        redis_key = "techadmin:terminal:highlight"
        if not redis_client.exists(redis_key):
            raise AppException(message="未找到高亮正则和终端命令初始化数据")
        data = json.loads(redis_client.get(name=redis_key))
        terminal_str, init_reg = data.get("terminal_str", ""), data.get("init_reg", "")
        return jsonify(AppResponse(code=0, data={"init_reg": init_reg, "terminal_str": terminal_str}, message="success"))


    @permission.check(p_list['p_auxiliary_terminal_highlight'])
    def put(self):
        """
        function: 修改高亮正则和终端命令数据
        """
        parser_args = prepare_args_for_parser(parser.copy())
        params = parser_args.parse_args()
        redis_key = "techadmin:terminal:highlight"
        if not redis_client.exists(redis_key):
            raise AppException(message="未找到高亮正则和终端命令初始化数据")
        data = json.loads(redis_client.get(name=redis_key))
        data['last_modified_by_id'] = session['user_id']
        data['last_modified_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if params.get("init_reg"):
            data["init_reg"] = params.get("init_reg")
        if params.get("terminal_str"):
            data["terminal_str"] = params.get("terminal_str")
        redis_client.set(name=redis_key, value=json.dumps(data))
        return jsonify(AppResponse(code=0, data={}, message="success"))