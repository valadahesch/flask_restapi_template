import copy
import re
import time

from flask import Blueprint, session, jsonify
from flask_restful import Resource
from app.enums.permission_enum import p_list
from app.extensions import permission, executor, apollo_util, logger, message_gw, crm_api
from app.controllers import ESService
from app.controllers.dao import BusinessLeadDao, SysUserDao, CrmViewsDao
from app.controllers.schema import BusinessLeadSchema
from app.utils.func_util import prepare_args_for_parser
from flask_restful.reqparse import RequestParser
from app.controllers.response import marsh_response, BusinessLeadList, LeadDetail
from app.utils.api_util import Api, AppException, AppResponse
from app.utils.http_api.msg_template import BusinessEmail, BusinessWeWork
from app.enums.business_enum import enums
from app.models import db

leads_app = Blueprint('leads', __name__, url_prefix='/api/business/leads')
leads_api = Api(leads_app)

post_leads_parser = RequestParser()
post_leads_parser.add_argument('company_name', location='json', type=str, required=True)
post_leads_parser.add_argument('description', location='json', type=str, required=True)
post_leads_parser.add_argument('customer_id', location='json', type=str, required=True, dest='crm_customer_id')
post_leads_parser.add_argument('customer_name', location='json', type=str, required=True, dest='crm_customer_name')
post_leads_parser.add_argument('owner_id', location='json', type=str, required=True, dest='crm_owner_id')
post_leads_parser.add_argument('owner_name', location='json', type=str, required=True, dest='crm_owner_name')
post_leads_parser.add_argument('contact_name', location='json', type=str, required=True)
post_leads_parser.add_argument('contact_role', location='json', type=int, required=True)
post_leads_parser.add_argument('contact_way', location='json', type=str, required=True)
post_leads_parser.add_argument('province', location='json', type=str)
post_leads_parser.add_argument('city', location='json', type=str)

get_leads_parser = RequestParser()
get_leads_parser.add_argument('company_name', location='args', type=str)
get_leads_parser.add_argument('lead_code', location='args', type=str)
get_leads_parser.add_argument('customer_name', location='args', type=str, dest='crm_customer_name')
get_leads_parser.add_argument('owner_id', location='args', type=str, dest='crm_owner_id')
get_leads_parser.add_argument('page', location='args', type=int, default=1)
get_leads_parser.add_argument('size', location='args', type=int, default=1000)


@leads_api.resource('')
class BusinessLeadsAPI(Resource):

    @permission.check(p_list['p_business_leads_list'])
    @marsh_response(BusinessLeadList)
    def get(self):
        """
        商机线索查询列表
        :return:
        """
        parser_args = prepare_args_for_parser(get_leads_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")), "size": int(params.get("size")),
        }

        create_by = session['user_id']
        data["total"], lead_list = BusinessLeadDao.queryBusinessLeadByFilter(create_by, **params)

        schema = BusinessLeadSchema()
        data["list"] = schema.dump(lead_list, many=True)

        return data

    @permission.check(p_list['p_business_leads_mutation'])
    def post(self):
        """
        创建商机线索
        :return:
        """
        parser_args = prepare_args_for_parser(post_leads_parser.copy())
        params = parser_args.parse_args()

        crm_post_data = copy.deepcopy(params)
        create_user = SysUserDao.querySysUserById(session['user_id'])
        if not create_user:
            raise AppException("创建失败，创建人信息获取失败")

        owner = ESService.queryCrmSystemUserByUserId(crm_post_data['crm_owner_id'])
        if not owner:
            raise AppException("创建失败，归属销售查询失败")

        crm_account = ESService.queryCrmAccountByAccountId(crm_post_data['crm_customer_id'])
        if not crm_account:
            raise AppException("创建失败，CRM客户信息查询失败查询失败")

        crm_post_data['crm_customer_id'] = crm_account['CrmAccountId']
        crm_post_data['crm_owner_id'] = owner['systemuserid']
        crm_post_data["create_user"] = create_user.display_name
        contact_role_map = enums['business']['contact_role']
        crm_post_data['contact_role'] = contact_role_map.get(params['contact_role'])
        resp = crm_api.createLead(**crm_post_data)
        if not resp:
            raise AppException("创建失败，创建CRM线索失败")

        if not resp.get('Data'):
            raise AppException("创建失败，创建CRM线索失败")

        search = re.search('id=(.*)', resp.get('Data'))
        if not search:
            logger.error("createLead response data: {}".format(resp.get('Data')))
            raise AppException("创建失败，未获取到CRM创建的ID")
        lead_id = search.group(1).upper()

        params['lead_id'] = lead_id
        params['create_by'] = session['user_id']
        params['email_pushed'] = 1
        params['wework_pushed'] = 1
        schema = BusinessLeadSchema()
        new_leads = schema.load(params)
        _id = BusinessLeadDao.addBusinessLead(new_leads)
        if not _id:
            raise AppException("创建失败，创建ID不存在")

        for i in range(5):
            time.sleep(0.3)
            crm_lead = CrmViewsDao.queryLeadListByLeadId(lead_id)
            if not crm_lead:
                continue
            update_data = {"lead_code": crm_lead[1]}
            BusinessLeadDao.updateBusinessLeadById(_id, update_data)
            break

        data = {"id": _id}
        return jsonify(AppResponse(data=data))


