# 在线工具-配置转山石

```
"p_online_tools_conf2hs": "online_tools.conf2hs:all"

显示路由：
菜单路径：在线工具-配置转山石
路由：/onlinetools/conf2hs/

```

## API

### 获取商列表
URL: '/onlinetools/conf2hs/brands'
Method: GET
```json
{
  "code": 0,
  "data": {
    "list": [
      {"key": "legendsec", "label": "网神"}
    ]
  },
  "message": "successful"
}
```

### 获取版本和模块选项
URL: '/onlinetools/conf2hs/brand/items'
Method: GET
Params: 

| 字段名 | 类型 | 是否必须 | 描述 |
| ---- | ---- | --- | ---- |
| brand_name | string | 是 | brand_name |

```json
{
  "code": 0,
  "data": {
    "version": ["1.1"],
    "models": [
      {"key": "address", "label": "地址簿"}
    ],
    "export": [
      {"key": "configure_translation", "label": "配置翻译"}
    ]
  },
  "message": "successful"
}
```

### 解析配置文件
异步解析，通过查看历史result查看状态
URL: '/onlinetools/conf2hs/brand/transform'
Method: POST
Params: Form

| 字段名 | 类型 | 是否必须 | 描述 |
| ---- | ---- | --- | ---- |
| file | files | file_str其中一个必须 | 配置文件 |
| file_str | str | 否 | 配置文件文本 |
| brand_name | str | 是 | 厂商Key |
| brand_version | str | 是 | 厂商版本 |
| models | list[str] | 是 | 模块key |
| export | list[str] | 是 | 模块key |


```json
{
  "code": 0,
  "data": {},
  "message": "successful"
}
```

### 获取历史记录
URL: '/onlinetools/conf2hs/history'
Method: GET
Params: 

| 字段名 | 类型 | 是否必须 | 描述 |
| ---- | ---- | --- | ---- |
| page | files | 否 | 页 |
| size | str | 否 | 每页数 |
| brand_name | str | 否 | 厂商名称 |


```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": "", 
        "file_name": "",
        "brand_name": "",
        "export": [],
        "created_date": "",
        "result": "running、successful、failed"
      }
    ]
  },
  "message": "successful"
}
```

### 获取历史详请
URL: '/onlinetools/conf2hs/history/:history_id'
Method: GET

```json
{
  "code": 0,
  "data": {
    "id": "",
    "file_name": "",
    "brand_name": "",
    "brand_version": "",
    "models": [],
    "export": [],
    "result": "",
    "created_date": "",
    "attachments": [
			{ "id": "", "filename": "", "file_size": 0, "file_type": "" }
		]
  },
  "message": "successful"
}
```