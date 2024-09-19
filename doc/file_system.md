## 项目文件管理系统
只实现文件管理，权限由业务权限来控制
以工单系统为例：工单负责人有项目文件所有操作权限，其他人有查看权限(fs_mutation)

### 数据结构

| 字段名              | 数据类型 | 描述               |
| ------------------- | -------- |------------------|
| id                  | string   | 文件、目录ID          |
| parent_id           | string   | 父级ID             |
| obj_type            | string   | 对象类型，文件/目录       |
| obj_name            | string   | 对象名，文件或者目录名      |
| file_type           | string   | 文件类型             |
| file_size           | int   | 文件大小（字节为单位）      |
| created_by_id       | string   | 创建人              |
| created_date     | datetime | 创建时间             |
| deleted_by_id       | string   | 删除人              |
| deleted_date        | datetime | 删除时间             |
| related_object_type | string   | 关联对象（工单、项目）      |
| related_object_id   | string   | 关联ID （工单ID，项目ID） |

### 文件类型分三种: 根目录(root_dir), 一般二级目录(dir), 文件(file)

### 创建文件根目录
url: `/filesystem/:related_object_type`  
method: `post`

params：

| 字段名              | 类型 | 是否必须 | 描述             |
|------------------| ---- |------| ---------------- |
| related_object_id | string  | 是    | 关联ID  |

resp:

```json
{
	"code": 0,
	"data": {
		"id": "根目录ID"
	},
	"message": "successful"
}
```


### 获取项目文件根目录
url: `/filesystem/:related_object_type`  
method: `get`

params：

| 字段名              | 类型 | 是否必须 | 描述             |
|------------------| ---- |------| ---------------- |
| related_object_id | string  | 是    | 关联ID  |

resp:

```json
{
	"code": 0,
	"data": {
		"id": "根目录ID"
	},
	"message": "successful"
}
```


### 获取目录下的所有文件和目录
url: `/filesystem/folder/:folder_id`  
method: `get`

resp:

```json
{
	"code": 0,
	"data": {
		"list": [
			{
              "id": "",
              "parent_id": "",
              "obj_type": "",
              "obj_name": "",
              "file_type": "",
              "file_size": "",
              "created_by_id": "",
              "created_date": "",
              "created_by_name": ""
			}
		]
	},
	"message": "successful"
}
```


### 目录创建
url: `/filesystem/folder/:folder_id/create`  
method: `post`

params：json

| 字段名  | 类型 | 是否必须 | 描述        |
|------| ---- |------|-----------|
| name | string  | 是    | 目录名 |

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


### 判断文件名是否存在（上传文件前判断是否有重命，重命会覆盖）
url: `/filesystem/file/check`  
method: `POST`
params：

| 字段名       | 类型 | 是否必须 | 描述   |
|-----------| ---- | -------- |------|
| file_name | str  | 是       | 文件名  |
| folder_id | str  | 是       | 目录ID |


resp:

```json
{
	"code": 0,
	"data": {
		"has": true
	},
	"message": "successful"
}
```


### 上传文件
url: `/filesystem/file/upload`  
method: `POST`
params：dataform

| 字段名 | 类型 | 是否必须 | 描述             |
|--| ---- | -------- |----------------|
| meta | str(object)  | 是       | 元数据对象          |
| file | file         | 是       | 文件   (单文件200M) |
| folder_id | str  | 是       | 目录ID |


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


### 下载文件
url: `/filesystem/file/download/:file_id`  
method: `get`

resp:

```json
{
	"code": 0,
	"data": {
		"file_url": "",
        "filename": "文件名"
	},
	"message": "successful"
}
```


### 删除文件/目录
url: `/filesystem/delete/:id`  
method: `delete`


resp:

```json
{
	"code": 0,
	"data": {
	},
	"message": "successful"
}
```

### 目录/文件重命名
url: `/filesystem/rename/:id`  
method: `put`

params：json

| 字段名  | 类型 | 是否必须 | 描述      |
|------| ---- |------|---------|
| name | string  | 是    | 目录名、文件名 |

resp:

```json
{
	"code": 0,
	"data": {
	},
	"message": "successful"
}
```


### 目录/文件批量移动
url: `/filesystem/move`  
method: `put`

params：json

| 字段名 | 类型     | 是否必须 | 描述        |
|-----|--------|------|-----------|
| ids | []string | 是    | 目录/文件ID列表 |
| folder_id | string | 是    | 目标目录ID    |

resp:

```json
{
	"code": 0,
	"data": {
	},
	"message": "successful"
}
```


### 获取当前目录所有上级目录
url: `/filesystem/folder/:folder_id/parent_dirs`  
method: `get`


resp:

```json
{
	"code": 0,
	"data": {
      "list": [
			{
              "id": "",
              "parent_id": "",
              "obj_type": "",
              "obj_name": "",
              "file_type": "",
              "file_size": "",
              "created_by_id": "",
              "created_date": "",
              "created_by_name": ""
			}
		]
	},
	"message": "successful"
}
```