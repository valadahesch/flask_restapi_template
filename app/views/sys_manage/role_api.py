import copy

from app.enums.permission_enum import p_list
from app.extensions import permission
from flask import Blueprint, jsonify, session
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.utils.api_util import Api, AppResponse, AppException
from app.utils.func_util import prepare_args_for_parser, to_bool_or_none
from app.controllers.dao import SysRoleDao, SysRoleMenuDao, SysRoleUserDao, SysUserDao, TblEmployeeDao, \
    SysFieldPermissionDao
from app.controllers.schema import SysRoleSchema, SysMenuSchema, SysUserSchema, SysRoleUserSchema, SysRoleMenuSchema, \
    SysFieldPermissionSchema
from app.controllers.response import marsh_response, SysRoleUserList, SysRoleEmployeeList, PermissionInfoList, \
    SysRoleList

role_app = Blueprint('role', __name__, url_prefix='/api/sys/role')
role_api = Api(role_app)

role_parser = RequestParser()
role_parser.add_argument('name', location='args', type=str, nullable=True)
role_parser.add_argument('type', location='args', type=int, nullable=True)
role_parser.add_argument('is_deactivate', location='args', type=to_bool_or_none, default=False)
role_parser.add_argument('description', location='args', type=str, nullable=True)
role_parser.add_argument('page', location='args', type=int, default=1)
role_parser.add_argument('size', location='args', type=int, default=1000)

del_role_parser = RequestParser()
del_role_parser.add_argument('role_ids', location='json', type=list)

add_role_parser = RequestParser()
add_role_parser.add_argument('name', location='json', type=str, nullable=True, required=True)
add_role_parser.add_argument('type', location='json', type=int, nullable=True, required=True)
add_role_parser.add_argument('is_deactivate', location='json', type=bool, default=False)
add_role_parser.add_argument('expire_time', location='expire_time', type=str)
add_role_parser.add_argument('description', location='json', type=str, nullable=True)


@role_api.resource('', '')
class RoleAPI(Resource):

    @permission.check(p_list['p_role_list'])
    @marsh_response(SysRoleList)
    def get(self):
        """
        角色信息列表, 分页 , filter 条件查
        :return:
        """
        parser_args = prepare_args_for_parser(role_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")), "size": int(params.get("size"))
        }

        data["total"], roles = SysRoleDao.querySysRoleByFilter(**params)

        schema = SysRoleSchema()
        roles = schema.dump(roles, many=True)

        data["list"] = roles
        return data

    @permission.check(p_list['p_role_mutation'])
    def post(self):
        """
        新增角色
        :return:
        """
        parser_args = prepare_args_for_parser(add_role_parser.copy())
        params = parser_args.parse_args()

        schema = SysRoleSchema()
        role = schema.load(params)
        role.create_by, role.update_by = session['user_id'], session['user_id']
        SysRoleDao.addSysRole(role)

        return jsonify(AppResponse())

    @permission.check(p_list['p_role_mutation'])
    def delete(self):
        """
        批量删除角色
        :return:
        """
        failed_list = []
        parser_args = prepare_args_for_parser(del_role_parser.copy())
        params = parser_args.parse_args()

        for role_id in params['role_ids']:
            try:
                SysRoleDao.deleteSysRole(role_id)
            except AppException as e:
                failed_list.append({"id": role_id, "message": e.message})

        if failed_list:
            data = {"failed_list": failed_list}
            return jsonify(AppResponse(data))

        return jsonify(AppResponse())


@role_api.resource('', '/<role_id>')
class RoleByRoleIdAPI(Resource):

    @permission.check(p_list['p_role_mutation'])
    def put(self, role_id):
        """
        修改角色基本信息
        :return:
        """
        parser_args = add_role_parser.copy()
        parser_args.replace_argument('name', location='json', type=str, nullable=True)
        parser_args.replace_argument('type', location='json', type=int, nullable=True)
        parser_args = prepare_args_for_parser(parser_args)
        params = parser_args.parse_args()

        params['update_by'] = session['user_id']

        SysRoleDao.updateSysRole(role_id, params)

        return jsonify(AppResponse())

    def delete(self, role_id):
        """
        删除角色，角色相关人的提示，删除角色和权限的关系没影响，失败返回绑定人的信息
        :return:
        """
        pass


