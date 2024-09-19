import random
import string

from datetime import datetime
from urllib.parse import urlparse
from flask import Blueprint, request, session, redirect, current_app
from flask_restful import Resource
from app.extensions import sso_util, redis_client, jwt_util, logger, qywx_api
from app.config import SessionConfig
from app.enums.code_enum import CODE_LOGINEXPIRE
from app.controllers.dao import SysUserDao, SysRoleUserDao, SysRoleDao, TblEmployeeDao
from app.controllers.schema import SysUserSchema, SysRoleUserSchema
from app.controllers.response import marsh_response, SSOUser, UserInfo
from app.utils.api_util import Api, AppException, AppResponse

auth_app = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_api = Api(auth_app)


@auth_api.resource('/login')
class Login(Resource):

    def get(self):
        """
        SSO认证接口，认证成功后返回token
        :return:
        """
        if "code" not in request.args:
            if not request.args.get('return_url'):
                raise AppException('缺少return_url信息')

            state = ''.join(random.sample(string.ascii_letters + string.digits, 10))
            session['state'] = state
            session['return_url'] = request.args.get('return_url')
            base_url = request.base_url
            if request.headers.get('X-Forwarded-Proto'):
                base_url = "{}://{}/api/auth/login".format(request.headers.get('X-Forwarded-Proto'), request.host)
            session['login_url'] = base_url
            redirect_url = sso_util.authorize_url(redirect_uri=base_url, state=state)
            return redirect(redirect_url)

        else:
            state = session.get("state")
            if not state:
                raise AppException("登录状态异常，，请重新登录！")

            if session['state'] == request.args.get('state'):
                code = request.args.get('code')

                sso_access_token = sso_util.access_token(code, session['login_url'])
                sso_user = sso_util.get_user_info(sso_access_token)
                sso_user = SSOUser(**sso_user).to_dict()

                # 登陆系统后创建用户
                only = [
                    'id', 'user_id', 'user_name', 'dp_name', 'first_name', 'last_name', 'nick_name',
                    'birthday', 'user_type', 'company_name', 'mobile', 'email'
                ]
                user_schema = SysUserSchema(only=only)
                sys_user = user_schema.load(sso_user, unknown='exclude')
                user_id = SysUserDao.addSysUserBySSO(sys_user)
                if not user_id:
                    logger.error(f"用户创建失败，userId: {sso_user['user_id']}")
                    raise Exception("用户创建失败")

                # 获取角色，没有角色创建默认角色
                role_users = SysRoleUserDao.querySysRolesByUserId(user_id)
                if not role_users:
                    role_type = 1 if sso_user['user_type'] == 0 else 2
                    role = SysRoleDao.querySysRoleByType(role_type)
                    role_user = {"role_id": role.id, "user_id": user_id}
                    schema = SysRoleUserSchema()
                    role_user = schema.load(role_user)
                    SysRoleUserDao.addRoleUser(role_user)
                    role_users = [role_user]
                roles = [role_user.role_id for role_user in role_users]
                sso_user['roles'] = roles

                timestamp = datetime.now().timestamp()
                sso_user['timestamp'] = timestamp
                token = jwt_util.createToken(user_id, timestamp)
                # SSO登陆信息写入Redis缓存, key techadmin:online:userid
                redis_client.updateOnlineUser(user_id, sso_user, SessionConfig.get('sess_expire'))

                if not session.get("return_url"):
                    session['return_url'] = f'https://{current_app.config["SITE_DOMAIN"]}'
                session['return_url'] += ('&' if urlparse(session['return_url']).query else '?') + 'token=' + token
                return_url = session['return_url']
                session["user_id"] = user_id
                session['roles'] = roles
                return redirect(return_url)

            else:
                return AppException("请求携带的state不合法")


@auth_api.resource('/login/qywx')
class LoginQyWx(Resource):

    def get(self):
        if "code" not in request.args:
            raise AppException('认证失败')

        jscode2session = qywx_api.code2Session(request.args.get('code'))
        if not jscode2session:
            raise AppException('认证失败')

        qywx_user_id = jscode2session.get('userid')
        logger.info(f"LoginQyWx qywx_user_id: {qywx_user_id}")
        employee_sysuser = TblEmployeeDao.getESByEmployeeId(qywx_user_id)
        if not employee_sysuser:
            raise AppException('认证失败')

        sysuser_id = employee_sysuser[1].id

        role_users = SysRoleUserDao.querySysRolesByUserId(sysuser_id)
        if not role_users:
            raise AppException('认证失败')
        roles = [role_user.role_id for role_user in role_users]
        jscode2session['roles'] = roles

        timestamp = datetime.now().timestamp()
        jscode2session['timestamp'] = timestamp
        token = jwt_util.createToken(sysuser_id, timestamp)

        redis_client.updateWxOnlineUser(sysuser_id, jscode2session, SessionConfig.get('sess_expire'))

        return AppResponse(data={"token": token})


@auth_api.resource('/user_info')
class GetUserInfo(Resource):

    @marsh_response(UserInfo)
    def get(self):
        """
        获取用户信息接口
        :return:
        """
        user_id = session.get('user_id')
        if user_id is None:
            raise AppException("登陆异常，请重新登录！", c_code=CODE_LOGINEXPIRE)

        user = SysUserDao.querySysUserById(user_id)
        if not user:
            raise AppException("用户信息获取失败。", c_code=CODE_LOGINEXPIRE)

        user_schema = SysUserSchema()
        data = user_schema.dump(user)
        data['profile_url'] = 'https://passport.hillstonenet.com/MyProfile'

        return data
