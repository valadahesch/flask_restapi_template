# 辅助平台-报告盖章

说明： 本接口只处理盖章文件的上传和下载，详细盖章操作在OA系统里面。

```
"p_auxiliary_stamp": "auxiliary.stamp:all"

显示路由：
菜单路径：辅助平台-> [待确定]
路由：[待确定]

```
## 数据表（日志记录）

```sql
CREATE TABLE `auxiliary_ stamp_record` (
  `id` int NOT NULL AUTO_INCREMENT,
  `file_name` varchar(200) NOT NULL COMMENT '盖章材料文件名',
  `request_by_id` varchar(20) DEFAULT NULL COMMENT '请求盖章的人员',
  `reason` text COMMENT '请求盖章原因',
  `file_id` varchar(40) NOT NULL COMMENT '盖章材料ID（方便云平台获取文件）',
  `stamp_by_id` varchar(20) NOT NULL COMMENT '执行盖章操作的人员',
  `status` tinyint(1) NOT NULL COMMENT '是否盖章成功(1 是正在盖章中，2是盖章成功， 3是盖章失败)',
  `created_date` datetime NOT NULL COMMENT '创建时间',
  `stamp_date` datetime NOT NULL COMMENT '盖章时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='材料盖章日志记录';
```

## API


### 上传盖章文件
URL: '/api/auxiliary/stamp'  
method: `post`
permission: p_auxiliary_stamp
content-type: multipart/form-data
time-out: 5分钟 
params：

| 字段名            | 类型 | 是否必须 | 描述                                       |
| ----------------- | ---- | -------- | ----------------------------------------- |
| related_object | str  | 是       | 固定为字符串："auxiliary_stamp"       |
| file | file         | 是       | 文件, max-length 200M            |
| reason | str  | 否       | 请求盖章原因                           |
| request_by_id | str  | 否       | 请求人id, a替b,传的b                        |
 
 // request_by_id 复用/staff/list接口


```json
{
	"code": 0,
	"data": {
        "id": "文件id"
	},
	"message": "successful"
}
```

### 获取盖章后的文件
URL: '/api/auxiliary/stamp/ :file_id'  
method: `get`
permission: p_auxiliary_stamp
params：

| 字段名            | 类型 | 是否必须 | 描述                                       |
| ----------------- | ---- | -------- | ----------------------------------------- |
| file_id | str  | 是       | 文件id                             |


```json

#情况一： 生成盖章文件成功

{
	"code": 0,
	"data": {
    "file_url": "下载链接"
  },
	"message": "生成盖章文件成功"
}
#情况二: 正在生产盖章文件中
{
	"code": 0,
	"data": {
    "file_url": "" // 空字符串
  },
	"message": "正在生成盖章文件中"
}

#情况二： 生成盖章文件失败

{
	"code": -1,
	"data": {},
	"message": "生成盖章文件失败，请检查文件是否符合规范"
}
```


### 获取盖章文件历史记录

URL: '/api/auxiliary/stamp/list'  
method: `get`
permission: p_auxiliary_stamp
params：

| 字段名            | 类型 | 是否必须 | 描述                                       |
| ----------------- | ---- | -------- | ----------------------------------------- |
| page | int  | 否       | 第几页                             |
| size | int  | 否       | 页面尺寸                             |
| file_name    | str  | 否       | 文件名称（模糊查询）                             |
| created_date  | list(str)  | 否         | [创建开始时间,创建的结束时间]          |
| stamp_date    | list(str)  | 否         | [盖章开始时间,盖章结束时间]       |
| reason      | str  | 否       | 盖章原因  （模糊查询）                           |
| request_by_id | str  | 否       | 请求人                             |
| stamp_by_id | str  | 否       | 请求人                             |
| status | list(int)  | 否       | 盖章结果 [1, 2]  (1 是正在盖章中，2 是盖章成功， 3是盖章失败)  |


```json

{
	"code": 0,
	"data": {
        "list": [
            {
                "file_id": "文件唯一标识id",
                "reason": "由于什么原因盖章",
                "request_by_id": "请求人id",
                "request_by_name": "请求人昵称",
                "stamp_by_id": "盖章人id",
                "stamp_by_name": "盖章人昵称",
                "created_date": "2024-04-12 10:40:52",  // 请求盖章时间
                "stamp_date": "2024-04-12 10:40:52",   // 完成盖章时间
                "file_name": "文件.pdf",
                "status": 1  // 1 是正在盖章中，2是盖章成功， 3是盖章失败
            }
        ],
            "page": 1,
            "size": 10,
            "total": 15
	},
	"message": "sucess"
}

```