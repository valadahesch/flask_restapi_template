# CE 事务管理

内部事务现阶段完成的功能：  
1、 SE 可以搜索、筛选项目，系统显示所有相关项目列表。

    a)	“SE”包含SE工程师、SEM、SED等所有售前支持中心员工
    b)	“搜索”是指针对项目主题、编号、任务目标以及任务日志中的文字性内容进行全文搜索
    c)	“筛选”是指按照项目的状态、负责人及参与人进行筛选
    d)	“所有”并发指系统内所有的项目，而是指当前用户权限范围内的所有项目。用户的权限范围是指：用户自己或者用户的下属（包括下属的下属，以此类推）作为负责+参与的项目
    e)	项目列表展示的字段包括：项目编号、主题、创建日期、负责人、状态、参与人(多人)

2、 SE 分派员（某些特定用户）点击按钮弹出新建项目的窗口，填写相关字段后，系统将项目分配给对应的用户（负责人）

    a)	新建项目窗口需要填写的字段有：主题（必填，项目的简要描述）、项目类型（必填，下拉选择，可选值待定）、客户名称（非必填，基础数据来源于CRM，用户输入关键字后系统进行搜索并展示相关客户，用户选择对应的客户）、客户联系人（非必填，文本框输入）、客户联系方式（非必填，文本框输入）、负责人（必填，只能选择自己和下属）
    b)	新建项目成功后，系统自动向负责人发送邮件（通知模板待定）。此时项目进入待开始的状态（后续创建第一个任务后，项目进入进行中状态）

3、 用户点击项目列中的项目，进入项目详情页面（新页面）。

    a)	项目详情页面包括：项目概要、项目的任务清单、项目的参与人清单以及常用的项目操作按钮。包括以下按钮：创建主任务（仅项目负责人有权限）、项目归档（仅项目负责人有权限，并且所有相关任务均已归档）
    b)	项目概要显示项目的基本信息，包括：项目编号、项目主题、负责人、分配人、创建时间等等字段
    c)	项目编号、项目主题、负责人、分配人、创建时间等等字段
    d)
    e)	项目的任务清单显示所有相关的任务（表格形式），包括：编号、主题、责任人、支持方式(现场/远程)、状态(进行中、已结束和已删除)、创建时间和操作等列
    f)	“操作”列包括：查看、创建子任务(仅主任务)、归档(结束任务，后续无法修改，主任务必须子任务全部结束后才能进行归档。目标未完成的任务需要备注原因)、删除（只有主任务的负责人有权限对主任务及其子任务删除，仅标记为删除，不会物理删除）以及填写日志（弹出填写日志窗口）等按钮
    g)	主任务的负责人显示所有主任务和子任务(默认隐藏，点击主任务+ 图标后，展开后显示)
    h)	项目的参与人（即各个子任务的负责人）只显示其负责的子任务对应的主任务列表（点击主任务+ 图标后，展开后显示其负责子任务列表，主任务的其他子任务不显示），不相关的主任务也不显示

4、 用户点击项目详情任务列表中的任务“查看”按钮，进入任务详情页面（新页面），一般不需要进入此页面

    a)	任务详情页面包括任务概要、任务的日志清单以及常用的任务操作按钮，包括以下按钮：创建子任务 (仅主任务)、归档(结束任务，后续无法修改，主任务必须子任务全部结束后才能进行归档。目标未完成的任务需要备注原因)、删除（只有主任务的负责人有权限对主任务及其子任务删除，仅标记为删除，不会物理删除）以及填写日志（弹出填写日志窗口）等按钮
    b)	任务的日志清单按照时间轴的方式进行显示，时间轴默认只显示支持开始时间、结束时间、所用工时、附件数量及动态字段汇总后的简要（最多5行，防止内容过多），点击可以展开汇总内容的详情（可以缩回）。草稿状态的日志可以再次修改，发布状态的日志无法进行修改。草稿和发布两种状态的日志通过两个时间轴进行展示

5、 “填写日志”的窗口包括以下：支持日期、所用工时(单位：小时，必须为 0.5 的整数倍)、一些动态字段（根据项目类型决定）、附件（可以添加多个文件）、“草稿”按钮（点击之后进入保存草稿状态，后续可以修改该日志）以及“发布”按钮（点击之后进入发布状态，后续无法修改，所以点击之后会先弹框确认，提示后续无法修改）

