import json
import re
from datetime import datetime, date

from flask import Blueprint, session, jsonify
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from werkzeug.datastructures import FileStorage

from app.controllers import ESService
from app.controllers.dao import MainCollectFieldDao, MainInventoryDao, PsUserMappingDao, PsTaskDao, \
    PsTaskUploadHistoryDao, \
    PsCustomerArchivesDao, ProjectMainDao, FieldCustomValueDao, UserMainDao, SysUserDao
from app.controllers.response import marsh_response, PsTaskDetail, PsTaskUploadHistoryList, \
    PsTaskCustomerArchivesList
from app.controllers.schema import PsTaskSchema, PsTaskUploadHistorySchema, PsCustomerArchivesSchema
from app.enums.permission_enum import p_list
from app.extensions import office_util, procession_compression_util
from app.extensions import oss_util
from app.extensions import permission
from app.utils.api_util import Api, AppResponse, AppException
from app.utils.func_util import prepare_args_for_parser, validate_null

ps_inspection_app = Blueprint('ps', __name__, url_prefix='/api/ps')
ps_inspection_api = Api(ps_inspection_app)

get_inspection_parser = RequestParser()
get_inspection_parser.add_argument('task_id', location='args', type=str, required=False)
get_inspection_parser.add_argument('project_subject', location='args', type=str, required=False)
get_inspection_parser.add_argument('classification', location='args', choices=["all", "mine"], type=str, default="mine",
                                   required=True)
get_inspection_parser.add_argument('page', location='args', type=int, default=1, required=True)
get_inspection_parser.add_argument('size', location='args', type=int, default=1000, required=True)


