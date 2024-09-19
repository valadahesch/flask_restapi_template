# 辅助平台-许可申请平台

```
"p_auxiliary_license": "auxiliary.license:all"

显示路由：
菜单路径：辅助平台-> [待确定]
路由：[待确定]

```
## 数据表（日志记录）

```sql
/* 请确认以下SQL符合您的变更需求，务必确认无误后再提交执行 */

CREATE TABLE `auxiliary_apply_license_record` (
	`id` varchar(20) NOT NULL COMMENT 'ID',
	`account_id` varchar(40) NOT NULL COMMENT '设备所有客户名称',
	`sn` varchar(2000) NOT NULL COMMENT '申请许可的设备序列号',
	`product_name` varchar(40) NOT NULL COMMENT '设备名称',
	`license` varchar(2000) NOT NULL COMMENT '申请的许可类型',
	`created_date` datetime NOT NULL COMMENT '申请许可时间',
	`created_by_id` varchar(20) NOT NULL COMMENT '执行申请许可操作的用户',
	`email` varchar(40) NULL COMMENT '申请人邮箱',
	`status` varchar(40) NULL COMMENT '许可申请状态',
	`order_id` varchar(40) NOT NULL COMMENT '许可文件下载id',
	PRIMARY KEY (`id`)
) ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8 COLLATE=utf8_general_ci
COMMENT='许可申请记录表';

```

## API


### 申请许可接口
**URL**: '/api/auxiliary/license'     
**method**: `post`  
**permission**: p_auxiliary_license  
**params**：  
 

| 字段名            | 类型 | 是否必须 | 描述                                       |
| ----------------  | ---- | -------- | ---------------------------------------- |
| account_id          | str  | 是  |  客户名称, 关联接口: `internal/crm/customer`      |
| product_name      | str  | 是  |  产品名称, 举例: "SG-6000-E5560" |  
| sn                | str  | 是  |  设备sn, 举例:  "2508000100020003" |
| lic_params        | list | 是  |  许可类型, 举例: ["platform", "qos", "ips"]    |
| end_time          | str  | 是  |  该批许可到期时间，格式: "yyyy-mm-dd"           |

> 目前lic_params可选项: "platform"、"appdb"、"qos"、"ips"、"av"、"urldb"


**请求举例**
> 单次申请某个型号设备, 单个设备的许可
```json

{
	"account_id": "客户ID",
	"end_time": "2024-07-19",
	"product_name": "SG-6000-E5560",
	"lic_params": ["platform", "qos", "ips"],
	"sn": "2508000100020003" 
}
```

**resp**:  
```json
{
	"code": 0,
	"data": {
        "id": "许可申请订单id"
	},
	"message": "successful"
}
```

### 获取许可文件
**URL**: '/api/auxiliary/license/download/: license_id'    
**method**: `get`  
**permission**: p_auxiliary_license  
**params**：  

| 字段名            | 类型 | 是否必须 | 描述                                       |
| ----------------- | ---- | -------- | ----------------------------------------- |
| license_id | str  | 是       | 许可订单id                            |


```json

{
	"code": 0,
	"data": {
		"file_url": ""
	},
	"message": "正在生成许可文件中"
}

```


### 获取盖许可申请历史记录

URL: '/api/auxiliary/license/list'  
method: `get`
permission: p_auxiliary_license
params：

| 字段名            | 类型 | 是否必须 | 描述                                       |
| ----------------- | ---- | -------- | ----------------------------------------- |
| crm_order    | str   | 否       | crm编号（模糊查询）                             |
| account_id | str | 否 | 客户名称ID(模糊查询)  | 
| sn      | str | 否       | 单个SN                       |
| product_name | str  | 否       | 产品名称                              |
| lic_param | list(str)  | 否       | 申请的许可类型  |
| status | list(str) | 否 | 许可申请状态 ['success', 'fail', 'pending']  | 


```json

{
	"code": 0,
	"data": {
        "list": [
            {
                "id": "id",
				"order_id": "申请许可订单ID",
                "account_id": "客户名称ID",
				"account_name": "客户名称",
                "sn": "2508000100020003",
                "product_name": "SG-6000-E5560",
                "lic_params": ["platform", "qos", "ips"], 
                "created_by_id": "申请人id",
                "created_by_name": "申请人昵称",
				"created_date": "创建时间",
				"status": "success",
				"end_time": "许可有效期截止时间",
				"error_msg": "申请失败原因"
            },
			{...}
        ],
        "page": 1,
        "size": 10,
        "total": "16"
	},
	"message": "sucess"
}

```



--- 
下面需求暂时不需要实现
---


###  搜索枚举crm_order

###  搜索枚举customer

###  搜索枚举product_name

###  搜索枚举lic_params（可申请的许可类型）