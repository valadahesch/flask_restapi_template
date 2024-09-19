#### 客户名称 CRM客户查询接口        
url: 'internal/crm/customer'      
method: get  
params:    

| 字段名 | 类型 | 是否必须 | 描述 |
| ---- | ---- | --- | ---- |
| customer | string | 是 | 客户名，没有传空字符串，空字符串查10条（没有会有上万条，为了展示不崩溃） |

resp:
```text
{
  "code": 0,
  "data": {
    "list": [{
        "account_id": "", //客户id
        "account_log_type": "",
        "account_name": "",
        "account_type": "",
        "approval_status": "",
        "crm_account_id": "",
        "hide": false,
        "industry_1st": "",
        "industry_2nd": "",
        "industry_3_dim": "",
        "is_assign_account": false,
        "is_effective_account": true,
        "owner_id": "",
        "owner_name": "",
        "province": "",
        "sales_platform": "",
        "sales_unit": "",
        "status": "",
        "tac_account_log_type": ""
      }]
  },
  "message": "successful"
}
```


#### CRM客户ID查询接口  
url: 'api/internal/crm/customer/:id'  
method: get

resp:
```text
{
  "code": 0,
  "data": {
    "account_id": "", //客户id
    "account_log_type": "",
    "account_name": "",
    "account_type": "",
    "approval_status": "",
    "crm_account_id": "",
    "hide": false,
    "industry_1st": "",
    "industry_2nd": "",
    "industry_3_dim": "",
    "is_assign_account": false,
    "is_effective_account": true,
    "owner_id": "",
    "owner_name": "",
    "province": "",
    "sales_platform": "",
    "sales_unit": "",
    "status": "",
    "tac_account_log_type": ""
  },
  "message": "successful"
}
```

#### CRM销售查询接口  
url: 'api/internal/crm/sysuser'  
method: get  
params:    

| 字段名 | 类型 | 是否必须 | 描述 |
| ---- | ---- | --- | ---- |
| sysuser | string | 是 | 用户名，没有空字符串，空字符串查10条，里头包含了离职人员 |

resp:  
```text
{
  "code": 0,
  "data": {
    "list": [{
        "internal_email": "",
        "sales_unit": "",
        "state": "可用",
        "system_user_id": "", // CRM系统用户ID
        "user_id": "", // SSO用户ID
        "user_name": ""
      }]
  },
  "message": "successful"
}
```

#### CRM销售user_id查询接口  
url: 'api/internal/crm/sysuser/:user_id'  
method: get

resp:  
```text
{
  "code": 0,
  "data": {
    "internal_email": "",
    "sales_unit": "",
    "state": "可用",
    "system_user_id": "", // CRM系统用户ID
    "user_id": "",  // SSO用户ID
    "user_name": ""
  },
  "message": "successful"
}
```


#### 自己及自己所有下属的部门
url: 'api/internal/manage/department'  
method: get

resp:  
```text
{
  "code": 0,
  "data": [
    {
        "id": 1,
        "name": "部门"
    }
  ],
  "message": "successful"
}
```


#### 个人中心信息查询
url: 'api/internal/person/info'  
method: get

resp:  
```text
{
  "code": 0,
  "data": {
        "display_name": "",
        "employee_name": "",
        "mobile": "",
        "email": "",
        "employee_number": "",
        "company"： "",
        "rank": "职级",
        "manage_id": "",
        "manage_name": "",
        "entry_time": "入职时间",
        "department": "",
        "position": "",
        "work_city_adcode": "",
        "work_city": "",
  },
  "message": "successful"
}
```

#### 个人中心编辑信息
url: 'api/internal/person/info'  
method: put  
params:    

| 字段名          | 类型 | 是否必须 | 描述                    |
|--------------| ---- |------|-----------------------|
| manage_id    | string | 否    | 系统用户ID，/hr/staff/list |
| work_city_adcode| string | 否    | 区域编号 |
| work_city | string | 否    | 城市名               |

resp:  
```text
{
  "code": 0,
  "data": {},
  "message": "successful"
}
```

#### 行政区域查询
url: 'api/internal/district/list'  
method: get  

resp:  
```text
{
  "code": 0,
  "data": {
    "list": [{
        "key": "3702",
        "name": "青岛市",
        "parent_key": "37"
    }] 
  },
  "message": "successful"
}
```


#### 个人所有下属
url: 'api/internal/person/subordinate'  
method: get  

resp:  
```text
{
  "code": 0,
  "data": {
    "list": [{
        "id": "",
        "name": "",
        "manage_id": ""
    }] 
  },
  "message": "successful"
}
```


#### 公共接口-上传资源、图片、不需要认证，尽量不用

1.附件管理，附件 ID、200M  
url: `/api/common/attachment/upload`  
method: `post`
permission: 所有登录用户
params：

| 字段名            | 类型 | 是否必须 | 描述                                       |
| ----------------- | ---- | -------- | ----------------------------------------- |
| meta | str(object)  | 是       | 元数据对象                               |
| file | file         | 是       | 文件                                     |

resp:

```json
{
	"code": 0,
	"data": {
		"url": "https://linkapi.hillstonenet.com/api/common/attachment/download/:filename（永久，固定）",
    "filename": "文件名"
	},
	"message": "successful"
}
```



#### 获取附件下载链接

url: `/api/common/attachment/download/:filename`  
method: `get`

resp: 文件流   stream


#### 公共接口-上传资源、图片、需要登录

1.附件管理，附件 ID、200M  
url: `/api/common/auth/attachment/upload`  
method: `post`
permission: 所有登录用户
params：

| 字段名            | 类型 | 是否必须 | 描述                                       |
| ----------------- | ---- | -------- | ----------------------------------------- |
| meta | str(object)  | 是       | 元数据对象                               |
| file | file         | 是       | 文件                                     |

resp:

```json
{
	"code": 0,
	"data": {
		"url": "https://linkapi.hillstonenet.com/api/common/auth/attachment/download/:filename（永久，固定）",
    "filename": "文件名"
	},
	"message": "successful"
}
```



#### 获取附件下载链接

url: `/api/common/auth/attachment/download/:filename`  
method: `get`

resp: 文件流   stream


## 落地城市查询

- method: get
- url: /api/multi_permission/district/list

- permission: p_common_district

- resp:
```
{
    "code": 0,
    "message": "success!",
    "data": {
        "key": "3702",
        "name": "青岛市",
        "parent_key": "37"
    }
}
```

## 查询客户

- method: get
- url: /api/multi_permission/crm/customer

- permission: p_common_customer

- resp:
```
{
    "code": 0,
    "message": "success!",
    "data": {
        "list": [{
        "account_id": "", //客户id
        "account_log_type": "",
        "account_name": "",
        "account_type": "",
        "approval_status": "",
        "crm_account_id": "",
        "hide": false,
        "industry_1st": "",
        "industry_2nd": "",
        "industry_3_dim": "",
        "is_assign_account": false,
        "is_effective_account": true,
        "owner_id": "",
        "owner_name": "",
        "province": "",
        "sales_platform": "",
        "sales_unit": "",
        "status": "",
        "tac_account_log_type": ""
      }]
    }
}
```


## 我的分派员列表

- method: get
- url: /api/internal/crm/my_assigner

- permission: p_internal_api_list

- resp:
```
{
    "code": 0,
    "message": "success!",
    "data": {
        "list": [
           {
              "id": "",
              "internal_email": "",
              "user_name": ""
           }
        ]
    }
}
```