put_permission_parser = RequestParser()
put_permission_parser.add_argument('role_permission', location='json', type=dict, action='append', nullable=True)


@role_api.resource('', '/<role_id>/permission')
class RolePermissionByRoleIdAPI(Resource):

    @permission.check(p_list['p_menu_list'])
    @marsh_response(PermissionInfoList)
    def get(self, role_id):
        """
        根据角色ID，查询角色下面的权限
        :return:
        """
        data = {"list": []}

        rm_menu_list = SysRoleMenuDao.getRMByRoleId(role_id)
        for rm_menu in rm_menu_list:
            role_menu, menu = rm_menu[0], rm_menu[1]
            schema = SysMenuSchema()
            menu = schema.dump(menu)

            field_permission_list = SysFieldPermissionDao.queryFieldPermissionByRoleMenuId(role_menu.id)
            field_scope = [field_permission.field_id for field_permission in field_permission_list]

            schema = SysRoleMenuSchema()
            role_menu = schema.dump(role_menu)
            role_menu['permission_info'] = menu
            role_menu['field_scope'] = field_scope
            data["list"].append(role_menu)

        return data

    @permission.check(p_list['p_role_mutation'])
    def put(self, role_id):
        """
        绑定角色权限, 权限列表可以为空数组， 解绑权限
        :return:
        """
        failed_list, permission_ids = [], []
        put_permission_params = put_permission_parser.copy().parse_args()

        if put_permission_params.get('role_permission'):
            for role_permission in put_permission_params['role_permission']:
                if 'permission_id' not in role_permission:
                    raise AppException(f"`permission_id` 不能为空")
                if 'effect' not in role_permission:
                    raise AppException(f"`effect` 不能为空")
                permission_ids.append(role_permission['permission_id'])

        role_menu_dict = {}
        role_menu_list = SysRoleMenuDao.querySysRoleMenuByRoleId(role_id)
        for role_menu in role_menu_list:
            role_menu_dict.update({role_menu.menu_id: role_menu})

        # 角色-功能列表中不在更新的列表中则删除权限和字段
        for role_menu in role_menu_list:
            if role_menu.menu_id not in permission_ids:
                try:
                    SysRoleMenuDao.deleteRoleMenu(role_menu.id)
                except AppException as e:
                    failed_list.append({"id": role_menu.id, "message": e.message})
                    continue

                SysFieldPermissionDao.deleteFieldPermissionByRoleMenuId(role_menu.id)

        if put_permission_params['role_permission']:
            for role_permission in put_permission_params['role_permission']:
                permission_id = role_permission['permission_id']
                if permission_id not in role_menu_dict.keys():
                    # 更新的列表中不在角色-功能列表中则创建权限和绑定字段
                    role_permission['menu_id'], role_permission['role_id'] = permission_id, role_id
                    schema = SysRoleMenuSchema(unknown='exclude')
                    role_menu = schema.load(role_permission)
                    try:
                        _id = SysRoleMenuDao.addRoleMenu(role_menu)
                    except AppException as e:
                        failed_list.append({"id": permission_id, "message": e.message})
                        continue

                    # 绑定字段权限
                    if _id and role_permission.get('field_scope'):
                        for field_id in role_permission['field_scope']:
                            field_permission = {
                                "role_menu_id": _id,
                                "field_id": field_id,
                                "effect": role_permission['effect']
                            }
                            schema = SysFieldPermissionSchema()
                            field_permission = schema.load(field_permission)
                            try:
                                SysFieldPermissionDao.addFieldPermission(field_permission)
                            except AppException as e:
                                failed_list.append({"id": permission_id, "message": e.message})

                else:
                    # 更新的列表中在角色-功能列表中则更新权限和绑定字段
                    role_menu = role_menu_dict.get(permission_id)
                    data_scope = role_permission['data_scope'] if role_permission.get('data_scope') else None
                    if role_menu.data_scope != data_scope or role_menu.effect != role_permission['effect']:
                        try:
                            update_data = {"data_scope": data_scope, "effect": role_permission['effect']}
                            SysRoleMenuDao.updateRoleMenu(role_menu.id, update_data)
                        except AppException as e:
                            failed_list.append({"id": permission_id, "message": e.message})

                    field_ids_dict = {}
                    field_permission_list = SysFieldPermissionDao.queryFieldPermissionByRoleMenuId(role_menu.id)
                    for field_permission in field_permission_list:
                        field_ids_dict.update({field_permission.field_id: field_permission})

                    # 绑定字段权限
                    if role_permission.get('field_scope'):
                        for field_id in role_permission.get('field_scope'):
                            if field_id not in field_ids_dict.keys():
                                field_permission = {
                                    "role_menu_id": role_menu.id,
                                    "field_id": field_id,
                                    "effect": role_permission['effect']
                                }
                                schema = SysFieldPermissionSchema()
                                field_permission = schema.load(field_permission)
                                try:
                                    SysFieldPermissionDao.addFieldPermission(field_permission)
                                except AppException as e:
                                    failed_list.append({"id": permission_id, "message": e.message})

                    for field_id in field_ids_dict.keys():
                        # 删除字段权限
                        if role_permission.get('field_scope'):
                            if field_id not in role_permission['field_scope']:
                                try:
                                    SysFieldPermissionDao.deleteFieldPermission(field_ids_dict.get(field_id).id)
                                except AppException as e:
                                    failed_list.append({"id": permission_id, "message": e.message})

                if failed_list:
                    data = {"failed_list": failed_list}
                    return jsonify(AppResponse(data))

        return jsonify(AppResponse())


