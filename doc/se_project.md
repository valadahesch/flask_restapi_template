TODO
表结构
description

# SE 项目管理

```
1、创建项目有CRM推送数据发起，创建主任务也有CRM推送数据发起。CRM推送的数据。技术部站点在项目和任务表，分别建立crm_raw字段完整记录原始数据
2、技术部站点需要做的操作有：创建子任务（项目负责人）、填写并提交日志（任务负责人）、编辑草稿日志（任务负责人）、审批日志（项目创建人）、任务归档提交（任务负责人）、审批任务归档（项目创建人）、子任务删除（子任务创建人，且状态未开始）
3、项目列表分为六个子Tab：全部、我负责的、我参与的、我下属的、我关注的、归档项目
4、打开项目详情之后，默认展示任务列表。
5、任务列表顶部增加统计信息：主任务总数、按照状态统计各个状态主任务数量。
6、增加列任务归档审批，所以需要增项目列表平级增加待审批任务

项目不允许删除，主任务也不允许删除

变更项目负责人

项目详情，有个特殊的权限字段，金额，有的人有，有的人没有，有的话就展示

TODO 项目恢复， 看他们需求，去确认， 我们归档了，他们还推主任务
待办事项：不直接操作错，告警信息等
```

## 权限标识

```
"p_se_project_manage_list": "se.project_manage:list"
"p_se_project_manage_mutation": "se.project_manage:mutation"

显示路由：
菜单路径：业务平台-售前支持-项目管理
路由：/business_platform/presales_support/project_manage

隐藏路由：
菜单路径：项目管理项目详情
路由：/business_platform/presales_support/project_manage/project_detail/:project_id

菜单路径：项目管理任务详情
路由：/business_platform/presales_support/project_manage/task_detail/:task_id

```

## 数据表