@ps_inspection_api.resource('/inspection')
class InspectionTaskListAPI(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    def get(self):
        """
        获取任务列表(项目管理系统中获取)
        :return:
        """
        parser_args = prepare_args_for_parser(get_inspection_parser.copy())
        params = parser_args.parse_args()

        page, size = params["page"], params["size"]
        data = {"list": [], "total": 0, "page": page, "size": size}

        if params.get("classification") == 'all':
            total, task_list = MainCollectFieldDao.queryCollectFieldByFilter(**params)
        else:
            mapping = PsUserMappingDao.queryUserMappingById(session['user_id'])

            if not mapping:
                raise AppException("参数错误，用户关系未添加，请联系管理员")

            total, task_list = MainCollectFieldDao.queryCollectFieldByFilter(uid=mapping.project_system_id, **params)

        for task_dict in task_list:
            task, project, project_user = task_dict
            task_user = UserMainDao.queryUserMainByUid(task.uid)

            task_user = SysUserDao.querySysUserByEmail(task_user.email)
            sys_user = SysUserDao.querySysUserByEmail(project_user.email)

            task_dic = {
                "project_id": task.project_id,
                "task_id": task.issue_id,
                "task_subject": task.summary,
                "project_subject": task.project_name,
                "project_account": task.org_name,
                "project_owner": sys_user.display_name if sys_user else project_user.display_user_name,
                "project_owner_id": sys_user.id if sys_user else '',
                "task_owner_id": task_user.id if task_user else '',
                "task_owner": task_user.display_name if task_user else task.display_user_name,
                "task_start_date": task.start_date,
                "task_end_date": task.due_date
            }

            data['list'].append(task_dic)

        data["total"] += total
        # data["list"] = data["list"][(page - 1) * size:((page - 1) * size + size)]
        return jsonify(AppResponse(data))


@ps_inspection_api.resource("/inspection/task/<task_id>")
class InspectionTaskDetailAPI(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    @marsh_response(PsTaskDetail)
    def get(self, task_id):
        """
        获取任务详情
        """
        ps_task = MainCollectFieldDao.queryCollectFieldByIssueId(task_id)
        if not ps_task:
            raise AppException("查询失败，任务不存在")

        project, user = ProjectMainDao.getProjectByUser(ps_task.project_id)
        if not project:
            raise AppException("查询失败，项目不存在")

        task = PsTaskDao.queryTaskByTaskId(task_id)
        field = FieldCustomValueDao.queryFieldCustomValueByIssueId(task_id, '474')

        schema = PsTaskSchema()
        data = schema.dump(task)
        data["task_subject"] = ps_task.summary
        data["task_owner"] = ps_task.display_user_name
        data["task_start_date"] = ps_task.start_date.strftime("%Y-%m-%d %H:%M:%S")
        data["task_end_date"] = ps_task.due_date.strftime("%Y-%m-%d %H:%M:%S")
        data["project_subject"] = ps_task.project_name
        data["project_account"] = ps_task.org_name
        data["project_owner"] = user.display_user_name
        data["contrast"] = True if field and field.text_value else False
        data["external"] = json.loads(data['external']) if data['external'] else {}

        return data


@ps_inspection_api.resource("/inspection/task/<task_id>/history")
class InspectionTaskHistoryListAPI(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    @marsh_response(PsTaskUploadHistoryList)
    def get(self, task_id):
        """
        获取任务上传文件的历史记录列表
        """
        data = {"list": [], "total": 0, "total_use": 0}

        task = PsTaskDao.queryTaskByTaskId(task_id)
        if not task:
            return data

        task_pco_list = PsTaskUploadHistoryDao.getTaskUploadHistoryByTaskId(task.id)

        for task_pco in task_pco_list:

            if task_pco.deciphering == 'False':
                continue

            schema = PsTaskUploadHistorySchema()
            task = schema.dump(task_pco)

            task["upload_file_url"] = oss_util.generatePreSignedUrl(task['upload_file_id'], 'tech-attachment')
            customer = PsCustomerArchivesDao.queryCustomerArchivesByTaskId(task['id'], 'origin')
            task['count'] = len(customer)

            edit_customer = PsCustomerArchivesDao.queryCustomerArchivesByTaskId(task['id'], 'edit')
            data["total_use"] += len(edit_customer)
            data["total"] += len(customer)
            data["list"].append(task)

        if data["total_use"] == 0:
            data["total_use"] = data["total"]
        return data


post_inspection_check_parser = RequestParser()
post_inspection_check_parser.add_argument('list', location='json', type=list, required=True)
post_inspection_check_parser.add_argument('date_tag', location='json', type=str)


@ps_inspection_api.resource("/inspection/task/<task_id>/check")
class InspectionTaskCheckAPI(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    @marsh_response(PsTaskCustomerArchivesList)
    def get(self, task_id):
        """
        导出报告前预检
        """
        task = PsTaskDao.queryTaskByTaskId(task_id)
        if not task:
            raise AppException("查询失败，任务不存在")

        data = {"list": []}
        tip_data = {"city": "落地城市", "account_name": "客户名称", "area": "部署区域",
                    "online_date": "上线时间", "purchase_date": "购买时间", "machine_room": "机房位置"}
        customer_archives = PsCustomerArchivesDao.getTaskJoinHistoryJoinCustomerByTaskId(task.id, 'all')

        for customer in customer_archives:
            if customer.status == 'delete':
                continue

            schema = PsCustomerArchivesSchema()
            customer = schema.dump(customer)
            customer['tip'] = []

            for key, value in tip_data.items():
                if not customer[key]:
                    customer['tip'].append(value)

            data['list'].append(customer)
        return data

    @permission.check(p_list['p_ps_inspection_all'])
    def post(self, task_id):
        """
        预检提交
        """
        parser_args = prepare_args_for_parser(post_inspection_check_parser.copy())
        params = parser_args.parse_args()

        task = PsTaskDao.queryTaskByTaskId(task_id)
        if not task:
            raise AppException("查询失败，任务不存在")

        data = {"is_pass": False}
        tip_data = {"city": "落地城市", "account_name": "客户名称", "account_id": "客户ID", "area": "部署区域",
                    "online_date": "上线时间", "purchase_date": "购买时间", "machine_room": "机房位置"}
        quarter_dic = {"1": "一", "2": "二", "3": "三", "4": "四"}
        monthly_dic = {"01": "一", "02": "二", "03": "三", "04": "四", "05": "五", "06": "六", "07": "七", "08": "八",
                       "09": "九", "10": "十", "11": "十一", "12": "十二"}
        verify_list = []

        customer_archives = PsCustomerArchivesDao.getTaskJoinHistoryJoinCustomerByTaskId(task.id, 'all')  # 全部信息
        delete_customer = []  # 不需要删除状态的信息
        schema = PsCustomerArchivesSchema()
        for archives in params.get("list"):
            tip = []
            update_info = {}

            # 必填字段验证、客户id忽略
            for key, name in tip_data.items():
                if key not in archives or not archives[key] and key != 'account_id':
                    tip.append(name)
                else:
                    update_info[key] = archives[key]

            # 判断该条记录是否通过校验
            if tip:
                verify_list.append({
                    "id": archives['id'],
                    "tip": tip
                })
                update_info['is_publish'] = "False"
            else:
                update_info['is_publish'] = 'True'

            update_info["status"] = 'edit'

            # 更新记录信息（原始数据的话怎加新数据）
            if archives['status'] == 'origin':
                edit_data = PsCustomerArchivesDao.queryCustomerArchivesBySN(archives['task_id'], archives['device_sn'], 'edit')
                if edit_data:
                    archives_id = edit_data.id
                else:
                    original_data = PsCustomerArchivesDao.queryCustomerArchivesBySN(archives['task_id'], archives['device_sn'], 'origin')
                    formatting = schema.dump(original_data)
                    formatting.pop("id")
                    formatting['status'] = "edit"
                    archives_insert = schema.load(formatting)

                    archives_id = PsCustomerArchivesDao.addCustomerArchives(archives_insert)
            else:
                archives_id = archives['id']
            PsCustomerArchivesDao.updateCustomerArchivesById(archives_id, update_info)
            delete_customer.append({"task_id": archives['task_id'], "device_sn": archives['device_sn']})

        # 已删除数据记录更新
        if len(delete_customer) != len(customer_archives):
            for customer in customer_archives:
                if customer.status == 'delete':
                    continue
                for delete in delete_customer:
                    if customer.task_id == delete['task_id'] and customer.device_sn == delete['device_sn']:
                        break
                else:
                    formatting = schema.dump(customer)
                    formatting.pop("id")
                    formatting['status'] = "delete"
                    archives = schema.load(formatting)

                    archives_id = PsCustomerArchivesDao.addCustomerArchives(archives)

        # 通过校验生成初步巡检报告
        if not verify_list:
            record_list = PsCustomerArchivesDao.getTaskJoinHistoryJoinCustomerByTaskId(task.id, 'edit')
            data['is_pass'] = True
            record_customer = []
            record_inspection_type = []
            schema = PsCustomerArchivesSchema()
            for index, record in enumerate(record_list):
                record = schema.dump(record)

                if record['cur_cpu'][:-1]:
                    if float(record['cur_cpu'][:-1]) > 70:
                        record['cpu_assess'] = '异常'
                if record['cp_memory'][:-1]:
                    if float(record['cp_memory'][:-1]) > 70:
                        record['cp_assess'] = '异常'
                if record['dp_memory'][:-1]:
                    if float(record['dp_memory'][:-1]) > 70:
                        record['dp_assess'] = '异常'
                if record['ps_status']:
                    if record['ps_status'] == '正常':
                        record['power_status'] = '正常'
                        record['ps_status'] = 'Fine'
                    else:
                        power_supply = re.findall("(PS\d+)", record['ps_status'], flags=re.IGNORECASE)
                        record['ps_status'] = "、".join(power_supply) + "异常"
                        record['power_status'] = '具体异常电源名'
                if record['fan_status']:
                    if record['fan_status'] == '正常':
                        record['fan_evaluation'] = '正常'
                        record['fan_status'] = 'Fine'
                    else:
                        electric_fan = re.findall("(Fan\d+)", record['fan_status'], flags=re.IGNORECASE)
                        record['fan_status'] = "、".join(electric_fan) + "异常"
                        record['fan_evaluation'] = '具体异常风扇名'
                if record['module_status']:
                    if record['module_status'] == '正常':
                        record['module_status'] = "Fine"
                        record['board_status'] = "正常"
                    else:
                        if record['module_status'] != '无板卡':
                            board_card = re.findall("(slot\d+/*\d)", record['module_status'], re.IGNORECASE)
                            record['module_status'] = "、".join(board_card) + "异常"
                        record['board_status'] = "具体异常板卡名"
                if record['env_cpu_temperature']:
                    if 0 <= float(record['env_cpu_temperature']) <= 80:
                        record['env_cpu_evaluation'] = "温度正常"
                    elif 80 < float(record['env_cpu_temperature']) <= 90:
                        record['env_cpu_evaluation'] = "温度偏高"
                    elif 90 < float(record['env_cpu_temperature']):
                        record['env_cpu_evaluation'] = "温度过高"
                    else:
                        record['env_cpu_evaluation'] = "温度异常"
                if params.get("date_tag"):
                    quarterly_data = PsCustomerArchivesDao.queryCustomerArchivesBySnFirst(params.get("date_tag"), [record['device_sn']])
                    quarterly_data = schema.dump(quarterly_data)
                    if quarterly_data:
                        if quarterly_data['inspection_type']:
                            quarterly = quarterly_data['inspection_type'].split("-")
                        else:
                            if not record_inspection_type:
                                history = PsTaskUploadHistoryDao.queryTaskUploadHistoryById(quarterly_data['task_id'])
                                quarterly_task = PsTaskDao.queryTaskById(history.task_id)
                                quarterly_quarterly = MainCollectFieldDao.queryCollectFieldByIssueId(quarterly_task.task_id)
                                month = quarterly_quarterly.start_date.month
                                quarter = (month - 1) // 3 + 1
                                record_inspection_type = ['q', str(quarterly_quarterly.start_date), str(quarter)]
                            quarterly = record_inspection_type

                        if quarterly[0] == 'q':
                            quarterly_data["date_tag"] = "%s年第%s季度" % (quarterly[1], quarter_dic[quarterly[2]])
                        else:
                            quarterly_data["date_tag"] = "%s年第%s月度" % (quarterly[1], monthly_dic[quarterly[2]])

                        if quarterly_data['module_status']:
                            if quarterly_data['module_status'] == '正常':
                                quarterly_data['board_status'] = "正常"
                            else:
                                quarterly_data['board_status'] = "具体异常板卡名"
                        record["quarterly_data"] = quarterly_data
                    else:
                        record["quarterly_data"] = {}
                else:
                    record["quarterly_data"] = {}

                record_customer.append(record)

            collect = MainCollectFieldDao.queryCollectFieldByIssueId(task_id)
            report_file_id = office_util.renderTheInspectionReportTemplate(record_customer, task, collect.org_name, collect.start_date, params.get("date_tag"), oss_util=oss_util)
            PsTaskDao.updateTaskById(task.id, {"is_pass": 'True', "report_file_id": report_file_id})
        else:
            PsTaskDao.updateTaskById(task.id, {"is_pass": 'False'})
            data["tip_list"] = verify_list
        return jsonify(AppResponse(data))


post_attachment_parser = RequestParser()
post_attachment_parser.add_argument('subject', location='form', type=validate_null, required=True)
post_attachment_parser.add_argument('city', location='form')
post_attachment_parser.add_argument('area', location='form')
post_attachment_parser.add_argument('account_id', location='form')
post_attachment_parser.add_argument('account_name', location='form')
post_attachment_parser.add_argument('machine_room', location='form', default='', required=False)
post_attachment_parser.add_argument('file', location='files', type=FileStorage, required=True)


@ps_inspection_api.resource("/inspection/task/<task_id>/export")
class InspectionTaskExportAPI(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    def post(self, task_id):
        """
        上传巡检文件
        """
        parser_args = prepare_args_for_parser(post_attachment_parser.copy())
        params = parser_args.parse_args()

        # struct_version = "1.0.0"

        data = {"id": ""}

        file_storage = params.pop("file")
        if 'machine_room' in params:
            machine_room = params.pop("machine_room")
        else:
            machine_room = ''

        data_zip = procession_compression_util.unzipTheFile(file_storage)
        if not data_zip[0]:
            raise AppException("本站点巡检服务支持的结构体版本区间为:%s-%s" % (data_zip[1]['start'], data_zip[1]['end']))
        file_storage.seek(0)

        # 写入任务列表
        task = MainCollectFieldDao.queryCollectFieldByIssueId(task_id)
        Inspection_type = FieldCustomValueDao.queryFieldCustomValueByIssueId(task_id, '473')
        year_quarter = FieldCustomValueDao.queryFieldCustomValueByIssueId(task_id, '474')

        inspection_type = ''
        if Inspection_type and year_quarter:
            year_quarter = year_quarter.text_value.split("-")
            if Inspection_type.string_value == "季度巡检":
                quarter = {'Q1': '1', "Q2": "2", "Q3": '3', "Q4": '4'}
                inspection_type = "q-%s-%s" % (year_quarter[0], quarter[year_quarter[1]])
            elif Inspection_type.string_value == '月度巡检':
                inspection_type = "m-%s-%s" % (year_quarter[0], year_quarter[1])

        info = {
            "task_id": task_id,
            "project_id": str(task.project_id),
            "is_pass": "False",
            "inspection_type": inspection_type
        }
        schema = PsTaskSchema()
        ps_task = schema.load(info)
        task_id = PsTaskDao.addTask(ps_task)

        # 文件上传-上传历史记录
        file_meta = {
            "ContentType": file_storage.content_type,
            "ContentDisposition": f"attachment; filename={'_'.join([task.org_name, file_storage.filename])}"
        }
        _id = oss_util.uploadFileStream(file_storage, "tech-attachment", file_meta)

        # 写入上传历史记录
        params["file_name"] = file_storage.filename
        params["task_id"] = task_id
        params["upload_file_id"] = _id
        params["deciphering"] = 'False'
        params["created_by_id"] = session["user_id"]
        schema = PsTaskUploadHistorySchema()
        attachment = schema.load(params)
        data["id"] = PsTaskUploadHistoryDao.addTaskUploadHistory(attachment)

        # 客户档案信息写入
        project, user = ProjectMainDao.getProjectByUser(task.project_id)
        account_manager = FieldCustomValueDao.queryFieldCustomValueByIssueId(ps_task.task_id, '32')
        contact_way = FieldCustomValueDao.queryFieldCustomValueByIssueId(ps_task.task_id, '33')
        total, customer_list = ESService.queryCrmAccountByAccountName(task.org_name)

        schema = PsCustomerArchivesSchema()
        for device in data_zip[1]:

            device_area = PsCustomerArchivesDao.queryCustomerArchivesByDeviceSN(device['sn'])
            inventory = MainInventoryDao.queryInventoryBySN(device['sn'])

            info = {
                "task_id": data["id"],
                "city": task.city if task else params.get("city"),
                "account_id": (customer_list[0]['account_id'] if total == 1 else "") if not params.get(
                        "account_id") else params.get("account_id"),
                "account_name": task.org_name if not params.get("account_name") else params.get("account_name"),
                "area": device_area.area if device_area else (
                        inventory.district if inventory else params.get("area")),
                "device_name": device['hostname'],
                "device_sn": device['sn'],
                "device_model": device['product_name'],
                "ha_state": device['ha']['ha_status'],
                "software_version": device['version'],
                "uptime": device['uptime'],
                "feature": device['feature'],
                "plat_expiration": device['plat_expiration'],
                "session_info": device["session"]["max_session"],
                "alloc_session": device['session']['rampup_session'],
                "cur_cpu": device['cpu']['cpu_24h_max'],
                "cp_memory": device['cp_memory'],
                "dp_memory": device['dp_memory'],
                "throughput": device['throughput'],
                "fan_status": device['env_fan_status'],
                "module_status": device['module_status'],
                "env_cpu_temperature": device['cpu']['env_cpu_temperature'],
                "snat_rate": device['rate']['snat使用率'],
                "dnat_rate": device['rate']['dnat使用率'],
                "address_rate": device['rate']['address使用率'],
                "server_rate": device['rate']['service使用率'],
                "policy_rate": device['rate']['policy使用率'],
                "alg_staus": device['alg'],
                "ha_status_info": device['ha']['ha_status'],
                "log_folder": device['logging_status'],
                "attack_info": device['log_threat'],
                "exception_log_info": device['log_event'],
                "clock": device['clock'],
                "original_manager": user.display_user_name,
                "account_manager": account_manager.text_value,
                "contact_info": contact_way.text_value,
                "purchase_date": None,
                "online_date": inventory.Launch_date.strftime("%Y-%m-%d") if inventory and inventory.Launch_date else datetime.today().strftime("%Y-%m-%d"),
                "created_by_id": session['user_id'],
                "status": 'origin',
                "is_publish": 'False',
                "raw_data": json.dumps(device, ensure_ascii=False),
                "lic_expiration_time": device['plat_expiration'] if device['plat_expiration'] else datetime.now().strftime("%Y-%m-%d"),
                "route_entry": device['rate']['route使用率'],
                "machine_room": machine_room,
                "ps_status": device['env_pssum_status'],
                "inspection_type": inspection_type,
                "compare_main_baseconfig": json.dumps(device['compare_main_baseconfig'], ensure_ascii=False) if device['compare_main_baseconfig'] else "",
                "password_policy": device['password_policy'],
                "admin_lockout_duration": device['admin_lockout_duration'],
                "unsafe_interface": device['unsafe_interface'],
                "admin_host": device['admin_host'],
                "logging_status": device['logging_status'],
                "log_threat": device['log_threat'],
                "log_alarm": device['log_alarm'],
                "all_passrlue": device['all_passrlue'],
                "ha_group": device['ha_group'],
                "synced": device['synced'],
                "poor": device['poor'],
            }
            # info["session_info"] = json.dumps(device["session"], ensure_ascii=False)
            # "ps_status": {},
            # "ha_status_info": json.dumps(device['ha'], ensure_ascii=False),
            #
            # ps_status = {}
            #
            # if 'env_ps0_status' in device:
            #     ps_status["env_ps0_status"] = device['env_ps0_status']
            # if 'env_ps1_status' in device:
            #     ps_status["env_ps1_status"] = device['env_ps1_status']
            #
            # info["ps_status"] = json.dumps(ps_status, ensure_ascii=False)

            device_info = schema.load(info)
            PsCustomerArchivesDao.addCustomerArchives(device_info)

        PsTaskUploadHistoryDao.updateTaskUploadHistoryById(data["id"], {"deciphering": "True"})

        return jsonify(AppResponse(data))


get_inspection_permission_parser = RequestParser()
get_inspection_permission_parser.add_argument('task_id', location='args', type=str, required=True)


@ps_inspection_api.resource("/inspection/permission/<page_title>")
class InspectionTaskPermissionAPI(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    def get(self, page_title):
        """
        任务详情，业务权限
        """
        parser_args = prepare_args_for_parser(get_inspection_permission_parser.copy())
        params = parser_args.parse_args()

        data = {"list": []}
        if page_title == 'task_detail':
            if not params.get("task_id"):
                raise AppException("参数错误，任务ID不能为空")

            mapping = PsUserMappingDao.queryUserMappingById(session["user_id"])
            if not mapping:
                return jsonify(AppResponse(data))
                # raise AppException("参数错误，为查询到用户关系，请联系管理员")

            ps_task = MainCollectFieldDao.queryCollectFieldByIssueId(params.get("task_id"))
            if str(ps_task.uid) == mapping.project_system_id:
                data["list"] += ["upload"]

            task = PsTaskDao.queryTaskByTaskId(params.get('task_id'))
            if not task:
                return jsonify(AppResponse(data))

            task_history = PsTaskUploadHistoryDao.getTaskUploadHistoryByTaskId(task.id)
            if task_history and task:
                for history in task_history:
                    if history.deciphering == 'True':
                        data["list"] += ["check", "restore"]
                        break
                if task.report_file_id and task.is_pass == 'True':
                    data["list"].append("download")
                    if 'upload' in data["list"]:
                        data["list"].remove("upload")
                    if "check" in data["list"]:
                        data["list"].remove("check")
                    if "restore" not in data["list"]:
                        data["list"].append("restore")


        return jsonify(AppResponse(data))


@ps_inspection_api.resource("/inspection/task/<task_id>/restore")
class InspectionTaskRestoreAPI(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    def put(self, task_id):
        """
        重置预检成功后的客户档案数据
        """
        ps_task = MainCollectFieldDao.queryCollectFieldByIssueId(task_id)
        if not ps_task:
            raise AppException("查询失败，任务不存在")

        task = PsTaskDao.queryTaskByTaskId(task_id)
        if not task:
            raise AppException("查询失败，任务不存在")

        if task.is_pass == 'False':
            raise AppException("重置失败，当前任务数据未完成预检")

        history = PsTaskUploadHistoryDao.getTaskUploadHistoryByTaskId(task.id)
        for custom in history:
            PsCustomerArchivesDao.deleteCustomerArchivesByTaskId(custom.id)

        PsTaskDao.updateTaskById(task.id, {"is_pass": "False"})

        return jsonify(AppResponse())


post_inspection_download_parser = RequestParser()
post_inspection_download_parser.add_argument('external_list', location='json', type=list)


@ps_inspection_api.resource("/inspection/task/<task_id>/download")
class InspectionTaskReportFileDownloadAPI(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    def post(self, task_id):
        """
        下载巡检报告
        """
        parser_args = prepare_args_for_parser(post_inspection_download_parser.copy())
        params = parser_args.parse_args()

        task = PsTaskDao.queryTaskByTaskId(task_id)
        if not task:
            raise AppException("查询失败，未找到任务信息")

        external = {
            "external_list": params.get("external_list")
        }
        PsTaskDao.updateTaskById(task.id, {"external": json.dumps(external)})
        record_list = PsCustomerArchivesDao.getTaskJoinHistoryJoinCustomerByTaskId(task.id, 'edit')

        collect = MainCollectFieldDao.queryCollectFieldByIssueId(task_id)
        summary_file_id = office_util.summaryOfInspectionDocuments(task.report_file_id, task.summary_file_id, task.id, collect.org_name, external, total=len(record_list), oss_util=oss_util)

        PsTaskDao.updateTaskById(task.id, {"summary_file_id": summary_file_id})

        report_url = oss_util.generatePreSignedUrl(summary_file_id, 'tech-attachment')
        data = {
            "url": report_url
        }

        return jsonify(AppResponse(data))


@ps_inspection_api.resource("/inspection/task/<task_id>/preview")
class InspectionTaskReportFilePreviewAPI(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    def get(self, task_id):
        """
        预览文件
        """
        task = PsTaskDao.queryTaskByTaskId(task_id)
        if not task:
            raise AppException("查询失败，未找到任务信息")

        if not task.report_file_id:
            raise AppException("预览失败，未检索到巡检报告")

        collect = MainCollectFieldDao.queryCollectFieldByIssueId(task_id)
        _id = office_util.convertToPDFFileV2(task.report_file_id, task, collect.org_name, oss_util=oss_util)
        if not _id:
            raise AppException("预览失败，请联系管理员确认")

        PsTaskDao.updateTaskById(task.id, {"preview_file_id": _id})

        preview_url = oss_util.generatePreSignedUrl(_id, 'tech-attachment')

        data = {
            "url": preview_url
        }

        return jsonify(AppResponse(data))


@ps_inspection_api.resource("/inspection/date_tag")
class InspectionDataTag(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    def get(self):
        """
        季度对比标签
        """
        data = {"list": []}
        quarter_dic = {"1": "一", "2": "二", "3": "三", "4": "四"}
        monthly_dic = {"01": "一", "02": "二", "03": "三", "04": "四", "05": "五", "06": "六", "07": "七", "08": "八",
                       "09": "九", "10": "十", "11": "十一", "12": "十二"}

        start_date = datetime.now().year
        year = str(start_date - 2)

        date_tag = PsTaskDao.queryTaskGroupByInspection(year)

        if date_tag:
            for tag in date_tag:
                if tag[0]:
                    template = {}
                    inspection = tag[0].split("-")
                    if "q" == inspection[0]:
                        template['date_tag'] = tag[0]
                        template['label'] = "%s第%s季度" % (inspection[1], quarter_dic[inspection[2]])
                    else:
                        template['date_tag'] = tag[0]
                        template['label'] = "%s第%s月" % (inspection[1], monthly_dic[inspection[2]])

                    data["list"].append(template)

        return jsonify(AppResponse(data))


get_inspection_history_archive_parser = RequestParser()
get_inspection_history_archive_parser.add_argument('date_tag', location='args', type=str)
get_inspection_history_archive_parser.add_argument('sn[]', location='args', type=str, action='append', dest='sn')


@ps_inspection_api.resource("/inspection/history/archive")
class InspectionHistoryArchive(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    @marsh_response(PsTaskCustomerArchivesList)
    def get(self):
        """
        获取季度对比数据
        """
        parser_args = prepare_args_for_parser(get_inspection_history_archive_parser.copy())
        params = parser_args.parse_args()

        data = {"list": []}
        quarter_dic = {"1": "一", "2": "二", "3": "三", "4": "四"}
        monthly_dic = {"01": "一", "02": "二", "03": "三", "04": "四", "05": "五", "06": "六", "07": "七", "08": "八",
                       "09": "九", "10": "十", "11": "十一", "12": "十二"}

        customer_archives = PsCustomerArchivesDao.queryCustomerArchivesByInspectionBySn(params.get("date_tag"), params.get('sn'))

        customer_list =[]
        for customer in customer_archives:
            if customer.device_sn in customer_list:
                continue
            customer_list.append(customer.device_sn)
            schema = PsCustomerArchivesSchema()
            archives = schema.dump(customer)

            archives['date_tag'] = archives['inspection_type']
            if 'q' == archives['inspection_type'][0]:
                archives['date_tag_label'] = "第%s季度" % quarter_dic[archives['inspection_type'][-1]]
            else:
                archives['date_tag_label'] = "第%s月度" % monthly_dic[archives['inspection_type'][-2:]]

            data["list"].append(archives)

        return data


@ps_inspection_api.resource("/inspection/version_interval")
class InspectionVersionInterval(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    def get(self):
        data = {
            "start_version": procession_compression_util.start_version,
            "end_version": procession_compression_util.end_version
        }

        return jsonify(AppResponse(data))


@ps_inspection_api.resource("/inspection/task/<task_id>/summary_field")
class InspectionFieldInformation(Resource):

    @permission.check(p_list['p_ps_inspection_all'])
    def get(self, task_id):
        task = PsTaskDao.queryTaskByTaskId(task_id)
        if not task:
            raise AppException("查询失败，未找到任务信息")

        data = {"list": [
            {
                "id": "1",
                "name": "device_name_sn",
                "title": "设备名称+SN",
                "type": "select",
                "default_value": "",
                "options": [],
                "width": 200
            },
            {
                "id": "2",
                "name": "occurrence_time",
                "title": "发生时间",
                "type": "text",
                "default_value": "",
                "options": []
            },
            {
                "id": "3",
                "name": "concrete_issue",
                "title": "具体问题",
                "type": "text",
                "default_value": "",
                "options": []
            },
            {
                "id": "3",
                "name": "solution",
                "title": "解决方案",
                "type": "text",
                "default_value": "",
                "options": []
            },
            {
                "id": "3",
                "name": "risk_grade",
                "title": "风险等级",
                "type": "select",
                "default_value": "高",
                "options": [
                    "高",
                    "中",
                    "低"
                ]
            }
        ]}

        device_sn = []
        record_list = PsCustomerArchivesDao.getTaskJoinHistoryJoinCustomerByTaskId(task.id, 'edit')
        for record in record_list:
            device_sn.append("_".join([record.device_name, record.device_sn]))

        data["list"][0]['options'] = device_sn

        return jsonify(AppResponse(data))