push_leads_parser = RequestParser()
push_leads_parser.add_argument('email', location='json', type=bool)
push_leads_parser.add_argument('wework', location='json', type=bool)


@leads_api.resource('/push/<_id>')
class LeadsPushAPI(Resource):

    @permission.check(p_list['p_business_leads_mutation'])
    def put(self, _id):
        """
        线索推送
        :return:
        """
        parser_args = prepare_args_for_parser(push_leads_parser.copy())
        params = parser_args.parse_args()

        lead = BusinessLeadDao.queryBusinessLeadById(_id)
        if not lead:
            raise AppException("推送失败，线索不存在")

        if lead.create_by != session['user_id']:
            raise AppException("推送失败，只允许线索创建人推送")

        pushed = {}
        if params.get('email'):
            if lead.email_pushed == 2:
                raise AppException("正在发送，请稍等")
            else:
                pushed['email_pushed'] = 2
        if params.get('wework') and lead.wework_pushed != 2:
            if lead.wework_pushed == 2:
                raise AppException("正在发送，请稍等")
            else:
                pushed['wework_pushed'] = 2
        if pushed:
            BusinessLeadDao.updateBusinessLeadById(_id, pushed)

        owner = ESService.queryCrmSystemUserByUserId(lead.crm_owner_id)
        if not owner:
            raise AppException("推送失败，归属销售查询失败")
        owner_email = owner["internalemail"]

        create_user = SysUserDao.querySysUserById(session['user_id'])
        if not create_user:
            raise AppException("推送失败，创建人信息获取失败")

        db_app = db.get_app()

        def updatePushed(**kwargs):
            try:
                update, pushed_status = {}, 4
                resp = message_gw.push(**kwargs)
                if resp:
                    if resp.get('code') == 0:
                        pushed_status = 3

                template_type = type(kwargs.get("template"))
                if template_type == BusinessEmail:
                    update['email_pushed'] = pushed_status
                elif template_type == BusinessWeWork:
                    update['wework_pushed'] = pushed_status

                with db_app.app_context():
                    BusinessLeadDao.updateBusinessLeadById(_id, update)

            except Exception as e:
                logger.error("LeadsPushAPI Exception: {}".format(str(e)))

        if params.get('email'):
            cc, target = [create_user.email], owner_email
            sales_manager = apollo_util.getValue("sales_manager")
            if sales_manager:
                for sm in sales_manager.keys():
                    if lead.crm_owner_id.upper() == sm.upper():
                        manager = ESService.queryCrmSystemUserByUserId(sm)
                        cc.append(manager["internalemail"])
            email_cc = apollo_util.getValue("business_lead_email_cc")
            if email_cc:
                cc += email_cc

            template = BusinessEmail()
            template.update({
                "companyname": lead.company_name, "lead_name": lead.lead_code, "leadid": lead.lead_id,
                "fullname": lead.contact_name, "phone": lead.contact_way, "requiredescribe": lead.description,
                "province": lead.province, "caseuser": create_user.display_name, "ownername": owner["username"]
            })
            executor.submit(updatePushed, target=target, template=template, cc=cc, reply_to=create_user.email)

        if params.get('wework'):
            target = owner_email.replace('@Hillstonenet.com', '')
            template = BusinessWeWork()
            template.update({
                "companyname": lead.company_name, "lead_name": lead.lead_code, "leadid": lead.lead_id,
                "fullname": lead.contact_name, "phone": lead.contact_way, "requiredescribe": lead.description,
                "province": lead.province, "caseuser": create_user.display_name, "ownername": owner["username"]
            })
            executor.submit(updatePushed, target=target, template=template)

        return jsonify(AppResponse())


@leads_api.resource('/detail/<_id>')
class LeadsDetailAPI(Resource):

    @permission.check(p_list['p_business_leads_list'])
    @marsh_response(LeadDetail)
    def get(self, _id):
        """
        商机详情
        :return:
        """
        data = BusinessLeadDao.queryBusinessLeadById(_id)
        if not data:
            raise AppException("查询失败，商机线索不存在")

        schema = BusinessLeadSchema()
        data = schema.dump(data)

        return data
