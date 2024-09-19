from app.controllers import ESService
from app.enums.permission_enum import p_list
from app.controllers.dao import SeProjectApprovalDao, SeProjectTaskDao, DataScopeDao, SeWorkApprovalDao, SeEcoApprovalDao
from app.controllers.dao.dic_ticket_dao import DICTicketsDao, DICTicketTaskDao


def SeProjectMinePendingRecord(db_app, user_id):
    with db_app.app_context():
        approval_rtpc_list = SeProjectApprovalDao.getApprovalRecordByUserId(user_id)

    mine_pending_record = {
        '_name': "售前支持-项目管理-我的待办.待批日志",
        'count': len(approval_rtpc_list)
    }

    result = {'business.presales-manage.mine_pending_record': mine_pending_record}
    return result


def SeProjectMinePendingTask(db_app, user_id):
    count = 0
    with db_app.app_context():
        approval_list = SeProjectApprovalDao.getApprovalTaskByUserId(user_id)
        if approval_list:
            task_ids = [approval.task_id for approval in approval_list]
            task_pco_list = SeProjectTaskDao.getTasksJoinSysUserByIds(task_ids)
            count = len(task_pco_list)

    mine_pending_task = {
        '_name': "售前支持-项目管理-我的待办.待批归档任务",
        'count': count
    }

    result = {'business.presales-manage.mine_pending_task': mine_pending_task}
    return result


def SeProjectTaskMinePendingTask(db_app, user_id):
    with db_app.app_context():
        task_list, total = SeProjectTaskDao.getTaskProjectJoinSysUserByUserId(user_id,1,10,[1,4,5],'','','','',[],[],[])

    mine_task_list = {
        '_name': "售前支持-项目管理-任务列表-我负责的",
        'count': total
    }

    result = {'business.presales-manage.mine_task_list': mine_task_list}
    return result

def SeProjectMineEnableProject(db_app, user_id):
    with db_app.app_context():
        user_ids = DataScopeDao.getSysUserByRank(user_id, p_list['p_se_project_manage_list'])
        if not user_ids:
            return {}

    params = {
        "page": 1,
        "size": 500,
        'user_id': user_id,
        "classification": "mine",
        "status": [1]
    }
    total, es_res = ESService.querySeProjectByFilter(user_ids, **params)
    mine_enable_project = {
        '_name': "售前支持-项目管理-我的待办.待确认项目",
        'count': total
    }

    result = {'business.presales-manage.mine_enable_project': mine_enable_project}
    return result


def SeProjectMineEnableTask(db_app, user_id):
    with db_app.app_context():
        task_pco_list = SeProjectTaskDao.getPreEnableTaskJoinSysUserByCreateId(user_id)

    mine_enable_task = {
        '_name': "售前支持-项目管理-我的待办.待确认任务",
        'count': len(task_pco_list)
    }

    result = {'business.presales-manage.mine_enable_task': mine_enable_task}
    return result


def SeWorkPendingRecord(db_app, user_id):
    with db_app.app_context():
        approval_rtc_list = SeWorkApprovalDao.getApprovalRecordByUserId(user_id)

    pending_record = {
        '_name': "售前支持-内部事务-待审批日志",
        'count': len(approval_rtc_list)
    }

    result = {'business.presales-internal.pending_record': pending_record}
    return result


def SeEcoPendingRecord(db_app, user_id):
    with db_app.app_context():
        approval_rtc_list = SeEcoApprovalDao.getApprovalRecordByUserId(user_id)

    pending_record = {
        '_name': "售前支持-生态渠道-待审批日志",
        'count': len(approval_rtc_list)
    }

    result = {'business.presales-eco-partner.pending_record': pending_record}
    return result


