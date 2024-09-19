from datetime import datetime, timedelta
from flask import Blueprint
from flask_restful import Resource
from app.enums.permission_enum import p_list
from app.utils.api_util import AppException
from app.extensions import aliyun_util, oss_util, permission
from app.utils.func_util import prepare_args_for_parser
from flask_restful.reqparse import RequestParser
from app.controllers.response import marsh_response, CallDetailRecordList, CallMono
from app.utils.api_util import Api

call_app = Blueprint('call', __name__, url_prefix='/api/support/aliyun_ccc/call_record')
call_api = Api(call_app)

record_parser = RequestParser()
record_parser.add_argument('agent_id', location='args', type=str)
record_parser.add_argument('agent_names', location='args', type=str)
record_parser.add_argument('calling_number', location='args', type=str)
record_parser.add_argument('called_number', location='args', type=str)
record_parser.add_argument('page', location='args', type=int, default=1)
record_parser.add_argument('size', location='args', type=int, default=1000)


@call_api.resource('')
class CallRecord(Resource):

    @permission.check(p_list['p_support_call_record_list'])
    @marsh_response(CallDetailRecordList, p_list['p_support_call_record_list'])
    def get(self):
        """
        获取通话记录接口
        :return:
        """

        parser_args = prepare_args_for_parser(record_parser.copy())
        params = parser_args.parse_args()

        params["agent_id"] = params.get("agent_id") if params.get("agent_id") else params.get('agent_names')
        if not params.get('start_time'):
            params['start_time'] = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
        result = aliyun_util.listCallDetailRecords(**params)
        if not result:
            return {"List": []}

        for record in result["List"]:
            if not record.get('CallDuration') and 'CallDuration' in record.keys():
                record['CallDuration'] = 0

        if params.get("page") != 1:
            params['page'] = 1
            params['size'] = 1
            result_total = aliyun_util.listCallDetailRecords(**params)
            if result_total.get("TotalCount"):
                result["TotalCount"] = result_total.get("TotalCount")

        if result.get('TotalCount') > 10000:
            result["TotalCount"] = 10000

        return result


mono_parser = RequestParser()
mono_parser.add_argument('contact_id', location='args', type=str)


@call_api.resource('/mono_recording')
class MonoRecording(Resource):

    @permission.check(p_list['p_support_call_record_list'])
    @marsh_response(CallMono)
    def get(self):
        parser_args = prepare_args_for_parser(mono_parser.copy())
        params = parser_args.parse_args()

        file_name = f'{params["contact_id"]}.mp3'
        url = oss_util.generatePreSignedUrl(file_name, "aliyun-ccc")
        if not url:
            raise AppException("暂无录音文件")

        data = {"file_url": url, "file_name": params['contact_id'] + ".mp3"}
        return data

