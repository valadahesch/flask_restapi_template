from marshmallow import fields
from app.controllers.response.response_schema import ResponseSchema


# /api/cloud_lab/user/templates
class TemplateInfo(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    id = fields.Str(metadata={"label": "模板ID"}, load_default="")
    name = fields.Str(metadata={"label": "模板名称"})
    description = fields.Str(metadata={"label": "模板描述"}, load_default="", allow_none=True)
    key = fields.Str(metadata={"label": "模板KEY"})
    picture = fields.Str(metadata={"label": "模板显示图片"}, allow_none=False)
    create_by = fields.Str(metadata={"label": "创建人user_id"})
    create_by_name = fields.Str(metadata={"label": "创建人姓名"}, load_default="", allow_none=True)
    create_time = fields.Str(metadata={"label": "创建时间"}, load_default="", allow_none=True)
    update_by = fields.Str(metadata={"label": "更新人人user_id"})
    update_by_name = fields.Str(metadata={"label": "更新人人姓名"}, load_default="", allow_none=True)
    update_time = fields.Str(metadata={"label": "更新时间"}, load_default="", allow_none=True)


class TemplateList(ResponseSchema):
    list = fields.List(fields.Nested(TemplateInfo(unknown="exclude")), required=True, data_key="list")


# /api/cloud_lab/user/template/<string:template_id>

class TemplateData(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    id = fields.Str(metadata={"label": "模板ID"}, load_default="")
    name = fields.Str(metadata={"label": "模板名称"})
    description = fields.Str(metadata={"label": "模板描述"}, load_default="", allow_none=True)
    key = fields.Str(metadata={"label": "模板KEY"})
    picture = fields.Str(metadata={"label": "模板显示图片"}, allow_none=False)
    create_by = fields.Str(metadata={"label": "创建人user_id"})
    create_by_name = fields.Str(metadata={"label": "创建人姓名"}, load_default="", allow_none=True)
    create_time = fields.Str(metadata={"label": "创建时间"}, load_default="", allow_none=True)
    update_by = fields.Str(metadata={"label": "更新人人user_id"})
    update_by_name = fields.Str(metadata={"label": "更新人人姓名"}, load_default="", allow_none=True)
    update_time = fields.Str(metadata={"label": "更新时间"}, load_default="", allow_none=True)
    cells = fields.List(fields.Raw(), metadata={"label": "模板数据"}, load_default={}, allow_none=False)

# /api/cloud_lab/user/instance


class CreateInstanceResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    id = fields.Str(metadata={"label": "新创建的实例ID"}, load_default="", allow_none=False)


# /api/cloud_lab/instance/list

class Instance(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    id = fields.Str(metadata={"label": "某个用户的实例ID"}, load_default="", allow_none=False)
    name = fields.Str(metadata={"label": "实例ID对应名称"}, load_default="", allow_none=False)
    template_id = fields.Str(metadata={"label": "实例对应模板"}, load_default="", allow_none=False)
    template_name = fields.Str(metadata={"label": "模板名称"}, load_default="", allow_none=True)
    create_time = fields.Str(metadata={"label": "创建时间"}, load_default="", allow_none=False)
    status = fields.Integer(metadata={"label": "实例状态"}, load_default="", allow_none=False)
    expire = fields.Integer(metadata={"label": "有效期"}, load_default="", allow_none=False)


class InstanceList(ResponseSchema):
    list = fields.List(fields.Nested(Instance(unknown="exclude")), required=True, data_key="list")
    total = fields.Integer(metadata={"label": "实例数量"}, load_default="", allow_none=True)

# /api/cloud_lab/user/instance/<string:instance_id>


class InstanceCellInfo(ResponseSchema):
    id = fields.Str(metadata={"label": "cell id"}, load_default="", allow_none=False)
    type = fields.Str(metadata={"label": "cell type"}, load_default="", allow_none=False)
    graph = fields.Dict(metadata={"label": "cell 图标数据"}, load_default="", allow_none=False)
    name = fields.Str(metadata={"label": "cell 名称"}, load_default="", allow_none=False)
    description = fields.Str(metadata={"label": "cell描述"}, load_default="", allow_none=True)
    image_id = fields.Str(metadata={"label": "node镜像ID"}, load_default="", allow_none=True)
    node_type = fields.Str(metadata={"label": "node类型：device/net"}, load_default="", allow_none=False)
    login = fields.List(fields.Raw(), allow_none=False)
    node_ip = fields.Str(metadata={"label": "node ip"}, load_default="", allow_none=True)
    node_cpu = fields.Integer(metadata={"label": "node cpu数量"}, load_default="", allow_none=True)
    node_ram = fields.Integer(metadata={"label": "node 内存大小"}, load_default="", allow_none=True)
    node_interface_num = fields.Integer(metadata={"label": "node 节点数量"}, load_default="", allow_none=True)


class InstanceInfo(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    id = fields.Str(metadata={"label": "实例ID"}, load_default="", allow_none=False)
    name = fields.Str(metadata={"label": "实例ID对应名称"}, load_default="", allow_none=False)
    description = fields.Str(metadata={"label": "描述"}, load_default="", allow_none=False)
    template_id = fields.Str(metadata={"label": "实例对应模板"}, load_default="", allow_none=False)
    template_name = fields.Str(metadata={"label": "模板名称"}, load_default="", allow_none=True)
    create_time = fields.Str(metadata={"label": "创建时间"}, load_default="", allow_none=False)
    picture = fields.Str(metadata={"label": "图片链接"}, load_default="", allow_none=False)
    status = fields.Integer(metadata={"label": "实例状态: using/delete/failyre"}, load_default="", allow_none=False)
    cells = fields.List(fields.Raw(), metadata={"label": "模板数据"}, load_default=[], allow_none=False)


# /api/cloud_lab/user/instance/<string:instance_id>/progress/starting

class DeviceProgress(ResponseSchema):
    id = fields.Str(metadata={"label": "node ID"}, load_default="", allow_none=False)
    name = fields.Str(metadata={"label": "node ID"}, load_default="", allow_none=False)
    status = fields.Integer(metadata={"label": "设备状态"}, load_default=1, allow_none=False)


class InstanceStep(ResponseSchema):
    name = fields.Str(metadata={"label": "创建进度标识"}, load_default="", allow_none=False)
    label = fields.Str(metadata={"label": "创建进度中文标识"}, load_default="", allow_none=False)
    status = fields.Integer(metadata={"label": "状态"}, load_default="", allow_none=False)
    spend_time = fields.Integer(metadata={"label": "创建花费时间"}, load_default="", allow_none=False)
    detail = fields.List(fields.Nested(DeviceProgress(unknown="exclude")), required=True, data_key="detail")


class CreateProgress(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    status = fields.Integer(metadata={"label": "实例ID"}, load_default="", allow_none=False)
    queue = fields.Integer(metadata={"label": "排队人数"}, load_default="", allow_none=False)
    schedule = fields.Integer(metadata={"label": "实例ID对应名称"}, load_default="", allow_none=False)
    estimate_create_time = fields.Integer(metadata={"label": "预估创建时长，秒"}, load_default="", allow_none=False)
    create_time = fields.Str(metadata={"label": "实例开始创建时间"}, load_default="", allow_none=False)
    server_time = fields.Str(metadata={"label": "请求那一刻服务端的时间"}, load_default="", allow_none=False)
    local_time = fields.Str(metadata={"label": "客户端本地时间，请求那一刻的时间"}, load_default="", allow_none=False)
    step = fields.List(fields.Nested(InstanceStep(unknown="exclude")), required=True, data_key="step")


class DeleteInstance(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'


class RefreshInstance(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'


class NodeLogin(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    url = fields.Str(metadata={"label": "实例登录链接"}, load_default="", allow_none=False)


# /api/cloud_lab/user/instance/<string:instance_id>/progress/running

class InstanceRunningAction(ResponseSchema):
    type = fields.Str(metadata={"label": "设备运行状态"}, load_default="", allow_none=False)
    label = fields.Str(metadata={"label": "设备运行状态标识"}, load_default="", allow_none=False)
    available = fields.Bool(metadata={"label": "状态可用性"}, load_default="", allow_none=False)


class InstanceRunningLogin(ResponseSchema):
    name = fields.Str(metadata={"label": "登录方式"}, load_default="", allow_none=False)
    type = fields.Str(metadata={"label": "登录类型"}, load_default="", allow_none=False)
    protocol = fields.Str(metadata={"label": "协议"}, load_default="", allow_none=False)
    url = fields.Str(metadata={"label": "登录链接"}, load_default="", allow_none=False)
    username = fields.Str(metadata={"label": "用户名"}, load_default="", allow_none=False)
    password = fields.Str(metadata={"label": "密码"}, load_default="", allow_none=False)
    available = fields.Bool(metadata={"label": "密码"}, load_default=True, allow_none=False)



class InstanceRunningPort(ResponseSchema):
    index = fields.Int(metadata={"label": "登录方式"}, load_default="0", allow_none=False)
    id = fields.Str(metadata={"label": "登录类型"}, load_default="", allow_none=False)
    status = fields.Str(metadata={"label": "协议"}, load_default="up", allow_none=False)



class InstanceRunningDeviceStatus(ResponseSchema):
    id = fields.Str(metadata={"label": "node id"}, load_default="", allow_none=False)
    status = fields.Integer(metadata={"label": "状态"}, load_default="", allow_none=False)
    description = fields.Str(metadata={"label": "描述"}, load_default="", allow_none=True)
    action = fields.List(fields.Nested(InstanceRunningAction(unknown="exclude")), required=True, data_key="action")
    login = fields.List(fields.Nested(InstanceRunningLogin(unknown="exclude")), required=True, data_key="login")
    port_status = fields.List(fields.Nested(InstanceRunningPort(unknown="exclude")), required=True, allow_none=True, data_key="port_status")


class InstanceRunning(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    status = fields.Integer(metadata={"label": "状态"}, load_default="", allow_none=False)
    expire = fields.Integer(metadata={"label": "状态"}, load_default="", allow_none=False)
    device_status = fields.List(fields.Nested(InstanceRunningDeviceStatus(unknown="exclude")), required=True, data_key="device_status")


# /api/cloud_lab/user/instance/<string:instance_id>/<string:node_id>

class NodeAction(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    

#/api/cloud_lab/custom_topology/template
class AddTemplate(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'


# /api/cloud_lab/custom_topology/node_meta

class NodeMeta(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    list = fields.List(fields.Raw(), metadata={"label": "模板数据"}, load_default=[], allow_none=False)


# /api/cloud_lab/user/instance/<string:instance_id>/port/<string:port_id>
class PortOperationsResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'


# /api/cloud_lab/resource_status


class ResourceStatusServer(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    memory = fields.Integer(metadata={"label": "服务器总内存"}, load_default=0, allow_none=False)
    cpu_count = fields.Integer(metadata={"label": "服务器CPU总核数"}, load_default=0, allow_none=False)
    used_cpu_count = fields.Integer(metadata={"label": "已使用CPU核数"}, load_default=0, allow_none=False)
    used_memory = fields.Integer(metadata={"label": "已使用CPU核数"}, load_default=0, allow_none=False)
    memory_percent = fields.Float(metadata={"label": "内存使用率"}, load_default=0, allow_none=False)
    cpu_percent = fields.Float(metadata={"label": "cpu使用率"}, load_default=0, allow_none=False)


class ResourceStatusResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    instance_queue = fields.Integer(metadata={"label": "排队数量"}, load_default=0, allow_none=False)
    instance_starting = fields.Integer(metadata={"label": "正在创建实例数量"}, load_default=0, allow_none=False)
    instance_running = fields.Integer(metadata={"label": "正在运行的实例数量"}, load_default=0, allow_none=False)
    instance_pause = fields.Integer(metadata={"label": "暂停的实例数量"}, load_default=0, allow_none=True)
    server = fields.Nested(ResourceStatusServer(unknown="exclude"))

# /api/cloud_lab/user/instance/<string:instance_id>  [put]


class InstanceActionResponse(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'CloudLab.info'
    