role_user_parser = RequestParser()
role_user_parser.add_argument('page', location='args', type=int, default=1)
role_user_parser.add_argument('size', location='args', type=int, default=100)
role_user_parser.add_argument('name', location='args', type=str)


@role_api.resource('', '/<role_id>/user')
class RoleUserByRoleIdAPI(Resource):

    @permission.check(p_list['p_role_list'])
    @marsh_response(SysRoleUserList)
    def get(self, role_id):
        """
        查询角色下面的用户
        :return:
        """
        parser_args = prepare_args_for_parser(role_user_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")), "size": int(params.get("size"))
        }

        data["total"], ru_list = SysRoleUserDao.queryRUByRoleIdByFilter(role_id, **params)

        employee_ids = [rued[1].employee_id for rued in ru_list if rued[1].employee_id]
        employee_department_map = {}
        employee_department_list = TblEmployeeDao.queryEDByEmployeeIds(employee_ids)
        for employee_department in employee_department_list:
            employee, department = employee_department
            employee_department_map.update({employee.id: employee_department})

        for ru in ru_list:
            schema = SysUserSchema()
            user = schema.dump(ru[1])
            if user['employee_id']:
                employee_department = employee_department_map.get(user['employee_id'])
                if not employee_department:
                    continue

                employee, department = employee_department
                if employee:
                    user['employee_name'] = employee.name
                    user['gender'] = int(employee.gender)
                if department:
                    user['department'] = department.name

            data["list"].append(user)

        return data


put_role_parser = RequestParser()
put_role_parser.add_argument('user_list', location='json', type=list)


@role_api.resource('', '/<role_id>/local')
class RoleUserLocalAPI(Resource):

    @permission.check(p_list['p_role_mutation'])
    def put(self, role_id):
        """
        单角色批量增加/修改系统人员，部分人员绑定失败返回失败人员列表，每个失败的原因
        :return:
        """
        failed_list = []
        parser_args = prepare_args_for_parser(put_role_parser.copy())
        params = parser_args.parse_args()

        role_user_list = SysRoleUserDao.querySysRolesByRoleId(role_id)
        role_user_id = [role_user.user_id for role_user in role_user_list]

        for role_user in role_user_list:
            if role_user.user_id not in params['user_list']:
                try:
                    SysRoleUserDao.deleteRoleUser(role_user.id)
                except AppException as e:
                    failed_list.append({"id": role_id, "message": e.message})

        for user_id in params['user_list']:
            if user_id not in role_user_id:
                role_user = {"role_id": role_id, "user_id": user_id}
                schema = SysRoleUserSchema()
                role_user = schema.load(role_user)
                try:
                    SysRoleUserDao.addRoleUser(role_user)
                except AppException as e:
                    failed_list.append({"id": role_id, "message": e.message})

        if failed_list:
            data = {"failed_list": failed_list}
            return jsonify(AppResponse(data))

        return jsonify(AppResponse())