```sql
#审批表
CREATE TABLE `se_project_approval_record`  (
  `id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `record_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '日志ID',
  `task_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '任务id',
  `project_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '主任务ID',
  `result` varchar(5) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '审批结果',
  `incomplete_reason` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '不通过原因',
  `created_date` datetime(0) NULL DEFAULT NULL COMMENT '创建时间',
  `approval_date` datetime(0) NULL DEFAULT NULL COMMENT '审批时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

#项目表
CREATE TABLE `se_project_project`  (
  `id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'ID',
  `project_type` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '项目类型：固定为商机管理',
  `project_number` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '项目编号',
  `opportunity_number` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '商机编号',
  `opportunity_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '商机名称',
  `subject` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '项目主题：默认为CRM的资源申请名称',
  `sale_by_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '申请人：销售',
  `owner_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '责任人：被分配SE',
  `account_id` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '客户id',
  `account_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '客户名称',
  `contact_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '客户联系人',
  `contact_info` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '客户联系方式',
  `status` smallint(0) NULL DEFAULT NULL COMMENT '状态',
  `opportunity_value` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '商机金额',
  `customer_requirement` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '客户需求描述',
  `created_by_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '创建人：SE分派员邮箱',
  `created_date` datetime(0) NULL DEFAULT NULL COMMENT '创建时间',
  `last_modified_by_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '上次修改人',
  `last_modified_date` datetime(0) NULL DEFAULT NULL COMMENT '上次修改时间',
  `deleted_by_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '删除人',
  `deleted_date` datetime(0) NULL DEFAULT NULL COMMENT '删除时间',
  `crm_raw_data` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'crm原始数据',
  `project_phase` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '项目阶段',
  `task_result` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '项目归档结果',
  `task_incomplete_reason` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '项目归档结果备注',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `se_project_project_UN`(`project_number`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'SE 商机项目' ROW_FORMAT = Dynamic;

#日志表
CREATE TABLE `se_project_record`  (
  `id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'ID',
  `support_start_date` datetime(0) NULL DEFAULT NULL COMMENT '支持开始时间',
  `support_end_date` datetime(0) NULL DEFAULT NULL COMMENT '支持结束时间',
  `support_duration` int(0) NULL DEFAULT NULL COMMENT '所用工时',
  `published_date` datetime(0) NULL DEFAULT NULL COMMENT '发布时间',
  `status` smallint(0) NULL DEFAULT NULL COMMENT '状态',
  `unapproval_reason` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '未通过原因',
  `task_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '任务Id',
  `created_by_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '创建人',
  `created_date` datetime(0) NULL DEFAULT NULL COMMENT '创建时间',
  `last_modified_by_id` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '上次修改人',
  `last_modified_date` datetime(0) NULL DEFAULT NULL COMMENT '上次修改时间',
  `deleted_by_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '删除人',
  `deleted_date` datetime(0) NULL DEFAULT NULL COMMENT '删除时间',
  `record_content` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT '其他动态字段',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

#任务表
CREATE TABLE `se_project_task`  (
  `id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'ID',
  `task_number` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '任务编号',
  `event_number` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '活动编号',
  `subject` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '主题',
  `created_date` datetime(0) NULL DEFAULT NULL COMMENT '创建时间',
  `created_by_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '创建人',
  `owner_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '责任人',
  `account_id` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '客户id',
  `account_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '客户名称',
  `contact_name` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '客户联系人',
  `contact_info` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '客户联系方式',
  `status` smallint(0) NULL DEFAULT NULL COMMENT '状态',
  `support_mode` smallint(0) NULL DEFAULT NULL COMMENT '支持方式',
  `support_type_1st` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '支持类型',
  `support_type_2nd` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '支持项',
  `task_start_date` datetime(0) NULL DEFAULT NULL COMMENT '任务开始时间',
  `task_end_date` datetime(0) NULL DEFAULT NULL COMMENT '任务结束时间',
  `task_result` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '任务结果',
  `task_incomplete_reason` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '任务未完成原因',
  `unapproval_reason` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '任务审批未通过原因',
  `last_modified_by_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '上次修改人',
  `last_modified_date` datetime(0) NULL DEFAULT NULL COMMENT '上次修改时间',
  `deleted_by_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '删除人',
  `deleted_date` datetime(0) NULL DEFAULT NULL COMMENT '删除时间',
  `parent_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '父任务id',
  `project_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT '项目id',
  `crm_raw_data` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'crm原始数据',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

#项目关注(跟踪)表
CREATE TABLE `se_project_focus`  (
  `id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `project_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '项目ID',
  `follower_id` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '关注者ID',
  `followed_date` datetime(0) NULL DEFAULT NULL COMMENT '关注时间',
  `deleted_date` datetime(0) NULL DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

```



## API

### CRM 项目推送接口

### TODO crm 那边要认证这个接口问题，crm 调用这个接口，不是给前端用的

URL: '/presales/project_manage/crm_async'
Method: POST
Params：

| 字段名                             | 类型  | 是否必须 | 描述           |
| ---------------------------------- | ----- | -------- | -------------- |
| new_name                           | str   | 是       | 活动编号       |
| subject                            | str   | 是       | 资源申请名称   |
| new_type                           | str   | 是       | 申请类型       |
| new_apply_for_key_customer_support | str   | 否       | 是否大项目支持 |
| new_opportunity_code               | str   | 否       | 商机编号       |
| new_opportunity_id                 | str   | 否       | 商机名称       |
| opportunityratingcode              | str   | 否       | 商机分级       |
| new_account_name                   | str   | 否       | 客户名称       |
| new_contact_id                     | str   | 否       | 客户联系人     |
| new_accountcontactnumber           | str   | 否       | 客户联系方式   |
| new_projectproducttioncause        | str   | 否       | 客户需求描述   |
| new_is_letter                      | str   | 否       | 是否信创项目   |
| new_placeorderforecast             | str   | 否       | 下单预测       |
| new_business_stage                 | str   | 否       | 商机阶段       |
| new_predictenddate                 | str   | 否       | 关单日期       |
| new_actualvalue                    | float | 否       | 商机金额       |
| new_salesengineer                  | str   | 是       | 被分配SE邮箱   |
| quotedetailproductlist             | list  | 否       | 产品明细       |
| saleemail                          | str   | 是       | 销售邮箱       |
| topsaleemail                       | str   | 是       | 销售上级邮箱   |
| semail                             | str   | 是       | SE分派员邮箱   |

Todo：确认响应消息结构

```json
{
	"code": 0,
	"data": {
        "id": 1 //任务id
    },
	"message": "successful"
}
```

### 查询项目列表

URL: '/presales/project_manage/project'
Method: GET
Params:

| 字段名         | 类型                                                         | 是否必须 | 描述                                       |
| -------------- | ------------------------------------------------------------ | -------- | ------------------------------------------ |
| query          | str                                                          | 否       | 关键模糊查询                               |
| date_range     | list[str, str]                                               | 否       | 创建时间范围                               |
| update_date_range  | list[str, str]                                           | 否       | 上次修改时间范围                           |
| last_record_created_date_range | list[str, str]    | 否       | 上次日志提交时间范围                           |
| last_record_support_start_date_range | list[str, str]    | 否       | 上次日志支持时间范围                           |
| order_column     | str                                                          | 否       | 排序列                      |
| order_direct     | str                                                          | 否       | 排序方向                      |
| owner_id       | list[str]                                                    | 否       | 负责人                                     |
| created_by_id  | list[str]                                                    | 否       | SE 分配人                                  |
| status         | list[str]                                                    | 否       | 未开始(1)，进行中(2)，已结束(3)，已删除(4) |
| participants   | list[str]                                                    | 否       | 参与人                                     |
| classification | str("all", "mine","participant","subordinate", "favor", "archive") | 否       | 项目分类                                   |
| task_result | list[str] | 否 |  项目结果 | 
| page           | int                                                          | 否       | 当前页                                     |
| size           | int                                                          | 否       | 每页数量                                   |

resp：

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "ID",
				"project_type": "项目类型：固定为商机管理",
				"pre_bidding_date": "计划招标（采购）时间",
				"project_number": "编号",
				"subject": "主题",
				"owner_id": "责任人id",
                "owner_name": "责任人名称",
				"account_id": "客户id",
				"account_name": "客户名称",
				"created_by_id": "创建人ID",
				"created_by_name": "创建人显示名",
				"status": 1, // 状态
				"created_date": "创建时间",
				"last_modified_by_id": "上次修改人",
				"last_modified_by_name": "上次修改人显示名",
				"last_modified_date": "上次修改时间",
				"last_record_created_date": "上次日志提交时间",
				"last_record_support_start_date": "上次日志支持时间",
				"opportunity_name": "商机名称",
				"opportunity_number": "商机编号",
                "sale_by_id": "销售id",
                "sale_by_name": "销售显示名",
				"taken_hours": 0.0, // 耗时
				"task_incomplete_reason": "项目未完成原因",
                "participants": [ //项目参与人
                    {
                        "display_name": "用户名称",
                        "id": "用户id"
                    }
                ],
        		"permission": ["project_archive"] //权限id
			}
		],
		"page": 1, 
		"size": 10,
		"total": 100
	},
	"message": "successful"
}
```


### 获取待审批日志列表 （仅具有创建项目权限的人员可见）
url: `/presales/project_manage/record/pending`  
method: `get`

params：

| 字段名 | 类型 | 描述         |
| ------ | ---- | ------------ |
| page   | str  | 页码         |
| size   | str  | 页面显示数量 |

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "日志ID",
				"support_start_date": "支持开始时间",
				"support_end_date": "支持结束时间",
				"support_duration": "所用工时",
				"created_by_id": "创建人id",
				"created_by_name": "创建人名称",
				"created_date": "创建时间",
				"published_date": "发布时间",
				"status": 1, // 状态
				"task_id": "任务id",
				"task_number": "任务编号",
				"task_subject": "任务主题",
                "last_modified_by_id": "上次修改人id",
                "last_modified_date": "上次修改时间",
				"record_content": [ //日志字段
					{
						"key": "TrainingTargets",
						"name": "培训对象",
						"required": true,
						"type": "input",
						"content": "",
						"index": 1
					}
				],
				"attachments": [ //附件信息
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


### 日志详情
url: `/presales/project_manage/record/:record_id`  
method: `get`

resp:

```json
{
	"code": 0,
	"data": {
		"id": "日志ID",
		"support_start_date": "支持开始时间",
		"support_end_date": "支持结束时间",
		"support_duration": "所用工时",
		"created_by_id": "创建人ID",
		"created_by_name": "创建人名称",
		"created_date": "创建时间",
		"published_date": "发布时间",
		"status": 1, // 状态
		"task_id": "任务ID",
        "task_number":"任务编号",
        "task_subject": "任务主题",
        "parent_task": { //任务信息
            "id":"任务ID",
            "task_number":"任务编号",
            "subject": "主题",
     		...
    	},
    	"project": { //项目信息
            "id": "项目ID",
            "project_number": "项目编号",
            "subject": "主题",
          	...
        },
		"record_content": [ //日志信息
			{
				"key": "TrainingTargets",
				"name": "培训对象",
				"required": true,
				"type": "input",
				"content": "",
				"index": 1
			}
		],
		"attachments": [ //附件信息
			{ "id": "", "filename": "", "file_size": 0, "file_type": "" }
		],
	},
	"message": "successful"
}
```

### 审批日志
URL: '/presales/project_manage/record/:record_id/approval'
Method: PUT
Params:

| 字段名            | 类型 | 是否必须 | 描述             |
| ----------------- | ---- | -------- | ---------------- |
| approval          | int  | 是       | 1-通过、2-不通过 |
| unapproval_reason | str  | 否       | 不通过时候才有   |

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```


### 查询项目详情
URL: '/presales/project_manage/project/:project_id'
Method: GET

resp:

```json
{
	"code": 0,
	"data": {
		"id": "项目ID",
		"project_type": "项目类型",
		"project_number": "项目编号",
		"subject": "主题",
		"sale_by_id": "销售ID",
        "sale_by_name": "销售名称",
		"owner_id": "负责人ID",
        "owner_name": "负责人名称",
		"account_id": "客户ID",
		"account_name": "客户名称",
		"contact_name": "客户联系人",
		"contact_info": "客户联系方式",
		"status": 1, // 状态
		"customer_requirement": "客户需求描述",
		"created_by_id": "创建人ID",
        "created_by_name": "创建人名称",
		"created_date": "创建时间",
		"last_modified_by_id": "上次修改人ID",
		"last_modified_date": "上次修改时间",
		"last_record_created_date": "上次日志提交时间",
		"last_record_support_start_date": "上次日志支持时间",
		"project_phase": { //项目进展
			"key": "",
			"name": "商机及预算",
			"parent_key": ""
		},
        "focused": true
	},
	"message": "successful"
}
```


### 编辑项目

URL: '/presales/project_manage/project/:project_id'
Method: put

字段描述

| 字段名             | 类型 | 描述                 |
| ------------------ | ---- | -------------------- |
| application_type         | str  | 申请类型           |
| opportunity_level  | str  | 商机分级           |
| account_id       | str  | 客户ID           |
| account_name      | str  | 客户名称 |
| is_itai_project | str  | 是否大项目           |
| project_phase | str  | 商机阶段           |
| contact_name | str  | 客户联系人           |
| contact_info | str  | 联系方式           |
| customer_requirement | str  | 客户需求描述           |
| deploy_core | str | 是否部署在核心位置 |
| return_reason | str | 回退原因 |

```json
{
	"code": 0,
	"data": {
	},
	"message": "successful"
}
```

### 任务列表统计(项目详情页面任务列表上方)

URL: '/presales/project_manage/project/:project_id/task_statistics'
Method: GET

字段描述

| 字段名             | 类型 | 描述                 |
| ------------------ | ---- | -------------------- |
| task_total         | int  | 主任务总数           |
| total_in_progress  | int  | 进行中数量           |
| closed_total       | int  | 已结束数量           |
| pending_total      | int  | 待审批（审批中）数量 |
| unrecognized_total | int  | 未开始数量           |

```json
{
	"code": 0,
	"data": {
		"task_total": 10, //主任务数量
		"total_in_progress": 10, //进行中数量
        "closed_total": 10, //已结束数量
        "pending_total": 10, //待审批（审批中）数量
        "unrecognized_total": 10 //未开始数量
	},
	"message": "successful"
}
```

### 查询任务列表

### total 是主任务的，可再加个字段，统计所有任务(total记录的主任务个数，totality所有主任务与子任务个数)

URL: '/presales/project_manage/project/:project_id/task'
Method: GET

Params：

| 字段名 | 类型 | 是否必须 | 描述     |
| ------ | ---- | -------- | -------- |
| page   | int  | 否       | 当前页   |
| size   | int  | 否       | 每页数量 |

resp：

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "任务ID",
				"task_number": "任务编号",
				"event_number": "活动编号",
				"subject": "主题",
				"created_date": "创建时间",
				"created_by_id": "创建人ID",
                "created_by_name": "创建人名称",
				"owner_id": "负责人ID",
                "owner_name": "责任人名称",
				"status": 1, // 状态
				"support_mode": "支持方式",
				"support_type_1st": { //支持类型
					"key": "",
					"name": "商机及预算",
					"parent_key": ""
				},
				"support_type_2nd": { //支持项
					"key": "",
					"name": "单一来源审批表编写",
					"parent_key": ""
				},
				"task_start_date": "任务开始时间",
				"task_end_date": "任务结束时间",
				"task_result": "任务结果",
				"task_incomplete_reason": "任务未完成原因",
				"unapproval_reason": "任务审批未通过原因",
				"last_modified_by_id": "上次修改人ID",
				"last_modified_name": "上次修改人名称",
				"last_modified_date": "上次修改时间",
				"permission": [ //权限
					"create_subtask", //创建子任务权限
					"create_record", //创建日志权限
					"archive_task", //归档任务权限
          			"archive_subtask" //归档子任务权限
					"delete_subtask" //删除子任务权限
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

### 待审批的任务列表, 主任务默认未启用

URL: '/presales/project_manage/project/:project_id/task/approval'
Method: GET

Params：

| 字段名 | 类型 | 是否必须 | 描述     |
| ------ | ---- | -------- | -------- |
| page   | int  | 否       | 当前页   |
| size   | int  | 否       | 每页数量 |

resp：

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "任务ID",
				"task_number": "任务编号",
				"event_number": "活动编号",
				"subject": "主题",
				"created_date": "创建时间",
				"created_by_id": "创建人ID",
                "created_by_name": "创建人名称",
				"owner_name": "责任人名称",
				"status": 1, // 状态
				"support_mode": "支持方式",
				"support_type_1st": { //支持类型
					"key": "",
					"name": "商机及预算",
					"parent_key": ""
				},
				"support_type_2nd": {//支持项
					"key": "",
					"name": "单一来源审批表编写",
					"parent_key": ""
				},
				"task_start_date": "任务开始时间",
				"task_end_date": "任务结束时间",
				"task_result": "任务结果",
				"task_incomplete_reason": "任务未完成原因",
				"unapproval_reason": "任务审批未通过原因",
				"last_modified_by_id": "上次修改人ID",
				"last_modified_name": "上次修改人名称",
				"last_modified_date": "上次修改时间"
			}
		],
		"size": 1,
		"page": 1,
		"total": 1
	},
	"message": "successful"
}
```

### 任务归档审批

URL: '/presales/project_manage/task/:task_id/approval'
Method: PUT
Params:

| 字段名            | 类型 | 是否必须 | 描述             |
| ----------------- | ---- | -------- | ---------------- |
| approval          | int  | 是       | 1-通过、2-不通过 |
| unapproval_reason | str  | 否       | 不通过时候才有   |

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

### 主任务确认启用

URL: '/presales/project_manage/task/:task_id/receive'
Method: PUT
Params:

| 字段名           | 类型 | 是否必须 | 描述     |
| ---------------- | ---- | -------- | -------- |
| support_type_1st | str  | 是       | 支持类型 |
| support_type_2nd | str  | 是       | 支持项   |
| support_mode     | int  | 否       | 支持方式 |
| start_time       | str  | 否       | 开始时间 |
| end_date         | str  | 否       | 结束时间 |

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

### 支持项列表

任务类型，确定日志模板  
url: `/presales/project_manage/task/support_type`  

method: GET

跟内部事务类似，字段需要去确认

```json
{
    "code": 0,
    "data": {
        "list": [
            {
                "key": "BusinessOpportunitiesAndBudgetRecognition",
                "name": "商机及预算确认",
                "parent_key": ""
    		},	
    		{
                "key": "PreparationOfProjectInitiationReport",
                "name": "立项报告编写",
                "parent_key": "BusinessOpportunitiesAndBudgetRecognition",
                "record_struct": [
                    {
                        "key": "SupportSummaryKeyActionRecord",
                        "name": "支持总结（关键动作记录）",
                        "required": True,
                        "type": "text_area",
                        "content": "",
                        "index": 1
                    },
                    {
                        "key": "ProjectRisk",
                        "name": "项目风险",
                        "required": True,
                        "type": "text_area",
                        "content": "",
                        "index": 2
                    },
                    {
                        "key": "NextActionPlan",
                        "name": "下一步行动计划",
                        "required": True,
                        "type": "text_area",
                        "content": "",
                        "index": 3
                    }
                ]
            }
        ]
    }
}
```



### 创建子任务

URL: '/presales/project_manage/task/:main_task_id/subtask'
Method: POST
Params:

| 字段名           | 类型      | 是否必须 | 描述                                          |
| ---------------- | --------- | -------- | --------------------------------------------- |
| subject          | str       | 是       | 主题                                          |
| owner_id         | list(str) | 是       | 责任人 ID(创建可选多个,实际 copy 多次子任务)  |
| account_id       | str       | 否       | 客户名称ID                                    |
| account_name     | str       | 否       | 客户名称                                      |
| contact_name     | str       | 否       | 客户联系人                                    |
| contact_info     | str       | 否       | 客户联系方式                                  |
| support_mode     | str       | 是       | 支持方式可选值有：现场(On-site)、远程(Remote) |
| task_start_date  | str       | 是       | 任务开始时间                                  |
| task_end_date    | str       | 是       | 任务结束时间                                  |
| support_type_2nd | str       | 是       | 支持项                                        |

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

### 查询任务详情

URL: '/presales/project_manage/task/:task_id'
Method: GET

resp:

```json
{
	"code": 0,
	"data": {
		"id": "任务ID",
		"task_number": "任务编号",
		"event_number": "活动编号",
		"subject": "主题",
		"created_date": "创建时间",
		"created_by_id": "创建人ID",
        "created_by_name": "创建人名称",
		"owner_id": "责任人ID",
		"owner_name": "责任人名称",
		"account_id": "客户ID",
		"account_name": "客户名称",
		"contact_name": "客户联系人",
		"contact_info": "客户联系方式",
		"status": 1, // 状态
		"support_mode": "支持方式",
		"support_type_1st": { //支持类型
			"key": "",
			"name": "商机及预算",
			"parent_key": ""
		},
		"support_type_2nd": { //支持项
			"key": "",
			"name": "单一来源审批表编写",
			"parent_key": ""
		},
		"task_start_date": "任务开始时间",
		"task_end_date": "任务结束时间",
		"task_result": "任务结果",
		"task_incomplete_reason": "任务未完成原因",
		"unapproval_reason": "任务审批未通过原因",
		"last_modified_by_id": "上次修改人ID",
		"last_modified_date": "上次修改时间",
		"deleted_by_id": "删除人ID",
		"deleted_date": "删除时间",
		"parent_id": "主任务ID",
		"project_id": "项目ID",
        "project_number": "项目编号",
        "project_subject": "项目主题"
	},
	"message": "successful"
}
```

### 创建日志

### attachments, related_object 这个看叫什么，去看内部事务

#### related_object：se_project_record

URL: '/presales/project_manage/task/:task_id/record'
Method: POST
Params:

| 字段名             | 类型                | 是否必须 | 描述                                              |
| ------------------ | ------------------- | -------- | ------------------------------------------------- |
| support_start_date | str                 | 是       | 支持开始时间                                      |
| support_end_date   | str                 | 是       | 支持结束时间                                      |
| support_duration   | int                 | 是       | 所用工时                                          |
| status             | str                 | 是       | 状态， 草稿(Draf)，发布(Publish)，已删除(Deleted) |
| record_content     | list[dict]          | 是       | 支持项的详细记录内容                              |
| attachments        | list[attachment_id] | 是       | 附件 ID 列表                                      |

```json
{
	"code": 0,
	"data": {
		"id": "日志ID"
	},
	"message": "successful"
}
```

### 编辑日志

URL: '/presales/project_manage/record/:record_id'
Method: PUT
Params:

| 字段名             | 类型                | 是否必须 | 描述                                              |
| ------------------ | ------------------- | -------- | ------------------------------------------------- |
| support_start_date | str                 | 是       | 支持开始时间                                      |
| support_end_date   | str                 | 是       | 支持结束时间                                      |
| support_duration   | int                 | 是       | 所用工时                                          |
| status             | str                 | 是       | 状态， 草稿(Draf)，发布(Publish)，已删除(Deleted) |
| record_content     | list[dict]          | 是       | 支持项的详细记录内容                              |
| attachments        | list[attachment_id] | 是       | 附件 ID 列表                                      |

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```


### 日志撤回（待审批中日志可以由提交人主动撤回、已发布日志撤回功能）

URL: '/presales/project_manage/record/:record_id/return'
Method: PUT
Params:


```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

### 删除草稿日志

URL: '/presales/project_manage/record/:record_id'
Method: DELETE

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

### 

### 查询主任务下所有子任务以及自身的日志列表

URL: '/presales/project_manage/main_task/:main_task_id/all_record'
Method: GET

Params:

| 字段名 | 类型 | 是否必须 | 描述        |
| ------ | ---- | -------- |-----------|
| status | str  | 是       | 状态(已发布日志) |


resp：

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "日志ID",
				"support_start_date": "支持开始时间",
				"support_end_date": "支持结束时间",
				"support_duration": "所用工时",
				"created_by_id": "创建人ID",
				"created_by_name": "创建人名称",
				"created_date": "创建时间",
				"published_date": "发布时间",
				"status": 1, // 状态
				"task_id": "任务ID",
				"task_number": "任务编号",
				"task_subject": "任务主题",
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
				"attachments": [ //附件信息
					{
						"id": "",
						"filename": "",
						"file_size": 0,
						"file_type": ""
					}
				],
                "permission": ["return"] // return：项目创建人，已发布，任务未归档todo 
			}
		]
	},
	"message": "successful"
}
```

### 查询日志（草稿，审批中）列表

URL: '/presales/project_manage/task/:task_id/record'
Method: GET

Params:

| 字段名 | 类型 | 是否必须 | 描述                     |
| ------ | ---- | -------- | ------------------------ |
| status | str  | 是       | 状态(草稿，日志，审批中) |
| page   | int  | 否       | 当前页                   |
| size   | int  | 否       | 每页数量                 |

resp：

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "日志ID",
				"support_start_date": "支持开始时间",
				"support_end_date": "支持结束时间",
				"support_duration": "所用工时",
				"created_by_id": "创建人ID",
				"created_by_name": "创建人名称",
				"created_date": "创建时间",
				"published_date": "发布时间",
				"status": 1, // 状态
				"task_id": "任务ID",
				"task_number": "任务编号",
				"task_subject": "任务主题",
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
				"attachments": [ //附件信息
					{
						"id": "",
						"filename": "",
						"file_size": 0,
						"file_type": ""
					}
				],
                "permission": ["return"] // return：项目创建人，已发布，任务未归档todo 或者 审批中提交人可以撤回 
			}
		],
		"size": 1,
		"page": 1,
		"total": 1
	},
	"message": "successful"
}
```

### 任务详情，业务权限， page_title(task_detail，project_detail，record_detail)

url: `/presales/project_manage/permission/page_title`  
method: `get`  
params:

| 字段名  | 类型 | 是否必须 | 描述                        |
| ------- | ---- | -------- | --------------------------- |
| task_id | str  | 否       | 主任务 ID，当为 task_detail |

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
          "create_record", 
          "task_archive",
          "record_approval",
          "project_archive",
          "project_return",
          "project_leader_editor",
		  "project_combine"# 本项目没有归档和当前项目创建人，
          "task_return" # 任务退回, 主任务负责人，待确认状态,
          "project_record" # 项目若有日志，只有项目的创建人、责任人、创建人所有上级  和 责任人所有人上级
        ]
	},
	"message": "successful"
}
```


### 子任务删除

URL: '/presales/project_manage/task/:task_id'
Method: DELETE
Params:

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```


