import re
import traceback
import time

from urllib.parse import urlparse
from app.enums.code_enum import *
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app, session, abort, redirect
from sqlalchemy.exc import SQLAlchemyError
from requests.exceptions import Timeout
from marshmallow.exceptions import MarshmallowError
from app.config import ServerConfig, SessionConfig
from app.extensions import jwt_util, redis_client, logger
from app.utils.api_util import AppException
from app.models import db

main_app = Blueprint('main', __name__, static_folder=ServerConfig['avatar'])

DevStaticPath = [
    "\.html$", "\.html/$", "\.json$", "/doc/swagger", "(/swagger-resources/)+", "/favicon.ico$", "\.css$",
    "\.js$", "(/webSocket/)+", "/swagger-ui.html$", "(/swagger-resources/)+", "(/webjars/)+", "(/apidocs)+",
    "(/api-docs)+", "(/avatar/)+", "(/file/)+", "(/druid/)+", "(/code)", "\.png$", "\.map$"
]

WhiteList = [
    "/auth/login", "(/sys/resource/download/)+", "(/sys/resource/raw)", "(/common/attachment/download/)+",
    "/api/ping", "(/async_cloud_lab/instance/)+"
]

InternalPaths = ["/api/tools/sync", "/api/presales/project_manage/crm_async"]

TokenAuthPaths = ["/api/tools/assistant/opensearch/request/", "/api/tools/assistant/aiask/request/"]


@main_app.before_app_request
def check_csrf():
    if request.routing_exception:
        if request.routing_exception.code == 404:
            abort(404)
    if request.method == 'OPTIONS':
        return

    token = request.headers.get("Authorization")
    if token is not None:
        token = token.replace("Bearer ", "")
        if len(token) == 32:
            if token == 'nzWmCm3USFboWZrnZ2pp5y8ZETwmycg6' and any(
                    [re.findall(x, request.path) for x in InternalPaths]):
                return
            raise AppException("校验错误，请重新登录！", c_code=CODE_LOGINEXPIRE)

        token_decoded = jwt_util.loadsToken(token)
        if not token_decoded:
            raise AppException("校验错误，请重新登录！", c_code=CODE_LOGINEXPIRE)

        user_id = token_decoded.get('userid')
        timestamp = token_decoded.get('timestamp')

        platform = request.headers.get("X-Platform")
        simulation = request.headers.get("X-Real-User-Id")

        if platform:
            online_key = f"techadmin:online:qywx:userid:{user_id}"
        elif simulation:
            online_key = f"techadmin:online:simulation:userid:{user_id}"
        else:
            online_key = f"techadmin:online:userid:{user_id}"
        user = redis_client.getValueToJson(online_key)
        if user is None:
            raise AppException("登录已过期，请重新登录！", c_code=CODE_LOGINEXPIRE)
        if user['timestamp'] != timestamp:
            raise AppException("认证失败，请重新登录！", c_code=CODE_LOGINEXPIRE)

        session['user_id'] = user_id
        session['roles'] = user['roles']
        refresh_time = datetime.strptime(user["refresh_time"], '%Y-%m-%d %H:%M:%S')

        # token续期
        # 间隔时间大于 sess_renew 时，重新设置 loginTime 保持会话状态
        if datetime.now() - refresh_time >= timedelta(seconds=SessionConfig['sess_renew']):
            if "simulation" in online_key:
                redis_client.updateSimulationOnlineUser(user_id, user, SessionConfig.get('sess_expire'))
            elif "techadmin:online:userid" in online_key: 
                redis_client.updateOnlineUser(user_id, user, SessionConfig.get('sess_expire'))
        if request.method in ['POST', 'PUT'] and request.headers.get("Content-Type") == "application/json":
            logger.info(f'POST/PUT RequestBody: {request.json}, Request: {request.__dict__}')
        return

    elif (request.method == 'GET' and 'token' in request.args.keys() and
          any([re.findall(x, request.path) for x in TokenAuthPaths])
    ):
        token = request.args.get("token")
        token_decoded = jwt_util.loadsToken(token)
        if not token_decoded:
            raise AppException("校验错误，请重新登录！", c_code=CODE_LOGINEXPIRE)

        user_id = token_decoded.get('userid')
        timestamp = token_decoded.get('timestamp')

        platform = request.headers.get("X-Platform")
        simulation = request.headers.get("X-Real-User-Id")

        if platform:
            online_key = f"techadmin:online:qywx:userid:{user_id}"
        elif simulation:
            online_key = f"techadmin:online:simulation:userid:{user_id}"
        else:
            online_key = f"techadmin:online:userid:{user_id}"

        user = redis_client.getValueToJson(online_key)
        if user is None:
            raise AppException("登录已过期，请重新登录！", c_code=CODE_LOGINEXPIRE)
        if user['timestamp'] != timestamp:
            raise AppException("认证失败，请重新登录！", c_code=CODE_LOGINEXPIRE)

        session['user_id'] = user_id
        session['roles'] = user['roles']
        return

    else:
        white_list = WhiteList
        if current_app.config['ENV'] == 'dev':
            white_list += DevStaticPath
        if any([re.findall(x, request.path) for x in white_list]):
            return

    if session.get("user_id") and session.get("roles") and current_app.config['ENV'] == 'dev':
        return

    raise AppException("认证失败！")


