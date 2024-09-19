import json
from flask import Blueprint, jsonify, Response, current_app
from flask_restful import Resource
from werkzeug.datastructures import FileStorage
from flask_restful.reqparse import RequestParser
from app.utils.api_util import Api, AppResponse, AppException
from app.utils.func_util import prepare_args_for_parser
from app.config import *
from app.utils.oss.oss_util import OSSUtilCommon

common_app = Blueprint('common', __name__, url_prefix='/api/common')
common_api = Api(common_app)
oss_util = OSSUtilCommon(InspurConfig['tac-ccc']['access_key'], InspurConfig['tac-ccc']['access_secret'])

post_common_parser = RequestParser()
post_common_parser.add_argument('meta', location='form', type=str)
post_common_parser.add_argument('file', location='files', type=FileStorage, required=True)


@common_api.resource("/attachment/upload")
class ResourceAPI(Resource):

    def post(self):
        """
        上传资源，文件+TAG, meta(scence, X_node_type....)
        """
        parser_args = prepare_args_for_parser(post_common_parser.copy())
        params = parser_args.parse_args()
        data = {"id": ""}
        file_storage = params.pop("file")
        file_storage.stream.seek(0)
        file_meta = {
            "ContentType": file_storage.content_type,
            "ContentDisposition": f"attachment; filename={file_storage.filename}",
            "Metadata": json.loads(params.get("meta"))
        }
        
        _id = oss_util.uploadFileStream(file_storage, "tech-uploads", file_meta)
        site_domain = current_app.config["API_DOMAIN"]
        data["url"] = f'https://{site_domain}/api/common/attachment/download/{_id}'
        data["id"] = _id
        return jsonify(AppResponse(data))


@common_api.resource("/attachment/download/<string:current_year>/<string:filename>")
class ResourceDownloadAPI(Resource):

    def get(self, current_year, filename):
        """
        资源下载
        """
        file_stream, resp_header = oss_util.getObject('tech-uploads', current_year+"/"+filename)
        if not resp_header:
            raise AppException("获取资源失败，资源不存在")
        return Response(file_stream, headers=resp_header)
