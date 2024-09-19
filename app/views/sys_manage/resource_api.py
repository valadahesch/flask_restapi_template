import json
import time

from datetime import datetime
from flask import Blueprint, session, jsonify, Response, current_app
from flask_restful import Resource
from werkzeug.datastructures import FileStorage
from flask_restful.reqparse import RequestParser
from app.extensions import permission
from app.enums.permission_enum import p_list
from app.controllers.dao import SysUserDao
from app.controllers.elasticsearch_service import ESService
from app.utils.api_util import Api, AppResponse, AppException
from app.utils.func_util import prepare_args_for_parser
from app.extensions import oss_util

resource_app = Blueprint('resource', __name__, url_prefix='/api/sys/resource')
resource_api = Api(resource_app)


post_resource_parser = RequestParser()
post_resource_parser.add_argument('meta', location='form', type=str)
post_resource_parser.add_argument('description', location='form', type=str, required=True)
post_resource_parser.add_argument('file', location='files', type=FileStorage, required=True)


get_resource_parser = RequestParser()
get_resource_parser.add_argument('name', location='args', type=str)
get_resource_parser.add_argument('description', location='args', type=str)
get_resource_parser.add_argument('page', location='args', type=int, required=True)
get_resource_parser.add_argument('size', location='args', type=int, required=True)


@resource_api.resource('')
class ResourceAPI(Resource):

    @permission.check(p_list['p_sys_resource_all'])
    def post(self):
        """
        上传资源，文件+TAG, meta(scence, X_node_type....)
        :return:
        """
        parser_args = prepare_args_for_parser(post_resource_parser.copy())
        params = parser_args.parse_args()

        data = {"id": ""}

        file_storage = params.pop("file")
        file_size = len(file_storage.read())
        file_storage.stream.seek(0)
        file_meta = {
            "ContentType": file_storage.content_type,
            "ContentDisposition": f"attachment; filename={file_storage.filename}"
        }

        _id = oss_util.uploadFileStream(file_storage, "tech-resource", file_meta)
        data["id"] = _id

        doc = {
            "id": _id, "meta": params.get("meta"),
            "description": params.get("description"), "file_mime": file_storage.content_type,
            "file_name": file_storage.filename, "file_size": file_size, "created_by_id": session["user_id"],
            "created_date": datetime.now(), "last_modified_by_id": session["user_id"],
            "last_modified_date": datetime.now()
        }

        sys_user = SysUserDao.querySysUserById(session["user_id"])
        if sys_user:
            doc["created_by_name"] = sys_user.display_name
        ESService.upsertSysResourceById(_id, doc)

        for i in range(3):
            time.sleep(0.3)
            data = ESService.querySysResourceById(_id)
            if data:
                break

        return jsonify(AppResponse(data))

    @permission.check(p_list['p_sys_resource_all'])
    def get(self):
        """
        资源列表
        :return:
        """
        parser_args = prepare_args_for_parser(get_resource_parser.copy())
        params = parser_args.parse_args()

        meta, description = params.get("name"), params.get("description")
        page, size = params.get("page"), params.get("size")
        data = {"list": [], "total": 0, "page": page, "size": size}

        site_domain = current_app.config["API_DOMAIN"]
        total, res = ESService.querySysResource(meta, description, page, size)
        for r in res:
            r["url"] = f'https://{site_domain}/api/sys/resource/raw/{r["id"]}'
            r["created_date"] = datetime.strptime(
                r["created_date"], '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S')

            if 'created_by_name' in r.keys():
                sys_user = SysUserDao.querySysUserByDisplayName(r["created_by_name"])
                if sys_user:
                    r['sys_user_id'] = sys_user.id
            elif 'created_by_id' in r.keys():
                sys_user = SysUserDao.querySysUserById(r["created_by_id"])
                if sys_user:
                    r["created_by_name"] = sys_user.display_name
                    r['sys_user_id'] = sys_user.id
            data["list"].append(r)

        data["total"] = total
        return jsonify(AppResponse(data))


put_resource_parser = RequestParser()
put_resource_parser.add_argument('meta', location='json', type=str)
put_resource_parser.add_argument('description', location='json', type=str)


@resource_api.resource('', '/<resource_id>')
class ResourceIdAPI(Resource):

    @permission.check(p_list['p_sys_resource_all'])
    def put(self, resource_id):
        """
        修改资源
        :return:
        """
        parser_args = prepare_args_for_parser(put_resource_parser.copy())
        params = parser_args.parse_args()

        now_datetime = datetime.now()
        doc = {
            "id": resource_id, "last_modified_by_id": session["user_id"],
            "last_modified_date": now_datetime
        }
        if params.get("meta"):
            doc["meta"] = params.get("meta")
        if params.get("description"):
            doc["description"] = params.get("description")
        ESService.updateSysResourceById(resource_id, doc)

        for i in range(3):
            time.sleep(0.3)
            data = ESService.querySysResourceById(resource_id)
            if data:
                if data["last_modified_date"] == now_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f'):
                    break

        return jsonify(AppResponse())

    def get(self, resource_id):
        """
        单个资源
        :return:
        """
        data = ESService.querySysResourceById(resource_id)
        if data:
            site_domain = current_app.config["API_DOMAIN"]
            data["url"] = f'https://{site_domain}/api/sys/resource/raw/{data["id"]}'
            data["created_date"] = datetime.strptime(
                data["created_date"], '%Y-%m-%dT%H:%M:%S.%f').strftime('%Y-%m-%d %H:%M:%S')
            if 'created_by_name' not in data.keys():
                sys_user = SysUserDao.querySysUserById(data["created_by_id"])
                if sys_user:
                    data["created_by_name"] = sys_user.display_name
            return jsonify(AppResponse(data))
        return jsonify(AppResponse())


@resource_api.resource('', '/download/<resource_id>')
class ResourceDownloadAPI(Resource):

    def get(self, resource_id):
        """
        资源下载
        :return:
        """
        file_stream, resp_header = oss_util.getObject('tech-resource', resource_id)
        if not resp_header:
            raise AppException("获取资源失败，资源不存在")
        resp_header["Content-Type"] = "application/octet-stream"
        return Response(file_stream, headers=resp_header)


@resource_api.resource('', '/raw/<resource_id>')
class ResourceRawAPI(Resource):

    def get(self, resource_id):
        """
        获取资源Raw
        :return:
        """
        file_stream, resp_header = oss_util.getObject('tech-resource', resource_id)
        if not resp_header:
            raise AppException("获取资源失败，资源不存在")
        del resp_header["Content-Disposition"]
        return Response(file_stream, headers=resp_header)