role_employee_parser = RequestParser()
role_employee_parser.add_argument('page', location='args', type=int, default=1)
role_employee_parser.add_argument('size', location='args', type=int, default=100)
role_employee_parser.add_argument('name', location='args', type=str)
role_employee_parser.add_argument('department', location='args', type=str)


@role_api.resource('', '/<role_id>/employee')
class RoleEmployeeAPI(Resource):

    @permission.check(p_list['p_role_mutation'])
    def put(self, role_id):
        """
        单角色批量增加/修改企业人员，部分人员绑定失败返回失败人员列表，每个失败的原因
        :return:
        """
        failed_list, user_list = [], []
        parser_args = prepare_args_for_parser(put_role_parser.copy())
        params = parser_args.parse_args()

        # 查询企业用户是否为系统用户，不是则创建用户
        for employee_id in params['user_list']:
            sys_user = SysUserDao.querySysUserByEmployeeId(employee_id)
            if not sys_user:
                employee = TblEmployeeDao.queryEmployeeById(employee_id)
                if not employee:
                    failed_list.append({"id": role_id, "message": "未查询到企业用户ID"})

                email = employee.email.lower()
                if 'hillstonenet.com' in email:
                    sysuser = SysUserDao.querySysUserByEmail(email)
                    if sysuser:
                        update_data = {"employee_id": employee.id}
                        SysUserDao.updateSysUserById(sysuser.id, update_data)

                        role = SysRoleDao.querySysRoleByType(2)
                        role_user = SysRoleUserDao.querySysRoleByRoleUserId(role.id, sys_user.id)
                        if role_user:
                            role_user_list = SysRoleUserDao.querySysRolesByUserId(sys_user.id)
                            if len(role_user_list) > 1:
                                failed_list.append({"id": role_id, "message": "绑定失败，请先解除绑定其他角色"})
                                continue
                            SysRoleUserDao.deleteRoleUser(role_user.id)
                        user_id = sys_user.id
                    else:
                        schema = SysUserSchema(only=['id', 'display_name', 'employee_id'])
                        sys_user = schema.load({"display_name": employee.name, "employee_id": employee_id})
                        user_id = SysUserDao.addSysUserByEmployee(sys_user)

                    if user_id:
                        role = SysRoleDao.querySysRoleByType(1)
                        role_user = SysRoleUserDao.querySysRoleByRoleUserId(role.id, user_id)
                        if not role_user:
                            role_user = {"role_id": role.id, "user_id": user_id}
                            schema = SysRoleUserSchema()
                            role_user = schema.load(role_user)
                            SysRoleUserDao.addRoleUser(role_user)

                        user_list.append(sysuser.id)
                else:
                    failed_list.append({"id": role_id, "message": "非内部邮箱用户"})
            else:
                user_list.append(sys_user.id)

        # 获取角色绑定的用户
        role_user_ids, role_user_list = [], []
        ru_user_list = SysRoleUserDao.queryRUByRoleId(role_id)
        for ru_user in ru_user_list:
            role_user, sys_user = ru_user[0], ru_user[1]
            if sys_user.employee_id:
                role_user_list.append(role_user)
                role_user_ids.append(role_user.user_id)

        # 删除绑定的系统人员
        for role_user in role_user_list:
            if role_user.user_id not in user_list:
                try:
                    SysRoleUserDao.deleteRoleUser(role_user.id)
                except AppException as e:
                    failed_list.append({"id": role_id, "message": e.message})
                    continue
                role_user_ids.remove(role_user.user_id)

        # 绑定系统人员
        for user_id in user_list:
            if user_id not in role_user_ids:
                try:
                    role_user = {"role_id": role_id, "user_id": user_id}
                    schema = SysRoleUserSchema()
                    role_user = schema.load(role_user)
                    SysRoleUserDao.addRoleUser(role_user)
                except AppException as e:
                    failed_list.append({"id": role_id, "message": e.message})

        if failed_list:
            data = {"failed_list": failed_list}
            return jsonify(AppResponse(data))

        return jsonify(AppResponse())

    @permission.check(p_list['p_employee_list'])
    @marsh_response(SysRoleEmployeeList)
    def get(self, role_id):
        """
        查询角色下面的企业用户
        :return:
        """
        parser_args = prepare_args_for_parser(role_employee_parser.copy())
        params = parser_args.parse_args()

        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")), "size": int(params.get("size"))
        }

        data["total"], rueb_list = SysRoleUserDao.queryRUEDByRoleIdFilter(role_id, **params)
        for rued in rueb_list:
            role_user, sys_user, employee, department = rued
            data["list"].append({
                "id": employee.id, "name": employee.name, "department": department.name,
                "sys_user_id": sys_user.id
            })

        return data


