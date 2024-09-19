from flask import session, Blueprint, request
from flask_restful import Resource
from app.controllers.response import marsh_response
from app.extensions import permission
from app.enums.permission_enum import p_list
from app.utils.api_util import Api, AppException
from flask_restful.reqparse import RequestParser
from app.utils.func_util import prepare_args_for_parser
from app.controllers.response.cloudlab_response import TemplateList, TemplateData, CreateInstanceResponse, InstanceList, \
                                                        InstanceInfo, CreateProgress, DeleteInstance, RefreshInstance, \
                                                        NodeLogin, InstanceRunning, NodeAction, AddTemplate, \
                                                        PortOperationsResponse, ResourceStatusResponse, InstanceActionResponse
from app.controllers.service.CloudLab import CloudLab
from app.controllers.service.CloudLab.Instance import Instance
from app.controllers.service.CloudLab.Instance.Node import Node
from app.controllers.dao.cloud_lab_redis_dao import RedisUtils
from app.controllers.dao.cloud_lab_dao import CloudLabUserTemplateInstanceDao

cloudlab_app = Blueprint('cloudlab', __name__, url_prefix='/api/cloud_lab')
cloud_lab_api = Api(cloudlab_app)

post_lab_parser = RequestParser()
post_lab_parser.add_argument('template_id', location='json', type=str)
post_lab_parser.add_argument('name', location='json', type=str)
post_lab_parser.add_argument('description', location='json', type=str)
post_lab_parser.add_argument('picture', location='json', type=str)
post_lab_parser.add_argument('cells', location='json', type=list)
post_lab_parser.add_argument('action', location='json', type=str)

get_lab_parser = RequestParser()
get_lab_parser.add_argument('instance_id', location='args', type=str)
get_lab_parser.add_argument('name', location='args', type=str)
get_lab_parser.add_argument('local_time', location='args', type=str)

instances_lab_parser = RequestParser()
instances_lab_parser.add_argument('name', location='args', type=str)
instances_lab_parser.add_argument('page', location='args', type=int)
instances_lab_parser.add_argument('size', location='args', type=int)
instances_lab_parser.add_argument('status[]', location='args', type=int, action='append', dest='status')


put_lab_parser = RequestParser()
put_lab_parser.add_argument('action', location='json', type=str)


