import json
import pandas as pd

from datetime import datetime, timedelta
from app.extensions import oss_util, tac_api
from app.controllers import ESService
from app.enums.se_project_template import getSeProjectProjectType
from app.enums.eco_partner_template import getSeEcoTaskType
from app.enums.se_project_enum import enums as project_enums
from app.enums.eco_partner_enum import enums as eco_enums
from app.enums.se_work_enum import enums as work_enums
from app.controllers.dao import SeWeeklyDao, SysUserDao, SeEcoTaskDao, SeProjectRecordDao, SeEcoRecordDao, \
    SeWorkRecordDao, SeProjectProjectDao, SeProjectFocusDao, SeProjectTaskDao, SeWorkTaskDao, SeWorkProjectDao


def getLastWeeklyDate(user_id, department_ids=None):
    last_date = None
    last_weekly = SeWeeklyDao.queryLastWeekly(user_id, department_ids)
    if last_weekly:
        last_date = last_weekly.end_date

    if not last_date:
        today = datetime.today()
        last_saturday = today - timedelta(days=(today.weekday() - 5) % 7)
        last_date = last_saturday.replace(hour=0, minute=0, second=0, microsecond=0)
    return last_date


def getSeEcoNumber(user_ids, last_date):
    eco_tasks = SeEcoTaskDao.getCloseTasksByOwnerIds(user_ids, last_date)
    return len(eco_tasks) if eco_tasks else 0


def getProjectWorkingHours(user_ids, last_date):
    working_hours = 0
    records = SeProjectRecordDao.queryTotalRecordByIds(user_ids, last_date)
    if records:
        for record in records:
            working_hours += record.support_duration/60
    return working_hours


def getEcologicalWorkingHours(user_ids, last_date):
    working_hours = 0
    records = SeEcoRecordDao.queryTotalRecordByIds(user_ids, last_date)
    if records:
        for record in records:
            working_hours += record.support_duration / 60
    return working_hours


def getInternalWorkWorkingHours(user_ids, last_date):
    working_hours = 0
    records = SeWorkRecordDao.queryTotalRecordByIds(user_ids, last_date)
    if records:
        for record in records:
            working_hours += record.support_duration / 60
    return working_hours


def getOwnerProjects(user_id, last_date):
    project_maps = {}
    focus_projects = SeProjectFocusDao.getFocusJoinProjectByFollowerId(user_id)
    if focus_projects:
        for focus_project in focus_projects:
            _, project = focus_project
            project_maps[project.id] = project

    projects = SeProjectProjectDao.getProjectByOwner(user_id, last_date)
    if projects:
        for project in projects:
            if project.id in project_maps.keys():
                continue
            project_maps[project.id] = project

    return project_maps


def getSubWeeklyData(subordinate_ids, last_date, module):
    project_map, index = {}, 1
    sub_weekly_list = SeWeeklyDao.getSubWeekly(subordinate_ids, last_date)
    if sub_weekly_list:
        for sub_weekly in sub_weekly_list:
            data, _ = oss_util.getObject('tech-template', f'SeWeekly_{sub_weekly.id}.data')
            if data:
                weekly_module = json.loads(data).get(module)
                if weekly_module:
                    if weekly_module.get("list"):
                        for weekly in weekly_module.get("list"):
                            if weekly.get("id"):
                                if weekly["id"] in project_map.keys():
                                    continue
                                project_map[weekly["id"]] = weekly
                            else:
                                project_map[index] = weekly
                                index += 1
                    elif weekly_module.get("obj"):
                        project_map["obj"] = weekly_module["obj"]
    return project_map


