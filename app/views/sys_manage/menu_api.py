from flask import Blueprint, session, jsonify, request
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.extensions import permission
from app.enums.permission_enum import p_list
from app.utils.api_util import Api, AppResponse, AppException
from app.utils.func_util import prepare_args_for_parser, to_bool_or_none
from app.controllers.dao import SysRoleMenuDao, SysMenuDao, SysRoleDao, SysRoleUserDao, SysUserDao, TblEmployeeDao, \
    SysSubsystemObjectDao, SysFieldPermissionDao
from app.controllers.schema import SysMenuSchema, SysRoleSchema, SysUserSchema, SysRoleMenuSchema
from app.controllers.response import marsh_response, SysRoleList, MenuInfoList, SysMenuUserList

menu_app = Blueprint('menu', __name__, url_prefix='/api/sys/menu')
menu_api = Api(menu_app)

get_menu_parser = RequestParser()
get_menu_parser.add_argument('parentid', location='args', type=str, dest='parent_id')
get_menu_parser.add_argument('title', location='args', type=str)
get_menu_parser.add_argument('type', location='args', type=int, dest='menu_type')
get_menu_parser.add_argument('permission', location='args', type=str)
get_menu_parser.add_argument('link', location='args', type=str)
get_menu_parser.add_argument('link_type', location='args', type=int)
get_menu_parser.add_argument('hidden', location='args', type=to_bool_or_none, default=False)


@menu_api.resource('', '')
class MenuAPI(Resource):

    @permission.check(p_list['p_menu_list'])
    @marsh_response(MenuInfoList)
    def get(self):
        """
        功能管理，获取全部功能列表
        :return:
        """
        data = {"list": []}
        parser_args = prepare_args_for_parser(get_menu_parser.copy())
        params = parser_args.parse_args()

        menus, menu_ids, all_menu_ids = [], [], []
        _, menu_list = SysMenuDao.querySysMenuByFilter(**params)
        for menu in menu_list:
            menus.append(menu)
            menu_ids.append(menu.id)
            all_menu_ids += menu.full_path.split('/')

        all_menu_ids = list(set(all_menu_ids))
        parent_menu_ids = [element for element in all_menu_ids if element not in menu_ids]
        parent_menu_list = SysMenuDao.querySysMenuByIds(parent_menu_ids)
        menus += parent_menu_list

        schema = SysMenuSchema()
        menus = schema.dump(menus, many=True)

        for menu in menus:
            if menu.get('field_object'):
                sub_object = SysSubsystemObjectDao.querySubObjectById(menu['field_object'])
                if sub_object:
                    menu['object_name'] = sub_object.name
                    menu['object_description'] = sub_object.description

        data["list"] = menus

        return data


@menu_api.resource('', '/list')
class MenuListAPI(Resource):

    @permission.check(p_list['p_menu_list'])
    @marsh_response(MenuInfoList)
    def get(self):
        """
        功能和权限全部列表
        :return:
        """
        data = {"list": []}
        parser_args = prepare_args_for_parser(get_menu_parser.copy())
        params = parser_args.parse_args()

        if not params:
            menus = SysMenuDao.querySysMenu()
        else:
            menus, menu_ids = [], []
            _, menu_list = SysMenuDao.querySysMenuByFilter(**params)
            for menu in menu_list:
                if menu.id in menu_ids:
                    continue
                menus.append(menu)
                menu_ids.append(menu.id)
                parent_menus = SysMenuDao.queryParentMenusById(menu.id)
                for parent_menu in parent_menus:
                    if parent_menu.id in menu_ids:
                        continue
                    menu_ids.append(parent_menu.id)
                    menus.append(parent_menu)

        schema = SysMenuSchema()
        menus = schema.dump(menus, many=True)

        data["list"] = menus

        return data


@menu_api.resource('', '/personal')
class MenuPersonalAPI(Resource):

    @marsh_response(MenuInfoList)
    def get(self):
        """
        获取个人左侧功能列表
        :return:
        """
        data = {"list": []}
        menu_list = SysRoleMenuDao.getAllowMenuByRolesId(session['roles'])
        schema = SysMenuSchema(many=True)
        menu = schema.dump(menu_list)
        data["list"] = menu

        return data