6、 “创建任务”（主任务及子任务）的窗口包括以下：任务主题、支持方式、客户名称、客户联系人、客户联系方式、支持开始时间、支持结束时间（如果为子任务，以上字段默认自动加载主任务的对应字段的值，可直接在页面上修改）。责任人（主任务时不可填写，即主任务时自动为项目责任人）。任务创建完成后，通过邮件向对应的任务责任人发送邮件通知（通知模板待定）

7、 草稿状态的日志 只对自己开放，不对其他人开放（包括上级）

8、 项目的责任人或参与人拥有相应的操作和查看权限，项目的责任人或参与人的上级只继承其下级的相关项目、任务及日志的查看权限，不继承操作权限。

9、 操作(对系统数据有修改)包括：

    a)	项目归档（项目的责任人）
    b)	创建主任务(项目的责任人)
    c)	创建子任务(主任务的责任人)
    d)	删除主/子任务(主任务的责任人)
    e)	任务归档（主/子任务的责任人），子任务归档时检查主任务下属的子任务是否都已归档，如果都已归档，则向主任务的责任人发送邮件通知提醒进行主任务归档。主任务归档时，检查所有主任务是否都已归档，如果都已归档，则向项目责任人发送邮件通知提醒进行项目归档
    f)	填写/更新任务日志（主/子任务的责任人）。

10、动态字段：
"dependence ": "progress_100" 表示进度为 100 时必须有附件

```
{
    "key": "SalesEnablement",
    "name": "销售赋能",
    "parent_key": ""
},
{
    "key": "SalesToolCreation",
    "name": "销售工具制作",
    "parent_key": "SalesEnablement"
    "record_struct": [
        {
            "key": "CommunicationPartner",
            "name": "销售工具制作完成进度",
            "required": true,
            "type": "input_number",
            "content": "",
            "dependence ": "progress_100",
            "index": 1
        },{
            "key": "PurposeOfCommunication",
            "name": "销售工具内容说明",
            "required": true,
            "type": "text_area",
            "content": "",
            "index": 2
        },{
            "key": "Tip",
            "name": "如有编写交流PPT等材料，需要提交相关交流材料",
            "required": true,
            "type": "tip",
            "content": "",
            "index": 3
        }
    ]
},
```

### 接口

公共接口，客户名称 CRM 客户查询接口  
url: 'internal/crm/customer'

#### 操作权限查询

1.创建主任务，项目详情， page_title(project_detail、task_detail)
url: `/presales/internal_work/permission/:page_title`  
method: `get`  
params:

| 字段名     | 类型 | 是否必须 | 描述                        |
| ---------- | ---- | -------- | --------------------------- |
| task_id    | str  | 否       | 主任务 ID，当为 task_detail |
| project_id | str  | 否       | 项目 ID，project_detail     |

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			"create_task",
			"project_archive",
			"create_record",
			"create_subtask",
			"task_archive",
			"project_delete"
		]
	},
	"message": "successful"
}
```

#### 项目

1.支持字段排序，筛选（责任人、参与人；我的，下属，具体用户名，关键词（所有字段）搜索，分页  
url: `/presales/internal_work/project/list`  
method: `get`  
params:

| 字段名        | 类型           | 是否必须 | 描述                                       |
| ------------- | -------------- | -------- | ------------------------------------------ |
| query         | str            | 否       | 关键字模糊查询                             |
| date_range    | list[str, str] | 否       | 日期范围                                   |
| order_column     | str                                                          | 否       | 排序列                      |
| order_direct     | str                                                          | 否       | 排序方向                      |
| owner_id      | list[str]      | 否       | 负责人                                     |
| created_by_id | list[str]      | 否       | SE 分配人                                  |
| status        | list[int]      | 否       | 未开始(1)，进行中(2)，已结束(3)，已删除(4) |
| participants  | list[str]      | 否       | 参与人                                     |
| page          | int            | 否       | 当前页                                     |
| size          | int            | 否       | 每页数量                                   |

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "",
				"project_number": "",
				"subject": "",
				"created_date": "",
				"owner_id": "",
				"owner_name": "",
				"created_by_id": "",
				"created_by_name": "",
				"account_id": "",
				"account_name": "",
				"status": 1,
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
				"last_modified_by_id": "",
				"last_modified_by_name": "",
				"last_modified_date": "",
				"participants": [{ "id": "", "name": "" }]
			}
		],
		"page": 1,
		"size": 10,
		"total": 100
	},
	"message": "successful"
}
```

2.项目负责人列表查询， 从项目列表中查询所有负责人  
url: `/presales/internal_work/project/owner/list`  
method: `get`  
params:

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "",
				"display_name": ""
			}
		]
	},
	"message": "successful"
}
```

3.创建人列表查询， 从项目列表中查询所有创建人  
url: `/presales/internal_work/project/create_by/list`  
method: `get`  
params:

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "",
				"display_name": ""
			}
		]
	},
	"message": "successful"
}
```