@cloud_lab_api.resource('/user/templates')
class TemplateList(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(TemplateList)
    def get(self):
        # 获取用户模板列表bm4zkmvqil
        return CloudLab().getTemplateList()


@cloud_lab_api.resource('/user/template/<string:template_id>')
class TemplateInfo(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(TemplateData)
    def get(self, template_id):
        # 显示模板拓扑信息
        return CloudLab().getTemplateDataView(template_id)


@cloud_lab_api.resource('/user/instance')
class CreateInstance(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(CreateInstanceResponse)
    def post(self):
        # 创建实例
        parser_args = prepare_args_for_parser(post_lab_parser.copy())
        params = parser_args.parse_args()
        template_id = params.get("template_id")
        instance_name = params.get("name")
        if CloudLabUserTemplateInstanceDao.getInstanceByName(instance_name, session['user_id']):
            raise AppException("实例名称和已有实例冲突,请更换后尝试")
        instance = CloudLab().requestCreateInstanceByTemplate(template_id, instance_name, session['user_id'], request.host)
        return instance


@cloud_lab_api.resource('/user/instances')
class GetInstances(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(InstanceList)
    def get(self):
        # 获取实例列表
        parser_args = prepare_args_for_parser(instances_lab_parser.copy())
        params = parser_args.parse_args()
        name = params.get("name")
        status = params.get("status")
        page = params.get("page")
        size = params.get("size")
        return Instance().getInstanceList(user_id=session["user_id"], name=name, status=status, page=page, size=size)


@cloud_lab_api.resource('/user/instance/<string:instance_id>')
class InstanceOperate(Resource):

    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(InstanceInfo)
    def get(self, instance_id):
        # 获取实例信息
        return Instance().getInstanceInfo(instance_id, session["user_id"])
    
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(DeleteInstance)
    def delete(self, instance_id):
        # 删除实例
        nodes_status_data = RedisUtils().getNodeProgressDataByInstanceId(instance_id)
        creating_node = [item for item in nodes_status_data if item["status"] in [1, 4, 12]]
        status = CloudLabUserTemplateInstanceDao().getInstanceInfo(instance_id=instance_id).get("status")
        if creating_node:
            if status == 1:   # 新建启动中的实例不允许删除
                raise AppException("实例存在未完全启动的节点,请等待节点完全启动之后再执行操作")
            else:
                Instance().requestdeleteInstance(instance_id)
        else:
            Instance().requestdeleteInstance(instance_id)
        return None
    
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(InstanceActionResponse)
    def put(self, instance_id):
        # 实例节点开关机操作
        parser_args = prepare_args_for_parser(put_lab_parser.copy())
        params = parser_args.parse_args()
        action = params.get("action")
        if action == "power_on":
            Instance().powerOnInstance(instance_id)
        elif action == "shutdown":
            nodes_status_data = RedisUtils().getNodeProgressDataByInstanceId(instance_id)
            creating_node = [item for item in nodes_status_data if item["status"] in [1, 4, 12]]
            if creating_node:
                raise AppException("实例存在未完全启动的节点,请等待节点完全启动之后再执行操作")
            else:
                Instance().shutdownInstance(instance_id)
        return None


@cloud_lab_api.resource('/user/template/<string:template_id>/instance_startup')
class TemplateStartUP(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(InstanceList)
    def get(self, template_id):
        # 查询某个用户当前模板下是否有正在创建中的实例
        return Instance(). getStartingInstanceByTemplateId(template_id, session['user_id'])


@cloud_lab_api.resource('/user/interface/<string:instance_id>/<string:node_id>/<string:login_key>')
class NodeLogin(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(NodeLogin)
    def get(self, instance_id, node_id, login_key):
        # 获取某个设备的某种登录方式
        return Node().nodeLogin(instance_id, node_id, login_key, session['user_id'], request.host)


@cloud_lab_api.resource('/user/instance/<string:instance_id>/renewal')
class AddInstanceTTL(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(RefreshInstance)
    def put(self, instance_id):
        # 刷新实例的存活时间 -> 增加30分钟
        return Instance().addInstanceTTL(instance_id)


@cloud_lab_api.resource('/user/instance/<string:instance_id>/progress/starting')
class CreateProgress(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(CreateProgress)
    def get(self, instance_id):
        # 获取实例创建进度(启动中)
        parser_args = prepare_args_for_parser(get_lab_parser.copy())
        params = parser_args.parse_args()
        local_time = params.get("local_time") or "2106-01-01 00:00:00"
        progress_data = Instance().getInstanceProgressStarting(instance_id=instance_id, local_time=local_time)
        return progress_data


@cloud_lab_api.resource('/user/instance/<string:instance_id>/progress/running')
class CreateProgressRunning(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(InstanceRunning)
    def get(self, instance_id):
        # 获取实例创建进度(运行中)
        progress_data = Instance().getInstanceProgressRunning(instance_id)
        return progress_data


@cloud_lab_api.resource('/user/instance/<string:instance_id>/<string:node_id>')
class InstanceRunningStatus(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(NodeAction)
    def put(self, instance_id, node_id):
        # 实例节点开关机操作
        parser_args = prepare_args_for_parser(put_lab_parser.copy())
        params = parser_args.parse_args()
        action = params.get("action")
        if action == "power_on":
            Node().powerOnInstanceNode(instance_id=instance_id, node_id=node_id)
        elif action == "power_off":
            Node().powerOffInstanceNode(instance_id=instance_id, node_id=node_id)
        elif action == "force_reboot":
            Node().forceRebootInstanceNode(instance_id=instance_id, node_id=node_id)
        elif action == "shutdown":
            Node().shutdownInstanceNode(instance_id=instance_id, node_id=node_id)
        elif action == "restart":
            Node().restartInstanceNode(instance_id=instance_id, node_id=node_id)
        return None


@cloud_lab_api.resource('/custom_topology/node_meta')
class NodeMeta(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    # @marsh_response(NodeMeta)
    def get(self):
        # 节点信息列表
        return CloudLab.getNodeMeta()

    

@cloud_lab_api.resource('/custom_topology/template')
class CreateTemplate(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab_manage_edit'])
    @marsh_response(AddTemplate)
    def post(self):
        parser_args = prepare_args_for_parser(post_lab_parser.copy())
        params = parser_args.parse_args()
        template_data_view = params
        CloudLab().createTemplate(template_data_view, session['user_id'])
        return None
    

@cloud_lab_api.resource('/custom_topology/instance')
class CreateNewInstance(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(CreateInstanceResponse)
    def post(self):
        parser_args = prepare_args_for_parser(post_lab_parser.copy())
        params = parser_args.parse_args()
        instance_name = params.get("name")
        if len(instance_name) > 20:
            raise AppException("实例名称过长, 请不要超过20位")
        if CloudLabUserTemplateInstanceDao.getInstanceByName(instance_name, session['user_id']):
            raise AppException("实例名称和已有实例冲突,请更换后尝试")
        instance = CloudLab().requestCreateInstance(session['user_id'], request.host, params)
        return instance
    

@cloud_lab_api.resource('/resource_status')
class ResourceStatus(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab_manage_edit'])
    @marsh_response(ResourceStatusResponse)
    def get(self):
        return CloudLab().getServerHostResource()


@cloud_lab_api.resource('/user/instance/<string:instance_id>/port/<string:port_id>')
class PortOperations(Resource):
    @permission.check(p_list['p_learning_platform_cloud_lab'])
    @marsh_response(PortOperationsResponse)
    def post(self, instance_id, port_id):
        parser_args = prepare_args_for_parser(post_lab_parser.copy())
        params = parser_args.parse_args()
        action = params.get("action")
        Node().portOperations(instance_id, action, port_id)
        return None

