import casbin
import functools
import logging
import casbin_sqlalchemy_adapter
import os
import inspect

from datetime import datetime, date
from flask.json import JSONEncoder
from flask import session
from flask_restful import Api as _Api
from werkzeug.exceptions import HTTPException
from app.utils.casbin_grpc.protos import casbin_util_pb2_grpc
from app.utils.casbin_grpc.protos import casbin_util_pb2


class Api(_Api):
    def handle_error(self, e):
        if isinstance(e, HTTPException):
            raise HTTPException()
        else:
            raise Exception()


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            if isinstance(obj, date):
                return obj.strftime("%Y-%m-%d")
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


class AppException(Exception):
    """
    自定义请求异常
    """
    def __init__(self, message='接口请求异常', data=None, code=-1, c_code=None):
        self.data = data if data else {}
        self.message = message
        self.code = code
        self.c_code = c_code


class AppResponse(dict):
    """
    正常返回数据结构
    """
    def __init__(self, data=None, code=0, message='successful'):
        data = {} if data is None else data
        super().__init__(data=data, code=code, message=message)


class CasbinPolicyUtil:
    permission_api = {}

    def __init__(self, grpc_channel=None):
        self.ce = None
        self.stub = None
        if grpc_channel is not None:
            self.stub = casbin_util_pb2_grpc.CasbinUtilStub(grpc_channel)

    def init_app(self, engine):
        if self.stub:
            return
        file_filter = FileFilter()
        casbin_logger = logging.getLogger('casbin.rbac.default_role_manager.role_manager')
        casbin_logger.addFilter(file_filter)
        casbin_logger = logging.getLogger('casbin.model.assertion')
        casbin_logger.addFilter(file_filter)
        casbin_logger = logging.getLogger('casbin.core_enforcer')
        casbin_logger.addFilter(file_filter)

        model_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), './conf/casbin_model.conf')
        adapter = casbin_sqlalchemy_adapter.Adapter(engine)
        self.ce = casbin.Enforcer(model_path, adapter)

    def permissionApi(self, func, permission):
        module_name = inspect.getmodule(func).__name__
        if module_name.endswith('_api'):
            file_path = inspect.getmodule(func).__file__
            script_path = os.path.abspath(__file__)
            base_path = os.path.dirname(script_path).replace(r'\app\utils', '')
            relative_path = os.path.relpath(file_path, base_path).replace('\\', '/')
            line = inspect.getsourcelines(func)[1]
            class_name = func.__qualname__.split(".")[0].lower()

            if hasattr(inspect.getmodule(func), module_name):
                api = getattr(inspect.getmodule(func), module_name)
                if isinstance(permission, str):
                    self.permission_api.setdefault(permission, [])
                    self.permission_api[permission].append(
                        f'{func.__name__.upper()} [{api.blueprint.name}.{class_name}]({relative_path}#L{line})'
                    )
                elif isinstance(permission, list):
                    for p in permission:
                        self.permission_api.setdefault(p, [])
                        self.permission_api[p].append(
                            f'{func.__name__.upper()} [{api.blueprint.name}.{class_name}]({relative_path}#L{line})'
                        )

    def check(self, permission):
        def decorator(func):
            if os.environ.get('APP_SERVER', '') == 'permission_list':
                self.permissionApi(func, permission)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                user_id = session['user_id']

                def has_permission(p):
                    if self.stub:
                        feature = self.stub.enforce(casbin_util_pb2.UserPermission(user_id=user_id, permission=p))
                        return True if feature.verify_result else False
                    if self.ce:
                        return True if self.ce.enforce(user_id, p) else False

                is_allow = False
                if isinstance(permission, str):
                    is_allow = has_permission(permission)
                elif isinstance(permission, list):
                    for p in permission:
                        if has_permission(p):
                            is_allow = True
                            break

                if is_allow:
                    return func(*args, **kwargs)
                else:
                    raise AppException("您没有权限操作，请联系管理员！")

            return wrapper
        return decorator

    def addRoleUser(self, user_id, role_id):
        if self.ce:
            if role_id not in self.ce.get_roles_for_user(user_id):
                self.ce.add_role_for_user(user_id, role_id)
            return self.ce.get_roles_for_user(user_id)

        if self.stub:
            result = self.stub.getRolesUser(casbin_util_pb2.UserId(user_id=user_id))
            if role_id not in result.items:
                self.stub.addRoleUser(casbin_util_pb2.UserRole(user_id=user_id, role_id=role_id))
                result = self.stub.getRolesUser(casbin_util_pb2.UserId(user_id=user_id))
            return result.items

    def addRoleMenu(self, rule):
        if self.ce:
            self.ce.add_named_policy('p', rule)

        if self.stub:
            self.stub.addRule(casbin_util_pb2.Rule(rule=rule))

    def deleteRoleUser(self, user_id, role_id):
        if self.ce:
            if role_id in self.ce.get_roles_for_user(user_id):
                self.ce.delete_role_for_user(user_id, role_id)
            return self.ce.get_roles_for_user(user_id)

        if self.stub:
            result = self.stub.getRolesUser(casbin_util_pb2.UserId(user_id=user_id))
            if role_id in result.items:
                self.stub.deleteRoleUser(casbin_util_pb2.UserRole(user_id=user_id, role_id=role_id))
                result = self.stub.getRolesUser(casbin_util_pb2.UserId(user_id=user_id))
            return result.items

    def deleteRole(self, role_id):
        if self.ce:
            self.ce.delete_role(role_id)

        if self.stub:
            self.stub.deleteRole(casbin_util_pb2.RoleId(role_id=role_id))

    def deleteRoleMenu(self, rule):
        if self.ce:
            self.ce.remove_named_policy('p', rule)

        if self.stub:
            self.stub.deleteRoleMenu(casbin_util_pb2.Rule(rule=rule))

    def getPermissionByUserId(self, user_id):
        permission_list = []
        if self.ce:
            permissions = self.ce.get_implicit_permissions_for_user(user_id)
            for p in permissions:
                if p[2] == 'allow':
                    permission_list.append(p[1])
            return permission_list

        if self.stub:
            permissions = self.stub.getPermissionByUserId(casbin_util_pb2.UserId(user_id=user_id))
            for p in permissions.row:
                if p.items[2] == 'allow':
                    permission_list.append(p.items[1])
            return permission_list

    def userPermission(self, user_id, permission):
        if self.ce:
            permissions = self.ce.get_implicit_permissions_for_user(user_id)
            for p in permissions:
                if p[2] == 'allow' and p[1] in permission:
                    return True
            return False

        if self.stub:
            permissions = self.stub.getPermissionByUserId(casbin_util_pb2.UserId(user_id=user_id))
            for p in permissions.row:
                if p.items[2] == 'allow' and p.items[1] in permission:
                    return True
            return False


class FileFilter(logging.Filter):
    def filter(self, record):
        if record.filename in ['role_manager.py', 'assertion.py', 'core_enforcer.py']:
            return False
        return True