copy_role_parser = RequestParser()
copy_role_parser.add_argument('name', location='json', type=str)
copy_role_parser.add_argument('description', location='json', type=str)


@role_api.resource('', '/<role_id>/copy')
class RoleCopyAPI(Resource):

    @permission.check(p_list['p_role_mutation'])
    def post(self, role_id):
        """
        角色复制
        :return:
        """
        parser_args = prepare_args_for_parser(copy_role_parser.copy())
        params = parser_args.parse_args()

        role = SysRoleDao.querySysRoleById(role_id)

        schema = SysRoleSchema()
        copy_role = schema.load(params)
        for k in ['type', 'is_deactivate', 'expires_time']:
            setattr(copy_role, k, getattr(role, k))

        role.create_by, role.update_by = session['user_id'], session['user_id']
        SysRoleDao.addSysRole(copy_role)

        role_menu_list = SysRoleMenuDao.querySysRoleMenuByRoleId(role_id)
        for role_menu in role_menu_list:
            schema = SysRoleMenuSchema()
            role_menu = schema.dump(role_menu)

            copy_role_menu = copy.deepcopy(role_menu)
            copy_role_menu.pop('id')
            copy_role_menu['role_id'] = copy_role.id
            schema = SysRoleMenuSchema()
            copy_role_menu = schema.load(copy_role_menu)
            SysRoleMenuDao.addRoleMenu(copy_role_menu)

        return jsonify(AppResponse())


put_employee_bind_parser = RequestParser()
put_employee_bind_parser.add_argument('add', location='json', type=list)
put_employee_bind_parser.add_argument('delete', location='json', type=list)


