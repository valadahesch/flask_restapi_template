from __future__ import annotations

from app.models import db
from app.enums.sys_enum import enums
from app.utils.func_util import cacheable
from app.controllers.dao import SysUserDao, TblEmployeeDao
from app.controllers.schema import SysUserSchema
from app.models.techadmin import SysUser, TblEmployee, SysMenu, SysRoleUser, SysRoleMenu


class DataScopeDao:
    redis_key = 'models:datascope'

    @staticmethod
    def getDirectlyReportingById(user_id: str, department_ids: list = None) -> [(SysUser, TblEmployee)]:
        """
        获取直属下级
        :return:
        """
        sysuser_employee_list = []

        sysuser = SysUserDao.querySysUserById(user_id)
        if sysuser:
            temp = db.session.query(SysUser, TblEmployee).join(
                TblEmployee, SysUser.employee_id == TblEmployee.id
            ).filter(SysUser.manage_id == sysuser.employee_id)
            if department_ids:
                temp.filter(TblEmployee.department.in_(department_ids))
            sysuser_employee_list = temp.all()

        return sysuser_employee_list

    @staticmethod
    @cacheable(f'{redis_key}:getSubordinateIdById:user_id:$user_id', SysUserSchema, True)
    def getSubordinateIdById(user_id: str) -> [SysUser]:
        """
        获取所有下属的Id
        :return:
        """
        visited = set()
        sysuser_list = []

        def dfs(user_id):
            if user_id in visited:
                return

            visited.add(user_id)
            subordinate_list = SysUserDao.querySysUserByManageId(user_id)
            for sys_user in subordinate_list:
                if sys_user in sysuser_list:
                    continue
                sysuser_list.append(sys_user)
                dfs(sys_user.id)

        dfs(user_id)
        return sysuser_list

    @staticmethod
    @cacheable(f'{redis_key}:getEmployeeSubordinateIdById:user_id:$user_id', SysUserSchema, True)
    def getEmployeeSubordinateIdById(user_id: str) -> [SysUser]:
        """
        获取企业员工所有下属的Id
        :return:
        """
        visited = set()
        employee_list = []
        subordinate_sysuser_list = []
        sysuser_employee = SysUserDao.getSysUserEmployeeById(user_id)
        if not sysuser_employee:
            return subordinate_sysuser_list

        def dfs(employee_userid):
            if employee_userid in visited:
                return
            visited.add(employee_userid)

            subordinate_employee_list = TblEmployeeDao.queryEmployeeByLeader(employee_userid)
            for subordinate_employee in subordinate_employee_list:
                if subordinate_employee in employee_list:
                    continue
                employee_list.append(subordinate_employee)
                dfs(subordinate_employee.userid)

        dfs(sysuser_employee[1].userid)
        employee_ids = [employee.id for employee in employee_list]
        subordinate_sysuser_list = SysUserDao.querySysUserByEmployeeIds(employee_ids)
        return subordinate_sysuser_list

    @staticmethod
    @cacheable(f'{redis_key}:getDirectlySuperiorByUserId:user_id:$user_id', SysUserSchema)
    def getDirectlySuperiorByUserId(user_id: str) -> SysUser | None:
        """
        获取站点所有系统用户上级
        :return:
        """
        superiors_sysuser = None
        sys_user = SysUserDao.querySysUserById(user_id)
        if not sys_user:
            return superiors_sysuser

        if sys_user.manage_id:
            superiors_sysuser = SysUserDao.querySysUserById(sys_user.manage_id)
        return superiors_sysuser

    @staticmethod
    @cacheable(f'{redis_key}:getDirectlyEmployeeSuperiorByUserId:user_id:$user_id', SysUserSchema)
    def getDirectlyEmployeeSuperiorByUserId(user_id: str) -> SysUser | None:
        """
        获取企业所有系统用户上级
        :return:
        """
        superiors_sysuser = None
        sysuser_employee = SysUserDao.getSysUserEmployeeById(user_id)
        if not sysuser_employee:
            return superiors_sysuser

        sys_user, employee = sysuser_employee
        if employee.leader:
            superiors_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
            if superiors_employee:
                superiors_sysuser = SysUserDao.querySysUserByEmployeeId(superiors_employee.id)

        return superiors_sysuser


    @staticmethod
    @cacheable(f'{redis_key}:getSuperiorsByUserId:user_id:$user_id', SysUserSchema, True)
    def getSuperiorsByUserId(user_id: str) -> [SysUser]:
        """
        获取站点所有系统用户上级
        :return:
        """
        visited = set()
        superiors_sysuser_list = []
        sys_user = SysUserDao.querySysUserById(user_id)
        if not sys_user:
            return superiors_sysuser_list

        def dfs(sys_user):
            if sys_user.id in visited:
                return
            visited.add(sys_user.id)

            if sys_user.manage_id and sys_user.manage_id not in visited:
                superiors_sys_user = SysUserDao.querySysUserById(sys_user.manage_id)
                if superiors_sys_user:
                    superiors_sysuser_list.append(superiors_sys_user)
                    dfs(superiors_sys_user)

        dfs(sys_user)
        return superiors_sysuser_list

    @staticmethod
    @cacheable(f'{redis_key}:getEmployeeSuperiorsByUserId:user_id:$user_id', SysUserSchema, True)
    def getEmployeeSuperiorsByUserId(user_id: str) -> [SysUser]:
        """
        获取企业所有系统用户上级
        :return:
        """
        visited = set()
        superiors_employee_list = []
        superiors_sysuser_list = []
        sysuser_employee = SysUserDao.getSysUserEmployeeById(user_id)
        if not sysuser_employee:
            return superiors_sysuser_list

        def dfs(employee):
            employee_userid = employee.userid
            if employee_userid in visited:
                return
            visited.add(employee_userid)

            if employee.leader and employee.leader not in visited:
                superiors_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                if superiors_employee:
                    superiors_employee_list.append(superiors_employee)
                    dfs(superiors_employee)

        dfs(sysuser_employee[1])
        employee_ids = [employee.id for employee in superiors_employee_list]
        superiors_sysuser_list = SysUserDao.querySysUserByEmployeeIds(employee_ids)

        return superiors_sysuser_list

    @staticmethod
    def getSuperiorsIdById(user_id: str) -> [(SysUser, TblEmployee)]:
        """
        获取所有直属上级的Id
        :return:
        """
        visited = set()
        sysuser_employee_list = []
        sys_user = SysUserDao.querySysUserById(user_id)
        if not sys_user:
            return sysuser_employee_list

        def dfs(sys_user):
            if sys_user.id in visited:
                return
            visited.add(sys_user.id)
            if sys_user.manage_id and sys_user.manage_id not in visited:
                superiors = db.session.query(SysUser, TblEmployee).join(
                    TblEmployee, SysUser.employee_id == TblEmployee.id
                ).filter(SysUser.id == sys_user.manage_id).one_or_none()
                if superiors:
                    sysuser_employee_list.append(superiors)
                    dfs(superiors[0])


        dfs(sys_user)

        return sysuser_employee_list

    @staticmethod
    def _getAllEmployee() -> [(SysUser, TblEmployee)]:
        """
        获取所有企业用户
        :return:
        """
        sysuser_employee_list = db.session.query(SysUser, TblEmployee).join(
            TblEmployee, SysUser.employee_id == TblEmployee.id).all()
        return sysuser_employee_list

    @staticmethod
    @cacheable(f'{redis_key}:getAllSuperiorByUserId:user_id:$user_id', 'json')
    def getAllSuperiorByUserId(user_id: str) -> [str]:
        superiors_ids = []
        sys_superior = DataScopeDao.getDirectlySuperiorByUserId(user_id)
        if sys_superior:
            superiors_ids.append(sys_superior.id)

        employee_superior = DataScopeDao.getDirectlyEmployeeSuperiorByUserId(user_id)
        if employee_superior:
            superiors_ids.append(employee_superior.id)
        return list(set(superiors_ids))

    @staticmethod
    @cacheable(f'{redis_key}:getAllSuperiorsByUserId:user_id:$user_id', 'json')
    def getAllSuperiorsByUserId(user_id: str) -> [str]:
        superiors_ids = []
        sys_superior_list = DataScopeDao.getSuperiorsByUserId(user_id)
        if sys_superior_list:
            superiors_ids.extend([sys_superior.id for sys_superior in sys_superior_list])

        employee_superior_list = DataScopeDao.getEmployeeSuperiorsByUserId(user_id)
        if employee_superior_list:
            superiors_ids.extend([employee_superior.id for employee_superior in employee_superior_list])
        return list(set(superiors_ids))

    @staticmethod
    @cacheable(f'{redis_key}:getSysUserByRank:user_id:$user_id:permission_mark:$permission_mark', 'json')
    def getSysUserByRank(user_id: str, permission_mark: str) -> [str]:
        """
        根据职级获取系统用户
        :return:
        """
        role_users = SysRoleUser.query.filter(SysRoleUser.user_id == user_id).all()
        role_ids = [role_user.role_id for role_user in role_users]

        role_menu_list = db.session.query(SysRoleMenu).join(
            SysMenu, SysRoleMenu.menu_id == SysMenu.id).filter(
            SysMenu.permission == permission_mark, SysRoleMenu.role_id.in_(role_ids)
        ).all()
        data_scope_list = list(set([role_menu.data_scope for role_menu in role_menu_list if role_menu.data_scope]))

        data_scope = None
        if 1 in data_scope_list:
            data_scope = enums["sys_manage"]["data_scope"][1]
        elif 4 in data_scope_list:
            data_scope = enums["sys_manage"]["data_scope"][4]
        elif 2 in data_scope_list and 3 in data_scope_list:
            data_scope = enums["sys_manage"]["data_scope"][4]
        elif 2 in data_scope_list:
            data_scope = enums["sys_manage"]["data_scope"][2]
        elif 3 in data_scope_list:
            data_scope = enums["sys_manage"]["data_scope"][3]

        if data_scope == "全部":
            return ['*']
        elif data_scope == "下级":
            res1 = DataScopeDao.getSubordinateIdById(user_id)
            res2 = DataScopeDao.getEmployeeSubordinateIdById(user_id)
            user_ids = [sys_user.id for sys_user in res1 + res2]
            return list(set(user_ids))
        elif data_scope == "本级及下级":
            res1 = [SysUserDao.querySysUserById(user_id)]
            res2 = DataScopeDao.getSubordinateIdById(user_id)
            res3 = DataScopeDao.getEmployeeSubordinateIdById(user_id)
            user_ids = [sys_user.id for sys_user in res1 + res2 + res3]
            return list(set(user_ids))

        return []