def getSubWeeklyWorkingStatistics(subordinate_ids, last_date):
    project_map = {}
    sub_weekly_list = SeWeeklyDao.getSubWeekly(subordinate_ids, last_date)
    if sub_weekly_list:
        for sub_weekly in sub_weekly_list:
            data, _ = oss_util.getObject('tech-template', f'SeWeekly_{sub_weekly.id}.data')
            if data:
                workingstatistics = json.loads(data).get("workingstatistics")
                if workingstatistics:
                    user_id = sub_weekly.created_by_id
                    sys_user = SysUserDao.querySysUserById(user_id)
                    team = ""
                    project_hours = 0
                    ecological_hours = 0
                    internalwork_hours = 0
                    total_hours = 0
                    standard_work_hours = 0
                    saturation = 100

                    if len(workingstatistics.get("list")) > 1:
                        for weekly in workingstatistics.get("list"):
                            project_hours += weekly["workingstatistics.project_hours"]
                            ecological_hours += weekly["workingstatistics.ecological_hours"]
                            internalwork_hours += weekly["workingstatistics.internalwork_hours"]
                            total_hours += weekly["workingstatistics.total_hours"]
                            standard_work_hours += weekly["workingstatistics.standard_hours"]

                        team = sys_user.display_name + "团队"
                        if standard_work_hours:
                            saturation = int((total_hours / standard_work_hours) * 100)

                    elif len(workingstatistics.get("list")) == 1:
                        team = sys_user.display_name
                        weekly = workingstatistics.get("list")[0]
                        project_hours = weekly["workingstatistics.project_hours"]
                        ecological_hours = weekly["workingstatistics.ecological_hours"]
                        internalwork_hours = weekly["workingstatistics.internalwork_hours"]
                        total_hours = weekly["workingstatistics.total_hours"]
                        standard_work_hours = weekly["workingstatistics.standard_hours"]
                        saturation = weekly["workingstatistics.working_saturation"]

                    weekly_obj = {
                        "id": user_id,
                        "workingstatistics.team": team,
                        "workingstatistics.project_hours": project_hours,
                        "workingstatistics.ecological_hours": ecological_hours,
                        "workingstatistics.internalwork_hours": internalwork_hours,
                        "workingstatistics.total_hours": total_hours,
                        "workingstatistics.standard_hours": standard_work_hours,
                        "workingstatistics.working_saturation": saturation
                    }
                    project_map[weekly_obj["id"]] = weekly_obj
    return project_map


def getLastWeeklyData(user_id, module):
    project_map, index = {}, 1
    last_weekly = SeWeeklyDao.queryLastWeekly(user_id)
    if last_weekly:
        data, _ = oss_util.getObject('tech-template', f'SeWeekly_{last_weekly.id}.data')
        if data:
            weekly_module = json.loads(data).get(module)
            if weekly_module:
                if weekly_module.get("list"):
                    for weekly in weekly_module.get("list"):
                        if weekly.get("id"):
                            if weekly["id"] in project_map.keys():
                                continue
                            project_map[weekly["id"]] = weekly
                        else:
                            project_map[index] = weekly
                            index += 1
                elif weekly_module.get("obj"):
                    project_map["obj"] = weekly_module["obj"]
    return project_map


def getSummarySaleDepartment(user_id):
    sale_department = ""
    summary = getLastWeeklyData(user_id, "summary")
    if summary:
        sale_department = summary.get("obj").get("summary.sale_department") if summary.get("obj") else ""

    return sale_department


def getSaleUnitByUserId(user_id):
    sys_user = SysUserDao.querySysUserById(user_id)
    if not sys_user:
        return

    crm_user = ESService.queryCrmSysUserByEmail(sys_user.email)
    if crm_user:
        return crm_user
    return


def getProjectsProgressWeek(current_project, last_project_map, last_date):
    current_id = current_project.id
    if current_id not in last_project_map.keys():
        return "新增"
    else:
        modified_date = current_project.last_modified_date.strftime('%Y-%m-%d %H:%M:%S')
        if modified_date > last_date:
            return "更新"
        else:
            return "无变化"


def getProjectsLastStage(project):
    last_stage = ""
    task = SeProjectTaskDao.queryLastTaskByProjectId(project.id)
    if task.support_type_1st:
        last_stage = getSeProjectProjectType(task.support_type_1st)["name"]
    return last_stage


def getProjectsProduct(project):
    products_str = ""
    crm_raw_data = json.loads(project.crm_raw_data)
    quote_products = crm_raw_data.get("quotedetailproductlist")
    for quote_product in quote_products:
        products_str += f"{quote_product['new_product_idname']}({quote_product['skuname']})*" \
                        f"{quote_product['new_num']};<br/>"
    return products_str


def getProjectsBasicInformation(project):
    basic_information = f'客户名称: {project.account_name}<br/>客户需求描述: {project.customer_requirement}<br/>' \
                        f'商机金额: {project.opportunity_value}<br/>销售预测: <br/>' \
                        f'商机分级: {project.opportunity_level}'
    return basic_information