@role_api.resource('', '/<role_id>/employee/bind')
class RoleEmployeeBindAPI(Resource):

    @permission.check(p_list['p_role_mutation'])
    def put(self, role_id):
        """
        单角色批量增加/修改企业人员，部分人员绑定失败返回失败人员列表，每个失败的原因
        :return:
        """
        failed_list, add_user_list, del_user_list = [], [], []
        parser_args = prepare_args_for_parser(put_employee_bind_parser.copy())
        params = parser_args.parse_args()

        # 查询企业用户是否为系统用户，不是则创建用户
        for employee_id in params['add']:
            sys_user = SysUserDao.querySysUserByEmployeeId(employee_id)
            if not sys_user:
                employee = TblEmployeeDao.queryEmployeeById(employee_id)
                if not employee:
                    failed_list.append({"id": role_id, "message": "未查询到企业用户ID"})

                email = employee.email.lower()
                if 'hillstonenet.com' in email:
                    sysuser = SysUserDao.querySysUserByEmail(email)
                    if sysuser:
                        update_data = {"employee_id": employee.id}
                        SysUserDao.updateSysUserById(sysuser.id, update_data)

                        role = SysRoleDao.querySysRoleByType(2)
                        role_user = SysRoleUserDao.querySysRoleByRoleUserId(role.id, sys_user.id)
                        if role_user:
                            role_user_list = SysRoleUserDao.querySysRolesByUserId(sys_user.id)
                            if len(role_user_list) > 1:
                                failed_list.append({"id": role_id, "message": "绑定失败，请先解除绑定其他角色"})
                                continue
                            SysRoleUserDao.deleteRoleUser(role_user.id)
                        user_id = sys_user.id
                    else:
                        schema = SysUserSchema(only=['id', 'display_name', 'employee_id'])
                        sys_user = schema.load({"display_name": employee.name, "employee_id": employee_id})
                        user_id = SysUserDao.addSysUserByEmployee(sys_user)

                    if user_id:
                        role = SysRoleDao.querySysRoleByType(1)
                        role_user = SysRoleUserDao.querySysRoleByRoleUserId(role.id, user_id)
                        if not role_user:
                            role_user = {"role_id": role.id, "user_id": user_id}
                            schema = SysRoleUserSchema()
                            role_user = schema.load(role_user)
                            SysRoleUserDao.addRoleUser(role_user)

                        add_user_list.append(sysuser.id)
                else:
                    failed_list.append({"id": role_id, "message": "非内部邮箱用户"})
            else:
                add_user_list.append(sys_user.id)

        # 查询企业用户是否为系统用户
        for employee_id in params['delete']:
            sys_user = SysUserDao.querySysUserByEmployeeId(employee_id)
            if sys_user:
                del_user_list.append(sys_user.id)

        # 获取角色绑定的用户
        role_user_ids, role_user_list = [], []
        ru_user_list = SysRoleUserDao.queryRUByRoleId(role_id)
        for ru_user in ru_user_list:
            role_user, sys_user = ru_user[0], ru_user[1]
            if sys_user.employee_id:
                role_user_list.append(role_user)
                role_user_ids.append(role_user.user_id)

        # 删除绑定的系统人员
        for del_user_id in del_user_list:
            if del_user_id in role_user_ids:
                role_user = SysRoleUserDao.querySysRoleByRoleUserId(role_id, del_user_id)
                if not role_user:
                    continue
                try:
                    SysRoleUserDao.deleteRoleUser(role_user.id)
                except AppException as e:
                    failed_list.append({"id": role_id, "message": e.message})
                    continue
                role_user_ids.remove(role_user.user_id)

        # 绑定系统人员
        for user_id in add_user_list:
            if user_id in role_user_ids:
                continue
            try:
                role_user = {"role_id": role_id, "user_id": user_id}
                schema = SysRoleUserSchema()
                role_user = schema.load(role_user)
                SysRoleUserDao.addRoleUser(role_user)
            except AppException as e:
                failed_list.append({"id": role_id, "message": e.message})

        if failed_list:
            data = {"failed_list": failed_list}
            return jsonify(AppResponse(data))

        return jsonify(AppResponse())


put_local_bind_parser = RequestParser()
put_local_bind_parser.add_argument('add', location='json', type=list)
put_local_bind_parser.add_argument('delete', location='json', type=list)


@role_api.resource('', '/<role_id>/local/bind')
class RoleUserLocalBindAPI(Resource):

    @permission.check(p_list['p_role_mutation'])
    def put(self, role_id):
        """
        单角色批量增加/修改系统人员，部分人员绑定失败返回失败人员列表，每个失败的原因
        :return:
        """
        failed_list = []
        parser_args = prepare_args_for_parser(put_local_bind_parser.copy())
        params = parser_args.parse_args()

        role_user_list = SysRoleUserDao.querySysRolesByRoleId(role_id)
        role_user_ids = [role_user.user_id for role_user in role_user_list]

        # 删除绑定的系统人员
        del_user_list = params['delete']
        for del_user_id in del_user_list:
            if del_user_id in role_user_ids:
                role_user = SysRoleUserDao.querySysRoleByRoleUserId(role_id, del_user_id)
                if not role_user:
                    continue
                try:
                    SysRoleUserDao.deleteRoleUser(role_user.id)
                except AppException as e:
                    failed_list.append({"id": role_id, "message": e.message})
                    continue
                role_user_ids.remove(role_user.user_id)

        # 绑定系统人员
        add_user_list = params['add']
        for user_id in add_user_list:
            if user_id in role_user_ids:
                continue
            try:
                role_user = {"role_id": role_id, "user_id": user_id}
                schema = SysRoleUserSchema()
                role_user = schema.load(role_user)
                SysRoleUserDao.addRoleUser(role_user)
            except AppException as e:
                failed_list.append({"id": role_id, "message": e.message})

        if failed_list:
            data = {"failed_list": failed_list}
            return jsonify(AppResponse(data))

        return jsonify(AppResponse())
