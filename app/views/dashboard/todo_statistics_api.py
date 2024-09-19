import concurrent.futures

from app.models import db
from flask import Blueprint, session, jsonify
from app.extensions import permission, executor
from app.controllers.service.dashboard_service import *
from app.enums.permission_enum import p_list
from flask_restful import Resource
from app.utils.api_util import Api, AppResponse

todo_statistics_app = Blueprint('todo_statistics', __name__, url_prefix='/api/dashboard/todo_statistics')
todo_statistics_api = Api(todo_statistics_app)


@todo_statistics_api.resource('/<func_key>')
class TodoStatisticsAPI(Resource):

    def get(self, func_key):
        app_db = db.get_app()
        task_list, user_id = [], session['user_id']
        if func_key == 'se':
            if permission.userPermission(user_id, p_list['p_se_project_manage_list']):
                dashboard_service = [
                    SeProjectMinePendingRecord, SeProjectMinePendingTask, SeProjectMineEnableProject,
                    SeProjectMineEnableTask, SeEcoPendingRecord, SeProjectTaskMinePendingTask
                ]
                task_list.extend(dashboard_service)

            if permission.userPermission(user_id, p_list['p_sework_internel_project_add']):
                dashboard_service = [SeWorkPendingRecord]
                task_list.extend(dashboard_service)

            if permission.userPermission(user_id, p_list['p_sework_eco_all']):
                dashboard_service = [SeEcoPendingRecord]
                task_list.extend(dashboard_service)

        elif func_key == 'dic':
            if permission.userPermission(user_id, p_list['p_dic_ticket_manage_all']):
                dashboard_service = [
                    DicManageMineTicket, DicManageMineTask
                ]
                task_list.extend(dashboard_service)

        elif func_key == 'ticket':
            if permission.userPermission(user_id, p_list['p_dic_ticket_all']):
                dashboard_service = [DicMineTicket]
                task_list.extend(dashboard_service)

        data = {func_key: {}}
        futures = [executor.submit(task, app_db, user_id) for task in task_list]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            data[func_key].update(result)

        return jsonify(AppResponse(data))