def getProjectsLastStatus(current_project, last_project_map):
    current_id = current_project.id
    if current_id in last_project_map.keys():
        last_project = last_project_map[current_id]
        return last_project["projects.last_task"]
    return ""


def getProjectsLastTask(current_project):
    task_str = ""
    task = SeProjectTaskDao.queryLastTaskByProjectId(current_project.id)
    if task:
        support_type_1st = getSeProjectProjectType(task.support_type_1st)["name"] if task.support_type_1st else ""
        support_type_2st = getSeProjectProjectType(task.support_type_2nd)["name"] if task.support_type_2nd else ""
        support_date = task.created_date.strftime('%Y-%m-%d %H:%M:%S')

        work_hours = 0
        record_list = SeProjectRecordDao.getRecordJoinSysUserByStatus(task.id, "2")
        for record_user in record_list:
            record, user = record_user
            work_hours += record.support_duration / 60
        owner = SysUserDao.querySysUserById(task.owner_id)
        task_str = f'支持项: {support_type_1st}\n支持日期: {support_date}\n经办人: {owner.display_name}\n' \
                   f'支持类型: {support_type_2st}\n工时: {work_hours}\n' \
                   f'任务状态: {project_enums["project_manage"]["task_status"][task.status]}'
    return task_str


def getProjectsNextStep(current_project):
    current_id = current_project.id
    task = SeProjectTaskDao.queryLastTaskByProjectId(current_id)
    record = SeProjectRecordDao.queryLastRecordByStatus(task.id)
    if record:
        record_content = json.loads(record.record_content)
        for content in record_content:
            if content.get("key") == "NextActionPlan":
                return content.get("content")
    return ""


def getProjectsSupportTimes(current_project):
    current_id = current_project.id
    task = SeProjectTaskDao.queryLastTaskByProjectId(current_id)
    record_list = SeProjectRecordDao.getRecordJoinSysUserByStatus(task.id, "2")
    if record_list:
        return len(record_list)
    return 0


def getOwnerEcological(user_id, last_date):
    ecological_maps = {}
    eco_tasks = SeEcoTaskDao.getOwnerTasksByOwnerId(user_id, last_date)
    if eco_tasks:
        for eco_task in eco_tasks:
            if eco_task.id in ecological_maps.keys():
                continue
            ecological_maps[eco_task.id] = eco_task

    return ecological_maps


def getEcologicalPartnerIntroduction(task):
    partner_introduction = f'联系人: {task.partner_contact}\n联系电话: {task.partner_contact_info}\n'
    return partner_introduction


def getEcologicalTaskHours(task):
    work_hours = 0
    record_list = SeEcoRecordDao.queryTotalRecordByTaskId(task.id)
    for record in record_list:
        work_hours += record.support_duration / 60
    return work_hours


def getEcologicalActionRecord(task):
    action_record = ""
    record = SeEcoRecordDao.queryLastRecordByTaskId(task.id)
    if record:
        record_content = json.loads(record.record_content)
        for content in record_content:
            if content.get("type") == "tip":
                continue
            action_record += f'{content.get("name")}: {content.get("content")}\n'

    return action_record


def getOwnerInternalWork(user_id, last_date):
    internalworks_maps = {}
    internal_tasks = SeWorkTaskDao.getOwnerTasksByOwnerId(user_id, last_date)
    if internal_tasks:
        for internal_task in internal_tasks:
            if internal_task.id in internalworks_maps.keys():
                continue
            internalworks_maps[internal_task.id] = internal_task

    return internalworks_maps


def getInternalWorkCustomerInformation(task):
    customer_information = ""
    if task.account_name:
        customer_information += f'客户名称: {task.account_name}\n'
    if task.contact_name:
        customer_information += f'联系人: {task.contact_name}\n'
    if task.contact_info:
        customer_information += f'联系方式: {task.contact_info}\n'
    return customer_information


def getInternalWorkActionRecord(task):
    action_record = ""
    record = SeWorkRecordDao.queryLastRecordByTaskId(task.id)
    if record:
        record_content = json.loads(record.record_content)
        for content in record_content:
            if content.get("type") == "tip":
                continue
            action_record += f'{content.get("name")}: {content.get("content")}\n'

    return action_record


def getInternalWorkTaskHours(task):
    work_hours = 0
    record_list = SeWorkRecordDao.queryTotalRecordByTaskId(task.id)
    for record in record_list:
        work_hours += record.support_duration / 60
    return work_hours


