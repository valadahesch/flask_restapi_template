## todo 

动态字段类型 可能有一个特殊，附件

## 注意：

责任人和任务列表的关系，子任务责任人和父任务责任人，子任务责任人多个，主任务责任人一个

## 权限

```shell

"p_sework_eco_task_add": "sework.eco.task:add",   # 创建任务权限
"p_sework_eco_all": "sework.eco:all",   # 任务其他权限


菜单目录：业务平台-售前支持-生态渠道  ，点击生态渠道菜单之后，打开生态渠道任务列表页面
任务列表页面路由：business_platform/presales_support/eco_partner
任务详情页面路由：business_platform/presales_support/eco_partner/task_detail/:task_id

日志审批权限key: record_approval, create_sub_task

```

## 任务列表

公共接口，（合作伙伴列表）客户名称 CRM 客户查询接口  
url: 'internal/crm/customer'

创建任务 获取合作伙伴
url: `/presales/eco_partner/task`  
method: `post`
params：

| 字段名               | 类型 | 是否必须 | 描述                                |
| -------------------- | ---- | -------- | ----------------------------------- |
| subject              | str  | 是       | 任务主题                            |
| owner_id             | str  | 是       | 责任人                              |
| partner_id           | str  | 是       | 合作伙伴 ID                         |
| partner_name         | str  | 是       | 合作伙伴名称                        |
| partner_status       | str  | 否       | 合作伙伴状态                        |
| partner_industry     | str  | 否       | 合作伙伴行业方向                    |
| partner_contact      | str  | 否       | 合作伙伴联系人                      |
| partner_contact_info | str  | 否       | 合作伙伴联系方式                    |
| support_mode         | str  | 是       | 支持方式现场(On-site)、远程(Remote) |
| support_type_1st     | str  | 否       | 支持类型                            |
| support_type_2nd     | str  | 否       | 支持项                              |
| start_date      | str  | 是       | 开始时间                            |
| end_date        | str  | 是       | 结束时间                            |
| duration             | int  | 是       | 预计时长，步长为0.5小时，转化为分钟后传入                           |

创建子任务（父任务有合作伙伴，子任务的合作伙伴不能修改,继承合作伙伴和支持类型）
url: `/presales/eco_partner/task/:task_id/sub_task`  
method: `post`
params：

| 字段名           | 类型      | 是否必须 | 描述                                |
| ---------------- | --------- | -------- | ----------------------------------- |
| subject          | str       | 是       | 任务主题                            |
| owner_ids        | list[str] | 是       | 责任人列表                          |
| support_mode     | str       | 是       | 支持方式现场(On-site)、远程(Remote) |
| partner_contact          | str       | 是       | 联系人                            |
| partner_contact_info          | str       | 是       | 联系方式                            |
| start_time       | str       | 是       | 开始时间                            |
| end_date       | str       | 是       | 开始时间                            |
| duration | int       | 是       | 预计时长，步长为0.5小时，转化为分钟后传入                            |

删除任务(删除未进行状态的任务)
url: `/presales/eco_partner/task/:task_id`  
method: `delete`

任务归档
url: `/presales/eco_partner/task/:task_id/archive`  
method: `put`
params:

| 字段名                 | 类型 | 是否必须 | 描述                               |
| ---------------------- | ---- | -------- | ---------------------------------- |
| task_result            | str  | 是       | 完成(Complete)、未完成(Incomplete) |
| task_incomplete_reason | str  | 否       | 备注、未完成需要备注原因           |

任务详情（包含合作伙伴信息）
url: `/presales/eco_partner/task/:task_id`  
method: `get`  
resp:

```json
{
	"code": 0,
	"data": {
		"id": "",
		"task_number": "",
		"parent_id": "",
		"subject": "",
		"created_date": "",
		"owner_id": "",
		"owner_name": "",
		"status": "",
		"partner_id": "",
		"partner_name": "",
		"partner_contact": "",
		"partner_contact_info": "",
		"support_type_1st": {
			"key": "ChannelSupportInternal",
			"name": "渠道支持（内部）",
			"parent_key": ""
		},
		"support_type_2nd": {
			"key": "ChannelTraining",
			"name": "渠道培训",
			"parent_key": "ChannelSupportInternal"
		},
		"task_start_time": "",
		"task_end_date": "",
		"duration": 0,
		"task_result": "",
		"task_incomplete_reason": "",
		"created_by_id": "",
		"created_by_name": "",
		"last_modified_by_id": "",
		"last_modified_by_name": "",
		"last_modified_date": "",
		"participants": [{ "id": "", "name": "" }]
	},
	"message": "successful"
}
```