@menu_api.resource('', '/<menu_id>/permission')
class MenuPermissionByIdAPI(Resource):
    get_exclude = ['list.link', 'list.link_type']

    @marsh_response(MenuInfoList, exclude=get_exclude)
    def get(self, menu_id):
        """
        单个菜单下的所有按钮级别权限列表
        :return:
        """
        data = {"list": []}
        permission_list = SysMenuDao.querySysPermissionByParentId(menu_id)
        for p in permission_list:
            schema = SysMenuSchema()
            menu = schema.dump(p)
            data["list"].append(menu)

        return data


@menu_api.resource('', '/<menu_id>/permission/personal')
class LocalPermissionByIdAPI(Resource):

    def get(self, menu_id):
        """
        获取个人菜单下权限列表
        :return:
        """
        data = {"list": []}
        menu = SysMenuDao.querySysMenuById(menu_id)
        if menu:
            permission_list = [menu]
            permissions = permission.getPermissionByUserId(session['user_id'])
            permission_list += SysMenuDao.querySysPermissionByParentId(menu_id)
            for p in permission_list:
                if not p.permission:
                    continue

                if p.permission in permissions:
                    data["list"].append({"permission": p.permission})

        return jsonify(AppResponse(data))


menu_parser = RequestParser()
menu_parser.add_argument('parentid', location='json', type=str, dest='parent_id')
menu_parser.add_argument('title', location='json', type=str, required=True)
menu_parser.add_argument('type', location='json', type=int, required=True, dest='menu_type')
menu_parser.add_argument('page_key', location='json', type=str)
menu_parser.add_argument('permission', location='json', type=str)
menu_parser.add_argument('link', location='json', type=str)
menu_parser.add_argument('link_type', location='json', type=int)
menu_parser.add_argument('hidden', location='json', type=bool, default=False)
menu_parser.add_argument('object_id', location='json', type=str, dest='field_object')

del_menu_parser = RequestParser()
del_menu_parser.add_argument('permission_ids', location='json', type=list)


@menu_api.resource('', '/permission')
class MenuPermissionAPI(Resource):

    @permission.check(p_list['p_menu_mutation'])
    def post(self):
        """
        新增权限
        :return:
        """
        parser_args = prepare_args_for_parser(menu_parser.copy())
        params = parser_args.parse_args()
        if params['menu_type'] in (2, 3) and params.get("link_type") not in (2, 3) and not params.get('permission'):
            raise AppException('400 Bad Request. Message: `permission` is not null')

        if params['menu_type'] == 2:
            for arg in ['link', 'link_type']:
                if not params.get(arg):
                    raise AppException(f'400 Bad Request. Message: `{arg}` is not null')

            if params.get('link_type') == 1:
                if not params.get('page_key'):
                    raise AppException(f'400 Bad Request. Message: `{arg}` is not null')

        schema = SysMenuSchema()
        menu = schema.load(params)
        menu.create_by = session['user_id']
        menu.update_by = session['user_id']
        SysMenuDao.addSysMenu(menu)

        return jsonify(AppResponse())

    @permission.check(p_list['p_menu_mutation'])
    def delete(self):
        """
        软删除功能权限, 有关联的不给删， 删除失败时data返回关联的角色
        :return:
        """
        failed_list = []
        parser_args = prepare_args_for_parser(del_menu_parser.copy())
        params = parser_args.parse_args()

        for menu_id in params['permission_ids']:
            try:
                SysMenuDao.deleteSysMenu(menu_id)
            except AppException as e:
                failed_list.append({"id": menu_id, "message": e.message})

        if failed_list:
            data = {"failed_list": failed_list}
            return jsonify(AppResponse(data))

        return jsonify(AppResponse())


