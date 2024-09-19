import json

from app.extensions import permission
from app.enums.permission_enum import p_list
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, session
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.utils.api_util import Api, AppResponse, AppException
from app.utils.func_util import prepare_args_for_parser, validate_null
from app.controllers.dao import SysSubsystemObjectDao, SysFieldDao, SysMenuDao
from app.controllers.schema import SysSubsystemObjectSchema, SysFieldSchema
from app.controllers.response import marsh_response, SysFieldList, SysSubsystemObjectList, SysDeletedFieldList

fields_app = Blueprint('fields', __name__, url_prefix='/api/sys/fields')
fields_api = Api(fields_app)

menu_fields_parser = RequestParser()
menu_fields_parser.add_argument('front_url', location='args', type=validate_null)

add_field_parser = RequestParser()
add_field_parser.add_argument('subsystem_id', location='json', type=str, required=True)
add_field_parser.add_argument('object_ids', location='json', type=list, required=True)
add_field_parser.add_argument('field_info', location='json', type=dict, required=True)

field_info_parser = RequestParser()
field_info_parser.add_argument('name', location=['field_info'], type=validate_null, trim=True, required=True)
field_info_parser.add_argument('label', location=['field_info'], type=validate_null, trim=True, required=True)
field_info_parser.add_argument('ui_type', location=['field_info'], type=validate_null, trim=True, required=True, dest='type')
field_info_parser.add_argument('object_id', location=['field_info'], type=validate_null, trim=True)
field_info_parser.add_argument('required', location=['field_info'], type=bool)
field_info_parser.add_argument('values', location=['field_info'], type=dict, action='append')


@fields_api.resource('', '')
class FieldsAPI(Resource):

    @marsh_response(SysFieldList)
    def get(self):
        """
        查询菜单下所有字段列表，不校验权限
        :return:
        """
        parser_args = prepare_args_for_parser(menu_fields_parser.copy())
        params = parser_args.parse_args()

        data = {"list": []}
        field_object_list = []
        if 'front_url' in params.keys():
            menu = SysMenuDao.querySysMenuByLink(params['front_url'])
            if not menu:
                raise AppException("前端路由未绑定任何菜单")
            if menu.field_object:
                field_object_list = [object_id for object_id in menu.field_object.split(',')]
        else:
            sub_object_list = SysSubsystemObjectDao.queryObjectByNameType('common', 2)
            field_object_list = [sub_object_list.id]

        for object_id in field_object_list:
            sub_object = SysSubsystemObjectDao.querySubObjectById(object_id)
            _, fields = SysFieldDao.queryFieldsByFilter(object_id=object_id, **params)
            schema = SysFieldSchema()
            fields = schema.dump(fields, many=True)
            for field in fields:
                field['object'] = sub_object.name
                field['values'] = json.loads(field['values']) if field['values'] else []
                data["list"].append(field)
        return data

    @permission.check(p_list['p_field_mutation'])
    def post(self):
        """
        添加字段
        :return:
        """
        parser_args = prepare_args_for_parser(field_info_parser.copy())
        add_field_params = add_field_parser.copy().parse_args()
        field_params = parser_args.copy().parse_args(req=add_field_params)

        field_params['create_by'] = session['user_id']
        field_params['update_by'] = session['user_id']
        if field_params.get('values'):
            field_params['values'] = json.dumps(field_params['values'], ensure_ascii=False)

        for object_id in add_field_params['object_ids']:
            field_params['object_id'] = object_id
            schema = SysFieldSchema()
            field = schema.load(field_params, unknown="exclude")
            SysFieldDao.addField(field)

        return jsonify(AppResponse())


edit_filed_parser = RequestParser()
edit_filed_parser.add_argument('field_info', location='json', type=dict, required=True)


