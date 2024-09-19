from datetime import datetime
import json
from flask import Blueprint, current_app, jsonify, session, Response
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.controllers.dao.techadmin_dao import SysUserDao
from app.controllers.elasticsearch_service import ESService
from app.controllers.response.auxiliary_respone import LicenseRecordResponse
from app.controllers.response.response_schema import marsh_response
from app.enums.permission_enum import p_list
from app.extensions import permission, logger
from app.utils.http_api.crm_api import CrmLicAPI
from app.extensions import oss_util
from app.utils.func_util import prepare_args_for_parser, is_valid_date, getRandomNumber10
from app.utils.api_util import Api, AppResponse, AppException
from app.controllers.dao.auxiliary_license_dao import AuxiliaryApplyLicenseRecordDao


license_app = Blueprint('license', __name__, url_prefix='/api/auxiliary')
license_api = Api(license_app)


post_license_parser = RequestParser()
post_license_parser.add_argument('account_id', location='json', type=str, required=True)
post_license_parser.add_argument('product_name', location='json', type=str, required=True)
post_license_parser.add_argument('sn', location='json', type=str, required=True)
post_license_parser.add_argument('lic_params', location='json', type=list, required=True)
post_license_parser.add_argument('end_time', location='json', type=is_valid_date, required=True)


get_license_parser = RequestParser()
get_license_parser.add_argument('crm_order', location='args', type=str)
get_license_parser.add_argument('account_id', location='args', type=str)
get_license_parser.add_argument('sn', location='args', type=str)
get_license_parser.add_argument('product_name', location='args', type=str)
get_license_parser.add_argument('lic_param', location='args', type=str)
get_license_parser.add_argument('status[]', location='args', type=str, action='append', dest='status')
get_license_parser.add_argument('page', location='args', type=int)
get_license_parser.add_argument('size', location='args', type=int)

@license_api.resource('/license')
class ApplyLicense(Resource):

    @permission.check(p_list['p_auxiliary_license'])
    def post(self):
        """
        function: 申请许可文件
        """
        parser_args = prepare_args_for_parser(post_license_parser.copy())
        params = parser_args.parse_args()
        user_id = session['user_id']
        user_info = SysUserDao.getSysUserEmployeeById(user_id)
        if user_info:
            sys_user, employee_info = user_info[0], user_info[1]
        else:
            raise AppException(message="非企业员工无法执行该操作")
        
        email = employee_info.email
        account_id, product_name = params.get("account_id"), params.get("product_name")
        sn, lic_params, end_time = params.get("sn"), params.get("lic_params"), params.get("end_time")
        sn_list = sn.replace(" ", "").split(';') if ";" in sn else [sn]

        account_data = ESService.queryCrmAccountByAccountId(account_id)
        if account_data:
            account_name = account_data.get("AccountName")
        else:
            raise AppException(message="客户信息获取失败")
        crm_order = 'CASE-{0}'.format(getRandomNumber10())
        records_id = AuxiliaryApplyLicenseRecordDao.queryAllLicenseRecordID()
        while crm_order in records_id:
            crm_order = 'CASE-{0}'.format(getRandomNumber10())
        site_domain = current_app.config["API_DOMAIN"]
        order_type = 1 if site_domain == "linkapi.hillstonenet.com" else 0

        def transform_lic_params(lic_params, order_type):
            result = []
            for lic_param in lic_params:
                if lic_param not in ["platform", "av", "urldb", "appdb", "botnet", "qos", "ips"]:
                    raise AppException(message=f"未知的许可证类型{lic_param}")
                if order_type == 0:
                    lic_param = lic_param + "-trial"
                result.append({lic_param: end_time})
            return result
        
        base_info = {
                "crm_order": crm_order,
                "customer": account_name,
                "agent": "",
                "applicant": email,
                "order_sn": "",
                "order_type": order_type
            }
        lic_data = [{
                "is_auto": 1,
                "is_oversea": 0,
                "sku": "",
                "product_model": product_name,
                "start_time": end_time,
                "end_time": end_time,
                "user_id": "",
                "project": account_name,
                "country": "China",
                "line_no": crm_order,
                "sn": sn_list,
                "lic_params": transform_lic_params(lic_params, order_type)
            }]
        resp = CrmLicAPI().createLicnse(base_info, lic_data)
        if resp.get("status") != 0:
            error_msg = resp.get("errmsg")
            AuxiliaryApplyLicenseRecordDao.addLicenseRecord(crm_order, account_id, sn, product_name, lic_params,
                                                            user_id, email, 'fail', crm_order, end_time, '', error_msg)
            raise AppException(message=error_msg)
        order_id = crm_order + '_' + str(resp.get("data"))
        object_name = str(datetime.now().year) + "/license/" + order_id
        CrmLicAPI().downloadLinse(resp.get("data"), object_name)
        AuxiliaryApplyLicenseRecordDao.addLicenseRecord(crm_order, account_id, sn, product_name, lic_params, user_id,
                                                        email, 'success', order_id , end_time, object_name, '')
        return jsonify(AppResponse({"id": order_id}))

       

@license_api.resource('/license/download/<string:order_id>')
class DownloadLicenseFile(Resource):

    @permission.check(p_list['p_auxiliary_license'])
    def get(self, order_id):
        """
        function: 下载许可文件
        """

        record = AuxiliaryApplyLicenseRecordDao.getLicenseRecordByOrderID(order_id)
        if not record:
            raise AppException(message="未查到相关订单记录")
        download_url = oss_util.generatePreSignedUrl(filename=record.object_name, bucket='tech-uploads')
        if download_url:
            return jsonify(AppResponse(code=0, data={"file_url": download_url}, message="生成许可文件成功"))
        else:
            return jsonify(AppResponse(code=-1, data={}, message="未找到相关文件"))


        

@license_api.resource('/license/list')
class GetCreateLicenseRecord(Resource):

    @permission.check(p_list['p_auxiliary_license'])
    @marsh_response(LicenseRecordResponse)
    def get(self):
        """
        function: 获取个人许可申请记录表
        """
        parser_args = prepare_args_for_parser(get_license_parser.copy())
        params = parser_args.parse_args()
        params['user_id'] = session['user_id']
        page, size, total, query = AuxiliaryApplyLicenseRecordDao.queryLicenseRecord(**params)
        all_data = {"list": [], "page": page, "size": size, "total": total}
        try:
            for request_user, license in query.all():
                account_data = ESService.queryCrmAccountByAccountId(license.account_id)
                data = {
                    "created_by_id": request_user.id,
                    "created_by_name": request_user.display_name,
                    "created_date": str(license.created_date),
                    "lic_params": json.loads(license.lic_params),
                    "product_name": license.product_name,
                    "sn": license.sn,
                    "account_id": license.account_id,
                    "account_name": account_data.get("AccountName") if account_data else "",
                    "order_id": license.order_id,
                    "status": license.status,
                    "end_time": str(license.end_time),
                    "id": license.id,
                    "error_msg": license.error_msg
                }
                all_data["list"].append(data)
        except Exception as error:
            logger.info(f"/api/auxiliary/license/list, 获取记录失败,错误: {error}")
        return all_data