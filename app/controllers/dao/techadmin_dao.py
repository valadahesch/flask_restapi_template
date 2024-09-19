from __future__ import annotations

from datetime import datetime
import json
from app.models import db
from app.utils.func_util import cacheable, clearcache
from app.utils.api_util import AppException
from app.extensions import permission, redis_client, cache
from app.controllers.schema import SysUserSchema, SysSubsystemObjectSchema, SysRoleUserSchema, TbEmployeeSchema
from app.models.techadmin import SysUser, SysRoleUser, SysRoleMenu, SysRole, SysMenu, CasbinRule, SysField, \
    SysSubsystemObject, TblEmployee, TblDepartment, SysFieldPermission, SysAttachment, OperateHistory
from sqlalchemy import or_
from app.extensions import redis_client


class SysUserDao:
    redis_key = 'models:techadmin:sys_user'

    @staticmethod
    def addSysUserBySSO(sso_user: SysUser, login_time=True):
        """
        登陆SSO的用户信息，更新到SysUser表中并记录首次登陆时间
        :param login_time:
        :param sso_user: sso认证后返回的UserInfo
        :return:
        """
        exist_user = SysUserDao.querySysUserByUserId(sso_user.user_id)
        if not exist_user and sso_user.email.endswith('Hillstonenet.com'):
            employee = TblEmployeeDao.queryEmployeeByEmail(sso_user.email)
            if employee:
                exist_user = SysUserDao.querySysUserByEmployeeId(employee.id)

        if exist_user:
            clear, commit = False, False
            for sso_key in sso_user.__dict__.keys():
                if sso_key.startswith('_') or sso_key == 'id':
                    continue
                if getattr(exist_user, sso_key) != getattr(sso_user, sso_key):
                    setattr(exist_user, sso_key, getattr(sso_user, sso_key))
                    commit = True

            if not exist_user.first_login_time and login_time:
                exist_user.first_login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                commit = True

            if not exist_user.employee_id and sso_user.email:
                if sso_user.email.lower().endswith('hillstonenet.com'):
                    employee = TblEmployeeDao.queryEmployeeByEmail(sso_user.email)
                    if employee:
                        exist_user.employee_id = employee.id
                        exist_user.display_name = employee.name
                        commit, clear = True, True

            if not exist_user.display_name:
                exist_user.display_name = sso_user.dp_name
                commit, clear = True, True

            if commit:
                db.session.commit()
            if clear:
                cache.clear()
            return exist_user.id

        else:
            if sso_user.email:
                if sso_user.email.lower().endswith('hillstonenet.com'):
                    employee = TblEmployeeDao.queryEmployeeByEmail(sso_user.email)
                    if employee:
                        sso_user.display_name = employee.name
                        sso_user.employee_id = employee.id

            if not sso_user.display_name:
                sso_user.display_name = sso_user.dp_name

            if login_time:
                sso_user.first_login_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db.session.add(sso_user)
            db.session.commit()
            return sso_user.id

    @staticmethod
    def addSysUserByEmployee(sys_user: SysUser):
        exist = SysUserDao.querySysUserByEmployeeId(sys_user.employee_id)
        if exist:
            return

        db.session.add(sys_user)
        db.session.commit()
        return sys_user.id

    @staticmethod
    @cacheable(f'{redis_key}:_id:$_id', SysUserSchema)
    def querySysUserById(_id) -> SysUser:
        """
        根据ID查SysUser数据
        :param _id:
        :return:
        """
        res = SysUser.query.filter(SysUser.id == _id).one_or_none()
        return res

    @staticmethod
    @cacheable(f'{redis_key}:display_name:$display_name', SysUserSchema)
    def querySysUserByDisplayName(display_name) -> SysUser:
        """
        根据ID查SysUser数据
        :param display_name:
        :return:
        """
        res = SysUser.query.filter(SysUser.display_name == display_name).one_or_none()
        return res

    @staticmethod
    def querySysUserByIds(ids) -> [SysUser]:
        """
        根据ID查SysUser数据
        :param ids:
        :return:
        """
        res = SysUser.query.filter(SysUser.id.in_(ids)).all()
        return res

    @staticmethod
    @cacheable(f'{redis_key}:manage_id:$manage_id', SysUserSchema, True)
    def querySysUserByManageId(manage_id: str) -> [SysUser]:
        """
        根据manage_id查询所有下属
        :param manage_id:
        :return:
        """
        res = SysUser.query.filter(SysUser.manage_id == manage_id).all()
        return res

    @staticmethod
    @cacheable(f'{redis_key}:user_id:$user_id', SysUserSchema)
    def querySysUserByUserId(user_id) -> SysUser:
        """
        根据UserID查SysUser数据
        :param user_id:
        :return:
        """
        res = SysUser.query.filter(SysUser.user_id == user_id).one_or_none()
        return res

    @staticmethod
    @cacheable(f'{redis_key}:email:$email', SysUserSchema)
    def querySysUserByEmail(email) -> SysUser:
        """
        根据email查SysUser数据
        :param email:
        :return:
        """
        if email is None or len(email.strip()) == 0:
            return None
        res = SysUser.query.filter(SysUser.email == email).one_or_none()
        return res

    @staticmethod
    @cacheable(f'{redis_key}:employee_id:$employee_id', SysUserSchema)
    def querySysUserByEmployeeId(employee_id) -> SysUser:
        """
        根据UserID查SysUser数据
        :param employee_id:
        :return:
        """
        res = SysUser.query.filter(SysUser.employee_id == employee_id).one_or_none()
        return res

    @staticmethod
    def querySysUserByEmployeeIds(employee_ids) -> [SysUser]:
        """
        根据UserID查SysUser数据
        :param employee_ids:
        :return:
        """
        res = SysUser.query.filter(SysUser.employee_id.in_(employee_ids)).all()
        return res

    @staticmethod
    def querySysUser() -> [SysUser]:
        """
        查询所有系统用户
        :return:
        """
        users = SysUser.query.all()
        return users

    @staticmethod
    def querySysUserByFilter(**kwargs) -> (int, [SysUser]):
        """
        :param kwargs: 查询参数
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000
        temp_query = SysUser.query.filter()

        for k, v in kwargs.items():
            if k == 'is_employee':
                if v:
                    temp_query = temp_query.filter(SysUser.employee_id != None)
                else:
                    temp_query = temp_query.filter(SysUser.employee_id == None)

            elif k == 'is_login':
                if v:
                    temp_query = temp_query.filter(SysUser.first_login_time != None)
                else:
                    temp_query = temp_query.filter(SysUser.first_login_time == None)

            elif k == "user_ids":
                temp_query = temp_query.filter(SysUser.id.in_(v))

            elif k not in SysUser.__dict__.keys() or (not v and v != 0):
                continue

            else:
                if isinstance(v, (bool, int)):
                    temp_query = temp_query.filter(getattr(SysUser, k) == v)
                else:
                    temp_query = temp_query.filter(getattr(SysUser, k).like(f"%{v}%"))

        res = temp_query.order_by(SysUser.display_name).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items

    @staticmethod
    @clearcache
    def updateSysUserById(_id, update_data: dict):
        exist_user = SysUserDao.querySysUserById(_id)
        if not exist_user:
            return

        SysUser.query.filter(SysUser.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def getSysUserEmployeeById(_id: str) -> (SysUser, TblEmployee):
        """
        获取所有下属的Id
        :return:
        """
        res = db.session.query(SysUser, TblEmployee).join(
            TblEmployee, SysUser.employee_id == TblEmployee.id
        ).filter(SysUser.id == _id).one_or_none()
        return res

    @staticmethod
    def getAllSysUserEmployeeById() -> (SysUser, TblEmployee):
        """
        获取所有下属的Id
        :return:
        """
        res = db.session.query(SysUser, TblEmployee).join(
            TblEmployee, SysUser.employee_id == TblEmployee.id
        ).all()
        return res

    @staticmethod
    def getSysUserEDById(_id: str) -> (SysUser, TblEmployee, TblDepartment):
        """
        获取所有下属的Id
        :return:
        """
        res = db.session.query(SysUser, TblEmployee, TblDepartment).join(
            TblEmployee, SysUser.employee_id == TblEmployee.id).join(
            TblDepartment, TblEmployee.main_department == TblDepartment.id).filter(
            SysUser.id == _id
        ).one_or_none()
        return res

    @staticmethod
    def getSysUserEDByEmployeeName(employee_name: str) -> [(SysUser, TblEmployee, TblDepartment)]:
        """
        获取所有下属的Id
        :return:
        """
        res = db.session.query(SysUser, TblEmployee, TblDepartment).join(
            TblEmployee, SysUser.employee_id == TblEmployee.id).join(
            TblDepartment, TblEmployee.main_department == TblDepartment.id).filter(
            TblEmployee.name.like(f"%{employee_name}%")
        ).all()
        return res

    @staticmethod
    def getSysPersonSubordinateIdById(_id: str) -> [SysUser]:
        """
        获取所有下属的Id
        :return:
        """
        visited = set()
        person_subordinate_list = []

        def dfs(sysuser_id):
            if sysuser_id in visited:
                return
            visited.add(sysuser_id)
            subordinate_list = SysUserDao.querySysUserByManageId(sysuser_id)
            for sysuser in subordinate_list:
                if sysuser.id in visited:
                    continue
                person_subordinate_list.append(sysuser)
                dfs(sysuser.id)

        dfs(_id)
        return person_subordinate_list

    @staticmethod
    def getSubordinateIdById(_id: str) -> [(SysUser, TblEmployee)]:
        """
        获取所有下属的Id
        :return:
        """
        sysuser_employee_list = []
        sysuser_employee = SysUserDao.getSysUserEmployeeById(_id)
        if sysuser_employee:
            sysuser_employee_list = db.session.query(SysUser, TblEmployee).join(
                TblEmployee, SysUser.employee_id == TblEmployee.id
            ).filter(TblEmployee.leader == sysuser_employee[1].userid).all()
            for sysuser_employee in sysuser_employee_list:
                sysuser = sysuser_employee[0]
                sysuser_employee_list.extend(SysUserDao.getSubordinateIdById(sysuser.id))
        return sysuser_employee_list

    @staticmethod
    def queryUsernameByUserId(user_id: str):
        res = SysUser.query.filter(SysUser.id == user_id).first()
        data = {
            "user_id": res.user_id,
            "user_name": res.user_name,
            "display_name": res.display_name
        }
        return data
    
    @staticmethod
    def querySysUserInfoById(user_id: str) -> dict:
        query = db.session.query(SysUser, TblEmployee)
        query = query.outerjoin(TblEmployee, SysUser.employee_id == TblEmployee.id)
        query = query.filter(SysUser.id == user_id) 
        result = query.first()
        if result:
            user,employee = result
            return {"user": user, "employee": employee}
        else:
            user = db.session.query(SysUser).filter(SysUser.id == user_id).first()
            return {"user": user, "employee": None}


    @staticmethod
    def querySysUserByEmployeeUserId(employee_user_id: str):
        query = db.session.query(TblEmployee, SysUser)
        query = query.outerjoin(SysUser, SysUser.employee_id == TblEmployee.id)
        query = query.filter(TblEmployee.userid == employee_user_id) 
        employee, user = query.first()
        return user, employee

    @staticmethod
    def getSysUserEDByIdsAndFilter(ids: list, **kwargs) -> [(SysUser, TblEmployee, TblDepartment)]:
        """
        根据用户Ids获取所有用户及企业用户信息
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000

        temp_query = db.session.query(SysUser, TblEmployee, TblDepartment).join(
            TblEmployee, SysUser.employee_id == TblEmployee.id).join(
            TblDepartment, TblEmployee.main_department == TblDepartment.id
        )

        if ids != ["*"]:
            temp_query = temp_query.filter(SysUser.id.in_(ids))

        for k, v in kwargs.items():
            obj = None
            if '.' in k:
                obj_name, k = k.split('.')[0], k.split('.')[1]
                if obj_name == 'E':
                    obj = TblEmployee
                elif obj_name == 'D':
                    obj = TblDepartment
                elif obj_name == 'U':
                    obj = SysUser

            if not obj:
                if k in TblEmployee.__dict__.keys():
                    obj = TblEmployee
                elif k in TblDepartment.__dict__.keys():
                    obj = TblDepartment
                elif k in SysUser.__dict__.keys():
                    obj = SysUser

            if obj:
                if isinstance(v, (bool, int)):
                    temp_query = temp_query.filter(getattr(obj, k) == v)
                else:
                    temp_query = temp_query.filter(getattr(obj, k).like(f"%{v}%"))

        res = temp_query.order_by(TblEmployee.name).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items

    @staticmethod
    def getDirectlyLeaderByUserId(user_id: str) -> [SysUser]:
        """
        获取站点及EHR直属上级
        :return:
        """
        directly_leader_list = []

        sysuser_employee = SysUserDao.getSysUserEmployeeById(user_id)
        if sysuser_employee:
            sys_user, employee = sysuser_employee
            if sys_user.manage_id:
                sysuser_manage = SysUserDao.querySysUserById(sys_user.manage_id)
                if sysuser_manage:
                    directly_leader_list.append(sysuser_manage)

            if employee.leader:
                employee_sysuser_leader = TblEmployeeDao.getESByEmployeeId(employee.leader)
                if employee_sysuser_leader:
                    employee, sysuser_leader = employee_sysuser_leader
                    if sysuser_leader not in directly_leader_list:
                        directly_leader_list.append(sysuser_leader)

        return directly_leader_list