4.项目参与人列表查询， 所有项目的所有任务、日志的负责人、创建人的集合  
url: `/presales/internal_work/project/participants/list`  
method: `get`  
params:

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "",
				"display_name": ""
			}
		]
	},
	"message": "successful"
}
```

5.项目类型，确定日志模板  
url: `/presales/project/support_type`  
method: `get`
params:

resp:

```json
{
  "code": 0,
  "data": {
    "list": [
     [
      {
        "key": "ChannelSupportInternal",
        "name": "渠道支持（内部）",
        "parent_key": ""
      },
      {
        "key": "ChannelTraining",
        "name": "渠道培训",
        "parent_key": "ChannelSupportInternal",
        "record_struct": [
          {
            "content": "",
            "index": 1,
            "key": "TrainingTargets",
            "name": "培训对象",
            "required": true,
            "type": "input"
          },
          {
            "content": "",
            "index": 2,
            "key": "NumberOfTrainees",
            "name": "培训人数",
            "required": true,
            "type": "input_number"
          },
          {
            "content": "",
            "index": 3,
            "key": "PurposeOfTraining",
            "name": "培训目的",
            "required": true,
            "type": "input"
          },
          {
            "content": "",
            "index": 4,
            "key": "ContentOfTraining",
            "name": "培训内容",
            "required": true,
            "type": "text_area"
          },
          {
            "content": "",
            "index": 5,
            "key": "BusinessOpportunityTapping",
            "name": "商机挖掘",
            "required": true,
            "type": "input"
          },
          {
            "index": 6,
            "key": "Tip",
            "name": "要求提交渠道培训的PPT相关材料",
            "required": true,
            "type": "tip"
          }
        ]
      }
     ]
  },
  "message": "successful"
}
```

7.责任人（当前用户及下属列表）  
url: `/presales/project/owner`  
method: `get`  
params:

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "",
				"internal_email": "",
				"user_name": ""
			}
		]
	},
	"message": "successful"
}
```

8.创建项目  
url: `presales/internal_work/project`  
method: `post`  
params:

| 字段名           | 类型 | 是否必须 | 描述         |
| ---------------- | ---- | -------- | ------------ |
| subject          | str  | 是       | 主题         |
| owner_id         | str  | 是       | 责任人 ID    |
| account_id       | str  | 否       | 客户 ID      |
| account_name     | str  | 否       | 客户名称     |
| contact_name     | str  | 否       | 客户联系人   |
| contact_info     | str  | 否       | 客户联系方式 |
| support_type_1st | str  | 是       | 支持类型 Key |
| support_type_2nd | str  | 是       | 支持项 Key   |

resp:

```json
{
	"code": 0,
	"data": {
		"project_number": "",
		"id": ""
	},
	"message": "successful"
}
```

9.查看项目详情, 项目编号、项目主题、负责人、分配人、创建时间等等字段  
url: `presales/internal_work/project/:project_id`  
method: `get`
resp:

```json
{
	"code": 0,
	"data": {
		"id": "",
		"project_number": "",
		"subject": "",
		"created_date": "",
		"owner_id": "",
		"owner_name": "",
		"created_by_id": "",
		"created_by_name": "",
		"account_id": "",
		"account_name": "",
		"status": 1,
		"contact_name": "",
		"contact_info": "",
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
		"last_modified_by_id": "",
		"last_modified_name": "",
		"last_modified_date": ""
	},
	"message": "successful"
}
```

项目删除
url: `presales/internal_work/project/:project_id`  
method: `delete`
resp:

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

10.项目参与人列表， 所有任务、日志的负责人、创建人的集合  
url: `/presales/internal_work/project/:project_id/participants/list`  
method: `get`

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"department": "",
				"display_name": "",
				"id": "",
				"name": "",
				"position": "",
				"role": "",
				"leader": ""
			}
		]
	},
	"message": "successful"
}
```

11.项目归档，
url: `/presales/internal_work/project/:project_id/archive`  
method: `put`

| 字段名 | 类型 | 是否必须 | 描述      |
| ------ | ---- | -------- | --------- |
| status | str  | 是       | 已完成(3) |

resp:

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

### 任务列表

1.查询项目任务列表 编号、主题、责任人、支持方式(现场/远程)、状态(进行中、已结束和已删除)、创建时间和操作等列  
url: `/presales/internal_work/task/list`  
method: `get`  
params：

| 字段名     | 类型 | 是否必须 | 描述     |
| ---------- | ---- | -------- | -------- |
| project_id | str  | 是       | 项目 ID  |
| page       | int  | 否       | 当前页   |
| size       | int  | 否       | 每页数量 |

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "",
				"task_number": "",
				"subject": "",
				"created_by_id": "",
				"created_by_name": "",
				"support_mode": 1,
				"status": 1,
				"created_date": "",
				"owner_name": "",
				"task_start_date": "",
				"task_result": "",
				"last_modified_by_id": "",
				"last_modified_name": "",
				"last_modified_date": "",
				"permission": ["create_subtask", "delete", "archive", "create_record"]
			}
		]
	},
	"message": "successful"
}
```

