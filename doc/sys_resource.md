## 资源管理

## 权限

```shell

"p_sys_resource_all": "sys.resource:all"


菜单目录：系统管理-资源管理
资源管理页面路由：sys/resource

```

## 资源管理

上传资源，文件+TAG, meta(scence, X_node_type....)
url: 'sys/resource'      
method: post  
params:    formdata

| 字段名 | 类型 | 是否必须 | 描述 |
| ---- | ---- | --- | ---- |
| meta | dict | 是 | 自定义元数据 |
| description | str | 是 | 描述 |
| file | file | 是 | 文件 |


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

修改资源
url: 'sys/resource/:resource_id'      
method: put  
params:    

| 字段名 | 类型 | 是否必须 | 描述 |
| ---- | ---- | --- | ---- |
| meta | dict | 否 | 自定义元数据 |
| description | str | 否 | 描述 |

resp:  
```json
{
  "code": 0,
  "data": {},
  "message": "successful"
}
```

资源列表, 搜索
url: 'sys/resource'      
method: get  
params:    

| 字段名 | 类型 | 是否必须 | 描述 |
| ---- | ---- | --- | ---- |
| meta | str | 否 | 自定义元数据 |
| description | str | 否 | 描述 |
| page | int | 是 |  |
| size | int | 是 |  |

resp:  
```json
{
  "code": 0,
  "data": {
    "list": [
      {
          "id": "",
          "meta": {},
          "file_mime": "",
          "file_name": "",
          "file_size": 123,
          "description": "",
          "created_by_id": "",
          "created_by_name": "",
          "created_date": "",
          "url": "linkapi..."
      }
    ],
    "page": 1,
    "size": 10,
    "total": 1
  },
  "message": "successful"
}
```

访问单个资源
url: '/resource/:resource_id'      
method: get  
params:    

resp:  filestream

