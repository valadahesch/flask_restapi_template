import io

from flask_restful.reqparse import RequestParser
from flask import Blueprint, jsonify
from flask_restful import Resource
from app.utils.api_util import Api, AppResponse, AppException
from werkzeug.datastructures import FileStorage
from app.utils.func_util import prepare_args_for_parser
from Configure_Conversion_SDK.Configure_Conversion import Mywin


conversion_app = Blueprint('conversion', __name__, url_prefix='/api/tools/conversion')
conversion_api = Api(conversion_app)


conversion_parser = RequestParser()
conversion_parser.add_argument('is_checked', location='form', type=str, default='')
conversion_parser.add_argument('vender', location='form', type=str, required=True)
conversion_parser.add_argument('file', location='files', type=FileStorage)


@conversion_api.resource('')
class ToolsConversionAPI(Resource):

    def post(self):
        """
        配置转化
        :return:
        """
        parser_args = prepare_args_for_parser(conversion_parser.copy())
        params = parser_args.parse_args()

        file_storage = params.pop("file")
        file_byte = file_storage.read()

        my_win = Mywin(file_byte, params.get("vender"), params.get("is_checked"))
        try:
            res = my_win.sum_outconfig()
        except Exception as e:
            raise AppException(str(e))

        return jsonify(AppResponse(data=res))
