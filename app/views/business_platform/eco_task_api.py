from flask import Blueprint, session, jsonify
from flask_restful import Resource
from app.enums.permission_enum import p_list
from app.extensions import permission
from app.controllers.elasticsearch_service import ESService
from app.controllers.dao import DataScopeDao
from app.utils.api_util import Api, AppResponse

eco_task_app = Blueprint('eco_task', __name__, url_prefix='/api/presales/task')
ecotask_api = Api(eco_task_app)


@ecotask_api.resource('/all/owner/list')
class EcoTaskOwnerAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    def get(self):
        """
        负责人列表查询
        :return:
        """
        userid_list = []
        data = {"list": [{"id": "me", "display_name": "我"}, {"id": "my_subordinates", "display_name": "我的下属"}]}
        user_id, user_roles = session["user_id"], session['roles']
        user_ids = DataScopeDao.getSysUserByRank(user_id, 'sework.internal:all')
        if not user_ids:
            return jsonify(AppResponse(data))

        total, res = ESService.querySeEcoPartnerByFilter(user_ids)
        if res:
            for hit in res:
                main_task = hit["_source"]
                if main_task.get("deleted_date") or (main_task["owner_id"] not in user_ids and user_ids[0] != "*"):
                    continue

                sub_task_list = main_task["sub_tasks"]
                for sub_task in sub_task_list:
                    if sub_task.get("deleted_date") or (sub_task["owner_id"] not in user_ids and user_ids[0] != "*"):
                        continue

                    if sub_task["owner_id"] not in userid_list and sub_task["owner_id"]:
                        data["list"].append({"id": sub_task["owner_id"], "display_name": sub_task["owner_name"]})
                        userid_list.append(sub_task["owner_id"])

                if main_task["owner_id"] not in userid_list and main_task["owner_id"]:
                    data["list"].append({"id": main_task["owner_id"], "display_name": main_task["owner_name"]})
                    userid_list.append(main_task["owner_id"])

        return jsonify(AppResponse(data))


@ecotask_api.resource('/all/participants/list')
class ProjectCreateAPI(Resource):

    @permission.check(p_list['p_sework_eco_all'])
    def get(self):
        """
        任务参与人
        :return:
        """
        userid_list = []
        data = {"list": [{"id": "me", "display_name": "我"}, {"id": "my_subordinates", "display_name": "我的下属"}]}
        user_id, user_roles = session["user_id"], session['roles']
        user_ids = DataScopeDao.getSysUserByRank(user_id, 'sework.internal:all')
        if not user_ids:
            return jsonify(AppResponse(data))

        total, res = ESService.querySeEcoPartnerByFilter(user_ids)
        if res:
            for hit in res:
                main_task = hit["_source"]
                if main_task.get("deleted_date"):
                    continue

                for participant in main_task["participants"]:
                    if participant in user_ids or user_ids[0] == "*":
                        if participant["id"] not in userid_list and participant.get("id"):
                            data["list"].append(participant)
                            userid_list.append(participant["id"])

        return jsonify(AppResponse(data))