# 辅助平台-SN查询

```
"p_auxiliary_sn_query": "auxiliary.sn_query:all"

显示路由：
菜单路径：辅助平台->SN查询
路由：/auxiliary_platform/sn_query

```

## API


### 提取SN
URL: '/api/auxiliary/sn/extract'  
Method: GET  
Params：  

| 字段名  | 类型     | 是否必须 | 描述    |
|------|--------|------|-------|
| text | string | 是    | 解析的文本 |

```json
{
  "code": 0,
  "data": {
    "list": [""]
  },
  "message": "successful"
}
```

### 获取SN信息 
URL: '/api/auxiliary/sn/query'  
Method: GET  
Params：  

| 字段名    | 类型     | 是否必须 | 描述        |
|--------|--------|------|-----------|
| source | string | 否    | 查找源（CRM、） |
| sn     | list   | 是    | SN列表      |
| page     | int   | 是    |       |
| size     | int   | 是    |       |


```json
{
  "code": 0,
  "data": {
     "sn1": {
        "list": [{
          "lic_type": "", 
          "sku": "", 
          "materialtype": "",
          "product_model": "", 
          "product_type": "",
          "start_date": "",
          "end_date": "",
          "account_name": "",
          "account_type": "", 
          "account_owner": ""
        }],
        "page": 1,
        "size": 2,
        "total": 2
      }
  },
  "message": "successful"
}
```