def getInternalWorkNextStep(task):
    record = SeWorkRecordDao.queryLastRecordByTaskId(task.id)
    if record:
        record_content = json.loads(record.record_content)
        for content in record_content:
            if content.get("key") == "SubsequentPlan":
                return content.get("content")
    return ""


def calculateWorkingHours(start_date):
    work_hours = 0
    end_date = datetime.now().strftime('%Y-%m-%d')
    date_range = pd.date_range(start=pd.to_datetime(start_date), end=pd.to_datetime(end_date))
    date_list = date_range.strftime('%Y-%m-%d').tolist()
    for date in date_list[1:]:
        resp = tac_api.getCalendar(date)
        if resp['data']['type'] > 0:
            work_hours += 8
    return work_hours


def getWorkingStatisticsPersonal(user_id, last_date):
    last_date = last_date.split(" ")[0]
    standard_work_hours = calculateWorkingHours(last_date)
    project_hours = getProjectWorkingHours([user_id], last_date)
    ecological_hours = getEcologicalWorkingHours([user_id], last_date)
    internalwork_hours = getInternalWorkWorkingHours([user_id], last_date)
    total_hours = project_hours+ecological_hours+internalwork_hours
    saturation = 100
    if standard_work_hours:
        saturation = int((total_hours/standard_work_hours)*100)

    sys_user = SysUserDao.querySysUserById(user_id)
    result = {
        "id": user_id,
        "workingstatistics.team": sys_user.display_name,
        "workingstatistics.project_hours": project_hours,
        "workingstatistics.ecological_hours": ecological_hours,
        "workingstatistics.internalwork_hours": internalwork_hours,
        "workingstatistics.total_hours": total_hours,
        "workingstatistics.standard_hours": standard_work_hours,
        "workingstatistics.working_saturation": saturation
    }
    return result


def weekSummary(user_id, subordinate_ids, last_date):
    SeWeeklyDao.queryLastWeekly(user_id)
    user_ids = [user_id] + subordinate_ids
    project_hours = getProjectWorkingHours(user_ids, last_date)
    ecological_hours = getEcologicalWorkingHours(user_ids, last_date)
    internalwork_hours = getInternalWorkWorkingHours(user_ids, last_date)
    result = {
        "obj": {
            "summary.sale_department": getSummarySaleDepartment(user_id),
            "summary.project_number": 0,
            "summary.update_project_number": 0,
            "summary.add_project_number": 0,
            "summary.winning_project": 0,
            "summary.lost_project_number": 0,
            "summary.lost_project_info": "",
            "summary.case_fr_number": 0,
            "summary.ecological_number": getSeEcoNumber(user_ids, last_date),
            "summary.total_working_hours": project_hours+ecological_hours+internalwork_hours,
            "summary.saturation": 0
        }
    }
    return result


def weekProjects(user_id, subordinate_ids, last_date):
    projects, sub_project_map = {"list": []}, {}
    if subordinate_ids:
        sub_project_map = getSubWeeklyData(subordinate_ids, last_date, "projects")
    owner_project_map = getOwnerProjects(user_id, last_date)
    last_project_map = getLastWeeklyData(user_id, "projects")
    for _id, project in owner_project_map.items():
        if _id in sub_project_map.keys():
            continue

        sale = getSaleUnitByUserId(project.sale_by_id)
        owner_user = SysUserDao.querySysUserById(project.owner_id)
        project_obj = {
            "id": _id,
            "projects.project_number": project.project_number,
            "projects.area": sale["salesunit"] if sale else "",
            "projects.opportunity_name": project.opportunity_name,
            "projects.project_name": project.subject,
            "projects.basic_information": getProjectsBasicInformation(project),
            "projects.progress_week": getProjectsProgressWeek(project, last_project_map, last_date),
            "projects.procurement_stage": project.business_stage if project.business_stage else "",
            "projects.project_stage": getProjectsLastStage(project),
            "projects.competitors": project.competitors if project.competitors else "",
            "projects.product_information": getProjectsProduct(project),
            "projects.sale": sale["username"] if sale else "",
            "projects.owner": owner_user.display_name if owner_user else "",
            "projects.itai_project": project.is_itai_project,
            "projects.deploy_core": project.is_big_project_support,
            "projects.previous_stage": getProjectsLastStatus(project, last_project_map),
            "projects.last_task": getProjectsLastTask(project),
            "projects.next_step": getProjectsNextStep(project),
            "projects.associate": "",
            "projects.support_times": getProjectsSupportTimes(project)
        }
        projects["list"].append(project_obj)

    for _id, project_obj in sub_project_map.items():
        projects["list"].append(project_obj)

    return projects


