import os
import json
import urllib.parse
from flask import session, Blueprint
from flask_restful import Resource
from werkzeug.datastructures import FileStorage
from app.controllers.response import marsh_response
from app.controllers.response.file_system_respone import QueryDirectoryDetailResponse
from app.extensions import permission
from app.enums.permission_enum import p_list
from app.utils.api_util import Api, AppException, AppResponse
from flask_restful.reqparse import RequestParser
from app.utils.func_util import prepare_args_for_parser
from app.controllers.dao import SysFileManageDao
from app.controllers.schema import FileManageSchema
from app.extensions import oss_aliyun_util


file_system_app = Blueprint('file_system', __name__, url_prefix='/api/filesystem')
file_system_api = Api(file_system_app)


root_directory_put_parser = RequestParser()
root_directory_put_parser.add_argument('related_object_id', location='json', type=str, required=True)

root_directory_get_parser = RequestParser()
root_directory_get_parser.add_argument('related_object_id', location='args', type=str, required=True)


@file_system_api.resource('/<string:related_object_type>')
class RootDirectory(Resource):
    @permission.check(p_list['p_file_system_all'])
    def post(self, related_object_type):
        """
        function: 创建文件根目录
        """
        parser_args = prepare_args_for_parser(root_directory_put_parser.copy())
        params = parser_args.parse_args()
        related_object_id = params['related_object_id']
        res = SysFileManageDao.queryRootDirectoryByRelatedObjectId(related_object_id)
        if res:
            raise AppException(message="已存在相同关系对象ID的根目录")
        schema = FileManageSchema()
        params['related_object_type'] = related_object_type
        params['obj_type'] = 'root_dir'
        params['created_by_id'] = session['user_id']
        file_data = schema.load(params)
        root_directory_id = SysFileManageDao.addDirectory(file_data)
        return AppResponse(data={'id': root_directory_id})

    @permission.check(p_list['p_file_system_all'])
    def get(self, related_object_type):
        """
        function: 获取项目文件根目录
        """
        parser_args = prepare_args_for_parser(root_directory_get_parser.copy())
        params = parser_args.parse_args()
        related_object_id = params.get('related_object_id')
        sys_file = SysFileManageDao.queryDirectoryByRelatedObject(related_object_type, related_object_id)
        if not sys_file:
            return AppResponse(data={}, code=0, message="未查询到对应根目录数据")
        return AppResponse(data={'id': sys_file.id})


@file_system_api.resource('/folder/<string:folder_id>')
class QueryDirectoryDetail(Resource):

    @permission.check(p_list['p_file_system_all'])
    @marsh_response(QueryDirectoryDetailResponse)
    def get(self, folder_id):
        """
        function: 获取目录下所有文件和目录
        """
        sys_files = SysFileManageDao.querySubByFolderId(folder_id)
        result = {'list': []}
        if sys_files:
            for sys_file, sys_user in sys_files:
                data = {
                    'id': sys_file.id,
                    'parent_id': sys_file.parent_id,
                    'obj_type': sys_file.obj_type,
                    'obj_name': sys_file.obj_name,
                    'file_type': sys_file.file_type,
                    'file_size': sys_file.file_size,
                    'created_by_id': sys_file.created_by_id,
                    'created_date': str(sys_file.created_date),
                    'created_by_name': sys_user.display_name
                }
                if not sys_file.deleted_by_id:
                    result['list'].append(data)
        return result


create_directory_parser = RequestParser()
create_directory_parser.add_argument('name', location='json', type=str, required=True)


@file_system_api.resource('/folder/<string:folder_id>/create')
class CreateDirectory(Resource):

    @permission.check(p_list['p_file_system_all'])
    def post(self, folder_id):
        """
        function: 目录创建
        """
        parser_args = prepare_args_for_parser(create_directory_parser.copy())
        params = parser_args.parse_args()
        folder = SysFileManageDao.queryFolderByFileName(folder_id, params["name"])
        if folder:
            raise AppException(message="创建失败，目录名已存在")

        params['parent_id'] = folder_id
        params['obj_type'] = 'dir'
        params['created_by_id'] = session['user_id']
        params['obj_name'] = params['name']
        del params['name']
        schema = FileManageSchema()
        file_data = schema.load(params)
        id = SysFileManageDao.addDirectory(file_data)
        return AppResponse(data={'id': id})
    