所有任务的合作伙伴列表
url: `/presales/eco_partner/tasks/partners`  
method: `get`  
params:

| 字段名       | 类型 | 是否必须 | 描述               |
| ------------ | ---- | -------- | ------------------ |
| partner_name | str  | 否       | 伙伴名称，模糊搜索 |
| page         | int  | 是       | 分页               |
| size         | int  | 是       | 分页               |

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "",
				"partner_name": "",
				"first_support_date": "",
				"last_support_date": "",
				"handing_number": 1,
				"all_number": 10
			}
		],
		"page": 1,
		"size": 10
	},
	"message": "successful"
}
```

根据合作伙伴查询下面的任务列表
特殊：分页 size 是主任务数量，还会查主任务下所有子任务。前端显示数量的时候注意文字
url: `/presales/eco_partner/tasks`  
method: `get`  
params:

| 字段名     | 类型 | 是否必须 | 描述        |
| ---------- | ---- | -------- | ----------- |
| partner_id | str  | 否       | 合作伙伴 id |
| query | str | 否 | 关键字模糊查询 |
| date_range | list[str, str] | 否 | 日期范围 |
| order_column     | str                                                          | 否       | 排序列                      |
| order_direct     | str                                                          | 否       | 排序方向                      |
| owner_id | list[str] | 否 | 负责人 |
| status | list[int] | 否 | 未开始(1)，进行中(2)，已结束(3)，已删除(4) |
| participants | list[str] | 否 | 参与人 |  
| page | int | 否 | 当前页 |  
| size | int | 否 | 每页数量 |  


resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "",
				"task_number": "",
				"parent_id": "",
				"subject": "",
				"created_date": "",
				"owner_id": "",
				"owner_name": "",
				"status": "",
				"support_type_1st": {
					"key": "ChannelSupportInternal",
					"name": "渠道支持（内部）",
					"parent_key": ""
				},
				"support_type_2nd": {
					"key": "ChannelTraining",
					"name": "渠道培训",
					"parent_key": "ChannelSupportInternal"
				},
				"created_by_id": "",
				"created_by_name": "",
				"last_modified_by_id": "",
				"last_modified_by_name": "",
				"last_modified_date": "",
				"participants": [{ "id": "", "name": "" }]
			}
		],
		"page": 1,
		"size": 10 //主任务的size
	},
	"message": "successful"
}
```

