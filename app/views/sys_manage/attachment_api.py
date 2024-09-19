from werkzeug.datastructures import FileStorage
from flask import Blueprint, jsonify, session
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.extensions import oss_util
from app.utils.func_util import prepare_args_for_parser, validate_null
from app.controllers.schema import SysAttachmentSchema
from app.controllers.response import marsh_response, SysAttachmentList, SysAttachmentDownload
from app.controllers.dao import SysAttachmentDao
from app.utils.api_util import Api, AppResponse, AppException

attachment_app = Blueprint('attachment', __name__, url_prefix='/api/attachment')
attachment_api = Api(attachment_app)


post_attachment_parser = RequestParser()
post_attachment_parser.add_argument('related_object', location='form', type=validate_null, required=True)
post_attachment_parser.add_argument('related_object_id', location='form', type=validate_null)
post_attachment_parser.add_argument('file', location='files', type=FileStorage, required=True)


get_attachment_parser = RequestParser()
get_attachment_parser.add_argument('related_object', location='args', type=validate_null, required=True)
get_attachment_parser.add_argument('related_object_id', location='args', type=validate_null, required=True)


@attachment_api.resource('')
class AttachmentAPI(Resource):

    def post(self):
        """
        上传附件
        :return:
        """
        parser_args = prepare_args_for_parser(post_attachment_parser.copy())
        params = parser_args.parse_args()

        data = {"id": ""}

        file_storage = params.pop("file")
        file_size = len(file_storage.read())
        file_storage.stream.seek(0)
        file_meta = {
            "ContentType": file_storage.content_type,
            "ContentDisposition": f"attachment; filename={file_storage.filename}"
        }
        _id = oss_util.uploadFileStream(file_storage, "tech-attachment", file_meta)

        params["id"] = _id
        params["file_name"] = file_storage.filename
        params["file_size"] = file_size
        params["created_by_id"] = session["user_id"]
        params["file_type"] = file_storage.content_type
        schema = SysAttachmentSchema()
        attachment = schema.load(params)
        data["id"] = SysAttachmentDao.addAttachment(attachment)

        return jsonify(AppResponse(data))

    @marsh_response(SysAttachmentList)
    def get(self):
        """
        上传附件
        :return:
        """
        parser_args = prepare_args_for_parser(get_attachment_parser.copy())
        params = parser_args.parse_args()

        data = {"list": []}
        attachment_create_list = SysAttachmentDao.queryAttachmentJoinUserByObjectId(
            params["related_object"], params["related_object_id"]
        )

        for attachment_create in attachment_create_list:
            attachment, create_user = attachment_create
            schema = SysAttachmentSchema()
            attachment = schema.dump(attachment)

            attachment["created_by_name"] = create_user.display_name
            data["list"].append(attachment)

        return data


@attachment_api.resource('/<attachment_id>/download')
class AttachmentDownloadAPI(Resource):

    @marsh_response(SysAttachmentDownload)
    def get(self, attachment_id):
        url = oss_util.generatePreSignedUrl(attachment_id, "tech-attachment")
        if not url:
            raise AppException("获取失败，附件不存在")

        data = {"file_url": url}
        return data

