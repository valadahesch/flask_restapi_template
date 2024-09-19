import time

from flask import Blueprint, Response, stream_with_context, session
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.extensions import opensearch_api, aiask_api
from app.utils.func_util import prepare_args_for_parser
from app.utils.api_util import Api, AppException, AppResponse


assistant_app = Blueprint('assistant', __name__, url_prefix='/api/tools/assistant')
assistant_api = Api(assistant_app)


post_assistant_parser = RequestParser()
post_assistant_parser.add_argument('text', location='json', type=str, required=True)
post_assistant_parser.add_argument('session_id', location='json', type=str)


opensearch_request_map = {}
aiask_request_map = {}


@assistant_api.resource('/opensearch')
class OpensearchAPI(Resource):

    def post(self):
        parser_args = prepare_args_for_parser(post_assistant_parser.copy())
        params = parser_args.parse_args()

        query_text = params.get("text")
        session_id = params.get("session_id")

        request_id = f"{session['user_id']}_{int(time.time()*1000)}"

        opensearch_request_map[request_id] = opensearch_api.stream_search(query_text, session_id)
        return AppResponse(data={"id": request_id})


@assistant_api.resource('/aiask')
class AiAskAPI(Resource):

    def post(self):
        parser_args = prepare_args_for_parser(post_assistant_parser.copy())
        params = parser_args.parse_args()

        query_text = params.get("text")
        request_id = f"{session['user_id']}_{int(time.time() * 1000)}"

        aiask_request_map[request_id] = aiask_api.stream_search(query_text)
        return AppResponse(data={"id": request_id})


@assistant_api.resource('/opensearch/request/<request_id>')
class OpensearchRequestAPI(Resource):

    def get(self, request_id):

        if request_id in opensearch_request_map.keys():
            resp_stream = opensearch_request_map.pop(request_id)
        else:
            def unknown_resp():
                yield f'会话不存在: {request_id}'
            resp_stream = unknown_resp

        return Response(resp_stream, content_type='text/event-stream')


@assistant_api.resource('/aiask/request/<request_id>')
class AiAskRequestAPI(Resource):

    def get(self, request_id):

        if request_id in aiask_request_map.keys():
            resp_stream = aiask_request_map.pop(request_id)
        else:
            def unknown_resp():
                yield f'会话不存在: {request_id}'
            resp_stream = unknown_resp

        resp = Response(resp_stream, content_type='text/event-stream')
        resp.headers['Cache-Control'] = 'no-cache'
        return resp
