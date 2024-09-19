## TODO
 

---

### 一 、数据表

#### 1.消息模版表

```shell


CREATE TABLE `message_template` (
  `id` varchar(16) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '唯一标识',
  `template_number` varchar(10) NOT NULL COMMENT '模版编号（可重复）',
  `subject` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '模版主题',
  `content` longtext NOT NULL COMMENT '模版内容',
  `created_by_id` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '创建人',
  `created_date` datetime NOT NULL COMMENT '创建时间',
  `last_modified_by_id` varchar(100) NOT NULL COMMENT '最后修改人',
  `last_modified_date` datetime NOT NULL COMMENT '最后修改时间',
  `enable` tinyint(1) NOT NULL COMMENT '是否可用',
  `media_type` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '模版类型,邮件，短信，企业微信',
  `language` varchar(6) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '语种：简体中文(zh_cn) 、English-United States(en_us)',
  `remark` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT '备注',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



```


---
### 二、平台权限划分

```shell


菜单：通信平台->消息网关->模板管理

新增模板页面路由 /communication_platform/message_gateway/message_template/add
模版列表页面路由 /communication_platform/message_gateway/message_template/list
模板修改页面路由 /communication_platform/message_gateway/message_template/edit/:template_id 
模板查看页面路由 /communication_platform/message_gateway/message_template/detail/:template_id

权限：
permission : p_message_gateway_template_all   "message_gateway:template:all"
```


---



### 三、 接口


#### - 新增消息模版

```shell

- method: POST
- url: /api/message_gateway/template
- param: {
    "template_number": "模版编号",
    "subject": "模版主题",
    "content": "模版内容",
    "enable": true,
    "media_type": "模版类型,邮件，短信，企业微信应用，企业微信群机器人等",
    "language": "语种, 选择项: zh_cn 、en_us",
    "remark": "【可选项】备注"
}

//简体中文(zh_cn) 、English-United States(en_us)

- permission: p_message_gateway_template_all
```

- response example

```json
{
    "code": 0,
    "message": " success!",
    "data": { 
        "id": "消息模版ID"
    }
```

#### - 修改消息模版

```shell

- method: PUT
- url: /api/message_gateway/template/:message_template_id
- param: {
    "template_number": "模版编号",
    "subject": "模版主题",
    "content": "模版内容",
    "enable": true,
    "media_type": "模版类型,邮件，短信，企业微信应用，企业微信群机器人等",
    "language": "选择项: zh_cn 、en_us",
    "remark": "【可选项】备注"
}
- permission: p_message_gateway_template_all
```

- response example

```json
{
    "code": 0,
    "message": " success!",
    "data": {}
```

#### - 获取消息模版

```shell

- method: GET
- url: /api/message_gateway/template/:message_template_id
- param:
- permission: p_message_gateway_template_all
```

- response example

```json
{
    "code": 0,
    "message": " success!",
    "data": {
        "id": "ID",
        "template_number": "模版编号",
        "subject": "模版主题",
        "content": "模版内容",
        "created_by_id": "创建人id",
        "created_by_name": "创建人昵称",
        "created_date": "创建时间",
        "last_modified_by_id": "最后修改人id",
        "last_modified_by_name": "最后修改人昵称",
        "last_modified_date": "最后修改时间",
        "enable": true,
        "media_type": "模版类型,邮件，短信，企业微信应用，企业微信群机器人等",
        "language": "zh_cn",
        "remark": "备注"
    }
```


#### - 获取消息模版列表

```shell

- method: GET
- url: /api/message_gateway/template/list
- param:
    {
        "enable": [true,false],
        "like": "template_number, subject, content, remark模糊搜索"，
        "media_type": ["sms"],
        "language": ["zh_cn"],
        "page": 1,
        "size": 10
    }
- permission: p_message_gateway_template_all
```

- response example

```json
{
    "code": 0,
    "message": " success!",
    "data": {
        "list": [
            {
                "id": "ID",
                "template_number": "模版编号",
                "subject": "模版主题",
                "content": "模版内容",
                "created_by_id": "创建人id",
                "created_by_name": "创建人昵称",
                "created_date": "创建时间",
                "last_modified_by_id": "最后修改人id",
                "last_modified_by_name": "最后修改人昵称",
                "last_modified_date": "最后修改时间",
                "enable": true,
                "media_type": "模版类型,邮件，短信，企业微信应用，企业微信群机器人等",
                "language": "zh_cn",
                "remark": "备注"
            },
            {...}
        ],
        "page": 1,
        "size": 10,
        "total": 88
    }
```