@main_app.app_errorhandler(404)  # 捕捉的全局所有404
def error_404(error):
    traceback_date = int(round(time.time() * 1000))
    logger.warning('app_errorhandler 404: {"request_path": "%s"}' % request.path)
    response = dict(code=-1, message=f'404 Not Found. Hit: {traceback_date}', data={})
    return jsonify(response), 200


@main_app.app_errorhandler(400)  # 捕捉的全局所有400
def error_400(error):
    traceback_date = int(round(time.time() * 1000))
    logger.warning('app_errorhandler 400: {"error": "%s", "request": "%s"}' % (error.description, request.__dict__))
    if hasattr(error, 'data'):
        message = error.data.get("message")
        result = ';'.join([f'`{key}` {value}' for key, value in message.items()])
        message = f'400 Bad Request. Message: {result}. Hit: {traceback_date}'
    else:
        message = f'400 Bad Request. Description: {error.description}. Hit: {traceback_date}'
    response = dict(
        code=-1, message=f'{message}', data={}
    )
    return jsonify(response), 200


@main_app.app_errorhandler(AppException)  # 自定义异常
def error_app(error):
    logger.warning('app_errorhandler AppException: {"request": "%s", "message": "%s"}'
                   % (request.__dict__, error.message))
    if request.path == '/api/auth/login':
        traceback_date = int(round(time.time() * 1000))
        return_url = "{}://{}/error".format(
            urlparse(session['return_url']).scheme, urlparse(session['return_url']).hostname
        )
        error_params = '?backend_unknow_error={}&source_id={}'.format(error.message, traceback_date)
        return redirect(return_url + error_params)

    response = dict(code=error.code, data=error.data, message=error.message)
    return jsonify(response)


@main_app.app_errorhandler(Exception)  # 程序异常
def error_all(error):
    code = -1
    traceback.print_exc()
    traceback_date = int(round(time.time() * 1000))
    if request.path == '/api/auth/login':
        logger.warning('Login Exception: {"request": "%s", "error_str": "%s", "hint": %d}'
                       % (request.__dict__, str(error), traceback_date))
        return_url = "{}://{}/error".format(
            urlparse(session['return_url']).scheme, urlparse(session['return_url']).hostname
        )
        if isinstance(error, SQLAlchemyError):
            db.session.rollback()
            error_params = '?backend_unknow_error={}&source_id={}'.format("数据库操作异常，请联系管理员", traceback_date)
            return redirect(return_url + error_params)

        else:
            error_params = '?backend_unknow_error={}&source_id={}'.format("遇到未知登陆错误，请联系管理员", traceback_date)
            return redirect(return_url + error_params)

    if isinstance(error, MarshmallowError):
        logger.error('app_errorhandler MarshmallowError: {"request": "%s", "error_str": "%s", "hint": %d}'
                     % (request.__dict__, str(error), traceback_date))

        msg = f'数据解析异常，请联系管理员。Hint：{traceback_date}'

    elif isinstance(error, SQLAlchemyError):
        logger.warning('app_errorhandler SQLAlchemyError: {"request": "%s", "error_str": "%s", "hint": %d}'
                       % (request.__dict__, str(error), traceback_date))

        db.session.rollback()
        msg = f'数据库操作异常，请联系管理员。Hint：{traceback_date}'

    elif isinstance(error, Timeout):
        logger.warning('app_errorhandler Timeout: {"request": "%s", "error_str": "%s", "hint": %d}'
                       % (request.__dict__, str(error), traceback_date))
        msg = f'请求服务超时，请联系管理员。Hint：{traceback_date}'

    else:
        logger.error('app_errorhandler Unknown: {"request": "%s", "error_type": "%s", "error_str": "%s"， "hint": %d}'
                     % (request.__dict__, type(error), str(error), traceback_date))
        msg = f'遇到未知错误，请联系管理员。Hint：{traceback_date}'

    response = dict(code=code, data={}, message=msg, c_code=CODE_SERVERERROR)
    return jsonify(response)


@main_app.after_app_request
def after_request(response):
    # response.headers.add('Access-Control-Allow-Origin', '*')
    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type,authorization')
    # response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    # response.headers.add('Access-Control-Allow-Credentials', 'true')
    db.session.remove()
    return response