@menu_api.resource('', '/permission/<permission_id>')
class MenuPermissionByPermissionIdAPI(Resource):

    @permission.check(p_list['p_menu_mutation'])
    def put(self, permission_id):
        """
        修改权限
        :return:
        """
        parser_args = menu_parser.copy()
        parser_args.replace_argument('title', location='json', type=str)
        parser_args.replace_argument('type', location='json', type=int, dest='menu_type')
        parser_args.replace_argument('permission', location='json', type=str)
        parser_args = prepare_args_for_parser(parser_args)
        params = parser_args.parse_args()

        if params['menu_type'] == 2:
            for arg in ['link', 'link_type']:
                if not params.get(arg):
                    raise AppException(f'400 Bad Request. Message: `{arg}` is not null')

            if params.get('link_type') == 1:
                if not params.get('page_key'):
                    raise AppException(f'400 Bad Request. Message: `{arg}` is not null')

        params['update_by'] = session['user_id']

        SysMenuDao.updateSysMenu(permission_id, params)

        return jsonify(AppResponse())


@menu_api.resource('', '/sort')
class MenuSortAPI(Resource):

    def put(self):
        """
        权限改排序
        :return:
        """
        params = request.get_json()
        for id_index in params:
            if 'id' not in id_index.keys():
                raise AppException("`id` 不能为空")

            if 'index' not in id_index.keys():
                raise AppException("`index` 不能为空")

        for id_index in params:
            menu_id = id_index.get('id')
            update_data = {"menu_sort": id_index.get("index")}
            SysMenuDao.updateSysMenu(menu_id, update_data)

        return jsonify(AppResponse())


@menu_api.resource('', '/permission/<permission_id>/role')
class MenuRoleByPermissionIdAPI(Resource):

    @permission.check(p_list['p_role_list'])
    @marsh_response(SysRoleList)
    def get(self, permission_id):
        """
        根据权限，查所绑定的角色列表
        :return:
        """
        data = {"list": []}
        role_menu_list = SysRoleMenuDao.querySysRoleMenuByMenuId(permission_id)
        for role_menu in role_menu_list:
            role = SysRoleDao.querySysRoleById(role_menu.role_id)
            schmea = SysRoleSchema()
            role = schmea.dump(role)

            field_permission_list = SysFieldPermissionDao.queryFieldPermissionByRoleMenuId(role_menu.id)
            field_scope = [field_permission.field_id for field_permission in field_permission_list]

            schema = SysRoleMenuSchema()
            role_menu = schema.dump(role_menu)
            role_menu['field_scope'] = field_scope
            role['purview'] = role_menu

            data["list"].append(role)

        return data

    def put(self, permission_id):
        """
        功能绑定多个角色
        :param permission_id:
        :return:
        """
        pass


menu_user_parser = RequestParser()
menu_user_parser.add_argument('name', location='args', type=str, nullable=True, dest='display_name')
menu_user_parser.add_argument('page', location='args', type=int, default=1)
menu_user_parser.add_argument('size', location='args', type=int, default=1000)


@menu_api.resource('', '/permission/<permission_id>/user')
class MenuUserByPermissionIdAPI(Resource):

    @permission.check(p_list['p_user_list'])
    @marsh_response(SysMenuUserList)
    def get(self, permission_id):
        """
        根据权限，查所绑定的人员列表
        :return:
        """
        parser_args = prepare_args_for_parser(menu_user_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")),
            "size": int(params.get("size"))
        }

        user_ids = set()
        role_menu_list = SysRoleMenuDao.querySysRoleMenuByMenuId(permission_id)
        for role_menu in role_menu_list:
            role_user_list = SysRoleUserDao.querySysRolesByRoleId(role_menu.role_id)
            for role_user in role_user_list:
                user_ids.add(role_user.user_id)

        params["user_ids"] = list(user_ids)
        total, user_list = SysUserDao.querySysUserByFilter(**params)
        data["total"] = total
        for user in user_list:
            schema = SysUserSchema(only=['id', 'display_name', 'employee_id'])
            user = schema.dump(user)
            if user.get('employee_id'):
                employee = TblEmployeeDao.queryEmployeeById(user['employee_id'])
                user['employee_name'] = employee.name
            data["list"].append(user)

        return data
