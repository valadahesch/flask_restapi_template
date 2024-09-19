## TODO

todo找ps确认，总结  是严格模式还是宽松模式，然后再确定字段结构




## 重要
版本，遵循semver规范，三位，大中版本每次更改需要商量，小版本直接更新，通知即可   


## 权限

名称：业务平台->售后支持->任务列表
路由：/business_platform/ps/task/list

名称：业务平台->售后支持->任务详情
路由：/business_platform/ps/task/detail/:task_id
隐藏路由    

权限: p_ps_inspection_all: "ps_inspection:all"   


# 获取任务列表

- method: GET
- url: /api/ps/inspection
- params: 
```
{
    "task_id": 111,
    "project_subject": "",
    "classification" "all, mine",
    "page": 1,
    "size": 2,
}
```
- permission: p_ps_inspection_all

- resp:
```
{
    "code": 0,
    "message": "acquire success!",
    "data": {
    	"list":[
            {
    			"project_id": "id",
                "task_id": "",
                "task_subject": "",
                "project_subject": "",
                "project_account": "",
                "project_owner": "",
                "project_owner_id": "",
                "task_owner": "",
                "task_owner_id": "",
                "task_start_date": "",
                "task_end_date": ""
            }
        ],
        "page": 1,
        "size": 1,
        "total": 1
    }
}
```

## 获取任务详情

- method: get
- url: /api/ps/inspection/task/<task_id>
- params: 

- permission: p_ps_inspection_all

- resp:
```
{
    "code": 0,
    "message": "acquire success!",
    "data": {
        "project_id": "id",
        "task_id": "",
        "task_subject": "",
        "project_subject": "",
        "project_account": "",
        "project_owner": "",
        "task_owner": "",
        "task_start_date": "",
        "task_end_date": ""，
        "is_pass": true,
        "contrast": true,
        ......
    }
}
```


## 获取任务上传文件历史记录列表

- method: get
- url: /api/ps/inspection/task/<task_id>/history
- params: 

- permission: p_ps_inspection_all

- resp:
```
{
    "code": 0,
    "message": "acquire success!",
    "data": {
        "list": [
            {
                "upload_file_id": "id",
                "file_name": "xxx.zip",
                "upload_file_url": "https://xx/common/auth/attachment/download/file_id",
                "created_by_date" "",
                "subject": "",
                "count": 10, //数量
                "city":"落地城市", //todo 项目系统中的城市，通过接口拿
                "area":"部署区域",
                "account_id":"可能没有，传空字符串",
                "account_name":"客户"
            }
        ],
        total: 10,
        total_use: 9
    }
}
```



## 导出报告前预检

- method: get
- url: /api/ps/inspection/task/<task_id>/check
- params: 

- permission: p_ps_inspection_all

- resp:
```
{
    "code": 0,
    "message": "acquire success!",
    "data": {
        "list": [
            {
                "客户档案设备列表": "",
                "tip": ["city必须"],
            }
        ]
    }
}
```

## 预检提交

- method: post
- url: /api/ps/inspection/task/<task_id>/check
- params: 

```
{   
    "date_tag": "",
    "list": [
        {
            "city":"落地城市",
            "area":"部署区域",
            "account_name":"客户名称",
            "account_id":"客户id",
            "online_date":"上线时间",
            "machine_room":"机房位置",
            "purchase_date":"购买时间",
            "客户档案设备列表": "",
        }
    ]
}
```

- permission: p_ps_inspection_all

- resp:
```
{
    "code": 0,
    "message": "success!",
    "data": {
        "is_pass": true/false,
        "tip_list": [
            {
                "id":"",
                "tip":["购买时间",..]
            }
        ]
    }
}
```


## 上传巡检数据文件
- method: post
- url: /api/ps/inspection/task/<task_id>/export
- formdata: 

```
{
    "subject": "",
    "file": xxx.zip,
    "city":"落地城市", //todo 项目系统中的城市，通过接口拿
    "area":"部署区域",
    "account_id":"可能没有，传空字符串",
    "account_name":"客户",
    "machine_room": "机房位置"

}
```