2.创建主任务（前端拉取项目详情）  
url: `/presales/internal_work/task`  
method: `post`
params：

| 字段名       | 类型 | 是否必须 | 描述                        |
| ------------ | ---- | -------- | --------------------------- |
| project_id   | str  | 是       | 项目 ID                     |
| subject      | str  | 是       | 主题                        |
| support_mode | int  | 是       | 支持方式现场（1）/远程（2） |
| account_id   | str  | 否       | 客户 ID                     |
| account_name | str  | 否       | 客户名称                    |
| contact_name | str  | 否       | 客户联系人                  |
| contact_info | str  | 否       | 客户联系方式                |
| start_time   | str  | 否       | 开始时间                    |
| end_date     | str  | 否       | 结束时间                    |

resp:

```json
{
	"code": 0,
	"data": {
		"id": ""
	},
	"message": "successful"
}
```

3.创建子任务（前端拉取主任务详情）  
url: `/presales/internal_work/task/:task_id/subtask`  
method: `post`
params：

| 字段名       | 类型      | 是否必须 | 描述                        |
| ------------ | --------- | -------- | --------------------------- |
| subject      | str       | 是       | 主题                        |
| support_mode | int       | 是       | 支持方式现场（1）/远程（2） |
| account_id   | str       | 否       | 客户 ID                     |
| owner_id     | list[str] | 是       | 责任人列表 ID               |
| account_name | str       | 否       | 客户名称                    |
| contact_name | str       | 否       | 客户联系人                  |
| contact_info | str       | 否       | 客户联系方式                |
| start_time   | str       | 否       | 开始时间                    |
| end_date     | str       | 否       | 结束时间                    |

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "",
				"task_number": ""
			}
		]
	},
	"message": "successful"
}
```

4.任务归档  
url: `/presales/internal_work/task/:task_id/archive`  
method: `put`
params：

| 字段名      | 类型 | 是否必须 | 描述                     |
| ----------- | ---- | -------- | ------------------------ |
| task_result | str  | 是       | 完成(1)、未完成(2)       |
| remark      | str  | 否       | 备注、未完成需要备注原因 |

resp:

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

5.任务删除  
url: `/presales/internal_work/task/:task_id`  
method: `delete`

resp:

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

6.任务详情查看  
url: `/presales/internal_work/task/:task_id`  
method: `get`

resp:

```json
{
	"code": 0,
	"data": {
		"id": "",
		"task_number": "",
		"subject": "",
		"created_by_id": "",
		"created_by_name": "",
		"owner_id": "",
		"owner_name": "",
		"account_id": "",
		"contact_name": "",
		"contact_info": "",
		"support_mode": 1,
		"status": 1,
		"created_date": "",
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
		"task_start_date": "",
		"task_end_date": "",
		"task_result": "",
		"task_incomplete_reason": "",
		"parent_id": "",
		"project_number": "",
		"project_subject": "",
		"project_id": "",
		"last_modified_by_id": "",
		"last_modified_by_name": "",
		"last_modified_date": ""
	},
	"message": "successful"
}
```

### 日志

1.日志列表（或草稿列表），显示支持开始时间、结束时间、所用工时  
url: `/presales/internal_work/task/:task_id/record/list`
method: `get`
params：

| 字段名 | 类型 | 是否必须 | 描述             |
| ------ | ---- | -------- | ---------------- |
| status | int  | 是       | 日志状态是否草稿 |

resp:

```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": "",
        "support_start_date": "",
        "support_end_date":"",
        "support_duration": "",
        "created_by_id": "",
        "created_by_name": "",
        "created_date": "",
        "published_date": "",
        "status": "",
        "task_id": "",
        "approval_id": "",
        "approval_name": "",
        "record_content": [{
                "key": "TrainingTargets",
                "name": "培训对象",
                "required": true,
                "type": "input",
                "content": "",
                "index": 1
            }],
        "attachments": [{"id": "", "filename": "", "file_size": 0, "file_type": ""}]
        "permission": ["delete_record", "update_record"]
      }
    ],
    "size": 1,
    "page": 1,
    "total": 1
  },
  "message": "successful"
}
```

2.创建日志, 支持日期、所用工时、一些动态字段、附件、草稿、发布  
url: `/presales/internal_work/task/:task_id/record`  
method: `post`  
params：

| 字段名             | 类型                | 是否必须 | 描述                                                            |
| ------------------ | ------------------- | -------- | --------------------------------------------------------------- |
| support_start_date | str                 | 是       | 支持开始时间                                                    |
| support_end_date   | str                 | 是       | 支持结束时间                                                    |
| support_duration   | str                 | 否       | 所用工时、只能为 0.5 的整数倍(传入参数为 30 的倍数，按分钟存储) |
| record_content     | list[dict]          | 是       | 支持项的详细记录内容                                            |
| attachments        | list[attachment_id] | 是       | 附件 ID 列表                                                    |
| status             | int                 | 是       | 草稿（1）、发布（2）                                            |

resp:

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

3.更新日志，判断是否草稿、只能草稿改发布  
url: `/presales/internal_work/task/:task_id/record/:record_id`  
method: `put`  
params：

| 字段名             | 类型                | 是否必须 | 描述                                                            |
| ------------------ | ------------------- | -------- | --------------------------------------------------------------- |
| support_start_date | str                 | 是       | 支持开始时间                                                    |
| support_end_date   | str                 | 是       | 支持结束时间                                                    |
| support_duration   | str                 | 否       | 所用工时、只能为 0.5 的整数倍(传入参数为 30 的倍数，按分钟存储) |
| record_content     | list[dict]          | 是       | 基于任务的支持项                                                |
| attachments        | list[attachment_id] | 是       | 附件 ID 列表                                                    |
| status             | int                 | 是       | 草稿（1）、发布（2）                                            |

resp:

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

4.删除草稿日志  
url: `/presales/internal_work/task/:task_id/record/:record_id`  
method: `delete`

resp:

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

5.获取待审批日志列表 （仅具有创建项目权限的人员可见）
url: `/presales/internal_work/record/pending`  
method: `get`

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
				]
			}
		],
		"size": 1,
		"page": 1,
		"total": 1
	},
	"message": "successful"
}
```