任务的获取待审批日志列表，所有人都有这个 tab, 查任务责任人
当前用户==任务责任人 and 待审批
url: `/presales/eco_partner/record/pending_approval`  
method: `get`
params：

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "",
				"support_start_date": "",
				"support_end_date": "",
				"support_duration": "",
				"status": "Pending",
				"created_by_id": "",
				"created_by_name": "",
				"last_modified_by_id": "",
				"last_modified_by_name": "",
				"last_modified_date": "",
				"task_id": "",
				"task_number": "",
				"task_subject": "",
				"record_content": []
			}
		]
	},
	"message": "successful"
}
```

任务支持项、支持方式列表，结构体和内部事务一致
todo 动态字段
url: `/presales/eco_partner/task/support_type`  
method: `get`
params：

resp:

```json
{
	"code": 0,
	"data": {
		"list": []
	},
	"message": "successful"
}
```

任务负责人列表查询
url: `/presales/task/all/owner/list`  
method: `get`   
params:     


resp:  
```json
{
  "code": 0,
  "data": {
    "list": [{
     "id": "",
     "display_name": ""
    }]
  },
  "message": "successful"
}
```

任务参与人列表查询
url: `/presales/task/all/participants/list`  
method: `get`   
params:     


resp:  
```json
{
  "code": 0,
  "data": {
    "list": [{
     "id": "",
     "display_name": ""
    }]
  },
  "message": "successful"
}
```

### 操作权限查询

任务详情，操作权限， page_title(task_detail)
url: `/presales/eco_partner/permission/:page_title`  
method: `get`  
params:

| 字段名  | 类型 | 是否必须 | 描述                      |
| ------- | ---- | -------- | ------------------------- |
| task_id | str  | 否       | 任务 ID，当为 task_detail |

resp:

```json
{
	"code": 0,
	"data": {
		"list": ["create_record", "task_archive", "create_sub_task"]
	},
	"message": "successful"
}
```

## 日志列表

创建日志
url: `/presales/eco_partner/task/:task_id/record`  
method: `post`
params：

| 字段名             | 类型                | 是否必须 | 描述                                                            |
| ------------------ | ------------------- | -------- | --------------------------------------------------------------- |
| support_start_date | str                 | 是       | 支持开始时间                                                    |
| support_end_date   | str                 | 是       | 支持结束时间                                                    |
| support_duration   | int                 | 是      | 所用工时、只能为 0.5 的整数倍(传入参数为 30 的倍数，按分钟存储) |
| record_content     | list[dict]          | 是       | 支持项的详细记录内容                                            |
| attachments        | list[attachment_id] | 是       | 附件 ID 列表                                                    |
| status             | str                 | 是       | 草稿（Draft）、发布（Publish）、待审批（Pending）                               |

resp:

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

编辑日志(编辑草稿)
url: `/presales/eco_partner/record/:record_id`  
method: `put`
params：

| 字段名             | 类型                | 是否必须 | 描述                                                            |
| ------------------ | ------------------- | -------- | --------------------------------------------------------------- |
| support_start_date | str                 | 是       | 支持开始时间                                                    |
| support_end_date   | str                 | 是       | 支持结束时间                                                    |
| support_duration   | str                 | 否       | 所用工时、只能为 0.5 的整数倍(传入参数为 30 的倍数，按分钟存储) |
| record_content     | list[dict]          | 是       | 支持项的详细记录内容                                            |
| attachments        | list[attachment_id] | 是       | 附件 ID 列表                                                    |
| status             | str                 | 是       | 草稿（Draft）、发布（Publish） 、审批（Pending）                          |

resp:

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

删除日志（草稿和待审批下）
url: `/presales/eco_partner/record/:record_id`  
method: `delete`

查看任务日志列表
url: `/presales/eco_partner/task/:task_id/record/list`  
method: `get`  
params：

| 字段名             | 类型                | 是否必须 | 描述                                                            |
| ------------------ | ------------------- | -------- | --------------------------------------------------------------- |
| status             | str                 | 是       | 草稿（Draft）、发布（Publish） 、审批（Pending）                          |

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "",
				"support_start_date": "",
				"support_end_date": "",
				"support_duration": "",
				"created_by_id": "",
				"created_by_name": "",
				"created_date": "",
				"published_date": "",
				"status": "",
				"unapproval_reason": "不通过原因",
				"task_id": "",
				"task_number": "",
				"task_subject": "",
				"record_content": [
					{
						"key": "TrainingTargets",
						"name": "培训对象",
						"required": true,
						"type": "input",
						"content": "",
						"index": 1
					}
				],
				"attachments": [
					{ "id": "", "filename": "", "file_size": 0, "file_type": "" }
				],
				"permission": ["delete_record", "update_record"]
			}
		]
	},
	"message": "successful"
}
```

日志审批，审批通过设置为发布状态，不通过设置为草稿
url: `/presales/eco_partner/record/:record_id/approval`  
method: `put`
params：

| 字段名            | 类型 | 是否必须 | 描述             |
| ----------------- | ---- | -------- | ---------------- |
| approval          | int  | 是       | 1-通过、2-不通过 |
| unapproval_reason | str  | 否       | 不通过时候才有   |

任务责任人在日志列表，有个“审批中”列表，只看
某个任务下，创建人==自己 and 状态审批中
url: `/presales/eco_partner/task/:task_id/record/pending_approval`  
method: `get`
params：

| page | int | 是 | 分页 |
| size | int | 是 | 分页 |

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "",
				"support_start_date": "",
				"support_end_date": "",
				"support_duration": "",
				"created_by_id": "",
				"created_by_name": "",
				"created_date": "",
				"published_date": "",
				"status": "",
				"task_id": "",
				"task_number": "",
				"task_subject": "",
				"record_content": [
					{
						"key": "TrainingTargets",
						"name": "培训对象",
						"required": true,
						"type": "input",
						"content": "",
						"index": 1
					}
				],
				"attachments": [
					{ "id": "", "filename": "", "file_size": 0, "file_type": "" }
				],
				"permission": ["delete_record", "update_record", "record_approval"]
			}
		],
		"size": 1,
		"page": 1,
		"total": 1
	},
	"message": "successful"
}
```