- permission: p_ps_inspection_all

- resp:
```
{
    "code": 0,
    "message": "success!",
    "data": {
        "id": "",
    }
}
```


### 客户接口  account_id对应接口：api/internal/crm/customer


### 任务详情，业务权限， page_title(task_detail)

url: `/api/ps/inspection/permission/page_title`  
method: `get`  
params:

| 字段名  | 类型 | 是否必须 | 描述                        |
| ------- | ---- | -------- | --------------------------- |
| task_id | str  | 是       | 任务 ID，当为 task_detail |

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
          "upload", //上传
          "check", //预览
          "download", //导出报告 
          "restore", //重置
        ]
	},
	"message": "successful"
}
```


## 恢复，反悔
### 重置，预检成功生成报告后，才有此按钮，为了能返回，重回到上传完时候的状态，不包含编辑的内容
- method: put
- url: /api/ps/inspection/task/<task_id>/restore

- permission: p_ps_inspection_all

- resp:
```
{
    "code": 0,
    "message": "success!",
    "data": {
    }
}
```

### 下载报告
- method: post
- url: /api/ps/inspection/task/<task_id>/download

- permission: p_ps_inspection_all

- params:

| 字段名  | 类型   | 是否必须 | 描述                                                                                                                                   |
| ------- |------| -------- |--------------------------------------------------------------------------------------------------------------------------------------|
| external | dict | 是       | 总结，{"external_list": [{"id":"序号", "device_name_sn":"设备名称+SN", "occurrence_time":"发生时间", "concrete_issue":"具体问题", "solution":"解决方案", "risk_grade":"风险等级"}]} |


- resp:
```
{
    "code": 0,
    "message": "success!",
    "data": {
        url:"后端能下载的地址"
    }
}
```

## 预览，打开后端路由，浏览器新tab展示

- method: get
- url: /api/ps/inspection/task/<task_id>/preview

- permission: p_ps_inspection_all

- resp:
```
{
    "code": 0,
    "message": "success!",
    "data": {
        url:"后端实际预览地址，有个凭证，包含了用户和过期时间信息"
    }
}
```

## 季度对比，季度标签

- method: get
- url: /api/ps/inspection/date_tag

- permisson:  p_ps_inspection_all

- response:  
{   
   "list": [
       {"date_tag": "q-2024-2", "label": "2024第二季度"},
       {"date_tag": "m-2024-02", "label": "2024第二月"}
   ]
}



## 季度对比，季度标签

- method: get
- url: /api/ps/inspection/history/archive

- permisson:  p_ps_inspection_all

- params:  
{
    "date_tag": "",
    "sn": ["", ""]
}

- permission: 
- resp:
```
{
    "code": 0,
    "message": "success!",
    "data": {
        "list": [
            {
                "客户档案设备列表": "",
                "date_tag": "",
                "date_tag_label": "某某季度/月度"
            }
        ]
    }
}
```


## 当前支持的版本区间

- method: get
- url: /api/ps/inspection/version_interval

- permisson:  p_ps_inspection_all

- permission: 
- resp:
```
{
    "code": 0,
    "message": "success!",
    "data": {
        "start_version": "1.0",
        "end_version": "1.0"
    }
}
```

## 巡检总结表格填写字段信息

- method: get
- url: /api/ps/inspection/task/<task_id>/summary_field

- permisson:  p_ps_inspection_all

- permission: 
- resp:
```
{
    "code": 0,
    "message": "success!",
    "data": {
        "list": [
            {
                "id": "1",  # 顺序
                "name": "", # 键值
                "title": "设备名称+SN", # 标题
                "type": "select", # 类型
                "default_value": "", # 默认值
                "options": [ # 选项
                    "sg-6000_0010029112099879",
                    ...
                ]
            },
            {
                "id": "2",
                "name": "",
                "title": "发生时间",
                "type": "date",
                "options": []
            },
            {
                "id": "3",
                "name": "",
                "title": "具体问题",
                "type": "text",
                "options": []
            },
            ......
        ]
    }
}
```