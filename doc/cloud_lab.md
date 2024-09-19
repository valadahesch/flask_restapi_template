## TODO



> cloud_lab_cell
>
> （1）看login登录方式如何设置
>
> cloud_lab_user_template_instance
>
> （1）新建instance失败（重建环境）或者使用过程无法管理/无法启动等未知故障（重建环境）------>新建环境
>
> （2）登录方式：地址栏跳转是如何进行区分不同设备的，地址栏看是一致的
>
>  (3) 接口编号
>  (4) 创建排队，有多少人，预计时间
>  (5) 创建负载均衡
>  (6) VNC websocket
>  (7) 虚拟机登陆新开tab页面
>  （8）创建实例完成之后再重新获取一次实例信息（instance.status = 2）
> (9) 测试实验环vlan等协议流量、mgt网卡显示隐藏(是否加入管理网络)
> 
## （10）验证多个进程对象是否使用的同一个kvm client对象

---


登录方式：

(1) gui 图形化显示（VNC、 RDP）
(2) CLI 命令行（SSH TELNET）
(3) webui 反向代理（HTTP HTTPS）





### 一 、数据表

`

#### 1. 模板表

```shell
-- techadmin.cloud_lab_template definition

CREATE TABLE `cloud_lab_template` (
  `id` varchar(20) NOT NULL COMMENT '模板ID',
  `name` varchar(20) NOT NULL COMMENT '模板名称',
  `description` varchar(20) NULL COMMENT '模板描述',
  `enable` boolean NULL COMMET '模板是否启用/发布（常见于管理员新建/管理模板，enable不能编辑, 目前无这个需求，用不到）'
  `picture` varchar(20) NULL COMMET '模板图片'
  `cells` text NULL COMMET '模板数据, 格式参考cell, list(cell)'
  `create_by` varchar(50) DEFAULT NULL COMMENT '创建人ID',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` varchar(50) DEFAULT NULL COMMENT '更新人ID',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```



#### 2. 细胞对象

```json
    {
        "id": "cell id",
        "graph": {shape,size,view,zIndex,ports,data:{picture_url}},
        "data": {
            "key": "firewall",
            "input_struct": [
                {
                    "key": "name",
                    "value": "防火墙-1"
                },
                {
                    "key": "software_version",
                    "value": "stoneos_5_5_r8p10",
                    "label": "软件版本文本",//有些前端需要做展示的，前端传, select里头的，还有可能refer_select,有unit的前端拼一下
                },
                {
                    "key": "interface_list",
                    "value": [
                        {
                            "index": 0,
                            "name": "gfgf",
                            "position": "top",
                            "_id": "ed7550b9-c3b2-4f6e-b959-7e6d55a11707",
                            "key": "0.65653617347068"
                        }
                    ]
                },
                {
                    "key": "license_list",
                    "value": [
                        {
                            "lic_type": "platform",
                            "value": 3
                        }
                    ]
                }
            ]
        }
    }
```

#### . 获取实例虚拟机实际登录地址

```shell
- method: GET
- url: /api/cloud_lab/user/interface/<instance_id>/<node_id>/<type>  # type: ssh, vnc, web(https) 
- resp: 
{
  "code": 0,
  "data": {
    "url": "https://云实验室登录服务域名/api/cloud_lab/login/<instance_id>/<node_id>/<type>?token=''"
  },
  "message": ""
}
```

#### 云实验室登录服务接口
token头认证

前端模板：render_template("ssh.html/vnc.html", {instance_id: "", node_id:"", token:""})

type: ssh => ssh.html,  vnc => vnc.html


#### 3. 镜像表

```shell
-- techadmin.cloud_lab_images definition

CREATE TABLE `cloud_lab_images` (
  `id` varchar(20) NOT NULL COMMENT 'image id',
  `name` varchar(20) NOT NULL COMMENT '镜像名称',
  `interface` int(20) NOT NULL COMMENT '镜像接口数目',
  `description` varchar(20) NULL COMMENT '镜像描述',
  `cpu` varchar(20) NOT NULL COMMENT '预定义CPU数量',
  `interface_num` int(20) NOT NULL COMMENT '预定义接口数量',
  `ram` varchar(20) NULL COMMENT '预定义内存大小',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

```



#### 4. 用户实例列表

```shell
-- techadmin.cloud_lab_user_template_instance definition

CREATE TABLE `cloud_lab_user_template_instance` (
  `id` varchar(20) NOT NULL COMMENT 'instance id',
  `user_id` varchar(20) NOT NULL COMMENT '用户ID',
  `template_id` varchar(20) NOT NULL COMMENT '模板ID',
  `create_time` varchar(20) NULL COMMENT '模板创建时间',
  `update_time` varchar(20) NULL COMMENT '最后操作时间',
  `status` varchar(20) NULL COMMENT 'using/delete/failure'
  `cells` text NULL COMMET '模板数据, 格式参考cell, list(cell)',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

---



### 二、平台权限划分

```shell

"p_learning_platform_cloud_lab": "learning_platform.cloud_lab:list",   # 用户的所有页面
"p_learning_platform_cloud_lab_manage_edit": "learning_platform.cloud_lab.manage.edit:mutation",   # 保存模板，修改模板, 启用/不启用


显示路由：

菜单路径：学习平台-云实验室-模板
路由：/learning_platform/cloud_lab/templates

菜单路径：学习平台-云实验室-实例
路由：/learning_platform/cloud_lab/instances


隐藏路由： 

菜单路径：学习平台-云实验室-模板[模板id], 配置的时候为"模板详情",tab签显示为“模板[模板id]”,下面这个:template_id必须这个名称，否则前端找不到
路由：/learning_platform/cloud_lab/templates/:template_id

菜单路径：学习平台-云实验室-实例[实例id]
路由：/learning_platform/cloud_lab/instances/:instance_id



菜单路径：学习平台-云实验室-自定义拓扑, 入口按钮是实例列表上方, 权限为 p_learning_platform_cloud_lab， 
有平台级的p_learning_platform_cloud_lab_manage_edit 控制 保存为模板按钮
路由：/learning_platform/cloud_lab/custom_topology

```

TODO 模板列表需要整改，有p_learning_platform_cloud_lab_manage_edit权限的，有enable等模板的列表
TODO 后端保存为模板，保存为实例，需要先验证数据是否合法，不合法接口提示

---



### 三、 接口

##### 接口权限

所有/cloud_lab/user的接口, permission都是learning_platform.cloud_lab:list

/cloud_lab/manage接口的，大部分为learning_platform.cloud_lab.manage:list


#### . 获取用户模板列表

```shell
- method: GET
- url: /api/cloud_lab/user/templates    
- permission : learning_platform.cloud_lab:list, cloud_lab_template表为enable数据。
```

- response example

```json
{
    "code": 0,
    "message": "acquire success!",
    "data": {
    	"list":[
            {
    			"id": "template_id",
                "name": "IPSec VPN场景",
                "key": "ipsec_vpn",
                "description": "...",
    			"picture": "模板图片",
    			"create_by": "创建人id",
      			"create_time": "创建时间",
        		"create_by_name": "创建人名称",
    			"update_by": "",
      			"update_time": "",
        		"update_by_name": ""
            }
	]
}
}
```



#### . 显示模板拓扑信息

```shell
- method: GET
- url: /api/cloud_lab/user/template/:template_id
- permission : learning_platform.cloud_lab:list
```

- response（从cloud_lab_cell表中获取）:

- response example

```json
{
    "code": 0,
    "message": "Successfully listed topology .",
    "data": {
        "id": "template_id",
        "name": "IPSec VPN场景",
        "key": "ipsec_vpn",
        "description": "...",
        "picture": "模板图片",
        "create_by": "创建人id",
        "create_time": "创建时间",
        "create_by_name": "创建人名称",
        "update_by": "",
        "update_time": "",
        "update_by_name": "",
        "cells":list(cell)
    }
}
```



#### . 实例列表

```shell
- method: GET
- url: /api/cloud_lab/user/instances
- params: # 下面参数全部为可选参数
{{
    "name": "实例名称",
    "status": 2 //实例状态,
    "page": 1 //第几页，
    "size": 12 //建议每页12条
}}
```

```json
{
    "code": 0,
    "message": "",
    "data": {
        "list": [{
            "id": "instance id",
            "name": "实例名称",
            "template_id": '模板ID',
            "template_name" : "模板名称",
            "create_time": '模板创建时间',
            "status": 'using/delete/failure',
            "expire": 3600
        }]
    }
}
```


#### . 创建实例（按钮事件），从模板创建实例
### todo 后端提前检测服务是否可用，不可用code-1, 前端强化try catch 

```shell
- method: POST
- url: /api/cloud_lab/user/instance
- params: {{template_id:"", name:""}}
# 后期传输可能会进行更改，node的ip信息
```

```json
- resp:
(1)success
{
    "code": 0, 
    "data": {
        "id": "instance_id",
    },
    "message": "The template is being created ."
}
# instance_id来源于cloud_lab_user_template_instance的id

(2)failure
{"code": -1, "data": {}, "message": "..."}
```


# deprecated 废弃
#### . 创建实例进度，设备状态

```shell
- method : GET
- url: /api/cloud_lab/user/instance/:instance_id/progress_node_status
```

```json
- resp:
{
    "code": 0, 
    "data": {
        "status": 1, //1进行中，2创建成功, 3创建失败（有一个设备失败都是失败）
        "schedule": 50, //进行中的时候进度小于100，成功为100，失败为-1
        "device_status": [
            {
                "id": "node_id",
                "status":1 / 2 / 3 - # 进行中/成功/失败,
            }
        ],
        "step": [
            {
                    "name": "host",
                    "label": "宿主机"
                    "value": 1
            },
            {
                    "name": "network",
                    "label": "网卡"
                    "value": 1
            },
            {
                    "name": "vm",
                    "label": "虚拟机"
                    "value": 1
            },
            {
                    "name": "config",
                    "label": "初始化配置"
                    "value": 1
            }
        ] 
    }, 
    "message": "The template is being created ."
}

```


#### . 创建实例进度，启动中的状态, 8秒一次

```shell
- method : GET
- url: /api/cloud_lab/user/instance/:instance_id/progress/starting
```

```json
- resp:
{
    "code": 0, 
    "data": {
        "status": 1, //1创建中，2创建成功, 3创建失败，5排队中（有一个设备失败都是失败）
        "queue": 10, //排队的实例数量
        "estimate_create_time": 200, //预估创建时长，秒
        "create_time": "2023-10-07 12:12:12", //实例创建时间
        "server_time": "2023-10-07 12:14:12", //请求那一刻服务端的时间
        "local_time": "", //客户端本地时间，请求那一刻的时间
        "schedule": 50, //进行中的时候进度小于100，成功为100，失败为-1
        "step": [
            {
                    "name": "host",
                    "label": "创建实验主机",
                    "status": 1,
                    "spend_time": 200,
                    "detail": []
            },
            {
                    "name": "network",
                    "label": "创建内部网络",
                    "status": 1,
                    "spend_time": 200,
                    "detail": [{
                        "id":"",
                        "name":"网卡名",
                        "status": 2 
                    }]
            },
            {
                    "name": "vm",
                    "label": "创建节点",
                    "status": 1,
                    "spend_time": 0,
                    "detail": [{
                        "id": "",
                        "name": "node1",
                        "status": 2 
                    }]
            },
            {
                    "name": "config",
                    "label": "初始化节点配置",
                    "status": 1,
                    "spend_time": 0,
                    "detail": [{
                        "id": "",
                        "name": "node1",
                        "status": 2 
                    }]
            }
        ] 
    }, 
    "message": ""
}

```


#### . 实例运行时的状态， 8秒一次

```shell
- method : GET
- url: /api/cloud_lab/user/instance/:instance_id/progress/running
```

```json
- resp:
{
    "code": 0, 
    "data": {
        "status": 2 / 3,
        "expire": 3600,
        "device_status": [
            {
                "id": "node_id",
                "status": 8/ 9 / 2 / 3 - # 重启中/关机/成功/失败,
                "port_status": [{"index":0, "id":"portid", "status": "up/down/todo其他不确定"}],
                "login": [{
                    "type": "string",
                    "url": "string",
                    "username": "string",
                    "password": "string",
                    "avalibale": false
                }],
                "action": [
                    {
                        type:"reboot", 
                        label:"重启", 
                        available: false
                    },
                    {
                        type:"shutdown",
                        label:"关机", 
                        available: true
                    }
                ]
            }
        ]
    }, 
    "message": ""
}

```



#### .  获取实例信息（创建实例成功后）

```shell
- method: GET
- url: /api/cloud_lab/user/instance/:instance_id
```

```json

resp:
{
    "code": 0, 
    "data": {
        "id": "instance id",
        "name": "实例名称",
        "description": "",
        "template_id": '模板ID',
        "template_name" : "模板名称",
  		"create_time": '实例创建创建时间',
  		"status": 'using/delete/failure',
        "cells": list(cell)
    },
    "message": "Template created."
}

```

#### .  更新实例刷新时间（创建实例成功后）

```shell
- method: PUT
- url: /api/cloud_lab/user/instance/:instance_id/renewal
```

```json
resp:
{
    "code": 0, 
    "data": {},
    "message": "Template created."
}

```

#### .  获取用户在当前设备下是否有创建中的实例
```shell
- method: GET
- url : /user/template/<string:template_id>/instance_startup
```

```json
resp:
{
    "code": 0,
    "message": "",
    "data": {
        "list": [{
            "id": "instance id",
            "name": "实例名称",
            "template_id": '模板ID',
            "template_name" : "模板名称",
            "create_time": '模板创建时间',
            "status": 'using/delete/failure',
        }]
    }
}
```

#### .  删除实例（正在运行中）

```shell
- method: DELETE
- url: /api/cloud_lab/user/instance/:instance_id
```

```json
resp:
{
    "code": 0, 
    "data": {},
    "message": "Template deleted."
}

```

#### . 开关机，重启
```shell
- method: PUT
- url : /api/cloud_lab/user/instance/:instance_id/:node_id
- params: {{action:"shutdown/reboot/poweron"}}
```

```json
resp:
{
    "code": 0, 
    "data": {},
    "message": ""
}

```


#### webssh
```shell
# 加密内容
{
  "user_info": {"id": "", "display_name": ""},
  "login_info": {'host': '', 'port': 22, 'username': '', 'password': ''}
}

# 公钥
public_pem = b"""-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA5r/Um6EqlaX3pa+j+dyx
kGuEK0WKIl+FZy0WEyqGA5DVjeYaAHb+G2DZMqqbtegI5xDq+xKLz99BkwhXq4ih
U/6ysNhyeDWarPk5EPtmrEAZVx9dWY6fBK+vPMiW7AVaHBLgSqeJKkTvYoJ2ImgT
WXa1wh4TRPi3bWSTyTTimPbOTQvsvQEQVhx9oXh2vZ+shOBU2ToLSkLtzqoCuaSd
PTAbqSVZFRJS37tIdvkmd52AWZiWPkVDGJnmjoHlW9yvlZ3MQAdd6jrHqPdqay0Z
QjBUBJgPeOQp8YbRqicOPGmLDjjgAORMAvma83TXcX9Hv/1OEny6vyf9e3jPFnbR
mQIDAQAB
-----END PUBLIC KEY-----
"""

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
public_key = serialization.load_pem_public_key(public_pem)
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        ciphertext = ciphertext.hex()
```


#### 自定义拓扑界面 节点信息列表
```shell
- method: GET
- url : /api/cloud_lab/custom_topology/node_meta
```

```json
resp:
{
    "code": 0,
    "data": 参见 https://git.tac.hillstonenet.com/devops/manage-site/-/blob/feature/cloudlab/mock/api/learning/node_meta.json ,
    "message": ""
}

```

#### 自定义拓扑界面，保存为模板，权限为p_learning_platform_cloud_lab_manage_edit
```shell
- method: POST
- url : /api/cloud_lab/custom_topology/template
- params: {
    "name": "IPSec VPN场景",
    "description": "...",
    "picture": "资源管理的链接",
    "cells":  [] //参考细胞对象
}
```

```json
resp:
{
    "code": 0,
    "message": "success!",
    "data": {
    	"id":""
    }
}

```

#### 自定义拓扑界面，保存为实例，直接创建的实例，跟从模板创建实例不同, 列表那个权限
```shell
- method: POST
- url : /api/cloud_lab/custom_topology/instance
- params: {
    "name": "IPSec VPN场景",
    "description": "...",
    "cells":  [] //同上
}
```

```json
resp:
{
    "code": 0,
    "message": "success!",
    "data": {
    	"id": ""
    }
}

```

#### 实例详情，改端口行为，up or down， 只有主动down(active_down)的才能发up, up的时候发down, 会改这个节点所对应的线的点，另一头改为被动down(passive_down)
```shell
- method: POST
- url : /api/cloud_lab/user/instance/:instance_id/port/:port_id
- params: {
    "action": "up/down"
}
```

```json
resp:
{
    "code": 0,
    "message": "success!",
    "data": {
    	
    }
}

```

#### .  实例开关机操作

```shell
- method: put
- url: /api/cloud_lab/user/instance/:instance_id
- params: {{action:"shutdown/poweron"}}
```

```json
resp:
{
    "code": 0, 
    "data": {},
    "message": "success"
}

```


#### .  管理员修改实例生存时间

```shell
- method: put
- url: /api/cloud_lab/user/instance/:instance_id/ttl
- params: {{ttl: 3600 }}  //单位秒
- permission:  p_learning_platform_cloud_lab_manage_edit:
    "learning_platform.cloud_lab.manage.edit:mutation",
```

```json
resp:
{
    "code": 0, 
    "data": {},
    "message": "success"
}

```

#### .  管理员查询正在运行的实例列表

```shell
- method: get
- url: /api/cloud_lab/user/instances/running
- params: {instance_id:"可以单独查一个，返回值是列表里头只一个", username:"可以查某个用户的所有正在运行的实例,模糊匹配"}
- permission:  p_learning_platform_cloud_lab_manage_edit:
    "learning_platform.cloud_lab.manage.edit:mutation",
```

```json
resp:
{
    "code": 0, 
    "data": {
        "list": [{
            "id":"实例id",
            "name": "实例名称",
            "description": "",
            "username": "真实用户名",
            "ttl": "剩余多长时间"
        }]
    },
    "message": "success"
}

```