def weekEcological(user_id, subordinate_ids, last_date):
    ecological, sub_ecological_map = {"list": []}, {}
    if subordinate_ids:
        sub_ecological_map = getSubWeeklyData(subordinate_ids, last_date, "ecological")
    owner_ecological_map = getOwnerEcological(user_id, last_date)
    for _id, task in owner_ecological_map.items():
        if _id in sub_ecological_map.keys():
            continue

        channel_manager = SysUserDao.querySysUserById(task.channel_manager_id) if task.channel_manager_id else ""
        owner_user = SysUserDao.querySysUserById(task.owner_id)
        support_type = getSeEcoTaskType(task.support_type_1st)
        task_type = getSeEcoTaskType(task.support_type_2nd)
        ecological_obj = {
            "id": _id,
            "ecological.task_number": task.task_number,
            "ecological.partner_name": task.partner_name,
            "ecological.partner_introduction": getEcologicalPartnerIntroduction(task),
            "ecological.channel_manager": channel_manager.display_name if channel_manager else channel_manager,
            "ecological.ecological.support_type": support_type["name"] if support_type else "",
            "ecological.task_owner": owner_user.display_name if owner_user else "",
            "ecological.task_type": task_type["name"] if task_type else "",
            "ecological.working_hours": getEcologicalTaskHours(task),
            "ecological.support_method": eco_enums["task"]["status"][task.status],
            "ecological.action_records": getEcologicalActionRecord(task),
            "ecological.other_instructions": "",
        }
        ecological["list"].append(ecological_obj)

    for _id, ecological_obj in sub_ecological_map.items():
        ecological["list"].append(ecological_obj)

    return ecological


def weekInternalWork(user_id, subordinate_ids, last_date):
    internalwork, sub_internalwork_map = {"list": []}, {}
    if subordinate_ids:
        sub_internalwork_map = getSubWeeklyData(subordinate_ids, last_date, "internalwork")
    owner_internalwork_map = getOwnerInternalWork(user_id, last_date)
    for _id, task in owner_internalwork_map.items():
        if _id in sub_internalwork_map.keys():
            continue

        create_user = SysUserDao.querySysUserById(task.created_by_id)
        owner_user = SysUserDao.querySysUserById(task.owner_id)
        internalwork_obj = {
            "id": _id,
            "internalwork.task_number": task.task_number,
            "internalwork.task_subject": task.subject,
            "internalwork.task_create": create_user.display_name if create_user else "",
            "internalwork.task_onwer": owner_user.display_name if owner_user else "",
            "internalwork.support_mode": work_enums["internal_work"]["support_mode"][task.support_mode],
            "internalwork.customer_information": getInternalWorkCustomerInformation(task),
            "internalwork.working_hours": getInternalWorkTaskHours(task),
            "internalwork.action_records": getInternalWorkActionRecord(task),
            "internalwork.next_step": getInternalWorkNextStep(task),
            "internalwork.remark": ""
        }
        internalwork["list"].append(internalwork_obj)

    for _id, internalwork_obj in sub_internalwork_map.items():
        internalwork["list"].append(internalwork_obj)

    return internalwork


def weekNeedProblem(user_id, subordinate_ids, last_date):
    needproblem, sub_needproblem_map = {"list": []}, {}
    if subordinate_ids:
        sub_needproblem_map = getSubWeeklyData(subordinate_ids, last_date, "summationproblem")

    for _id, ecological_obj in sub_needproblem_map.items():
        needproblem["list"].append(ecological_obj)

    return needproblem


def weekWorkPlan(user_id, subordinate_ids, last_date):
    workplan, sub_workplan_map = {"list": []}, {}
    if subordinate_ids:
        sub_workplan_map = getSubWeeklyData(subordinate_ids, last_date, "workplan")

    for _id, ecological_obj in sub_workplan_map.items():
        workplan["list"].append(ecological_obj)

    return workplan


