## TODO
 
-  父子工单是否用树状表示，设计分页查询, 目前关联还没想明白
-  删除任务
-  任务的数据
---

### 一 、数据表

#### 1.工单表

```shell

CREATE TABLE `dic_work_order` (
  `id` varchar(20) NOT NULL COMMENT 'ID',
  `parent_id` varchar(20) DEFAULT NULL COMMENT '父级工单，重复包含的工单进行归类',
  `number` varchar(10) NOT NULL COMMENT '系统10位工单编号',
  `subject` varchar(200) NOT NULL COMMENT '主题',
  `description` longtext COMMENT '描述',
  `support_type` varchar(30) NOT NULL COMMENT '支持类型（需求（requirement）、故障（fault）、咨询（consult）、其他（other））',
  `privacy` varchar(20) NOT NULL COMMENT '私有（private）、公有（public）',
  `save_time` int NOT NULL COMMENT '单次节省工时，转化成分钟',
  `status` varchar(30) NOT NULL COMMENT '工单状态：已提交（commit）、已取消（cancel）、已受理（accepting）、处理中（Processing）、交付中（delivery）、归档（archive）',
  `commit_by_id` varchar(20) NOT NULL COMMENT '提交人',
  `to_process` tinyint(1) DEFAULT NULL COMMENT '是否开发',
  `usage_annual` int NOT NULL COMMENT '年使用次数',
  `approval_reason` text COMMENT '审批原因',
  `priority` varchar(20) NOT NULL COMMENT '优先级（低、中、高、紧急（low,  medium, high、urgent））',
  `approval_by_id` varchar(20) DEFAULT NULL COMMENT '审批人',
  `approval_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '审批时间（受理人确认时间）',
  `feasibility` text COMMENT '可行性描述',
  `due_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '预估工单完成时间',
  `accepted_by_id` varchar(20) DEFAULT NULL COMMENT '受理人',
  `accepted_datetime` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '受理时间',
  `created_by_id` varchar(20) NOT NULL COMMENT '创建人',
  `created_by_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `last_modified_by_id` varchar(20) NOT NULL COMMENT '最后修改人',
  `last_modified_date` datetime NOT NULL COMMENT '最好修改时间',
  `deleted_by_id` varchar(20) DEFAULT NULL COMMENT '删除人',
  `deleted_by_date` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '删除时间',
  `cancel_by_id` varchar(20) DEFAULT NULL COMMENT '取消人',
  `cancel_by_date` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '取消时间',
  `cancel_by_reason` text COMMENT '取消原因',
  `actual_due_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '实际交付时间',
  `complete_date` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '实际完成时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='数字化支持中心面向技术部问题反馈系统的工单表';

```

#### 2. 项目表

```shell

CREATE TABLE `dic_project` (
  `id` varchar(20) NOT NULL COMMENT '项目ID',
  `project_name` varchar(100) NOT NULL,
  `project_path` varchar(300) NOT NULL,
  `created_by_id` varchar(20) NOT NULL COMMENT '创建人',
  `created_by_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


```

#### 3. 分配表

```shell