check_directory_parser = RequestParser()
check_directory_parser.add_argument('file_name', location='json', type=str, required=True)
check_directory_parser.add_argument('folder_id', location='json', type=str, required=True)


@file_system_api.resource('/file/check')
class CheckDirectory(Resource):

    @permission.check(p_list['p_file_system_all'])
    def post(self):
        """
        function: 判断文件名是否存在（上传文件前判断是否有重命，重命会覆盖）
        """
        parser_args = prepare_args_for_parser(check_directory_parser.copy())
        params = parser_args.parse_args()
        file_name = params.get('file_name')
        folder_id = params.get('folder_id')
        file = SysFileManageDao.queryFolderByFileName(folder_id, file_name)
        exist = True if file else False
        return AppResponse(data={'has': exist})


upload_file_parser = RequestParser()
upload_file_parser.add_argument('meta', location='form', type=str, required=True)
upload_file_parser.add_argument('file', location='files', type=FileStorage, required=True)
upload_file_parser.add_argument('folder_id', location='form', type=str, required=True)


@file_system_api.resource('/file/upload')
class UploadFile(Resource):

    @permission.check(p_list['p_file_system_all'])
    def post(self):
        """
        function: 上传文件
        """
        parser_args = prepare_args_for_parser(upload_file_parser.copy())
        params = parser_args.parse_args()
        parent_id = params.get("folder_id")
        file = SysFileManageDao.queryFolderById(parent_id)
        if not file:
            raise AppException(message="父级目标路径不存在")
        file_storage = params.pop("file")
        file_size = file_storage.stream.seek(0, os.SEEK_END)
        file_storage.stream.seek(0)
        try:
            meta = params.get("meta").replace('_', '-')
            metadata = {key: urllib.parse.quote(value) for key, value in json.loads(meta).items()}
        except:
            raise AppException(message="元数据解析异常")
        file_meta = {
            "ContentType": file_storage.content_type,
            "ContentDisposition": f"attachment; filename={file_storage.filename}",
            "Metadata": metadata
        }
        data = {
            "parent_id": parent_id,
            "obj_type": "file",
            "obj_name": file_storage.filename,
            "file_type": file_storage.mimetype,
            "file_size": file_size,
            "created_by_id": session['user_id'],
        }
        schema = FileManageSchema()
        file_data = schema.load(data)
        res = SysFileManageDao.queryFolderByFileName(parent_id, file_storage.filename)
        if res:
            SysFileManageDao.deleteFolderByid(file_id=res.id, delete_by_id=session['user_id'])
        file_id = SysFileManageDao.addDirectory(file_data)
        oss_aliyun_util.uploadFileStream(file_storage, "tech-filesystem", file_meta, object_name=file_id)
        
        return AppResponse(data={"id": file_id})
    

@file_system_api.resource('/file/download/<string:file_id>')
class DownloadFile(Resource):

    @permission.check(p_list['p_file_system_all'])
    def get(self, file_id):
        """
        function: 下载文件
        """
        file = SysFileManageDao.queryFolderById(file_id)
        if not file:
            raise AppException(message="目标文件/目录不存在")
        if file.obj_type != "file":
            raise AppException(message="非文件类型数据无法进行下载")
        file_url = oss_aliyun_util.generatePreSignedUrl(filename=file_id, bucket="tech-filesystem")
        return AppResponse(data={"file_url": file_url, "filename": file.obj_name})
    

@file_system_api.resource('/delete/<string:file_id>')
class DeleteFileOrDirectory(Resource):

    @permission.check(p_list['p_file_system_all'])
    def delete(self, file_id):
        """
        function: 删除文件或目录
        """
        file = SysFileManageDao.queryFolderById(file_id)
        if not file:
            raise AppException(message="文件不存在")
        if file.created_by_id != session['user_id']:
            raise AppException(message="您不是文件拥有者无法进行删除操作")
        if file.deleted_by_id:
            raise AppException(message="文件已经被删除")
        SysFileManageDao.deleteFolderByid(file_id, session['user_id'])
        return AppResponse(data={})
    

