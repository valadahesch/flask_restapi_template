## se 数字化周报

### 路由，菜单，权限

p_se_weekly_list: "se.weekly:list",

路由：/business_platform/presales_support/weekly
菜单：/业务平台/售前支持/周报

路由：/business_platform/presales_support/weekly/new
菜单：/业务平台/售前支持/新增周报

路由：/business_platform/presales_support/weekly/edit/:weekly_id
菜单：/业务平台/售前支持/编辑周报

路由：/business_platform/presales_support/weekly/:weekly_id
菜单：/业务平台/售前支持/周报详情

### 其他接口

邮箱： '/api/internal/hr/staff/list'

### 模板字段定义

模板的定义在前端techadmin仓库，src/business/weekly/common.ts里头commonWeeklyTemplate

### 周报列表

URL: '/presales/weekly/list'  
Method: GET

Params：

| 字段名             | 类型      | 是否必须 | 描述                                                   |
| ------------------ | --------- | -------- | ------------------------------------------------------ |
| page               | int       | 是       | 当前页                                                 |
| size               | int       | 是       | 每页数量                                               |
| subject            | str       | 否       | 主题                                                   |
| created_date_range | list(str) | 否       | 创建时间段，可用在创建周报时候查询本周周报情况，做提示 |
| receiver           | list(str) | 否       | 收件人邮箱列表                                         |
| status             | list(str)       | 是       | 草稿还是正式周报 ，"Draft","Published"                 |

Response：

```json
{
	"code": 0,
	"data": {
		"list": [
			{
				"id": "周报id",
				"receiver": [
					{
						"name": "收件人名称",
						"email": "收件人邮箱"
					}
				],
				"cc": [
					{
						"name": "抄送人名称",
						"email": "抄送人邮箱"
					}
				],
                "department": [
                  {
                    "id":  1, 
                    "name": "部门"
                  }
                ],
				"created_date": "创建时间",
				"created_by_id": "创建人id",
				"created_name": "创建人名称",
				"subject": "主题",
				"status": "状态",
                "start_date": "起始时间",
                "end_date": "截止时间",
				"send_date": "发送时间",
				"last_modified_date": "上次修改时间",
				"version": "0.0.1",
			}
		],
		"size": 1,
		"page": 1,
		"total": 1
	},
	"message": "successful"
}
```

### 周报详情

URL: '/presales/weekly/:weekly_id'  
Method: GET  
Description: 包含了统计数据，模板，以及模板对应的数据

Response：

```json
{
	"code": 0,
	"data": {
		"id": "周报id",
		"receiver": [
			{
				"name": "收件人名称",
				"email": "收件人邮箱"
			}
		],
		"cc": [
			{
				"name": "抄送人名称",
				"email": "抄送人邮箱"
			}
		],
        "department": [
              {
                "id":  1, 
                "name": "部门"
              }
        ],
		"created_date": "创建时间",
		"created_by_id": "创建人id",
		"created_name": "创建人名称",
        "start_date": "起始时间", 
        "end_date": "截止时间",
		"send_date": "发送时间",
		"last_modified_date": "上次修改时间",
		"subject": "主题",
		"status": "状态",
		"version": "0.0.1",
		"data": {
			"html": "状态为草稿的时候没有这个东西，<div>整体的html,前端渲染过的，没有js的，有js也实际最终被转义了执行不了，发邮件用</div>",
			"data": {
				""
			} 
		}
	},
	"message": "successful"
}
```

### 根据模板 key 获取个人的周报数据

URL: '/presales/weekly/template/data'  
Method: GET  
Description: 个人模板数据

Params：

| 字段名 | 类型     | 是否必须 | 描述                      |
| ------ | -------- | -------- | ------------------------- |
| key   | string | 是       | 模板 key, 如 summary，projects |
| department_ids   | list | 否       | 部门ID列表 |

Response：

