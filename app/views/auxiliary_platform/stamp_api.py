import base64
import datetime
import uuid
from app.config import *
from zeep import Client
from flask import Blueprint, jsonify, session, Response
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.controllers.dao.techadmin_dao import SysUserDao
from app.controllers.response.stamp_response import StampRecordListResponse
from app.enums.permission_enum import p_list
from app.extensions import permission, redis_client
from app.utils.func_util import prepare_args_for_parser
from app.utils.api_util import Api, AppResponse, AppException
from werkzeug.datastructures import FileStorage
from app.controllers.dao.auxiliary_stamp_dao import AuxiliaryStampDao
from app.utils.oss.oss_util import OSSUtil
from app.controllers.response import marsh_response


stamp_app = Blueprint('stamp', __name__, url_prefix='/api/auxiliary')
stamp_api = Api(stamp_app)
oss_util = OSSUtil(InspurConfig['tac-ccc']['access_key'], InspurConfig['tac-ccc']['access_secret'])

post_stamp_parser = RequestParser()
post_stamp_parser.add_argument('related_object', location='form', type=str, required=True)
post_stamp_parser.add_argument('file', location='files', type=FileStorage, required=True)
post_stamp_parser.add_argument('reason', location='form', type=str)
post_stamp_parser.add_argument('request_by_id', location='form', type=str)


@stamp_api.resource('/stamp')
class UploadStampMaterial(Resource):

    @permission.check(p_list['p_auxiliary_stamp'])
    def post(self):
        """
        function: 上传盖章材料 
        
        """
        parser_args = prepare_args_for_parser(post_stamp_parser.copy())
        params = parser_args.parse_args()
        request_by_id = params.get("request_by_id", "")
        reason = params.get("reason", "")
        related_object = params.get("related_object", "")
        file_storage = params.pop("file")
        file_content = file_storage.read()
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        user_info = SysUserDao.getSysUserEmployeeById(session['user_id'])
        if user_info:
            sys_user, employee_info = user_info[0], user_info[1]
        else:
            raise AppException(message="非企业员工无法执行该操作")
        workr_num = employee_info.employee_number
        email_prefix = employee_info.userid

        file_id = str(uuid.uuid4())
        object_name = str(datetime.datetime.now().year)+"/stamp/"+file_id
        while oss_util.isExist(object_name, "tech-uploads"):
            file_id = str(uuid.uuid4())
            object_name = str(datetime.datetime.now().year)+"/stamp/"+ file_id
        try:
            wsdl = 'http://10.88.7.56/services/TACService?wsdl'
            client = Client(wsdl)
            params = {
                'in0': workr_num,
                'in1': email_prefix, 
                'in2': '24',    
                'in3': file_id,
                'in4': file_base64
            }
            response = client.service.TacElectronSign(**params)
        except Exception as error:
            raise AppException(message=f"OA盖章接口出现异常{error}")
        if "成功" not in response:
            AuxiliaryStampDao.addStampRecord(file_name, request_by_id, reason, file_id, session['user_id'], 3)
            raise AppException(message=f"请求签名操作失败, {str(response)}")
        file_name = file_storage.filename
        redis_data = {"file_name": file_name, "email": employee_info.email, "related_object": related_object,
                      "user_name": employee_info.name}
        redis_client.set(name=f"techadmin:auxiliary:stamp:{file_id}", value=json.dumps(redis_data), ex=600)
        AuxiliaryStampDao.addStampRecord(file_name, request_by_id, reason, file_id, session['user_id'], 1, object_name)
        return jsonify(AppResponse({"file_id": file_id}))


@stamp_api.resource('/stamp/<string:file_id>')
class DownloadStampMaterial(Resource):

    @permission.check(p_list['p_auxiliary_stamp'])
    def get(self, file_id):
        """
        function: 返回盖章后的材料文本流
        """
        redis_key = redis_client.exists(f"techadmin:auxiliary:stamp:{file_id}")
        stamp_record = AuxiliaryStampDao.getStampRecordByFileId(file_id)
        if redis_key:
            if stamp_record:
                download_url = oss_util.generatePreSignedUrl(filename=stamp_record.object_name, bucket='tech-uploads')
                if download_url:
                    AuxiliaryStampDao.updateStatusByFileId(file_id, {"status": 2})
                    return jsonify(AppResponse(code=0, data={"file_url": download_url}, message="生成盖章文件成功"))
                else:
                    return jsonify(AppResponse(code=0, data={"file_url": ""}, message="生成盖章文件中..."))
            else:
                raise AppException(message="未找到相关盖章记录")
        else:
            if stamp_record.status == 2:
                download_url = oss_util.generatePreSignedUrl(filename=stamp_record.object_name, bucket='tech-uploads')
                if download_url:
                    return jsonify(AppResponse(code=0, data={"file_url": download_url}, message="生成盖章文件成功"))
                else:
                    raise AppException(message="盖章文件文件状态为2,但存储桶为获取到对应文件")
            else:
                AuxiliaryStampDao.updateStatusByFileId(file_id, {"status": 3})
                raise AppException(message="生成盖章文件失败")


list_stamp_parser = RequestParser()
list_stamp_parser.add_argument('file_name', location='args', type=str)
list_stamp_parser.add_argument('created_date[]', location='args', type=str, action='append', dest='created_date')
list_stamp_parser.add_argument('stamp_date[]', location='args', type=str, action='append', dest='stamp_date')
list_stamp_parser.add_argument('reason', location='args', type=str)
list_stamp_parser.add_argument('request_by_id', location='args', type=str)
list_stamp_parser.add_argument('stamp_by_id', location='args', type=str)
list_stamp_parser.add_argument('status[]', location='args', type=str, action='append', dest='status')
list_stamp_parser.add_argument('page', location='args', type=int)
list_stamp_parser.add_argument('size', location='args', type=int)


@stamp_api.resource('/stamp/list')
class GetStampMaterialList(Resource):

    @permission.check(p_list['p_auxiliary_stamp'])
    @marsh_response(StampRecordListResponse)
    def get(self):
        """
        function: 获取盖章材料历史记录
        """
        parser_args = prepare_args_for_parser(list_stamp_parser.copy())
        params = parser_args.parse_args()
        params["user_id"] = session["user_id"]
        page, size, total, query = AuxiliaryStampDao.queryConditionRecord(**params)
        all_data = {"list": [], "page": page, "size": size, "total": total}
        for request_user, stamp_user, stamp in query.all():
            if stamp.status == 1:
                redis_key = redis_client.exists(f"techadmin:auxiliary:stamp:{stamp.file_id}")
                if not redis_key:
                    AuxiliaryStampDao.updateStatusByFileId(stamp.file_id, {"status": 3})
            data = {
                "file_id": stamp.file_id,
                "reason": stamp.reason,
                "request_by_id": stamp.request_by_id,
                "request_by_name": request_user.display_name if request_user else "",
                "stamp_by_id": stamp.stamp_by_id,
                "stamp_by_name": stamp_user.display_name if stamp_user else "",
                "created_date": str(stamp.created_date),
                "stamp_date": str(stamp.stamp_date) if stamp.stamp_date else "",
                "file_name": stamp.file_name,
                "status": stamp.status
            }
            all_data["list"].append(data)
        return  all_data