### 主任务退回（填写退回原因(任务未完成原因字段)，标记为已删除）
URL: '/presales/project_manage/task/:task_id/return'
Method: PUT
Params:

| 字段名                 | 类型 | 是否必须 | 描述      |
| ---------------------- | ---- | -------- |---------|
| task_incomplete_reason | str  | 是       | 任务退回成原因 |

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```


### 任务归档提交
### 子任务需要归档
URL: '/presales/project_manage/task/:task_id/archive'
Method: PUT
Params:

| 字段名                 | 类型 | 是否必须 | 描述                               |
| ---------------------- | ---- | -------- | ---------------------------------- |
| task_result            | str  | 是       | 完成(Complete)、未完成(Incomplete) |
| task_incomplete_reason | str  | 是       | 任务未完成原因                     |

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```


### 项目归档

URL: '/presales/project_manage/project/:project_id/archive'
Method: PUT
Params:

| 字段名                 | 类型 | 是否必须 | 描述                               |
| ---------------------- | ---- | -------- | ---------------------------------- |
| task_result            | str  | 是       | 完成(Complete)、未完成(Incomplete) |
| task_incomplete_reason | str  | 是       | 任务未完成原因    

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```

### 关注项目

URL：'/presales/project_manage/project/:project_id/focus'

Method: POST

Params:

| 字段名     | 类型 | 是否必须 | 描述                                     |
| ---------- | ---- | -------- | ---------------------------------------- |
| project_id | str  | 是       | 项目ID                                   |
| action     | str  | 是       | 关注项目（Concern)、取消关注（Unfollow） |

resp:

```json
{
	"code": 0,
	"data": {},
	"message": "successful"
}
```
### 所有项目创建人列表查询

URL：'/presales/project_manage/project/create_by/list'

Method：GET

resp：

```json
{
    "code": 0,
    "data": {
        "list":[
            {
                "id": "用户id",
                "display_name": "用户名称"
            }
        ]
    },
    "message": "successful"
}
```

### 所有项目负责人列表查询

URL：'/presales/project_manage/project/owner/list'

Method: GET

resp:

```json
{
    "code": 0,
    "data": {
        "list":[
            {
                "id": "用户id",
                "display_name": "用户名称"
            }
        ]
    },
    "message": "successful"
}
```

### 所有项目参与人列表查询

URL：'/presales/project_manage/project/participants/list'

Method：GET

resp：

```json
{
    "code": 0,
    "data": {
        "list":[
            {
                "id": "用户id",
                "display_name": "用户名称"
            }
        ]
    },
    "message": "successful"
}
```

### 项目参与人列表查询

URL：'/presales/project_manage/project/:project_id/participants/list'

Method：GET

resp：
```json
{
    "code": 0,
    "data": {
        "list":[
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


### 查询项目报价产品的接口

URL：'/presales/project_manage/project/:project_id/products'

Method：GET

resp：
```json
{
    "code": 0,
    "data": {
        "list":[
            {
            "new_number": "订单编号",
            "new_product_group_idname": "产品线",
            "new_subline_idname": "",
            "new_product_idname": "产品名称",
            "POSKU": "SKU",
            "skuname": "SGSV-A5500-CN-60H",
            "new_num": 2,
            "new_servicemonth": 5,
            "createdon": "2023-07-18"
        }
        ],
      "page": 1,
      "size": 10,
      "total": 1
    },
    "message": "successful"
}
```


### 获取我的待审批归档任务列表

URL：'/presales/project_manage/archive/task/list'

Method：GET

Params：

| 字段名 | 类型 | 描述 |
| ------ | ---- | ---- |
| page   | str  | 页码 |
| size   | str  | 数量 |

resp：
```json
{
    "code": 0,
    "data": {
        "list":[
           {
				"id": "任务ID",
				"task_number": "任务编号",
				"subject": "主题",
                "project_subject": "所属项目主题",
				"created_date": "创建时间",
				"created_by_id": "创建人ID",
                "created_by_name": "创建人名称",
                "owner_id": "",
				"owner_name": "责任人名称",
				"status": 5, // 状态
				"support_mode": "支持方式",
				"support_type_1st": { //支持类型
					"key": "",
					"name": "商机及预算",
					"parent_key": ""
				},
				"support_type_2nd": {//支持项
					"key": "",
					"name": "单一来源审批表编写",
					"parent_key": ""
				},
				"task_start_date": "任务开始时间",
				"task_end_date": "任务结束时间",
			}
        ]
    },
    "message": "successful"
}
```

### 获取我的待确认任务列表

URL：'/presales/project_manage/enable/task/list'

Method：GET

Params：

| 字段名 | 类型 | 描述 |
| ------ | ---- | ---- |
| page   | str  | 页码 |
| size   | str  | 数量 |

resp：

```json
{
    "code": 0,
    "data": {
        "list":[
           {
				"id": "任务ID",
				"task_number": "任务编号",
				"subject": "主题",
                "project_subject": "所属项目主题",
				"created_date": "创建时间",
				"created_by_id": "创建人ID",
                "created_by_name": "创建人名称",
                "owner_id": "",
				"owner_name": "责任人名称",
				"status": 5, // 状态
				"support_mode": "支持方式",
				"support_type_1st": { //支持类型
					"key": "",
					"name": "商机及预算",
					"parent_key": ""
				},
				"support_type_2nd": {//支持项
					"key": "",
					"name": "单一来源审批表编写",
					"parent_key": ""
				},
				"task_start_date": "任务开始时间",
				"task_end_date": "任务结束时间",
			}
        ]
    },
    "message": "successful"
}
```

### 获取项目商机状态

URL：'/presales/project_manage/opportunity/status'

Method：GET

Params：

| 字段名         | 类型   | 描述     |
|-------------|------|--------|
| project_ids | list | 项目ID列表 |

resp：
```json
{
    "code": 0,
    "data": {
        "list":[{
          "project_id": "",
          "status": ""
        }]
    },
    "message": "successful"
}
```


### 我负责的任务列表（跨项目，所有项目）

URL：'/presales/project_manage/task/list/mine'

Method：GET

Params：

| 字段名         | 类型   |  是否必选  |  描述     |
|-------------|------|--------|------ |
| page   | int  | 是       | 当前页   |
| size   | int  | 是       | 每页数量 |
| status   | list（int）  | 否       | 任务状态，默认未开始和进行中 |
| task_number   | str  | 否       | 任务编号 |
| event_number   | str  | 否       | 活动编号 |
| subject   | str  | 否       | 主题 |
| project_number   | str  | 否       | 项目编号 |
| project_subject   | str  | 否       | 项目主题 |
| created_date_range | list[str, str] | 否 | 创建时间范围 |
| support_mode |  list[str] | 否 | 支持方式 |
| task_result  |  list[str] | 否 | 任务结果 |



resp：
```json
{
    "code": 0,
    "data": {
       "list": [
			{
				"id": "任务ID",
				"task_number": "任务编号",
				"event_number": "活动编号",
				"subject": "主题",
				"created_date": "创建时间",
				"created_by_id": "创建人ID",
                "created_by_name": "创建人名称",
				"owner_id": "负责人ID",
                "owner_name": "责任人名称",
				"status": 1, // 状态
				"support_mode": "支持方式",
				"support_type_1st": { //支持类型
					"key": "",
					"name": "商机及预算",
					"parent_key": ""
				},
				"support_type_2nd": { //支持项
					"key": "",
					"name": "单一来源审批表编写",
					"parent_key": ""
				},
				"task_start_date": "任务开始时间",
				"task_end_date": "任务结束时间",
				"task_result": "任务结果",
				"task_incomplete_reason": "任务未完成原因",
				"unapproval_reason": "任务审批未通过原因",
				"last_modified_by_id": "上次修改人ID",
				"last_modified_name": "上次修改人名称",
				"last_modified_date": "上次修改时间",
				"permission": [ //权限
					"create_subtask", //创建子任务权限
					"create_record", //创建日志权限
					"archive_task", //归档任务权限
          			"archive_subtask" //归档子任务权限
					"delete_subtask" //删除子任务权限
				],
				"project_id": "",
				"project_number": "编号",
				"project_subject": "主题",
				"account_name": "客户名称",
				"taken_hours": "任务耗时"
			}
		],
		"size": 1,
		"page": 1,
		"total": 1
    },
    "message": "successful"
}
```


### 项目合并(子项目和父项目都未关闭)

URL：'/presales/project_manage/project/:id/combine'

Method：post

Params：

| 字段名         | 类型   | 描述     |
|-------------|------|--------|
| parent_project_id   | str  |    父项目ID     |

response：
```json
{
    "code": 0,
    "data": {
        "id": ""
    },
    "message": "successful"
}
```


### 查询本项目下子项目列表

URL：'/presales/project_manage/project/:id/sub_project/list'

Method：get

Params：

response：
```json
{
    "code": 0,
    "data": {
        "list":[{
		"id": "项目ID",
		"project_type": "项目类型",
		"project_number": "项目编号",
		"subject": "主题",
		"sale_by_id": "销售ID",
        "sale_by_name": "销售名称",
		"owner_id": "负责人ID",
        "owner_name": "负责人名称",
		"account_id": "客户ID",
		"account_name": "客户名称",
		"contact_name": "客户联系人",
		"contact_info": "客户联系方式",
		"status": 1, // 状态
		"customer_requirement": "客户需求描述",
		"created_by_id": "创建人ID",
        "created_by_name": "创建人名称",
		"created_date": "创建时间",
		"last_modified_by_id": "上次修改人ID",
		"last_modified_date": "上次修改时间",
		"project_phase": { //项目进展
			"key": "",
			"name": "商机及预算",
			"parent_key": ""
		},
        "focused": true
	}]
    },
    "message": "successful"
}
```



### 个人日志列表  
url: `/presales/project_manage/record/mine/list`  
method: `get`

params：

| 字段名                      | 类型   | 描述         |
|--------------------------|------| ------------ |
| page                     | str  | 页码         |
| size                     | str  | 页面显示数量 |
| status                   | list  | 状态 |
| support_location_adcodes | list | 支持地点 |
| task_number              | str  | 任务编号 |
| task_subject             | str  | 任务主题 |
| project_number           | str  | 项目编号 |
| project_subject          | str  | 项目主题 |
| date_range          | list | 支持时间范围 |

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "日志ID",
				"support_start_date": "支持开始时间",
				"support_end_date": "支持结束时间",
				"support_duration": "所用工时",
				"created_by_id": "创建人id",
				"created_by_name": "创建人名称",
				"created_date": "创建时间",
				"published_date": "发布时间",
				"status": 1, // 状态
				"task_id": "任务id",
				"task_number": "任务编号",
				"task_subject": "任务主题",
                "last_modified_by_id": "上次修改人id",
                "last_modified_date": "上次修改时间",
                "support_location_adcode": "",
                "support_location": "支持地点",
                "task_parent_id": "",
                "task_event_number": "",
                "project_number": "",
                "attachments_count": "",
                "support_mode": ""
			}
		],
		"size": 1,
		"page": 1,
		"total": 1
	},
	"message": "successful"
}
```


### 增加项目所有日志列表功能

URL: '/presales/project_manage/project/:project_id/all_record'
Method: GET

Params:

resp：

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "日志ID",
				"support_start_date": "支持开始时间",
				"support_end_date": "支持结束时间",
				"support_duration": "所用工时",
				"created_by_id": "创建人ID",
				"created_by_name": "创建人名称",
				"created_date": "创建时间",
				"published_date": "发布时间",
				"status": 1, // 状态
				"task_id": "任务ID",
				"task_number": "任务编号",
				"task_subject": "任务主题",
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
				"attachments": [ //附件信息
					{
						"id": "",
						"filename": "",
						"file_size": 0,
						"file_type": ""
					}
				],
                "permission": ["return"] // return：项目创建人，已发布，任务未归档todo 
			}
		]
	},
	"message": "successful"
}
```


### 操作历史展示

URL: '/presales/project_manage/project/:project_id/history'
Method: GET

Params:

| 字段名                      | 类型   | 描述         |
|--------------------------|------| ------------ |
| page                     | str  | 页码         |
| size                     | str  | 页面显示数量 |

```json
{
	"code": 0,
	"data": {
		"list": [
          {
            "id": 1,
            "action": "delete，put，add",
            "content": "<user-info id="abc" label="名称"/> 分派项目<se-project id="abc" label="主题"/> 给 <user-info id="abc" label="名称"/>",
            "created_by_id": "创建人ID",
            "created_by_name": "创建人名称",
            "created_date": "创建时间",
        }
        ],
        "size": 1,
		"page": 1,
		"total": 1
	},
	"message": "successful"
}
```