rename_parser = RequestParser()
rename_parser.add_argument('name', location='json', type=str, required=True)


@file_system_api.resource('/rename/<string:file_id>')
class RenameFileOrDirectory(Resource):

    @permission.check(p_list['p_file_system_all'])
    def put(self, file_id):
        """
        function: 重命名文件或目录
        """
        parser_args = prepare_args_for_parser(rename_parser.copy())
        params = parser_args.parse_args()
        file = SysFileManageDao.queryFolderById(file_id)
        new_file_name = params.get('name')
        if not file:
            raise AppException(message="文件不存在")
        if file.created_by_id != session['user_id']:
            raise AppException(message="您不是文件拥有者无法进行重命名操作")
        if file.parent_id:
            res = SysFileManageDao.queryFolderByFileName(file.parent_id, new_file_name)
            if res:
                raise AppException(message=f"此目录下已经存在名为:{new_file_name}的文件或目录")
        update_data = {"obj_name": new_file_name} 
        SysFileManageDao.updataFolderByid(file_id, update_data)
        if file.obj_type == "file":
            content_disposition = f"attachment; filename={new_file_name}"
            oss_aliyun_util.updateContentDisposition("tech-filesystem", file_id, content_disposition)
        return AppResponse(data={})


move_file_parser = RequestParser()
move_file_parser.add_argument('ids', location='json', type=list, required=True)
move_file_parser.add_argument('folder_id', location='json', type=str, required=True)


@file_system_api.resource('/move')
class MoveFileOrDirectory(Resource):

    @permission.check(p_list['p_file_system_all'])
    def put(self):
        """
        function: 批量移动文件或目录
        """
        parser_args = prepare_args_for_parser(move_file_parser.copy())
        params = parser_args.parse_args()
        folder_id = params.get('folder_id')
        ids = params.get('ids')
        update_data = {"parent_id": folder_id} 
        parent_file = SysFileManageDao.queryFolderById(folder_id)
        if not parent_file:
            raise AppException(message="目标父级文件不存在")
        if parent_file.obj_type == "file":
            raise AppException(message="目标父级无法是文件类型, 必须为目录类型")
        if parent_file.deleted_by_id:
            raise AppException(message="目标父级文件已经被删除")
        for id in ids:
            if id == folder_id:
                raise AppException(message="文件/目录的父级目录无法是其本身")
            children_ids = SysFileManageDao.getAllChildren(parent_id=id)
            if folder_id in children_ids:
                raise AppException(message="无法将文件/目录移动到其子级目录下")
        for id in ids:
            SysFileManageDao.updataFolderByid(id, update_data)
        return AppResponse(data={})
    

@file_system_api.resource('/folder/<string:folder_id>/parent_dirs')
class QueryParentDirectory(Resource):

    @permission.check(p_list['p_file_system_all'])
    @marsh_response(QueryDirectoryDetailResponse)
    def get(self, folder_id):
        """
        function: 获取当前目录所有上级目录
        """
        data = {'list': []}
        schema = FileManageSchema()
        res = SysFileManageDao.queryFolderByIdOutJoinSysUser(folder_id)
        if not res:
            raise AppException(message="文件不存在")
        file, user = res
        if file.deleted_by_id:
            raise AppException(message="文件已被删除")
        
        file_data = schema.dump(file)
        file_data["created_by_name"] = user.display_name 
        data['list'].append(file_data)

        parent_id = file.parent_id
        while parent_id:
            res = SysFileManageDao.queryFolderByIdOutJoinSysUser(parent_id)
            if res:
                file, user = res 
                if not file.deleted_by_id:
                    file_data = schema.dump(file)
                    parent_id = file.parent_id
                    file_data["created_by_name"] = user.display_name 
                    data['list'].append(file_data)
                else:
                    parent_id = None
            else:
                parent_id = None
        return data