CREATE TABLE `dic_work_order_dispatch` (
  `id` varchar(20) NOT NULL,
  `work_order_id` varchar(20) NOT NULL COMMENT '工单ID',
  `project_id` varchar(20) NOT NULL COMMENT '对应项目ID',
  `milestone_title` varchar(200) NOT NULL COMMENT '里程碑标题',
  `assign_by_id` varchar(20) NOT NULL COMMENT '指派人',
  `cretaed_by_id` varchar(20) NOT NULL COMMENT '创建人',
  `cretaed_by_date` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `assign_by_date` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '指派时间',
  PRIMARY KEY (`id`),
  KEY `work_order_id` (`work_order_id`),
  KEY `project_id` (`project_id`),
  CONSTRAINT `project_id` FOREIGN KEY (`project_id`) REFERENCES `dic_project` (`id`),
  CONSTRAINT `work_order_id` FOREIGN KEY (`work_order_id`) REFERENCES `dic_work_order` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

```

#### 4. 留言表

```shell

CREATE TABLE `dic_message` (
  `id` varchar(20) NOT NULL COMMENT 'id',
  `parent_id` varchar(20) DEFAULT NULL COMMENT '父级id',
  `work_order_id` varchar(20) NOT NULL COMMENT '工单ID',
  `content` text NOT NULL COMMENT '评论内容',
  `to_user_id` varchar(20) NOT NULL COMMENT '给谁评论',
  `created_by_id` varchar(20) NOT NULL COMMENT '评论人',
  `created_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '评论时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


```


### 二、平台权限划分

```shell


我们的：
名称：业务平台->数字化支持->工单管理
权限: p_dic_ticket_manage_all: "dic_ticket_manage:all"      

1、提交工单：business_platform/dic/ticket_manage/add                                  pagekey:  dic.ticket_manage_add
2、查看工单：business_platform/dic/ticket_manage/detail/{ticket_id}                   pagekey:  dic.ticket_manage_detail
3、工单列表(我的工单，所有工单): business_platform/dic/ticket_manage                   pagekey:  dic.ticket_manage_list


右上角的：
名称：工单
权限: p_dic_ticket_all: "dic_ticket:all"
1、提交工单：business_platform/dic/ticket/add                                         pagekey:  dic.ticket_add    
2、查看工单：business_platform/dic/ticket/detail/{ticket_id}                          pagekey:  dic.ticket_detail   
3、工单列表：business_platform/dic/ticket/list                                        pagekey:  dic.ticket_list


```


---



### 三、 接口

// 需要权限判断的时候会传递权限标识： header. x_permission== plist.xxx
// 权限标识： p_dic_ticket_manage_all 和 p_dic_ticket_all

#### . 全量获取功能模块信息

```shell


- method: GET
- url: /api/dic/ticket/functional_module/list
- params: 
- permission: p_dic_ticket_manage_all 和 p_dic_ticket_all

- resp:
{
    "code": 0,
    "message": "acquire success!",
    "data": {
    	"list":[
            {
    			"id": "id",
                "name": "名称",
                "description": "描述",
            }
	]
    }
}
```


#### . 根据企业用户名搜系统用户

```shell

复用/staff/list接口，根据企业用户名搜系统用户，在SE需求创建任务时查询使用

```



#### . 提交工单


- request example

```shell

description: 当工单管理进入的时候，管理人为DIC有created_by_id字段

- method: POST
- url: /api/dic/ticket
- param: {
        "parent_id": "父级工单ID 【可空】"
        "subject": "主题",
        "description": "描述 【可空】富文本， 20M限制",
        "support_type": "支持类型（需求（requirement）、故障（fault）、咨询（consult）、其他（other））",
        "privacy": "私有（private）、公有（public）",
        "functional_module_id": "功能模块： 故障，优化有功能模块， 需求【可空】"
        "priority":  "优先级" //低、中、高、紧急（low,  medium, high、urgent）,
        "action": "暂时保存(Draft) / 提交受理(Commit)",
        "commit_by_id": "创建人"
}

- permission : p_dic_ticket_all 或者 p_dic_ticket_manage_all
```

- response example

```json
{
    "code": 0,
    "message": "submit success!",
    "data": {
        "id": "工单ID"
    }
}
```


#### . 删除草稿状态工单工单


- request example

```shell


- method: DELETE
- url: /api/dic/ticket/: ticket_id
- permission : p_dic_ticket_all 或者 p_dic_ticket_manage_all
```

- response example

```json
{
    "code": 0,
    "message": "success!",
    "data": {}
}
```


#### . 编辑工单


- request example

```shell

- description： 当编辑人员为DIC管理员时，可以修改工单状态，添加预计完成时间
- permission : p_dic_ticket_all 或者 p_dic_ticket_manage_all

- method: PUT
- url: /api/dic/ticket/: ticket_id


- DIC管理员更改 param: {
        "parent_id": "父级工单ID 【可空】"
        "subject": "主题",
        "description": "描述富文本， 20M限制",
        "support_type": "支持类型（需求（requirement）、故障（fault）、咨询（consult）、其他（other））",
        "privacy": "私有（private）、公有（public）",
        "functional_module_id": "功能模块： 故障，优化有功能模块， 需求【可空】"
        "priority":  "优先级" //低、中、高、紧急（low,  medium, high、urgent）,
        "created_by_id": "创建人",
        "due_time": "预估工单完成时间",
        "status": "可以改为已受理 Accepting"，
}

- description: 提交人在工单状态已受理之前可以修改

- 提交人更改 param: {
        "parent_id": "父级工单ID 【可空】"
        "subject": "主题",
        "description": "描述富文本， 20M限制",
        "support_type": "支持类型（需求（requirement）、故障（fault）、咨询（consult）、其他（other））",
        "privacy": "私有（private）、公有（public）",
        "functional_module_id": "功能模块： 故障，优化有功能模块， 需求【可空】"
        "priority":  "优先级" //低、中、高、紧急（low,  medium, high、urgent）,
}

- 管理员驳回 param: {
        "status": "Cancel"，
        "feasibility": "可行性 or 取消原因"
}

- 交付之前提交人取消 param: {
        "status": "Cancel"，
        "cancel_by_reason": "取消原因"
}


```

- response example

```json
{
    "code": 0,
    "message": "submit success!",
    "data": {}
}
```



#### . 获取工单列表


```shell
- method: GET
- url: /api/dic/ticket/list

- permission: p_dic_ticket_manage_all
- description: 当权限为DIC查询所有包含所有公有和所有私有，管理员视图可以看工单私有性；

- permission: p_dic_ticket_all
- description:当权限为其他人查询所有，包含所有公有和自己私有, 非管理员试图不能看工单私有性

// classification:    我参与的、 所有公有个案、 我的草稿
// status:  已提交（commit）、已取消（cancel）、已受理（accepting）、处理中（doing）、交付中（delivery）、已完成（complete）

- param: {
            "classification": "all, mine, draft",
            "status": [""], // 可以为空    "状态"
            "page": 1,
            "size": 1,
            "support_type": [],   // 可以为空 "需求（requirement）、故障（fault）、咨询（consult) "
            "priority": []   // 可以为空    "优先级"

         }   

- permission : 
```

- response example

 // 权限为p_dic_ticket_manage_all是可以查看工单私有性，新增字段：privacy
```json
{
    "code": 0,
    "message": "acquire success!",
    "data": {
    	"list":[
            {
    			"id": "id",
                "parent_id": "父级ID",
                "number": "工单编号",
                "subject": "主题",
                "status": "状态",
    			"created_by_id": "创建人",
    			"created_by_name": "创建人昵称",
    			"commit_by_id": "提交人",
    			"commit_by_name": "提交人昵称",
      			"created_date": "提交时间",
                "last_modified_by_id": "最后修改人",
      			"last_modified_date": "最后修改时间",
        		"support_type": "支持类型（ 需求（requirement）、故障（fault）、咨询（consult））",
    			"priority": "优先级",
                "schedule": "处理进度",
                "functional_module_id": "功能模块ID",
                "functional_module_name": "功能模块名称",
            }
	],
    "page": 1,
    "size": 1,
    "total": 1
    }
}
```


#### . 查看工单


- request example

```shell

description: 当工单管理进入的时候，管理人为DIC有created_by_id字段

- method: GET
- url: /api/dic/ticket/: ticket_id


- permission: p_dic_ticket_all
- response:
{
    "code": 0,
    "message": "success!",
    "data": {

        "id": "id",
        "parent_id": "父级ID",
        "number": "工单编号",
        "subject": "主题",
        "status": "状态",
        "commit_by_id": "提交人",
        "commit_date": "提交时间",
        "created_by_id": "创建人id",
        "created_by_name": "创建人昵称",
        "last_modified_by_id": "最后修改人",
        "last_modified_date": "最后修改时间",
        "support_type": "支持类型（ 需求（requirement）、故障（fault）、咨询（consult））",
        "priority": "优先级",
        "schedule": "处理进度",
        "functional_module_id": "功能模块ID",
        "functional_module_name": "功能模块名称",
        "privacy": "私有（private）、公有（public）",
        "due_time": "预估工单完成时间"
    }
} 

- permission: p_dic_ticket_manage_all
- response:
{
    "code": 0,
    "message": "success!",
    "data": {
        "id": "id",
        "parent_id": "父级ID",
        "number": "工单编号",
        "subject": "主题",
        "status": "状态",
        "commit_by_id": "提交人",
        "commit_date": "提交时间",
        "last_modified_by_id": "最后修改人",
        "last_modified_date": "最后修改时间",
        "support_type": "支持类型（ 需求（requirement）、故障（fault）、咨询（consult））",
        "priority": "优先级",
        "schedule": "处理进度",
        "functional_module_id": "功能模块ID",
        "functional_module_name": "功能模块名称",
        "privacy": "私有（private）、公有（public）",
        "due_time": "预估工单完成时间",

    }
} 


```

- response example

```json

```


### 操作权限查询

Draft: "草稿",
Commit: "已提交",
Cancel: "已取消",
Accepting: "已受理",
Doing: "处理中",
Delivery: "交付中",
Complete: "已完成",

重点：提交后的工单不能删除，草稿才能删除，直接物理删除
管理员看不到别人的草稿


工单详情，操作权限， page_title(ticket_detail)
header.x_permission==p_list.p_dic_ticket_all，status=="Draft"  ：["edit","commit", "delete"]
header.x_permission==p_list.p_dic_ticket_all，status=="Commit" : ["edit","cancel"]
header.x_permission==p_list.p_dic_ticket_all，status=="Cancel" : []
header.x_permission==p_list.p_dic_ticket_all，status=="Accepting" : ["cancel"]
header.x_permission==p_list.p_dic_ticket_all，status=="Doing" : ["cancel"]
header.x_permission==p_list.p_dic_ticket_all，status=="Delivery" : ["cancel", "complete", "doing"]
header.x_permission==p_list.p_dic_ticket_all，status=="Complete" : []


header.x_permission==p_list.p_dic_ticket_manage_all，status=="Draft"  ：["edit","commit", "delete"]
header.x_permission==p_list.p_dic_ticket_manage_all，status=="Commit" : ["edit","cancel","accepting"]
header.x_permission==p_list.p_dic_ticket_manage_all，status=="Cancel" : ["delete"]
header.x_permission==p_list.p_dic_ticket_manage_all，status=="Accepting" : ["cancel","doing", "add-task"]
header.x_permission==p_list.p_dic_ticket_manage_all，status=="Doing" : ["cancel","delivery", "add-task"]
header.x_permission==p_list.p_dic_ticket_manage_all，status=="Delivery" : ["cancel", "doing"]
header.x_permission==p_list.p_dic_ticket_manage_all，status=="Complete" : []



- url: `/api/dic/ticket/permission/:page_title`  
- method: `get`  
- params:

| 字段名  | 类型 | 是否必须 | 描述                      |
| ------- | ---- | -------- | ------------------------- |
| ticket_id | str  | 否       | 工单ID，当为 ticket_detail |

resp:

```json
{
	"code": 0,
	"data": {
		"list": ["cancel", "edit", "complete"]  //只有交付中可以将状态改成已完成
	},
	"message": "successful"
}
```




#### . 新建任务


- request example

```shell

description: 当工单管理进入的时候，管理人为DIC有created_by_id字段

- method: POST
- url: /api/dic/ticket/: ticket_id/task

- param: 
{
    data: [
        {
            "handle_type": "develop"
            "milestone_title": "里程碑标题",
            "description": "描述 【可空】富文本， 20M限制",
            "start_time": "开始时间",
            "end_time": "截止时间",
            "project_id": "项目ID",
            "subject": "仅用于展示"
        },
         {
            "handle_type": "non_develop"
            "description": "描述 【可空】富文本， 20M限制",
            "assign_by_id": "指派人",
            "subject": "仅用于展示"
        }
    ]
}


- permission : p_dic_ticket_manage_all
```

- response example

```json
{
    "code": 0,
    "message": "submit success!",
    "data": {
        "id": "任务ID"
    }
}
```


#### . 查看任务


- request example

```shell

- method: GET
- url: /api/dic/ticket/: ticket_id/task

- param: 
    {
        "page": 1,
        "size": 1
    }


- permission : p_dic_ticket_manage_all
```

- response example

```json
{
    "code": 0,
    "message": "submit success!",
    "data": {
        "list": [
            {
                "task_id": "",
                "handle_type": "develop",
                "description": "description",
                "milestone_title": "里程碑标题",
                "milestone_status": "里程碑状态",
                "milestone_schedule": "里程碑进度",
                "milestone_url": " 里程碑链接",
                "start_time": "开始时间",
                "end_time": "截止时间",
                "project_id": "项目ID",
                "issue":[
                    {
                        "issue_id": "issue ID",
                        "subject": "主题",
                        "label": ["标签1", "标签2"],
                        "end_time": "到期时间",
                    }
                ]
            },
            {
                "task_id": "",
                "handle_type": "non_develop",
                "description": "描述 【可空】富文本， 20M限制",
                "assign_by_id": "指派人"
            }
        ],
        "page": 1,
        "size": 1,
        "total": 10
    }
}
```



#### . 获取项目列表


```shell
- method: GET
- url: /api/dic/ticket/project/list
- param: 
- permission : 
```

- response example

```json
{
    "code": 0,
    "message": " success!",
    "data": {
    	"list":[
            {
    			"id": "id",
                "key": "项目唯一KEY",
                "project_name": "项目名称",
                "project_path": "项目路径",
    			"created_by_id": "创建人",
      			"created_date": "创建时间"
            }
	]
}
}
```


#### .添加留言


```shell
- method: POST
- url: /api/dic/ticket/:ticket_id/message
- param: {
    "parent_id": "父级评论ID,一级评论为空字符串",
    "content": "留言内容",
    "to_user_id": "被评论人ID",
    "to_username": "被评论人昵称",
    "need_reply": True,  // 当为True时; 1.如果工单状态为交付中改为处理中; 2.已回复自动改为False
}
- permission : p_dic_ticket_all 或者 p_dic_ticket_manage_all
```

- response example

```json
{
    "code": 0,
    "message": " success!",
    "data": { 
        "id": "留言ID"
    }
```


#### .获取留言


```shell
- method: GET
- url: /api/dic/ticket/:ticket_id/message
- param:
- permission : p_dic_ticket_all 或者 p_dic_ticket_manage_all
```

- response example

```json
{
    "code": 0,
    "message": " success!",
    "data": {
        "list": [
             {
                "id": "评论ID",
                "created_by_id": "评论人ID",
                "created_username": "评论人昵称", // 显示头像框或者昵称
                "to_user_id": "被评论人ID",
                "to_username": "被评论人昵称",
                "parent_id": "父级评论ID,一级评论为空字符串",
                "content": "留言内容",
                "created_date": "2024-04-17 11:01:26"
                "need_reply": True //是否需要回复
             }
        ],
    "page": 1,
    "size": 1,
    "total": 1
    }
```


#### .获取我的任务列表


```shell
- method: GET
- url: /api/dic/ticket/tasks
- param: 

{
        "page": 1,
        "size": 1,
        "ticket_status": [], #工单状态
        "task_subject": "", # 任务主题
        "ticket_like": "", # 工单模糊
}


- permission : p_dic_ticket_manage_all

- response example
```

```json
{
    "code": 0,
    "message": " success!",
    "data": {
        "list": [
             {
                "id": "任务ID",
                "subject": "",
                "created_by_name": "任务创建人",
    			"created_by_id": "任务创建人",
      			"created_date": "任务创建时间",
                "assign_by_id": "指派人",
                "assign_by_name": "指派人",
                "handle_type": "develop",
                "ticket_id": "",
                "ticket_subject": "",
                "ticket_status": "",
                "ticket_number": "",
                "ticket_support_type": "支持类型（ 需求（requirement）、故障（fault）、咨询（consult））",
    			"ticket_priority": "优先级"
                "functional_module_id": "",
                "functional_module_name": ""
             }
        ],
    "page": 1,
    "size": 1,
    "total": 1
    }
```