@fields_api.resource('', '/<fields_id>')
class FieldsIdAPI(Resource):

    @permission.check(p_list['p_field_mutation'])
    def put(self, fields_id):
        """
        编辑字段
        :return:
        """
        field_info_copy = field_info_parser.copy()
        field_info_copy.replace_argument('name', location=['field_info'], type=validate_null, trim=True)
        field_info_copy.replace_argument('label', location=['field_info'], type=validate_null, trim=True)
        field_info_copy.replace_argument('ui_type', location=['field_info'], type=validate_null, trim=True, dest='type')

        parser_args = prepare_args_for_parser(field_info_copy)
        edit_field_params = edit_filed_parser.copy().parse_args()
        field_params = parser_args.parse_args(req=edit_field_params)

        if field_params.get('values'):
            field_params['values'] = json.dumps(field_params['values'], ensure_ascii=False)

        field_params['update_by'] = session['user_id']
        field_params['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SysFieldDao.updateField(fields_id, field_params)

        return jsonify(AppResponse())

    @permission.check(p_list['p_field_mutation'])
    def delete(self, fields_id):
        """
        删除字段
        :return:
        """
        SysFieldDao.deleteField(fields_id)
        return jsonify(AppResponse())


object_parser = RequestParser()
object_parser.add_argument('name', location='json', type=validate_null, trim=True)
object_parser.add_argument('description', location='json', type=str)


@fields_api.resource('', '/subsystem')
class FieldsSubsystemAPI(Resource):

    @permission.check(p_list['p_field_list'])
    @marsh_response(SysSubsystemObjectList)
    def get(self):
        """
        获取子系统列表
        :return:
        """
        data = {"list": []}
        subsystems = SysSubsystemObjectDao.querySubsystem()
        schema = SysSubsystemObjectSchema()
        subsystems = schema.dump(subsystems, many=True)
        data["list"] = subsystems

        return data

    @permission.check(p_list['p_field_mutation'])
    def post(self):
        """
        添加子系统
        :return:
        """
        parser_args = object_parser.copy()
        parser_args.replace_argument('name', location='json', type=validate_null, trim=True, required=True)
        parser_args = prepare_args_for_parser(parser_args)
        object_params = parser_args.parse_args()

        object_params['type'] = 1
        schema = SysSubsystemObjectSchema()
        subsystem_object = schema.load(object_params, unknown="exclude")
        SysSubsystemObjectDao.addSubsystemObject(subsystem_object)

        return jsonify(AppResponse())


@fields_api.resource('', '/object/<subsystem_id>')
class FieldsObjectAPI(Resource):

    @permission.check(p_list['p_field_list'])
    @marsh_response(SysSubsystemObjectList)
    def get(self, subsystem_id):
        """
        获取子系统对象列表
        :return:
        """
        data = {"list": []}
        objects = SysSubsystemObjectDao.queryObjectByParentId(subsystem_id)
        schema = SysSubsystemObjectSchema()
        subsystems = schema.dump(objects, many=True)
        data["list"] = subsystems

        return data


@fields_api.resource('', '/subsystem/<subsystem_id>')
class FieldsSubsystemByIdAPI(Resource):

    @permission.check(p_list['p_field_mutation'])
    def put(self, subsystem_id):
        """
        编辑子系统、子系统对象
        :return:
        """
        parser_args = prepare_args_for_parser(object_parser.copy())
        object_params = parser_args.parse_args()

        SysSubsystemObjectDao.updateSubsystemObject(subsystem_id, object_params)

        return jsonify(AppResponse())

    @permission.check(p_list['p_field_mutation'])
    def post(self, subsystem_id):
        """
        添加子系统对象
        :return:
        """
        parser_args = prepare_args_for_parser(object_parser.copy())
        object_params = parser_args.parse_args()

        object_params['type'] = 2
        object_params['parent_id'] = subsystem_id
        schema = SysSubsystemObjectSchema()
        subsystem_object = schema.load(object_params, unknown="exclude")
        SysSubsystemObjectDao.addSubsystemObject(subsystem_object)

        return jsonify(AppResponse())

    @permission.check(p_list['p_field_mutation'])
    def delete(self, subsystem_id):
        """
        删除子系统、子系统对象
        :return:
        """
        SysSubsystemObjectDao.deleteSubsystemObject(subsystem_id)

        return jsonify(AppResponse())


field_parser = RequestParser()
field_parser.add_argument('label', location='args', type=str, nullable=True)
field_parser.add_argument('object', location='args', type=str, nullable=True)
field_parser.add_argument('name', location='args', type=str, nullable=True)
field_parser.add_argument('page', location='args', type=int, default=1)
field_parser.add_argument('size', location='args', type=int, default=1000)


@fields_api.resource('', '/<subsystem_id>/list')
class SubsystemFieldsAPI(Resource):

    @permission.check(p_list['p_field_list'])
    @marsh_response(SysFieldList)
    def get(self, subsystem_id):
        """
        字段管理页查询子系统下所有字段列表
        :return:
        """
        parser_args = prepare_args_for_parser(field_parser.copy())
        field_params = parser_args.parse_args()

        data = {
            "list": [],
            "page": int(field_params.get("page")),
            "size": int(field_params.get("size")),
            "total": 0
        }

        schema = SysFieldSchema()
        objects = SysSubsystemObjectDao.queryObjectByParentId(subsystem_id)
        for obj in objects:
            if field_params.get('object'):
                if field_params.get('object') not in obj.name:
                    continue

            total, fields = SysFieldDao.queryFieldsByFilter(object_id=obj.id, **field_params)
            data["total"] += total
            fields = schema.dump(fields, many=True)
            for field in fields:
                field['object'] = obj.name
                field['object_label'] = obj.description
                field['values'] = json.loads(field['values']) if field.get('values') else []
                data["list"].append(field)

        return data


@fields_api.resource('', '/recycle')
class FieldsRecycleAPI(Resource):

    @permission.check(p_list['p_field_list'])
    @marsh_response(SysDeletedFieldList)
    def get(self):
        """
        查询删除的字段信息
        :return:
        """
        parser_args = prepare_args_for_parser(field_parser.copy())
        field_params = parser_args.parse_args()
        data = {
            "list": [], "total": 0,
            "page": int(field_params.get("page")),
            "size": int(field_params.get("size"))
        }

        total, fields = SysFieldDao.queryFieldsByFilter(deleted=True, **field_params)
        data["total"] += total

        schema = SysFieldSchema()
        fields = schema.dump(fields, many=True)
        for field in fields:
            subsystem_obj = SysSubsystemObjectDao.querySubObjectById(field['object_id'])
            subsytem = SysSubsystemObjectDao.querySubObjectById(subsystem_obj.parent_id)
            field['object'] = subsystem_obj.name
            field['object_label'] = subsystem_obj.description
            field['subsystem'] = subsytem.name
            field['subsystem_id'] = subsytem.id
            field['subsystem_label'] = subsytem.description
            field['values'] = json.loads(field['values']) if field.get('values') else []
            field['expired_time'] = (datetime.strptime(field['delete_time'], '%Y-%m-%d %H:%M:%S')
                                     + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
            data["list"].append(field)

        return data


@fields_api.resource('', '/recycle/<delete_id>')
class FieldsDeleteRecycleAPI(Resource):

    @permission.check(p_list['p_field_mutation'])
    def put(self, delete_id):
        """
        还原删除字段
        :return:
        """
        update_data = {"delete_time": None}
        SysFieldDao.updateField(delete_id, update_data)

        return jsonify(AppResponse())
