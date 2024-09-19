import copy
import functools

from flask import jsonify, session
from app.utils.api_util import AppResponse
from marshmallow import Schema, fields
from app.controllers.dao import SysFieldPermissionDao


class ResponseSchema(Schema):
    __subsystem__ = ''
    __object__ = ''

    @classmethod
    def attributes(cls):
        attributes = []
        for name, field in cls().fields.items():
            attr = {
                'name': name, 'type': field.__class__.__name__, 'label': field.metadata.get('label')
            }
            attributes.append(attr)

        return attributes


def remove_empty_values(d):
    """
    遍历一个嵌套字典并删除值为空的字段
    """
    if isinstance(d, dict):
        return {k: remove_empty_values(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [remove_empty_values(v) for v in d if v is not None]
    else:
        return d


def get_fields(schema, allow, prefix="", result=None):
    if result is None:
        result = []

    for key in schema.fields:
        if isinstance(schema.fields[key], fields.Nested):
            get_fields(schema.fields[key].nested, allow, f"{prefix}{key}.", result)
        elif isinstance(schema.fields[key], fields.List):
            if key in allow:
                result.append(f"{prefix}{key}")
            if isinstance(schema.fields[key].inner, fields.Nested):
                get_fields(schema.fields[key].inner.nested, allow, f"{prefix}{key}.", result)
        else:
            if key in allow:
                result.append(f"{prefix}{key}")

    return result


def marsh_response(schema, permission=None, **mkwargs):
    """
    序列化响应数据，过滤字段
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mkwargs_copy = copy.copy(mkwargs)
            result = func(*args, **kwargs)
            if not result:
                return jsonify(AppResponse())

            result = remove_empty_values(result)
            if permission:
                field_names = SysFieldPermissionDao.getAllowFieldByRolePermission(session['roles'], permission)
                if field_names:
                    field_names += ['list', 'total', 'page', 'size']
                    data_keys = get_fields(schema(), field_names)

                    if "only" in mkwargs_copy.keys():
                        for field in mkwargs_copy["only"]:
                            if field not in data_keys:
                                mkwargs_copy["only"].remove(field)
                    elif data_keys:
                        mkwargs_copy.update({"only": data_keys})

            data = schema(**mkwargs_copy).load(result, unknown="exclude")
            return jsonify(AppResponse(data))
        return wrapper
    return decorator