6.日志详情
url: `/presales/internal_work/record/:record_id`  
method: `get`

resp:

```json
{
	"code": 0,
	"data": {
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
    "task_number":"",
    "task_subject": "",
    "parent_task": {
      "id":"",
      "task_number":"",
      "subject": "",
      ...
    },
    "project": {
      "id": "",
      "project_number": "",
      "subject": "",
      ...
    },
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
	},
	"message": "successful"
}
```

7.日志审批，审批通过设置为发布状态，不通过设置为草稿
url: `/presales/internal_work/record/:record_id/approval`  
method: `put`
params：

| 字段名            | 类型 | 是否必须 | 描述             |
| ----------------- | ---- | -------- | ---------------- |
| approval          | int  | 是       | 1-通过、2-不通过 |
| unapproval_reason | str  | 否       | 不通过时候才有   |

### 附件

1.附件管理，附件 ID、200M  
url: `/attachment`  
method: `post`

params：

| 字段名            | 类型 | 是否必须 | 描述                                       |
| ----------------- | ---- | -------- | ------------------------------------------ |
| related_object    | str  | 是       | 关联对象（se_work_record：内部事务固定值） |
| related_object_id | str  | 否       | 关联对象 ID                                |
| file              | file | 是       | 文件                                       |

resp:

```json
{
	"code": 0,
	"data": {
		"id": ""
	},
	"message": "successful"
}
```

2.获取附件，没用到
url: `/attachment`  
method: `get`

params：

| 字段名            | 类型 | 是否必须 | 描述                       |
| ----------------- | ---- | -------- | -------------------------- |
| related_object    | str  | 是       | 关联对象（se_work_record） |
| related_object_id | str  | 是       | 关联对象 ID                |

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"created_by_id": "",
				"created_by_name": "",
				"created_date": "",
				"file_size": 0,
				"file_type": "",
				"id": ""
			}
		]
	},
	"message": "successful"
}
```

3.获取附件下载链接
url: `/attachment/:attachment_id/download`  
method: `get`

resp:

```json
{
	"code": 0,
	"data": {
		"file_url": ""
	},
	"message": "successful"
}
```