def weekWorkingStatistics(user_id, subordinate_ids, last_date):
    workingstatistics, sub_workingstatistics_map = {"list": []}, {}
    if subordinate_ids:
        sub_workingstatistics_map = getSubWeeklyWorkingStatistics(subordinate_ids, last_date)

    owner_statistics_obj = getWorkingStatisticsPersonal(user_id, last_date)
    workingstatistics["list"].append(owner_statistics_obj)
    for _id, owner_statistics_obj in sub_workingstatistics_map.items():
        workingstatistics["list"].append(owner_statistics_obj)
    return workingstatistics


def queryWeeklyProject(number):
    projects = {"list": []}
    project = SeProjectProjectDao.queryProjectByNumber(number)
    if project:
        sale = getSaleUnitByUserId(project.sale_by_id)
        owner_user = SysUserDao.querySysUserById(project.owner_id)
        project_obj = {
            "id": project.id,
            "projects.project_number": project.project_number,
            "projects.area": sale["salesunit"] if sale else "",
            "projects.opportunity_name": project.opportunity_name,
            "projects.project_name": project.subject,
            "projects.basic_information": getProjectsBasicInformation(project),
            "projects.progress_week": "",
            "projects.procurement_stage": project.business_stage,
            "projects.project_stage": project.project_phase,
            "projects.competitors": project.competitors if project.competitors else "",
            "projects.product_information": getProjectsProduct(project),
            "projects.sale": sale["username"] if sale else "",
            "projects.owner": owner_user.display_name if owner_user else "",
            "projects.itai_project": project.is_itai_project,
            "projects.deploy_core": project.is_big_project_support,
            "projects.previous_stage": "",
            "projects.last_task": getProjectsLastTask(project),
            "projects.next_step": getProjectsNextStep(project),
            "projects.associate": "",
            "projects.support_times": getProjectsSupportTimes(project)
        }
        projects["list"].append(project_obj)

    return projects


def queryWeeklyEcological(number):
    ecological = {"list": []}
    task = SeEcoTaskDao.queryTaskByNumber(number)
    if task:
        channel_manager = SysUserDao.querySysUserById(task.channel_manager_id) if task.channel_manager_id else ""
        owner_user = SysUserDao.querySysUserById(task.owner_id)
        support_type = getSeEcoTaskType(task.support_type_1st)
        task_type = getSeEcoTaskType(task.support_type_2nd)
        ecological_obj = {
            "id": task.id,
            "ecological.task_number": task.task_number,
            "ecological.partner_name": task.partner_name,
            "ecological.partner_introduction": getEcologicalPartnerIntroduction(task),
            "ecological.channel_manager": channel_manager.display_name if channel_manager else channel_manager,
            "ecological.ecological.support_type": support_type["name"] if support_type else "",
            "ecological.task_owner": owner_user.display_name if owner_user else "",
            "ecological.task_type": task_type["name"] if task_type else "",
            "ecological.working_hours": getEcologicalTaskHours(task),
            "ecological.support_method": eco_enums["task"]["status"][task.status],
            "ecological.action_records": getEcologicalActionRecord(task),
            "ecological.training_feedback": "",
        }
        ecological["list"].append(ecological_obj)
    return ecological


def queryWeeklyInternalWork(number):
    internalwork = {"list": []}
    project = SeWorkProjectDao.queryProjectByNumber(number)
    if project:
        task = SeWorkTaskDao.queryLastTaskByProjectId(project.id)
        if task:
            create_user = SysUserDao.querySysUserById(project.created_by_id)
            owner_user = SysUserDao.querySysUserById(project.owner_id)
            internalwork_obj = {
                "id": task.id,
                "internalwork.task_number": task.task_number,
                "internalwork.task_subject": task.subject,
                "internalwork.task_create": create_user.display_name if create_user else "",
                "internalwork.task_onwer": owner_user.display_name if owner_user else "",
                "internalwork.support_mode": work_enums["internal_work"]["support_mode"][task.support_mode],
                "internalwork.customer_information": getInternalWorkCustomerInformation(task),
                "internalwork.working_hours": getInternalWorkTaskHours(task),
                "internalwork.action_records": getInternalWorkActionRecord(task),
                "internalwork.next_step": getInternalWorkNextStep(task),
                "internalwork.remark": ""
            }
            internalwork["list"].append(internalwork_obj)

    return internalwork