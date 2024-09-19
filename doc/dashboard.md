#### 首页仪表
##### func_key = "ps"|"se"|"dic"|"ticket"
##### ps为售前支持这个目录的权限, dic目前是业务平台-数字化支持-工单管理，ticket是数字化工单-工单列表
url: '/api/dashboard/todo_statistics/:func_key'  
method: get  

resp:  
```text
{
  "code": 0,
  "data": {
    "ps": {
        "business.presales-manage.mine_pending_record": {
            _name:"售前支持-项目管理-我的待办.待批日志",
            _description:"有权限就返回，没权限不返回，这个权限是后端控制的",
            count:10
        },
        "business.presales-manage.mine_pending_task": {
            _name:"售前支持-项目管理-我的待办.待批归档任务",
            _description:"有权限就返回，没权限不返回，这个权限是后端控制的",
            count:10
        },
        "business.presales-manage.mine_task_list": {
            _name:"售前支持-项目管理-任务列表-我负责的",
            _permission: p_list.p_se_project_manage_list,
            count:10
        },
        "business.presales-manage.mine_enable_project": {
            _name:"售前支持-项目管理-我的待办.待确认项目",
            _permission: p_list.p_se_project_manage_list,
            count:10
        },
        "business.presales-manage.mine_enable_task": {
            _name:"售前支持-项目管理-我的待办.待确认任务",
            _permission: p_list.p_se_project_manage_list,
            count:10
        },
        "business.presales-internal.pending_record": {
            _name:"售前支持-内部事务-待审批日志",
            _permission: p_list.p_sework_internal_all,
            count:10
        },
        "business.presales-eco-partner.pending_record": {
            _name:"售前支持-生态渠道-待审批日志",
            _permission: p_list.p_sework_eco_all,
            count:10
        }
    },
    "dic": {
        "dic.ticket_manage_list.mine_ticket": {
            _name:"数字化支持-工单管理-我的工单",
            _permission: p_list.p_dic_ticket_manage_all,
            draft_count: "草稿",
            commit_count: "已提交",
            cancel_count: "已取消",
            accepting_count: "已受理",
            doing_count: "处理中",
            delivery_count: "交付中",
            complete_count: "已完成",
        },
        "dic.ticket_manage_list.mine_task": {
            _name:"数字化支持-工单管理-我的任务",
            _permission: p_list.p_dic_ticket_manage_all,
            _description:"这个任务数量是工单的数量",
            commit_count: "已提交",
            cancel_count: "已取消",
            accepting_count: "已受理",
            doing_count: "处理中",
            delivery_count: "交付中",
            complete_count: "已完成",
        }
    },
    "ticket": {
        "dic.ticket_list.mine_ticket": {
            _name:"数字化工单-工单列表-我的工单",
            _permission: p_list.p_dic_ticket_all,
            draft_count: "草稿",
            commit_count: "已提交",
            cancel_count: "已取消",
            accepting_count: "已受理",
            doing_count: "处理中",
            delivery_count: "交付中",
            complete_count: "已完成",
        }
    }
  },
  "message": "successful"
}
```