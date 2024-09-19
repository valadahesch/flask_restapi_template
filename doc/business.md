# 商机平台

## 商机线索
### 需求
1.创建商机
```text
商机信息：
单位名称、需求描述、CRM客户（搜索并选择）、归属销售（搜索并选择）、联系人姓名、联系人角色（可选项）、联系方式、项目所在省份、项目所在城市

CRM客户： 需搜索从CRM同步过来的客户信息， 显示 <account_name>
归属销售： 需搜索从CRM同步过来的销售信息， 显示 <username>-<sales_unit>
联系人角色： 最终客户（1）、合作伙伴（2）、山石员工（3）、服务中心（4）、系统集成商（5）、联系人（6）
```

2.商机推送
创建商机后、点击推送选择邮件推送、企业微信，确认进行商机推送，部分销售有平台级经理抄送
前端交互逻辑：创建商机的时候，默认勾选推送，成功后，关drawer,刷列表，列表可再次推送，显示wework和email推送的状态。点详情或者推上，都可以再次进入，再次推送。


3.查询自己分享的商机
```text
线索编号、创建时间、单位名称、客户名称、归属销售、联系人角色、联系人姓名、联系人方式、项目所在省份城市、推送方式、详情（需求描述）
```

### 接口
1.公共接口，CRM客户查询接口
url: 'api/internal/crm/customer'  

2.公共接口，CRM客户ID查询接口  
url: 'api/internal/crm/customer/:id'  

3.公共接口，CRM销售查询接口  
url: 'api/internal/crm/sysuser'  

4.公共接口，CRM销售user_id查询接口  
url: 'api/internal/crm/sysuser/:user_id'  

5.创建商机接口  
url: 'api/business/leads'  
method: post  
params:

| 字段名 | 类型 | 是否必须 | 描述 |
| ---- | ---- | --- | ---- |
| company_name | string | 是 | 单位名称 |
| description | string | 是 | 需求描述 |
| customer_id | string | 是 | CRM客户id |
| customer_name | string | 是 | CRM客户id |
| owner_id | string | 是 | 归属销售user_id |
| owner_name | string | 是 | 归属销售用户名 |
| contact_name | string | 是 | 联系人姓名 |
| contact_role | int | 是 | 联系人角色 |
| contact_way | string | 是 | 联系方式 |
| province | string | 否 | 项目所在省份 |
| city | string | 否 | 项目所在城市 |

resp:  
```text
{
  "code": 0,
  "data": {
    "id": ""
  },
  "message": "successful"
}
```

6.商机查询列表接口，只查自己历史分享的（自己创建的）  
url: 'api/business/leads'  
method: get

| 字段名 | 类型 | 是否必须 | 描述 |
| ---- | ---- | --- | ---- |
| company_name | string | 否 | 单位名称 |
| lead_code | string | 否 | CRM线索编号 |
| customer_name | string | 否 | 客户名称 |
| owner_id | string | 否 | 归属销售系统用户ID |
| page | int | 否 | 页数 |
| size | int | 否 | 每页行数 |

展示排序： 线索编号lead_code、创建时间create_time、单位名称company_name、
客户名称customer_name、归属销售owner_name、联系人角色contact_role、联系人姓名contact_name、联系方
式contact_way和项目所在省份城市(province,city)

注释： wework_pushed和email_pushed和实际时间状态不一定能对上。

resp:  
```text
{
  "code": 0,
  "data": {
      "list": [{
            "id": "",
            "lead_code": "",
            "company_name": "",
            "customer_name": "",
            "owner_name": "",
            "contact_name": "",
            "contact_role": 1,
            "contact_way": "",
            "province": "",
            "city": "",
            "create_time": "",
            "wework_pushed": 1, // TODO 定义一下状态，枚举表
            "email_pushed": 2
      }],
      "page": 1,
      "size": 1,
      "total": 1
  },
  "message": "successful"
}
```

7.商机推送接口  
url: 'api/business/leads/push/:id'  
method: put

注释： email和wework，必须有一个
params:

| 字段名 | 类型 | 是否必须 | 描述 |
| ---- | ---- | --- | ---- |
| email | bool | 否 | 邮件方式 |
| wework | bool | 否 | 企业微信方式 |

resp:  
```text
{
  "code": 0,
  "data": {},
  "message": "successful"
}
```

8.商机详情接口  
url: 'api/business/leads/detail/:id'
method: get

resp:  
```text
{
  "code": 0,
  "data": {
    "description": "",
    "id": "",
    "lead_code": "",
    "company_name": "",
    "customer_id": "",
    "customer_name": "",
    "owner_id": "",
    "owner_name": "",
    "contact_name": "",
    "contact_role": 1,
    "contact_way": "",
    "province": "",
    "city": "",
    "create_time": "",
    "wework_pushed": 1, // TODO 定义一下状态，枚举表
    "email_pushed": 2
  },
  "message": "successful"
}
```