class SysRoleDao:

    @staticmethod
    def querySysRole() -> [SysRole]:
        """
        查询所有系统功能、权限
        :return:
        """
        roles = SysRole.query.filter(SysRole.is_deleted != 1).all()
        return roles

    @staticmethod
    def querySysRoleById(_id: str) -> SysRole:
        """
        通过角色ID查询角色
        :param _id: 角色ID
        :return:
        """
        role = SysRole.query.filter(SysRole.id == _id).one_or_none()
        return role

    @staticmethod
    def querySysRoleByIds(ids: list) -> [SysRole]:
        """
        通过角色ID查询角色
        :param ids: 角色ID
        :return:
        """
        role = SysRole.query.filter(SysRole.id.in_(ids), SysRole.is_deactivate == False).all()
        return role

    @staticmethod
    def querySysRoleByName(name: str) -> SysRole:
        """
        根据角色名称查询系统角色
        :param name: 角色ID
        :return:
        """
        role = SysRole.query.filter(SysRole.name == name).one_or_none()
        return role

    @staticmethod
    def querySysRoleByType(_type: int) -> SysRole:
        """
        通过角色类型查询角色
        :param _type: 角色ID
        :return:
        """
        role = SysRole.query.filter(SysRole.type == _type).one_or_none()
        return role

    @staticmethod
    def addSysRole(new_role: SysRole) -> [SysRole]:
        """
        添加系统角色
        :param new_role: 菜单ID
        :return:
        """
        role = SysRoleDao.querySysRoleById(new_role.id)
        if role:
            raise AppException("创建失败，请重试")

        role = SysRoleDao.querySysRoleByName(new_role.name)
        if role:
            if not role.is_deleted:
                raise AppException("创建失败，名称已被创建")

        if new_role.type < 100:
            role = SysRoleDao.querySysRoleByType(new_role.type)
            if role:
                if not role.is_deleted:
                    raise AppException("创建失败，该角色类型只能创建一条")

        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_role.create_time, new_role.update_time = now_datetime, now_datetime
        db.session.add(new_role)
        db.session.commit()

    @staticmethod
    def updateSysRole(_id, update_data: dict):
        """
        更新系统角色
        :param _id: 角色ID
        :param update_data: 更新数据
        :return:
        """
        exist = SysRoleDao.querySysRoleById(_id)
        if not exist:
            raise AppException("更新失败，角色不存在")

        if update_data.get('name'):
            role = SysRoleDao.querySysRoleByName(update_data['name'])
            if role:
                if role.id != _id:
                    raise AppException("更新失败，该字段名已存在")

        if update_data.get('type'):
            if not ((1 <= update_data['type'] < 100 and 1 <= exist.type < 100)
                    or (100 <= update_data['type'] < 200 and 100 <= exist.type < 200)
                    or (200 <= update_data['type'] < 300 and 200 <= exist.type < 300)):
                role_user = SysRoleUserDao.querySysRolesByRoleId(_id)
                if role_user:
                    raise AppException("更新失败，变更角色类型请先解除绑定的用户")

            if update_data['type'] < 100:
                role = SysRoleDao.querySysRoleByType(update_data['type'])
                if role:
                    raise AppException("更新失败，该角色类型只能创建一条")

        if update_data.get('is_deactivate') and update_data.get('is_deactivate') != exist.is_deactivate:
            permission.deleteRole(_id)

        elif not update_data.get('is_deactivate') and update_data.get('is_deactivate') != exist.is_deactivate:
            role_user_list = SysRoleUserDao.querySysRolesByRoleId(_id)
            for role_user in role_user_list:
                permission.addRoleUser(role_user.user_id, role_user.role_id)

            role_menu_list = SysRoleMenuDao.querySysRoleMenuByRoleId(_id)
            for role_menu in role_menu_list:
                menu = SysMenuDao.querySysMenuById(role_menu.menu_id)
                if menu.permission:
                    rule = [role_menu.role_id, menu.permission, role_menu.effect]
                    permission.addRoleMenu(rule)

        SysRole.query.filter(SysRole.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def deleteSysRole(_id: str):
        """
        删除系统角色
        :return:
        """
        role = SysRoleDao.querySysRoleById(_id)
        if not role:
            raise AppException("删除失败，ID不存在")

        role_user = SysRoleUserDao.querySysRolesByRoleId(_id)
        if role_user:
            raise AppException("删除失败，该角色下绑定了用户")

        role_menu = SysRoleMenuDao.querySysRoleMenuByRoleId(_id)
        if role_menu:
            raise AppException("删除失败，该角色下绑定了菜单")

        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SysRole.query.filter(SysRole.id == _id).update({"is_deleted": True, "deleted_time": now_datetime})
        db.session.commit()

    @staticmethod
    def querySysRoleByFilter(deleted=False, **kwargs) -> (int, [SysRole]):
        """
        根据过滤条件查询角色
        :param deleted: 是否删除
        :param kwargs: 过滤条件
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000
        temp_query = SysRole.query.filter()

        if deleted:
            temp_query = temp_query.filter(SysRole.deleted_time != None)
        else:
            temp_query = temp_query.filter(SysRole.deleted_time == None)

        for k, v in kwargs.items():
            if k not in SysRole.__dict__.keys() or v == None:
                continue

            if isinstance(v, (bool, int)):
                temp_query = temp_query.filter(getattr(SysRole, k) == v)
            else:
                temp_query = temp_query.filter(getattr(SysRole, k).like(f"%{v}%"))

        res = temp_query.order_by(SysRole.create_time).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items


class SysMenuDao:

    @staticmethod
    def querySysMenuByType() -> [SysMenu]:
        """
        查询所有系统功能
        :return:
        """
        menu = SysMenu.query.filter(
            SysMenu.deleted_time == None, or_(SysMenu.menu_type == 1, SysMenu.menu_type == 2)
        ).all()
        return menu

    @staticmethod
    def querySysMenu() -> [SysMenu]:
        """
        查询所有系统功能、权限
        :return:
        """
        menu = SysMenu.query.filter(SysMenu.deleted_time == None).all()
        return menu

    @staticmethod
    def querySysMenuById(_id: str) -> SysMenu:
        """
        通过ID查询系统功能、权限
        :param _id: 角色ID
        :return:
        """
        menu = SysMenu.query.filter(SysMenu.id == _id).one_or_none()
        return menu

    @staticmethod
    def querySysMenuByIds(ids: list) -> [SysMenu]:
        """
        通过ID查询系统功能、权限
        :param ids: 角色ID
        :return:
        """
        menu = SysMenu.query.filter(SysMenu.id.in_(ids), SysMenu.menu_type.in_([1, 2])).all()
        return menu

    @staticmethod
    def querySysMenuByParentTitle(parent_id, title: str) -> SysMenu:
        """
        通过父ID、Title名称查询系统功能、权限
        :param parent_id: 父ID
        :param title: 菜单名称
        :return:
        """
        menu = SysMenu.query.filter(
            SysMenu.parent_id == parent_id, SysMenu.title == title, SysMenu.deleted_time == None).one_or_none()
        return menu

    @staticmethod
    def querySysMenusByParentId(parent_id: str) -> [SysMenu]:
        """
        根据父节点ID查询子节点功能
        :param parent_id: 父节点Id
        :return:
        """
        menus = SysMenu.query.filter(SysMenu.parent_id == parent_id, SysMenu.deleted_time == None).all()
        return menus

    @staticmethod
    def querySysPermissionByParentId(parent_id: str) -> [SysMenu]:
        """
        根据父节点ID查询子节点权限
        :param parent_id: 父节点Id
        :return:
        """
        menus = SysMenu.query.filter(
            SysMenu.parent_id == parent_id, SysMenu.menu_type == 3, SysMenu.deleted_time == None).all()
        return menus

    @staticmethod
    def querySysMenuByPermission(permission_mark: str) -> [SysMenu]:
        """
        根据权限标识查权限
        :param permission_mark: 权限标识
        :return:
        """
        menu = SysMenu.query.filter(SysMenu.permission == permission_mark, SysMenu.deleted_time == None).all()
        return menu

    @staticmethod
    def querySysMenuByLink(link: str) -> SysMenu | None:
        """
        根据前端路由查权限
        :param link: 权限标识
        :return:
        """
        if not link:
            return
        menu = SysMenu.query.filter(SysMenu.link == link, SysMenu.deleted_time == None).one_or_none()
        return menu

    @staticmethod
    def queryChildMenuById(_id) -> [SysMenu]:
        menu = SysMenuDao.querySysMenuById(_id)
        if menu:
            menus = SysMenu.query.filter(SysMenu.full_path.like(f"{menu.full_path}%")).all()
            return menus
        return []

    @staticmethod
    def addSysMenu(new_menu: SysMenu):
        """
        添加菜单
        :return:
        """
        menu = SysMenuDao.querySysMenuById(new_menu.id)
        if menu:
            raise AppException("创建失败，请重试")

        menu = SysMenuDao.querySysMenuByParentTitle(new_menu.parent_id, new_menu.title)
        if menu:
            raise AppException("创建失败，名称已被创建")

        menu = SysMenuDao.querySysMenuByLink(new_menu.link)
        if menu:
            raise AppException("创建失败，链接已被创建")

        if new_menu.parent_id:
            menu = SysMenuDao.querySysMenuById(new_menu.parent_id)
            if menu:
                new_menu.full_path = f'{menu.full_path}/{new_menu.id}'
        else:
            new_menu.full_path = f'/{new_menu.id}'

        new_menu.menu_sort = SysMenuDao.getMenuIndexByIds(new_menu.parent_id) + 1

        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_menu.create_time = now_datetime
        new_menu.update_time = now_datetime
        db.session.add(new_menu)
        db.session.commit()

    @staticmethod
    def deleteSysMenu(_id: str):
        """
        删除菜单
        :return:
        """
        menu = SysMenuDao.querySysMenuById(_id)
        if not menu:
            raise AppException("删除失败，功能ID不存在")

        parent_menu = SysMenuDao.querySysMenusByParentId(_id)
        if parent_menu:
            raise AppException("删除失败，功能下绑定了其他功能")

        role_menu = SysRoleMenuDao.querySysRoleMenuByMenuId(_id)
        if role_menu:
            raise AppException("删除失败，功能下绑定了角色")

        now_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SysMenu.query.filter(SysMenu.id == _id).update({"is_deleted": True, "deleted_time": now_datetime})
        db.session.commit()

    @staticmethod
    def updateSysMenu(_id, update_data: dict):
        """
        更新功能
        :param _id: 功能ID
        :param update_data: 字段更新数据
        :return:
        """
        if update_data.get('parent_id') == _id:
            raise AppException("更新失败，无法绑定自身为父节点")

        exist = SysMenuDao.querySysMenuById(_id)
        if not exist:
            raise AppException("更新失败，功能不存在")

        if 'title' in update_data.keys():
            title = update_data.get('title')
            menu = SysMenuDao.querySysMenuByParentTitle(exist.parent_id, title)
            if menu:
                if menu.id != _id:
                    raise AppException("更新失败，该字段名已存在")

        if 'link' in update_data.keys() and update_data.get('link') != "":
            link = update_data.get('link')
            menu = SysMenuDao.querySysMenuByLink(link)
            if menu:
                if menu.id != _id:
                    raise AppException("更新失败，该链接已存在")

        if 'field_object' in update_data.keys() and update_data.get('field_object') != "":
            role_menu_list = SysRoleMenuDao.querySysRoleMenuByMenuId(exist.id)
            if role_menu_list:
                for role_menu in role_menu_list:
                    field_permission = SysFieldPermissionDao.queryFieldPermissionByRoleMenuId(role_menu.id)
                    if field_permission:
                        raise AppException("更新失败，请先解绑菜单下绑定的字段权限")

        update_data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SysMenu.query.filter(SysMenu.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def getMenuIndexByIds(parent_id: str) -> int:
        """
        获取菜单下标
        :param parent_id: 权限标识
        :return:
        """
        menu = SysMenu.query.filter(SysMenu.parent_id == parent_id).order_by(SysMenu.menu_type).first()
        if menu:
            return menu.menu_sort
        else:
            return 0

    @staticmethod
    def querySysMenuByFilter(deleted=False, **kwargs) -> (int, [SysMenu]):
        """
        根据过滤条件查询功能
        :param deleted: 是否删除
        :param kwargs: 过滤条件
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000

        temp_query = SysMenu.query.filter()

        if deleted:
            temp_query = temp_query.filter(SysMenu.deleted_time != None)
        else:
            temp_query = temp_query.filter(SysMenu.deleted_time == None)

        for k, v in kwargs.items():
            if k not in SysMenu.__dict__.keys() or v == None:
                continue

            if isinstance(v, (bool, int)):
                temp_query = temp_query.filter(getattr(SysMenu, k) == v)
            else:
                temp_query = temp_query.filter(getattr(SysMenu, k).like(f"%{v}%"))

        res = temp_query.order_by(SysMenu.create_time).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items

    @staticmethod
    def queryParentMenusById(_id) -> [SysMenu]:
        menus = []
        menu = SysMenuDao.querySysMenuById(_id)
        if menu.parent_id:
            menus.append(menu)
            menus += SysMenuDao.queryParentMenusById(menu.parent_id)
            return menus

        return [menu]


class SysRoleUserDao:
    redis_key = 'models:techadmin:sys_role_user'

    @staticmethod
    def queryRoleUser() -> [SysRoleUser]:
        """
        根据ID查角色-用户
        :return:
        """
        role_users = SysRoleUser.query.all()
        return role_users

    @staticmethod
    @cacheable(f'{redis_key}:_id:$_id', SysRoleUserSchema)
    def queryRoleUserById(_id: str) -> SysRoleUser:
        """
        根据ID查角色-用户
        :param _id: ID
        :return:
        """
        role_users = SysRoleUser.query.filter(SysRoleUser.id == _id).one_or_none()
        return role_users

    @staticmethod
    @cacheable(f'{redis_key}:user_id:$user_id', SysRoleUserSchema, True)
    def querySysRolesByUserId(user_id: str) -> [SysRoleUser]:
        """
        通过UserId查所有绑定的角色
        :param user_id: 用户ID
        :return:
        """
        role_users = SysRoleUser.query.filter(SysRoleUser.user_id == user_id).all()
        return role_users

    @staticmethod
    @cacheable(f'{redis_key}:role_id:$role_id', SysRoleUserSchema, True)
    def querySysRolesByRoleId(role_id: str) -> [SysRoleUser]:
        """
        通过RoleId查所有绑定的用户
        :param role_id: 用户ID
        :return:
        """
        role_users = SysRoleUser.query.filter(SysRoleUser.role_id == role_id).all()
        return role_users

    @staticmethod
    @cacheable(f'{redis_key}:role_id:$role_id:user_id:$user_id', SysRoleUserSchema)
    def querySysRoleByRoleUserId(role_id: str, user_id: str) -> SysRoleUser:
        """
        通过RoleId查所有绑定的用户
        :param user_id:
        :param role_id: 用户ID
        :return:
        """
        role_user = SysRoleUser.query.filter(
            SysRoleUser.user_id == user_id, SysRoleUser.role_id == role_id).one_or_none()
        return role_user

    @staticmethod
    @clearcache
    def addRoleUser(role_user: SysRoleUser):
        exist = SysRoleUserDao.queryRoleUserById(role_user.id)
        if exist:
            raise AppException("绑定失败，角色用户ID已被创建")

        exist = SysRoleUserDao.querySysRoleByRoleUserId(role_user.role_id, role_user.user_id)
        if exist:
            return

        role = SysRoleDao.querySysRoleById(role_user.role_id)
        if role:
            if role.type == 1:
                external_role = SysRoleDao.querySysRoleByType(2)
                exist = SysRoleUserDao.querySysRoleByRoleUserId(external_role.id, role_user.user_id)
                if exist:
                    raise AppException("绑定失败, 外部角色不能同时绑定内部角色")

            elif role.type == 2:
                inner_role = SysRoleDao.querySysRoleByType(1)
                exist = SysRoleUserDao.querySysRoleByRoleUserId(inner_role.id, role_user.user_id)
                if exist:
                    raise AppException("绑定失败，内部角色不能同时绑定外部角色")

            elif 100 <= role.type < 200:
                inner_role = SysRoleDao.querySysRoleByType(1)
                exist = SysRoleUserDao.querySysRoleByRoleUserId(inner_role.id, role_user.user_id)
                if not exist:
                    raise AppException("绑定失败，该角色不是内部角色")

            elif 200 <= role.type < 300:
                external_role = SysRoleDao.querySysRoleByType(2)
                exist = SysRoleUserDao.querySysRoleByRoleUserId(external_role.id, role_user.user_id)
                if not exist:
                    raise AppException("绑定失败，该角色不是外部角色")

        db.session.add(role_user)
        db.session.commit()

        roles = permission.addRoleUser(role_user.user_id, role_user.role_id)
        redis_client.updateUserRole(role_user.user_id, roles)

        return role_user.id

    @staticmethod
    @clearcache
    def deleteRoleUser(_id):
        exist = SysRoleUserDao.queryRoleUserById(_id)
        if not exist:
            raise AppException("删除失败，角色用户ID不存在")

        role = SysRoleDao.querySysRoleById(exist.role_id)
        if role.type in [1, 2]:
            role_user_list = SysRoleUserDao.querySysRolesByUserId(exist.user_id)
            if len(role_user_list) > 1:
                raise AppException("删除失败，请先解除绑定其他角色")

        SysRoleUser.query.filter(SysRoleUser.id == _id).delete()
        db.session.commit()

        roles = permission.deleteRoleUser(exist.user_id, exist.role_id)
        redis_client.updateUserRole(exist.user_id, roles)

    @staticmethod
    def getSRByByUserId(user_id) -> (SysRoleUser, SysRole):
        """
        :param user_id: 系统用户ID
        :return:
        """
        ru_role_list = db.session.query(
            SysRoleUser, SysRole).join(
            SysRole, SysRole.id == SysRoleUser.role_id).filter(
            SysRoleUser.user_id == user_id).all()

        return ru_role_list

    @staticmethod
    def queryRUByRoleId(role_id: str) -> [(SysRoleUser, SysUser)]:
        """
        通过RoleId查所有绑定的用户
        :param role_id: 用户ID
        :return:
        """
        ru_user_list = db.session.query(
            SysRoleUser, SysUser).join(
            SysUser, SysUser.id == SysRoleUser.user_id).filter(
            SysRoleUser.role_id == role_id).all()

        return ru_user_list

    @staticmethod
    def queryRUByRoleIdByFilter(role_id: str, **kwargs) -> [(SysRoleUser, SysUser)]:
        """
        通过RoleId分页查询绑定的用户
        :param role_id: 用户ID
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000
        temp = db.session.query(SysRoleUser, SysUser).join(
            SysUser, SysUser.id == SysRoleUser.user_id).filter(
            SysRoleUser.role_id == role_id
        )

        if kwargs.get("name"):
            temp = temp.filter(SysUser.display_name.like(f"%{kwargs.get('name')}%"))

        res = temp.order_by(SysUser.id).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items

    @staticmethod
    def queryRUEDByRoleIdFilter(role_id: str, **kwargs) -> (int, [(SysRoleUser, SysUser, TblEmployee, TblDepartment)]):
        """
        通过RoleId查所有绑定企业用户
        :param role_id: 用户ID
        :param kwargs: 查询参数
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000
        temp = db.session.query(SysRoleUser, SysUser, TblEmployee, TblDepartment).join(
            SysUser, SysUser.id == SysRoleUser.user_id).join(
            TblEmployee, TblEmployee.id == SysUser.employee_id).join(
            TblDepartment, TblDepartment.id == TblEmployee.department
        ).filter(
            SysRoleUser.role_id == role_id, SysUser.employee_id != ""
        )

        if kwargs.get("name"):
            temp = temp.filter(TblEmployee.name.like(f"%{kwargs.get('name')}%"))

        if kwargs.get("department"):
            temp = temp.filter(TblDepartment.name.like(f"%{kwargs.get('department')}%"))

        res = temp.order_by(SysUser.id).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items

    @staticmethod
    def getSRUByByUserId(user_id) -> (SysRoleUser, SysRole, SysUser):
        """
        :param user_id: 系统用户ID
        :return:
        """
        ru_role_user = db.session.query(
            SysRoleUser, SysRole, SysUser).join(
            SysRole, SysRole.id == SysRoleUser.role_id).join(
            SysUser, SysUser.id == SysRoleUser.user_id
        ).filter(SysRoleUser.user_id == user_id).all()

        return ru_role_user


class SysRoleMenuDao:

    @staticmethod
    def queryRoleMenu() -> [SysRoleMenu]:
        """
        根据ID查角色-用户
        :return:
        """
        role_menus = SysRoleMenu.query.all()
        return role_menus

    @staticmethod
    def querySysRoleMenuById(_id: str) -> SysRoleMenu:
        """
        通过RoleId查所有绑定的权限配置
        :param _id: 角色ID
        :return:
        """
        role_menus = SysRoleMenu.query.filter(SysRoleMenu.id == _id).one_or_none()
        return role_menus

    @staticmethod
    def querySysRoleMenuByRoleId(role_id: str) -> [SysRoleMenu]:
        """
        通过RoleId查所有绑定的权限配置
        :param role_id: 角色ID
        :return:
        """
        role_menus = SysRoleMenu.query.filter(SysRoleMenu.role_id == role_id).all()
        return role_menus

    @staticmethod
    def querySysRoleMenuByRoleIds(role_ids: list) -> [SysRoleMenu]:
        """
        通过RoleId查所有绑定的权限配置
        :param role_ids: 角色ID
        :return:
        """
        role_menus = SysRoleMenu.query.filter(SysRoleMenu.role_id.in_(role_ids)).all()
        return role_menus

    @staticmethod
    def querySysRoleMenuByRoleMenuId(role_id: str, menu_id: str) -> SysRoleMenu:
        """
        通过RoleId、menu_id查绑定的权限配置
        :param role_id: 角色ID
        :param menu_id: 菜单ID
        :return:
        """
        role_menu = SysRoleMenu.query.filter(
            SysRoleMenu.role_id == role_id, SysRoleMenu.menu_id == menu_id
        ).one_or_none()
        return role_menu

    @staticmethod
    def querySysRoleMenuByMenuId(menu_id: str) -> [SysRoleMenu]:
        """
        通过menu_id查绑定的权限配置
        :param menu_id: 菜单ID
        :return:
        """
        role_menu = SysRoleMenu.query.filter(SysRoleMenu.menu_id == menu_id).all()
        return role_menu

    @staticmethod
    def deleteRoleMenu(_id):
        exist = SysRoleMenuDao.getRoleJoinMenuById(_id)
        if not exist:
            raise AppException("删除失败，权限不存在")

        SysRoleMenu.query.filter(SysRoleMenu.id == _id).delete()
        db.session.commit()

        role_menu, menu = exist
        if menu.permission:
            menu_list = SysRoleMenuDao.getRoleJoinMenuByRoleId(role_menu.role_id, menu.permission)
            if not menu_list:
                rule = [role_menu.role_id, menu.permission, role_menu.effect]
                permission.deleteRoleMenu(rule)

    @staticmethod
    def addRoleMenu(role_menu: SysRoleMenu):
        exist = SysRoleMenu.query.filter(
            SysRoleMenu.role_id == role_menu.role_id, SysRoleMenu.menu_id == role_menu.menu_id,
            SysRoleMenu.effect == role_menu.effect
        ).one_or_none()
        if exist:
            raise AppException("创建失败，权限ID已存在")

        db.session.add(role_menu)
        db.session.commit()

        menu = SysMenuDao.querySysMenuById(role_menu.menu_id)
        if menu.permission:
            rule = [role_menu.role_id, menu.permission, role_menu.effect]
            permission.addRoleMenu(rule)

        return role_menu.id

    @staticmethod
    def updateRoleMenu(_id, update_data: dict):
        """
        更新字段
        :param _id: 权限ID
        :param update_data: 字段权限数据
        :return:
        """
        exist = SysRoleMenuDao.querySysRoleMenuById(_id)
        if not exist:
            raise AppException("更新失败，权限不存在")

        SysRoleMenu.query.filter(SysRoleMenu.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def getAllowMenuByRolesId(role_ids: list):
        allow_menu_ids, deny_menu_ids = [], []
        role_list = SysRoleDao.querySysRoleByIds(role_ids)
        role_list = [role.id for role in role_list]
        role_menu_list = SysRoleMenuDao.querySysRoleMenuByRoleIds(role_list)
        for role_menu in role_menu_list:
            if role_menu.effect == 'allow' and role_menu.menu_id not in allow_menu_ids:
                allow_menu_ids.append(role_menu.menu_id)
            elif role_menu.effect == 'deny':
                deny_menu_ids.append(role_menu.menu_id)

        for deny_menu_id in deny_menu_ids:
            if deny_menu_id not in allow_menu_ids:
                continue
            allow_menu_ids.remove(deny_menu_id)

        res = SysMenuDao.querySysMenuByIds(allow_menu_ids)
        return res

    @staticmethod
    def getRoleMenuByRolePermission(role_ids, permission_mark) -> [SysRoleMenu]:
        role_menu_ids = []
        menus = SysMenuDao.querySysMenuByPermission(permission_mark)
        for menu in menus:
            for role_id in role_ids:
                role_menu = SysRoleMenuDao.querySysRoleMenuByRoleMenuId(role_id, menu.id)
                role_menu_ids.append(role_menu)
        return role_menu_ids

    @staticmethod
    def getRMByRoleId(role_id) -> [(SysRoleUser, SysMenu)]:
        """
        :param role_id: 角色ID
        :return:
        """
        rm_menu_list = db.session.query(
            SysRoleMenu, SysMenu).join(
            SysMenu, SysMenu.id == SysRoleMenu.menu_id).filter(
            SysRoleMenu.role_id == role_id).all()

        return rm_menu_list

    @staticmethod
    def getRoleJoinMenuById(_id) -> (SysRoleUser, SysMenu):
        """
        :param _id: 角色-菜单ID
        :return:
        """
        rm_menu_list = db.session.query(
            SysRoleMenu, SysMenu).join(
            SysMenu, SysMenu.id == SysRoleMenu.menu_id).filter(
            SysRoleMenu.id == _id
        ).one_or_none()

        return rm_menu_list

    @staticmethod
    def getRoleJoinMenuByRoleId(role_id: str, permission_mark: str) -> [(SysRoleUser, SysMenu)]:
        """
        :param permission_mark:
        :param role_id: 角色ID
        :return:
        """
        rm_menu_list = db.session.query(
            SysRoleMenu, SysMenu).join(
            SysMenu, SysMenu.id == SysRoleMenu.menu_id).filter(
            SysRoleMenu.role_id == role_id, SysMenu.permission == permission_mark
        ).all()

        return rm_menu_list


class SysCasbinPolicyDao:

    @staticmethod
    def generateCasbinPolicy():
        """
        生成 Casbin Policy 模型到数据库
        :param:
        :return:
        """
        policy = []
        role_user_list = SysRoleUserDao.queryRoleUser()
        for role_user in role_user_list:
            policy.append({"ptype": 'g', 'v0': role_user.user_id, 'v1': role_user.role_id})

        role_menu_list = SysRoleMenuDao.queryRoleMenu()
        for role_menu in role_menu_list:
            menu = SysMenuDao.querySysMenuById(role_menu.menu_id)
            if menu.permission:
                policy.append({"ptype": 'p', 'v0': role_menu.role_id, 'v1': menu.permission, 'v2': role_menu.effect})

        return policy

    @staticmethod
    def addCasbinPolicy(policy: CasbinRule):
        """
        添加 Casbin Policy
        :param policy:
        :return:
        """
        exist_policy = CasbinRule.query.filter(
            CasbinRule.ptype == policy.ptype, CasbinRule.v0 == policy.v0,
            CasbinRule.v1 == policy.v1, CasbinRule.v2 == policy.v2
        ).one_or_none()
        if exist_policy:
            return

        db.session.add(policy)
        db.session.commit()


class SysFieldDao:

    @staticmethod
    def queryFieldById(_id) -> SysField:
        """
        查询所有子系统列表
        :return:
        """
        res = SysField.query.filter(SysField.id == _id).one_or_none()
        return res

    @staticmethod
    def addField(field: SysField):
        """
        新增字段
        :param field: 字段数据
        :return:
        """
        exist = SysFieldDao.queryFieldByNameObjectId(field.name, field.object_id)
        if exist:
            raise AppException("添加失败，字段Name已存在")

        field.create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.session.add(field)
        db.session.commit()

    @staticmethod
    def updateField(_id, update_data: dict):
        """
        更新字段
        :param _id: 字段数据
        :param update_data: 字段更新数据
        :return:
        """
        exist = SysFieldDao.queryFieldById(_id)
        if not exist:
            raise AppException("更新失败，字段不存在")

        if 'delete_time' in update_data.keys():
            if update_data.get('delete_time') == None:
                if SysFieldDao.queryFieldByNameObjectId(exist.name, exist.object_id):
                    raise AppException("恢复失败，该字段名已存在")

        if 'name' in update_data.keys():
            name = update_data.get('name')
            field = SysFieldDao.queryFieldByNameObjectId(name, exist.object_id)
            if field:
                if field.id != _id:
                    raise AppException("更新失败，该字段名已存在")

        SysField.query.filter(SysField.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def deleteField(_id):
        """
        删除字段
        :param _id: 字段数据
        :return:
        """
        exist = SysFieldDao.queryFieldById(_id)
        if not exist:
            raise AppException("删除失败，字段不存在")

        exist = SysFieldPermissionDao.queryFieldPermissionByFieldId(_id)
        if not exist:
            raise AppException("删除失败，请先删除绑定的权限")

        delete_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        SysField.query.filter(SysField.id == _id).update({"delete_time": delete_time})
        db.session.commit()

    @staticmethod
    def queryFieldByNameObjectId(name: str, object_id: str) -> SysField:
        """
        根据name, meta_id查SysField数据
        :param name: 字段名
        :param object_id: 字段元ID
        :return:
        """
        res = SysField.query.filter(
            SysField.name == name, SysField.object_id == object_id,
            SysField.delete_time == None
        ).one_or_none()
        return res

    @staticmethod
    def queryFieldsByObjectId(object_id: str) -> [SysField]:
        """
        根据meta_id查询所有SysField数据
        :param object_id: 字段元ID
        :return:
        """
        res = SysField.query.filter(SysField.object_id == object_id).all()
        return res

    @staticmethod
    def queryFieldsByFilter(object_id=None, deleted=False, **kwargs) -> (int, [SysField]):
        """
        根据object_id查询所有SysField数据
        :param deleted:
        :param object_id: 字段对象ID
        :param kwargs: 查询参数
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000
        temp_query = SysField.query.filter()
        if object_id:
            temp_query = temp_query.filter(SysField.object_id == object_id)

        if deleted:
            temp_query = temp_query.filter(SysField.delete_time != None)
        else:
            temp_query = temp_query.filter(SysField.delete_time == None)

        for k, v in kwargs.items():
            if k not in SysField.__dict__.keys() or not v:
                continue

            if isinstance(v, (bool, int)):
                temp_query = temp_query.filter(getattr(SysField, k) == v)
            else:
                temp_query = temp_query.filter(getattr(SysField, k).like(f"%{v}%"))

        res = temp_query.order_by(SysField.id).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items


class SysSubsystemObjectDao:
    redis_key = 'models:techadmin:sys_subsystem_object'

    @staticmethod
    def querySubsystem() -> [SysSubsystemObject]:
        """
        查询所有子系统列表
        :return:
        """
        res = SysSubsystemObject.query.filter(SysSubsystemObject.type == 1).all()
        return res

    @staticmethod
    @cacheable(f'{redis_key}:_id:$_id', SysSubsystemObjectSchema)
    def querySubObjectById(_id: str) -> SysSubsystemObject:
        """
        根据Id查询子系统及对象
        :return:
        """
        res = SysSubsystemObject.query.filter(SysSubsystemObject.id == _id).one_or_none()
        return res

    @staticmethod
    def queryObjectByParentId(parent_id: str) -> [SysSubsystemObject]:
        """
        查询所有子系统对象列表
        :return:
        """
        res = SysSubsystemObject.query.filter(SysSubsystemObject.parent_id == parent_id).all()
        return res

    @staticmethod
    def querySubsystemByName(name: str, parent_id: str = None) -> SysSubsystemObject:
        """
        查询子系统根据名称
        :return:
        """
        res = SysSubsystemObject.query.filter(
            SysSubsystemObject.name == name, SysSubsystemObject.parent_id == parent_id
        ).one_or_none()
        return res

    @staticmethod
    def queryObjectByNameType(name: str, _type: int = None) -> SysSubsystemObject:
        """
        查询子系统根据名称
        :return:
        """
        res = SysSubsystemObject.query.filter(
            SysSubsystemObject.name == name, SysSubsystemObject.type == 2
        ).one_or_none()
        return res

    @staticmethod
    @clearcache
    def addSubsystemObject(subsystem_object: SysSubsystemObject):
        """
        添加子系统、对象
        :return:
        """
        if subsystem_object.type == 1:
            exist = SysSubsystemObjectDao.querySubsystemByName(subsystem_object.name)
            if exist:
                raise AppException("添加失败，该子系统名已被使用。")
        elif subsystem_object.type == 2:
            subsystem = SysSubsystemObjectDao.querySubObjectById(subsystem_object.parent_id)
            if not subsystem:
                raise AppException("添加失败，子系统不存在")
            exist = SysSubsystemObjectDao.querySubsystemByName(subsystem_object.name, subsystem_object.parent_id)
            if exist:
                raise AppException("添加失败，该系统下对象名已被使用。")

        db.session.add(subsystem_object)
        db.session.commit()

    @staticmethod
    @clearcache
    def updateSubsystemObject(_id, update_data: dict):
        """
        更新子系统
        :return:
        """
        exist = SysSubsystemObjectDao.querySubObjectById(_id)
        if not exist:
            raise AppException("编辑失败，ID不存在。")

        if 'name' in update_data.keys():
            if SysSubsystemObjectDao.querySubsystemByName(update_data.get('name'), exist.parent_id):
                raise AppException("更新失败，该名称已存在")

        SysSubsystemObject.query.filter(SysSubsystemObject.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    @clearcache
    def deleteSubsystemObject(_id: str):
        """
        删除子系统根据Id
        :return:
        """
        exist = SysSubsystemObjectDao.querySubObjectById(_id)
        if not exist:
            raise AppException("删除失败，ID不存在")

        if not exist.parent_id:
            objects = SysSubsystemObjectDao.queryObjectByParentId(_id)
            if objects:
                raise AppException("删除失败，请先删除绑定的对象")

        exist_field = SysFieldDao.queryFieldsByObjectId(_id)
        if exist_field:
            raise AppException("删除失败，请先删除绑定的字段")

        SysSubsystemObject.query.filter(SysSubsystemObject.id == _id).delete()
        db.session.commit()


class TblEmployeeDao:
    redis_key = 'models:techadmin:tbl_employee'

    @staticmethod
    @cacheable(f'{redis_key}:_id:$_id', TbEmployeeSchema)
    def queryEmployeeById(_id: str) -> TblEmployee:
        """
        :param _id: ID
        :return:
        """
        res = TblEmployee.query.filter(TblEmployee.id == _id).one_or_none()
        return res

    @staticmethod
    @cacheable(f'{redis_key}:user_id:$user_id', TbEmployeeSchema)
    def queryEmployeeByUserId(user_id: str) -> TblEmployee:
        """
        :param user_id: UserName ID
        :return:
        """
        res = TblEmployee.query.filter(TblEmployee.userid == user_id).one_or_none()
        return res

    @staticmethod
    @cacheable(f'{redis_key}:department:$department', TbEmployeeSchema, True)
    def queryEmployeeByMainDepartment(department: int) -> [TblEmployee]:
        """
        :param department:
        :return:
        """
        res = TblEmployee.query.filter(TblEmployee.main_department == department).all()
        return res

    @staticmethod
    @cacheable(f'{redis_key}:email:$email', TbEmployeeSchema)
    def queryEmployeeByEmail(email: str) -> TblEmployee:
        """
        :param email:
        :return:
        """
        res = TblEmployee.query.filter(TblEmployee.email == email).one_or_none()
        return res

    @staticmethod
    @cacheable(f'{redis_key}:leader:$leader', TbEmployeeSchema, True)
    def queryEmployeeByLeader(leader: str) -> [TblEmployee]:
        """
        :param leader:
        :return:
        """
        res = TblEmployee.query.filter(TblEmployee.leader == leader).all()
        return res

    @staticmethod
    def queryEmployeeByFilter(**kwargs) -> (int, [TblEmployee]):
        """
        :param kwargs: 查询参数
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000
        temp_query = TblEmployee.query.filter()

        for k, v in kwargs.items():
            if k not in TblEmployee.__dict__.keys() or not v:
                continue

            if isinstance(v, (bool, int)):
                temp_query = temp_query.filter(getattr(TblEmployee, k) == v)
            else:
                temp_query = temp_query.filter(getattr(TblEmployee, k).like(f"%{v}%"))

        res = temp_query.order_by(TblEmployee.name).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items

    @staticmethod
    def addEmployee(employee: TblEmployee):
        exist = TblEmployeeDao.queryEmployeeByUserId(employee.userid)
        if exist:
            commit = False
            for employee_key in employee.__dict__.keys():
                if employee_key.startswith('_') or employee_key == 'id':
                    continue
                if getattr(exist, employee_key) != getattr(employee, employee_key):
                    setattr(exist, employee_key, getattr(employee, employee_key))
                    commit = True
            if commit:
                exist.update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                db.session.commit()
                cache.clear()
            return

        exist = TblEmployeeDao.queryEmployeeById(employee.id)
        if exist:
            raise AppException("创建失败，员工ID已存在")

        employee.update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.session.add(employee)
        db.session.commit()

        return employee.id

    @staticmethod
    @clearcache
    def updateEmployeeByUserId(user_id, update_data: dict):
        exist = TblEmployeeDao.queryEmployeeByUserId(user_id)
        if not exist:
            return

        if 'update_time' not in update_data.keys():
            update_data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        TblEmployee.query.filter(TblEmployee.userid == user_id).update(update_data)
        db.session.commit()

    @staticmethod
    @clearcache
    def deleteEmployee(user_id: str):
        exist = TblEmployeeDao.queryEmployeeByUserId(user_id)
        if not exist:
            return

        TblEmployee.query.filter(TblEmployee.userid == user_id).delete()
        db.session.commit()

    @staticmethod
    def getEDByEmployeeId(employee_id) -> [(TblEmployee, TblDepartment)]:
        """
        :param employee_id: 企业用户ID
        :return:
        """
        employee_department = db.session.query(
            TblEmployee, TblDepartment).join(
            TblDepartment, TblDepartment.id == TblEmployee.main_department).filter(
            TblEmployee.id == employee_id).first()

        return employee_department

    @staticmethod
    def queryEDByEmployeeIds(employee_ids) -> (TblEmployee, TblDepartment):
        """
        :param employee_ids: 企业用户ID
        :return:
        """
        employee_department = db.session.query(
            TblEmployee, TblDepartment).join(
            TblDepartment, TblDepartment.id == TblEmployee.main_department).filter(
            TblEmployee.id.in_(employee_ids)).all()

        return employee_department

    @staticmethod
    def getEDByDepartmentId(department_id) -> [(TblEmployee, TblDepartment)]:
        """
        :param department_id: 企业部门ID
        :return:
        """
        employee_department_list = db.session.query(
            TblEmployee, TblDepartment).join(
            TblDepartment, TblDepartment.id == TblEmployee.main_department).filter(
            TblEmployee.main_department == department_id).all()

        return employee_department_list

    @staticmethod
    def getEDUByDepartmentId(department_id) -> [(TblEmployee, TblDepartment, SysUser)]:
        """
        :param department_id: 企业部门ID
        :return:
        """
        employee_department_list = db.session.query(
            TblEmployee, TblDepartment, SysUser).join(
            TblDepartment, TblDepartment.id == TblEmployee.main_department).join(
            SysUser, SysUser.employee_id == TblEmployee.id
        ).filter(
            TblEmployee.main_department == department_id
        ).all()

        return employee_department_list

    @staticmethod
    def getESByEmployeeId(userid) -> [(TblEmployee, SysUser)]:
        """
        :param userid:
        :return:
        """
        res = db.session.query(
            TblEmployee, SysUser).join(
            SysUser, SysUser.employee_id == TblEmployee.id).filter(
            TblEmployee.userid == userid).one_or_none()

        return res

    @staticmethod
    def getEmployeeJoinDepartmentDByEmail(email: str) -> (TblEmployee, TblDepartment):
        """
        :param email: 查询邮箱
        :return:
        """
        res = db.session.query(
            TblEmployee, TblDepartment).join(
            TblDepartment, TblEmployee.main_department == TblDepartment.id).filter(
            TblEmployee.email == email,
            TblEmployee.is_deleted is not True
        ).one_or_none()

        return res

    @staticmethod
    def getEDByFilter(**kwargs) -> (int, [(TblEmployee, TblDepartment)]):
        """
        :param kwargs: 查询参数
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000
        temp_query = db.session.query(
            TblEmployee, TblDepartment).join(
            TblDepartment, TblEmployee.main_department == TblDepartment.id).filter(
            TblEmployee.is_deleted is not True
        )

        for k, v in kwargs.items():
            obj = None
            if '.' in k:
                obj_name, k = k.split('.')[0], k.split('.')[1]
                if obj_name == 'E':
                    obj = TblEmployee
                elif obj_name == 'D':
                    obj = TblDepartment

            if not obj:
                if k in TblEmployee.__dict__.keys():
                    obj = TblEmployee
                elif k in TblDepartment.__dict__.keys():
                    obj = TblDepartment

            if obj:
                if isinstance(v, (bool, int)):
                    temp_query = temp_query.filter(getattr(obj, k) == v)
                else:
                    temp_query = temp_query.filter(getattr(obj, k).like(f"%{v}%"))

        res = temp_query.order_by(TblEmployee.name).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items

    @staticmethod
    def getEDUByFilter(**kwargs) -> (int, [(TblEmployee, TblDepartment, SysUser)]):
        """
        :param kwargs: 查询参数
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000
        temp_query = db.session.query(
            TblEmployee, TblDepartment, SysUser).join(
            TblDepartment, TblEmployee.main_department == TblDepartment.id).join(
            SysUser, SysUser.employee_id == TblEmployee.id).filter(
            TblEmployee.is_deleted is not True
        )

        for k, v in kwargs.items():
            obj = None
            if '.' in k:
                obj_name, k = k.split('.')[0], k.split('.')[1]
                if obj_name == 'E':
                    obj = TblEmployee
                elif obj_name == 'D':
                    obj = TblDepartment

            if not obj:
                if k in TblEmployee.__dict__.keys():
                    obj = TblEmployee
                elif k in TblDepartment.__dict__.keys():
                    obj = TblDepartment

            if obj:
                if isinstance(v, (bool, int)):
                    temp_query = temp_query.filter(getattr(obj, k) == v)
                else:
                    temp_query = temp_query.filter(getattr(obj, k).like(f"%{v}%"))

        res = temp_query.order_by(TblEmployee.id).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items


class TblDepartmentDao:
    redis_key = 'models:techadmin:tbl_department'

    @staticmethod
    def queryAllHigherDepartment(user_id: str) -> list:
        try:
            department_ids = []
            query = db.session.query(SysUser, TblEmployee)
            query = query.outerjoin(TblEmployee, SysUser.employee_id == TblEmployee.id)
            query = query.filter(SysUser.id == user_id) 
            for user, employee in query.all():
                if employee is not None:
                    main_department = employee.main_department
                    while main_department != 1:
                        department = db.session.query(TblDepartment).filter(TblDepartment.id == main_department).first()
                        if department is None:
                            break
                        department_ids.append(department.name)
                        main_department = department.parentid
        except:
            department_ids = []
        return department_ids
    
    @staticmethod
    def queryDepartment() -> [TblDepartment]:
        """
        :return:
        """
        res = TblDepartment.query.all()
        return res

    @staticmethod
    def queryDepartmentById(_id: str) -> TblDepartment:
        """
        :param _id: ID
        :return:
        """
        res = TblDepartment.query.filter(TblDepartment.id == _id).one_or_none()
        return res

    @staticmethod
    def queryDepartmentByIds(ids: list) -> [TblDepartment]:
        """
        :param ids: ID
        :return:
        """
        res = TblDepartment.query.filter(TblDepartment.id.in_(ids)).all()
        return res


    @staticmethod
    def queryDepartmentByName(name: str) -> TblDepartment:
        """
        :param name: UserName ID
        :return:
        """
        res = TblDepartment.query.filter(TblDepartment.name == name).one_or_none()
        return res

    @staticmethod
    def queryDepartmentByFilter(**kwargs) -> (int, [TblDepartment]):
        """
        :param kwargs: 查询参数
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000
        temp_query = TblDepartment.query.filter()

        for k, v in kwargs.items():
            if k not in TblDepartment.__dict__.keys() or not v:
                continue

            if isinstance(v, (bool, int)):
                temp_query = temp_query.filter(getattr(TblDepartment, k) == v)
            else:
                temp_query = temp_query.filter(getattr(TblDepartment, k).like(f"%{v}%"))

        res = temp_query.order_by(TblDepartment.name).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items

    @staticmethod
    def updateDepartmentById(_id, update_data: dict):
        exist = TblDepartmentDao.queryDepartmentById(_id)
        if not exist:
            return

        if 'update_time' not in update_data.keys():
            update_data['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        TblDepartment.query.filter(TblDepartment.id == _id).update(update_data)
        db.session.commit()

    @staticmethod
    def addDepartment(department: TblDepartment):
        exist = TblDepartmentDao.queryDepartmentById(department.id)
        if exist:
            commit = False
            for department_key in department.__dict__.keys():
                if department_key.startswith('_') or department_key == 'id':
                    continue
                if getattr(exist, department_key) != getattr(department, department_key):
                    setattr(exist, department_key, getattr(department, department_key))
                    commit = True
            if commit:
                exist.update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                db.session.commit()
            return

        department.update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.session.add(department)
        db.session.commit()

    @staticmethod
    def deleteDepartment(department_id: str):
        exist = TblDepartmentDao.queryDepartmentById(department_id)
        if not exist:
            return

        TblDepartment.query.filter(TblDepartment.id == department_id).delete()
        db.session.commit()

    @staticmethod
    def queryParentDepartmentById(_id) -> [TblDepartment]:
        departments = []
        department = TblDepartmentDao.queryDepartmentById(_id)
        if department.parentid:
            departments.append(department)
            departments += TblDepartmentDao.queryParentDepartmentById(department.parentid)
            return departments

        return [department]


class SysFieldPermissionDao:
    redis_key = 'models:techadmin:sys_field_permisssion'

    @staticmethod
    def queryFieldPermissionById(_id: str) -> SysFieldPermission:
        """
        :return:
        """
        res = SysFieldPermission.query.filter(SysFieldPermission.id == _id).one_or_none()
        return res

    @staticmethod
    def queryFieldPermissionByFieldId(field_id: str) -> SysFieldPermission:
        """
        :return:
        """
        res = SysFieldPermission.query.filter(SysFieldPermission.field_id == field_id).one_or_none()
        return res

    @staticmethod
    def queryFieldPermissionByRoleMenuId(role_menu_id: str) -> [SysFieldPermission]:
        """
        :return:
        """
        res = SysFieldPermission.query.filter(SysFieldPermission.role_menu_id == role_menu_id).all()
        return res

    @staticmethod
    def addFieldPermission(field_permission: SysFieldPermission):
        exist = SysFieldPermission.query.filter(
            SysFieldPermission.role_menu_id == field_permission.role_menu_id,
            SysFieldPermission.field_id == field_permission.field_id
        ).one_or_none()
        if exist:
            raise AppException("绑定失败，该字段权限已绑定")

        db.session.add(field_permission)
        db.session.commit()
        return field_permission.id

    @staticmethod
    def deleteFieldPermission(_id: str):
        exist = SysFieldPermissionDao.queryFieldPermissionById(_id)
        if not exist:
            return

        SysFieldPermission.query.filter(SysFieldPermission.id == _id).delete()
        db.session.commit()

    @staticmethod
    def deleteFieldPermissionByRoleMenuId(role_menu_id: str):
        SysFieldPermission.query.filter(SysFieldPermission.role_menu_id == role_menu_id).delete()
        db.session.commit()

    @staticmethod
    def getFieldNameByRoleMenuId(role_menu_id):
        fields = {"allow": [], "deny": []}
        field_permission_list = SysFieldPermissionDao.queryFieldPermissionByRoleMenuId(role_menu_id)
        for field_permission in field_permission_list:
            field = SysFieldDao.queryFieldById(field_permission.field_id)
            if field_permission.effect == 'allow':
                fields["allow"].append(field.name)
            elif field_permission.effect == 'deny':
                fields["deny"].append(field.name)

        return fields

    @staticmethod
    def getAllowFieldByRolePermission(roles: [list], permission_mark):
        allow_field_list, deny_field_list, only_field = [], [], []

        menus = SysMenuDao.querySysMenuByPermission(permission_mark)
        for menu in menus:
            if menu.field_object:
                field_all = SysFieldDao.queryFieldsByObjectId(menu.field_object)
                field_all = [field.name for field in field_all]

                role_menu_list = SysRoleMenuDao.getRoleMenuByRolePermission(roles, permission_mark)
                for role_menu in role_menu_list:
                    if role_menu:
                        fields = SysFieldPermissionDao.getFieldNameByRoleMenuId(role_menu.id)
                        allow_field_list = allow_field_list + fields['allow']
                        deny_field_list = deny_field_list + fields['deny']

                allow_field_list = list(set(allow_field_list))
                deny_field_list = list(set(deny_field_list))
                if deny_field_list:
                    only_field = [field for field in field_all if field not in deny_field_list]
                    for deny_field in deny_field_list:
                        if deny_field in allow_field_list:
                            allow_field_list.remove(deny_field)

                only_field = list(set(only_field + allow_field_list))

        return only_field


class SysAttachmentDao:

    @staticmethod
    def queryAttachmentById(_id: str) -> SysAttachment:
        """
        :return:
        """
        res = SysAttachment.query.filter(SysAttachment.id == _id).one_or_none()
        return res

    @staticmethod
    def queryAttachmentByObjectId(related_object: str, related_object_id: str) -> [SysAttachment]:
        """
        :return:
        """
        res = SysAttachment.query.filter(
            SysAttachment.related_object == related_object,
            SysAttachment.related_object_id == related_object_id
        ).all()
        return res

    @staticmethod
    def queryAttachmentJoinUserByObjectId(related_object: str, related_object_id: str) -> [SysAttachment, SysUser]:
        """
        :return:
        """
        res = db.session.query(SysAttachment, SysUser).join(
            SysUser, SysAttachment.created_by_id == SysUser.id).filter(
            SysAttachment.related_object == related_object,
            SysAttachment.related_object_id == related_object_id
        ).all()
        return res

    @staticmethod
    def addAttachment(attachment: SysAttachment):
        now_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        attachment.created_date = now_date

        db.session.add(attachment)
        db.session.commit()
        return attachment.id

    @staticmethod
    def updateAttachmentById(_id, update_data: dict):
        exist = SysAttachmentDao.queryAttachmentById(_id)
        if not exist:
            return

        SysAttachment.query.filter(SysAttachment.id == _id).update(update_data)
        db.session.commit()


class SysUserRedisDao:
    
    def querySysUserInfo(user_id: str) -> dict:
        try:
            key = f"techadmin:internal:user:info:{user_id}"
            if redis_client.exists(key):
                value = redis_client.get(name=key)
                return json.loads(value)
        except:
            return None
        
    def setSysUserInfo(user_id: str, data: dict) -> bool:
        key = f"techadmin:internal:user:info:{user_id}"
        redis_client.set(name=key, value=json.dumps(data))
        return True


class OperateHistoryDao:

    @staticmethod
    def queryOperateHistory(target, target_id) -> [OperateHistory]:
        """
        :return:
        """
        res = OperateHistory.query.filter(
            OperateHistory.target == target, OperateHistory.target_id == target_id
        ).all()
        return res

    @staticmethod
    def addOperateHistory(operate_history: OperateHistory):
        db.session.add(operate_history)
        db.session.commit()
        return

    @staticmethod
    def getOperateHistoryJoinUser(target, target_id, **kwargs) -> [(OperateHistory, SysUser)]:
        """
        :return:
        """
        page = int(kwargs.get('page')) if kwargs.get('page') else 1
        size = int(kwargs.get('size')) if kwargs.get('size') else 1000

        temp_query = db.session.query(OperateHistory, SysUser).join(
            SysUser, OperateHistory.created_by_id == SysUser.id).filter(
            OperateHistory.target == target, OperateHistory.target_id == target_id
        )

        res = temp_query.order_by(OperateHistory.created_date.desc()).paginate(page=page, per_page=size, error_out=False)
        return res.total, res.items