summary, 其他
```json
{
	"code": 0,
	"data": {
        "start_date": "起始时间",
        "end_date": "截止时间",
		"sumary": {
			"obj": {
				"summary.project_number": 2
			}
		},
		"other": {
			"obj": {
				"other.content": ""
			}
		},
	},
	"message": "successful"
}
```

ecological, 本周项目， 内部事务，本周需求，下周工作计划
```json
{
	"code": 0,
	"data": {
		"ecological"： {
			"list": [{
				"ecological.partner_name": ""
			}]
		}
	},
	"message": "successful"
}
```


### 保存为草稿

URL: '/presales/weekly'  
Method: POST

Params:

```json
{
	"receiver": [{
		"name": "收件人名称",
		"email": "收件人邮箱"
	}],
	"cc": [{
		"name": "收件人名称",
		"email": "收件人邮箱"
	}],
    "start_date": "起始时间", 
    "end_date": "截止时间",
    "department_ids": [1,2],
	"subject": "主题",
	"data": {
		"version": "0.0.1",
		"data": {
			"ecological"： {
				"list": [{
					"ecological.partner_name": ""
				}]
			},
			"sumary": {
				"obj": {
					"summary.project_number": 2
				}
			},
			"other": {
				"obj": {
					"other.content": ""
				}
			},
		}
	}
}
```

Response：

```json
{
	"code": 0,
	"data": {
		"id": "周报id"
	},
	"message": "successful"
}
```

### 编辑草稿

URL: '/presales/weekly/:weekly_id'  
Method: put

Params:

```json
{
	"receiver": [{
		"name": "收件人名称",
		"email": "收件人邮箱"
	}],
	"cc": [{
		"name": "收件人名称",
		"email": "收件人邮箱"
	}],
    "start_date": "起始时间", 
    "end_date": "截止时间",
    "department_ids": [1,2],
	"subject": "主题",
	"data": {
		"version": "0.0.1",
		"data": {
			"ecological"： {
				"list": [{
					"ecological.partner_name": ""
				}]
			},
			"sumary": {
				"obj": {
					"summary.project_number": 2
				}
			},
			"other": {
				"obj": {
					"other.content": ""
				}
			},
		}
	}
}
```

Response：

```json
{
	"code": 0,
	"data": {
	},
	"message": "successful"
}
```

### 删除草稿, 发布的不能删

URL: '/presales/weekly/:weekly_id'  
Method: delete


### 发邮件，保存为Published

URL: '/presales/weekly/:weekly_id'  
Method: POST

Params:

```json
{
	"receiver": [{
		"name": "收件人名称",
		"email": "收件人邮箱"
	}],
	"cc": [{
		"name": "收件人名称",
		"email": "收件人邮箱"
	}],
    "start_date": "起始时间",
    "end_date": "截止时间",
    "department_ids": [1,2],
	"subject": "主题",
	"data": {
		"html": "实际邮件发送的"
	}
}
```

Response：

```json
{
	"code": 0,
	"data": {
		"id": "周报id"
	},
	"message": "successful"
}
```


### 项目，增加新行时候，根据project_number等搜索行数据, list里头只有一行
下周区域工作计划、本周需求、工时统计，都不调用这个接口

URL: '/presales/weekly/template/new/data'  
Method: GET

Params：

| 字段名 | 类型     | 是否必须 | 描述                      |
| ------ | -------- | -------- | ------------------------- |
| key   | string | 是       | 模板 key, 如 summary，projects |
| data   | string | 是       | 可能是任务编号，项目编号等 |

Response：

```json
{
	"code": 0,
	"data": {
		"projects": {
			"list": [{
				"other.content": ""
			}]
		},
	},
	"message": "successful"
}
```

### 查询哪些下属还没有发周报
URL: '/presales/weekly/not_send'  
Method: GET  

Response：

```json
{
	"code": 0,
	"data": {
		"list": [{
			"id":"",
			"name":""
		}]
	},
	"message": "successful"
}
```