def DicManageMineTicket(db_app, user_id):
    with db_app.app_context():
        draft_count = DICTicketsDao.queryDraftTickets(user_id, 'Draft', 1, 1000, [], [], [], '')
        commit_count = DICTicketsDao.queryTickets('mine', ['Commit'], 1, 1000, [], [], user_id, True, [], '')
        cancel_count = DICTicketsDao.queryTickets('mine', ['Cancel'], 1, 1000, [], [], user_id, True, [], '')
        accepting_count = DICTicketsDao.queryTickets('mine', ['Accepting'], 1, 1000, [], [], user_id, True, [], '')
        doing_count = DICTicketsDao.queryTickets('mine', ['Doing'], 1, 1000, [], [], user_id, True, [], '')
        delivery_count = DICTicketsDao.queryTickets('mine', ['Delivery'], 1, 1000, [], [], user_id, True, [], '')
        complete_count = DICTicketsDao.queryTickets('mine', ['Complete'], 1, 1000, [], [], user_id, True, [], '')

    mine_ticket = {
        '_name': "数字化支持-工单管理-我的工单",
        'draft_ticket': draft_count.get('total'),
        'commit_count': commit_count.get('total'),
        'cancel_count': cancel_count.get('total'),
        'accepting_count': accepting_count.get('total'),
        'doing_count': doing_count.get('total'),
        'delivery_count': delivery_count.get('total'),
        'complete_count': complete_count.get('total')
    }
    result = {'dic.ticket_manage_list.mine_ticket': mine_ticket}
    return result


def DicManageMineTask(db_app, user_id):
    with db_app.app_context():
        commit_count = DICTicketTaskDao.getTaskByUserId(user_id, 1, 1000, ['Commit'], '', '')
        cancel_count = DICTicketTaskDao.getTaskByUserId(user_id, 1, 1000, ['Cancel'], '', '')
        accepting_count = DICTicketTaskDao.getTaskByUserId(user_id, 1, 1000, ['Accepting'], '', '')
        doing_count = DICTicketTaskDao.getTaskByUserId(user_id, 1, 1000, ['Doing'], '', '')
        delivery_count = DICTicketTaskDao.getTaskByUserId(user_id, 1, 1000, ['Delivery'], '', '')
        complete_count = DICTicketTaskDao.getTaskByUserId(user_id, 1, 1000, ['Complete'], '', '')

    mine_task = {
        '_name': "数字化支持-工单管理-我的任务",
        'commit_count': commit_count.get('total'),
        'cancel_count': cancel_count.get('total'),
        'accepting_count': accepting_count.get('total'),
        'doing_count': doing_count.get('total'),
        'delivery_count': delivery_count.get('total'),
        'complete_count': complete_count.get('total')
    }
    result = {'dic.ticket_manage_list.mine_task': mine_task}
    return result


def DicMineTicket(db_app, user_id):
    with db_app.app_context():
        draft_count = DICTicketsDao.queryDraftTickets(user_id, 'Draft', 1, 1000, [], [], [], '')
        commit_count = DICTicketsDao.queryTickets('mine', ['Commit'], 1, 1000, [], [], user_id, False, [], '')
        cancel_count = DICTicketsDao.queryTickets('mine', ['Cancel'], 1, 1000, [], [], user_id, False, [], '')
        accepting_count = DICTicketsDao.queryTickets('mine', ['Accepting'], 1, 1000, [], [], user_id, False, [], '')
        doing_count = DICTicketsDao.queryTickets('mine', ['Doing'], 1, 1000, [], [], user_id, False, [], '')
        delivery_count = DICTicketsDao.queryTickets('mine', ['Delivery'], 1, 1000, [], [], user_id, False, [], '')
        complete_count = DICTicketsDao.queryTickets('mine', ['Complete'], 1, 1000, [], [], user_id, False, [], '')

    mine_ticket = {
        '_name': "数字化支持-工单管理-我的工单",
        'draft_ticket': draft_count.get('total'),
        'commit_count': commit_count.get('total'),
        'cancel_count': cancel_count.get('total'),
        'accepting_count': accepting_count.get('total'),
        'doing_count': doing_count.get('total'),
        'delivery_count': delivery_count.get('total'),
        'complete_count': complete_count.get('total')
    }
    result = {'dic.ticket_list.mine_ticket': mine_ticket}
    return result
