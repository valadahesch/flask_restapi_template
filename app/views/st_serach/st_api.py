import requests
from datetime import datetime
from flask import session, Blueprint, request, jsonify
from flask_restful import Resource
from app.controllers.response import marsh_response
from app.controllers.dao.st_dao import SysSearchController
from app.utils.api_util import Api
from app.extensions import permission
from app.enums.permission_enum import p_list
from app.utils.api_util import AppResponse, AppException
from app.controllers.response.st_response import StSitesList, StOverView, StDetailSchema
from flask_restful.reqparse import RequestParser
from app.utils.func_util import prepare_args_for_parser
from app.utils.st_util import overview, Common, getStSearchDetail, esAnalyzer

st_app = Blueprint('st', __name__, url_prefix='/api/aggregated_search')
st_api = Api(st_app)

record_parser = RequestParser()
record_parser.add_argument('q', location='args', type=str, default="")
record_parser.add_argument('id', location='json', type=int)
record_parser.add_argument('t', location='args', type=str)
record_parser.add_argument('page', location='args', type=str)
record_parser.add_argument('size', location='args', type=str)
record_parser.add_argument('search_info', location='json', type=str)
record_parser.add_argument('url', location='json', type=str, default="")


@st_api.resource('/site_list')
class StPower(Resource):
    @permission.check(p_list['p_internal_api_list'])
    @marsh_response(StSitesList)
    def get(self):
        """
        根据用户权限划分不同的访问目录,主要划分为: 内部(tac,dic,其他）和外部
        """
        if not session.get("role_department"):
            user_info = SysSearchController.queryRoleByUserid(user_id=session['user_id'])
            role_department = user_info.get("role_department") if user_info.get("user_type") == 0 else "other"
            session["role_department"] = role_department
        # role_department = "技术支持中心"
        site_datas = SysSearchController.querySiteByRole(session["role_department"])
        if not site_datas['list']:
            site_datas = SysSearchController.querySiteByRole("山石网科")
        return site_datas


@st_api.resource('/search_info')
class SearchInfo(Resource):
    @permission.check(p_list['p_internal_api_list'])
    def post(self):
        """
        记录用户搜索，站点访问记录（包含外链）
        """
        parser_args = prepare_args_for_parser(record_parser.copy())
        params = parser_args.parse_args()
        user_id = session['user_id']
        create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        SysSearchController.addVisitHistoryBySearch(user_id, create_time, 0, params.get("search_info"))
        return AppResponse()
    

@st_api.resource('/site/visit')
class SearchVisit(Resource):
    @permission.check(p_list['p_internal_api_list'])
    def post(self):
        """
        记录用户点击，站点访问记录
        """
        parser_args = prepare_args_for_parser(record_parser.copy())
        params = parser_args.parse_args()
        user_id = session['user_id']
        create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        SysSearchController.addVisitHistoryBySearch(user_id, create_time, params.get("id"), "")
        return AppResponse()
    

@st_api.resource('/search/visit')
class SearchUrlVisit(Resource):
    @permission.check(p_list['p_internal_api_list'])
    def post(self):
        """
        记录超链接的子链接
        """
        parser_args = prepare_args_for_parser(record_parser.copy())
        params = parser_args.parse_args()
        user_id = session['user_id']
        create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        SysSearchController.addVisitHistoryBySearch(user_id, create_time, 0, params.get("url", ""))
        return AppResponse()


@st_api.resource('/analyze')
class Analyze(Resource):
    @permission.check(p_list['p_internal_api_list'])
    def get(self):
        params = request.args
        if not params.get("q"):
            raise AppException(data="Missing parameter!")
        q = params.get("q").strip()
        if len(q) < 2:
            raise AppException(data="搜索关键词至少为两个字符")
        data = esAnalyzer(q)
        if data is None:
            raise AppException(data="分词失败!")
        return jsonify({'code': 0, 'data': data, 'message': ''})


@st_api.resource('/overview')
class SearchOverview(Resource):
    @permission.check(p_list['p_internal_api_list'])
    @marsh_response(StOverView)
    def get(self):
        """
        用于显示搜索来源
        """
        params = request.args
        if 'q' not in params: raise AppException(data="Missing parameter!")
        q = params.get("q").strip()
        next_id = int(params.get('id', 0))
        if len(q) < 2: raise AppException("Search terms must be at least two characters long!")
        if not session.get("role_department"):
            user_info = SysSearchController.queryRoleByUserid(user_id=session['user_id'])
            role_department = user_info.get("role_department") if user_info.get("user_type") == 0 else "山石网科"
            session["role_department"] = role_department
        role_department = session["role_department"]
        return overview(q, next_id, role_department)


@st_api.resource('/detail')
class SearchDetail(Resource):
    @permission.check(p_list['p_internal_api_list'])
    # @marsh_response(StDetailSchema)
    def get(self):
        """
        显示搜索来源对应搜索结果
        q: 搜索框用户输入信息
        t:搜索来源
        page: 第几页
        size: 页面大小(目前强制为5)
        """
        params = request.args
        q = params.get("q")
        if len(q) < 2 : raise AppException(data="Missing parameter!")
        q = params.get("q").strip()
        if len(q) < 2: raise AppException("Search terms must be at least two characters long!")
        if 't' not in params: raise AppException("Missing parameter!")
        t = params.get('t')
        s = Common.parseInt(params.get('s'), 10) if 's' in params else 10
        n = Common.parseInt(params.get('n'), 0) - 1 if 'n' in params else 0
        if not session.get("role_department"):
            user_info = SysSearchController.queryRoleByUserid(user_id=session['user_id'])
            role_department = user_info.get("role_department") if user_info.get("user_type") == 0 else "山石网科"
            session["role_department"] = role_department
        result = getStSearchDetail(q, t, s, n, session["role_department"], session["user_id"])
        return result


