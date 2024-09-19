import json
import time
import unittest
import os

from app import create_app
from app.models import db
from app.controllers import *
from app.controllers.dao import *
from app.controllers.schema import *
from app.controllers.response import *


class TestTechAdmin(unittest.TestCase):
    app = None
    app_context = None

    def dev_print(self, *args):
        if self.env == 'dev':
            print(*args)

    @classmethod
    def setUpClass(cls):
        if cls.app:
            return

        env = os.environ.get('APP_ENV', 'dev')
        cls.app = create_app('app.config.%sConfig' % env.capitalize())
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def setUp(self):
        self.env = os.environ.get('APP_ENV', 'dev')

    def tearDown(self):
        db.session.remove()

    def test_sys_role_user(self):
        roles = SysRoleUserDao.querySysRolesByUserId('2cc1bfee-b67e-402f-9ac2-ae885703d75d')
        self.dev_print(json.dumps([role_user.role_id for role_user in roles]))

    def test_sys_role_menu(self):
        menus = SysRoleMenuDao.querySysRoleMenuByRoleId('1c5y1ki4a82z89p')
        self.dev_print(menus)
        self.assertTrue(True if len(menus) > 0 else False)

    def test_sys_role_user_2(self):
        total, data = SysRoleUserDao.queryRUEDByRoleIdFilter("1c5y1ki4a82z89p")
        self.dev_print(total, data)

    def test_sys_user(self):
        users = SysUserDao.querySysUser()
        self.assertTrue(True if len(users) > 0 else False)
        users = SysUserDao.querySysUserByManageId('bvt7lbrd3m9m90t')

    def test_sys_subsystem_object(self):
        res = SysSubsystemObjectDao.querySubsystem()
        self.dev_print(res)
        self.assertTrue(True if len(res) > 0 else False)

        data = {"name": "System", "description": "系统管理"}
        keys = data.keys()
        schema = SysSubsystemObjectSchema(only=keys, partial=True)
        data_obj = schema.load(data)
        self.dev_print(data_obj)

    @unittest.skip("跳过测试")
    def test_sys_user_marshal(self):
        users = SysUserDao.querySysUser()
        from app.controllers.schema import SysUserSchema
        user_schema = SysUserSchema()
        for user in users:
            user_dict = user_schema.dumps(user)
            self.dev_print(user_dict)

    def test_menu_ids(self):
        menu_ids = SysRoleMenuDao.getAllowMenuByRolesId(['rgbqu8gxays7g8e'])
        self.dev_print(menu_ids)

    def test_generate_rbac(self):
        role_user_list = SysRoleUserDao.queryRoleUser()
        # for role_user in role_user_list:
        #     print("g, {}, {}".format(role_user.user_id, role_user.role_id))

        role_menu_list = SysRoleMenuDao.queryRoleMenu()
        for role_menu in role_menu_list:
            menu = SysMenuDao.querySysMenuById(role_menu.menu_id)
            # if menu.permission:
            #     print("p, {}, {}, {}".format(role_menu.role_id, menu.permission, role_menu.effect))

    def test_response_module(self):
        from app.controllers import response
        for k in dir(response):
            if not k.endswith('Response'):
                continue

            resp_class = getattr(response, k)
            self.dev_print(resp_class.__subsystem__, resp_class.__object__, resp_class.attributes())

    # @unittest.skip("跳过测试")
    def test_sysuser_add(self):
        sso_user = {
            'UserID': '2cc1bfee-b67e-402f-9ac2-ae885703d75d', 'UserName': 'zcding@Hillstonenet.com',
            'DisplayName': 'Zhicheng Ding(丁智成)', 'FirstName': 'Zhicheng', 'LastName': 'Ding',
            'NickName': 'zcding', 'Birthday': None, 'UserType': 0, 'CompanyName': '山石网科通信技术股份有限公司',
            'Mobile': '18855055162', 'Email': 'zcding@Hillstonenet.com', 'TimeDiff': 480, 'OEMBrand': '',
            'Language': 'zh-cn'
        }
        sso_user = SSOUser(**sso_user).to_dict()

        only = [
            'id', 'user_id', 'user_name', 'dp_name', 'first_name', 'last_name', 'nick_name',
            'birthday', 'user_type', 'company_name', 'mobile', 'email', 'time_diff', 'oem_brand', 'language'
        ]
        user_schema = SysUserSchema(only=only)
        sys_user = user_schema.load(sso_user)
        user_id = SysUserDao.addSysUserBySSO(sys_user)

        if sys_user.user_type == 0 and '@Hillstonenet.com' in sys_user.email:
            username_id = sys_user.email.replace('@Hillstonenet.com', '')
            employee = TblEmployeeDao.queryEmployeeByUserId(username_id)
            if employee:
                update = {"employee_id": employee.id}
                SysUserDao.updateSysUserById(user_id, update)

        user = SysUserDao.querySysUserByUserId(sso_user['user_id'])
        user_schema = SysUserSchema(only=['id', 'user_id', 'user_name'], exclude=['id'])
        user_dict = user_schema.dump(user)
        self.dev_print(user_dict)

    def test_update_sysuser_attr(self):
        extattr = [{"type": 0, "name": "文本名称", "text": {"value": "文本"}}]
        extattr = json.dumps(extattr, ensure_ascii=False)
        updatedata = {"extattr": extattr}
        SysUserDao.updateSysUserById('bvt7lbrd3m9m90t', updatedata)

    @unittest.skip("跳过测试")
    def test_sys_user_leader(self):
        user_id = 'bvt7lbrd3m9m90t'
        directly_leader_list = SysUserDao.getDirectlyLeaderByUserId(user_id)
        for directly_leader in directly_leader_list:
            print(directly_leader.email)

    @unittest.skip("跳过测试")
    def test_role_user_add(self):
        user_id = '1'
        role = SysRoleDao.querySysRoleByType(1)
        role_user = {"role_id": role.id, "user_id": user_id}
        schema = SysRoleUserSchema()
        role_user = schema.load(role_user)
        SysRoleUserDao.addRoleUser(role_user)

    @unittest.skip("跳过测试")
    def test_odsuser_to_localuser(self):
        wecom_users = TacOdsWeComUserDao.queryWecomUser()
        wecom_schema = OdsWecomUserSchema()
        wecom_users = wecom_schema.dump(wecom_users, many=True)
        for wecom_user in wecom_users:
            if wecom_user['is_deleted'] == 1:
                TblEmployeeDao.deleteEmployee(wecom_user['userid'])
            else:
                tbl_wecom_schema = TbEmployeeSchema()
                tbl_wecom = tbl_wecom_schema.load(wecom_user, unknown="exclude")
                TblEmployeeDao.addEmployee(tbl_wecom)

    @unittest.skip("跳过测试")
    def test_odsdepart_to_localdepartment(self):
        wecom_departs = TacOdsWeComDepartmentDao.queryWecomDepartment()
        wecom_schema = OdsWecomDepartmentSchema()
        wecom_departs = wecom_schema.dump(wecom_departs, many=True)
        for wecom_depart in wecom_departs:
            if wecom_depart['is_deleted'] == 1:
                TblDepartmentDao.deleteDepartment(wecom_depart['id'])
            else:
                tbl_wecom_schema = TblDepartmentSchema()
                tbl_wecom = tbl_wecom_schema.load(wecom_depart, unknown="exclude")
                TblDepartmentDao.addDepartment(tbl_wecom)

    def test_sysuser(self):
        user_id = '2cc1bfee-b67e-402f-9ac2-ae885703d75'
        user = SysUserDao.querySysUserById(user_id)
        self.dev_print(user)

        params = {
            "user_type": 0
        }
        user = SysUserDao.querySysUserByFilter(**params)
        self.dev_print(user)

    def test_sysmenus(self):
        menus = SysMenuDao.querySysMenuByType()
        self.dev_print(menus)
        schema = SysMenuSchema()
        menus = schema.dumps(menus, many=True)

    def test_sysmenu_parent(self):
        menus = SysMenuDao.queryParentMenusById('85tau9sxinl95st')
        self.dev_print(menus)

    def test_tbldepartment_parent(self):
        department = TblDepartmentDao.queryParentDepartmentById('840')
        self.dev_print(department)

    @unittest.skip("跳过测试")
    def test_field_permission(self):
        roles = ['1c5y1ki4a82z89p', 'rgbqu8gxays7g8e']
        allow_field_list, deny_field_list, only_field = [], [], []

        menus = SysMenuDao.querySysMenuByPermission('user:list')
        for menu in menus:
            if menu.field_object:
                field_all = SysFieldDao.queryFieldsByObjectId(menu.field_object)
                field_all = [field.name for field in field_all]

                role_menu_list = SysRoleMenuDao.getRoleMenuByRolePermission(roles, 'user:list')
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

        self.dev_print(only_field)

    def test_crm_view(self):
        lead = CrmViewsDao.queryLeadListByLeadId('793FA39D-D6DC-43B7-9B11-00318C4E3D2C')
        self.dev_print(lead)

        account = CrmViewsDao.queryAccountByName('酒泉市融媒体中心')

    def test_lead(self):
        lead = BusinessLeadDao.queryBusinessLeadById('6s5bag7dgjfr20y')
        self.dev_print(lead)

    def test_employee(self):
        emp = TblEmployeeDao.queryEmployeeByEmail('zcding@hillstonenet.com')
        self.dev_print(emp)
        total, employee_department_user = TblEmployeeDao.getEDUByFilter(**{"E.name": "冯桔林"})
        self.dev_print(employee_department_user)

    def test_query_subordinate(self):
        sysuser_list = DataScopeDao.getSubordinateIdById('72967kgqj7v1yez')
        for sysuser in sysuser_list:
            self.dev_print(sysuser.display_name)

    def test_data_scope(self):
        user_ids = DataScopeDao.getSysUserByRank('4tsvjifzn0mbjqc', 'sework.internal:all')
        self.dev_print(user_ids)

    def test_role_menu_permission(self):
        res = SysRoleMenuDao.getRoleJoinMenuByRoleId('1c5y1ki4a82z89p', 'employee:list')
        self.dev_print(res)

    def test_role_join_menu(self):
        res = SysRoleMenuDao.getRoleJoinMenuById('1ro9ygj9g0e3ycl')
        self.dev_print(res)

    def test_sework_es(self):
        params = {
            # "query": "任务",
            # "date_range": ["2023-08-01 07:56:32'", "2023-08-01 07:56:32"],
            "date_order": "desc",
            # "owner_id": ["bvt7lbrd3m9m90t", "ukrwkiyh9ntv5aj"],
            # "created_by_id": ["19mp0r4ex8h0fzb"],
            # "participants": ["bvt7lbrd3m9m90t"],
            # "status": [1],
            "page": 1,
            "size": 100
        }
        total, res = ESService.querySeWorkByFilter(['4tsvjifzn0mbjqc'], **params)
        self.dev_print(total, res)


    def test_employee_by_email(self):
        assign_employee = TblEmployeeDao.getEmployeeJoinDepartmentDByEmail("zcding@hillstonenet.com")
        self.dev_print(assign_employee)

    def test_sework_project_filter(self):
        params = {
            "owner_id": ["bvt7lbrd3m9m90t"]
            # "created_by_id": ["bvt7lbrd3m9m90t", "72967kgqj7v1yez"],
            # "date_range": ["2023-08-07 15:22:37", "2023-08-08 14:28:10"],
            # "status": [3]
        }
        total, project_co_list = SeWorkProjectDao.getProjectByOwnerAndFilter("bvt7lbrd3m9m90t", **params)
        self.dev_print(total)
        for project_co in project_co_list:
            project = project_co[0]
            self.dev_print(project.project_number)

    def test_employee_user_by_name(self):
        sysuser_ed_list = SysUserDao.getSysUserEDByEmployeeName('孙')
        for sysuser_employee_department in sysuser_ed_list:
            sysuser, employee, department = sysuser_employee_department
            self.dev_print(sysuser.id)
            self.dev_print(employee.name)
            self.dev_print(department.name)

    def test_undone_task(self):
        undone_task_list = []
        task_list = SeWorkTaskDao.queryDoTaskByProjectId('mikn0m17f9e4x6q')
        for task in task_list:
            if task.status == 1 and not task.parent_id:
                undone_task_list.append(task)

        self.dev_print(undone_task_list)

    def test_eco_task(self):
        user_ids = ["bvt7lbrd3m9m90t"]
        partner_id = "45"
        task_list = SeEcoTaskDao.getTasksJoinSysUserByIds(user_ids, partner_id)
        self.dev_print(task_list)

    def test_eco_partner(self):
        params = {"partner_name": "测试"}
        now = time.time()
        total, partner_ids = SeEcoTaskDao.queryTaskPartnerByUserId(['bvt7lbrd3m9m90t'], **params)

    def test_eco_approval(self):
        res = SeEcoApprovalDao.getApprovalRecordByUserId('bvt7lbrd3m9m90t')
        self.dev_print(res)

    def test_seeco_es(self):
        params = {
            # "query": "测试-4",
            "partner_id": "0012v00002VPbUUAA1",
            # "date_range": ["2023-09-11 07:56:32", "2023-09-15 07:56:32"],
            "date_order": "desc",
            # "owner_id": ["19mp0r4ex8h0fzb"],
            # "created_by_id": ["bvt7lbrd3m9m90t"],
            # "participants": ["bvt7lbrd3m9m90t"],
            # "status": [1],
            "page": 1,
            "size": 100
        }
        total, res = ESService.querySeEcoPartnerByFilter(['bvt7lbrd3m9m90t', '19mp0r4ex8h0fzb', 'o0xgrf3f8ort2v7', 'ukrwkiyh9ntv5aj'], **params)
        self.dev_print(total, res)

    def test_seeco_subtask_es(self):
        res = ESService.querySeEcoSubTaskById("h7x8wmtf8rsppn4", "00190000028KXIFAA4")
        self.dev_print(res)

    def test_sework_task_ids(self):
        task_co_list = SeWorkTaskDao.queryTaskJoinSysUserByUserIds(["*"])
        self.dev_print(len(task_co_list))

    @unittest.skip("跳过测试")
    def test_seproject_es(self):

        user_id = 'bvt7lbrd3m9m90t'
        user_ids = DataScopeDao.getSysUserByRank(user_id, 'employee:list')
        print(user_ids)
        params = {
            "page": 1,
            "size": 10,
        }
        total, sysuser_employee_department = SysUserDao.getSysUserEDByIdsAndFilter(user_ids, **params)

        for sed in sysuser_employee_department:
            employee, department = sed[1], sed[2]

            employee_schema = TbEmployeeSchema()
            employee = employee_schema.dump(employee)
            employee['gender'] = int(employee['gender'])
            employee['department'] = department.name
            print(employee)
        # subordinate_list = DataScopeDao.getSubordinateIdById(user_id)
        # params = {
        #     "query": "",
        #     # "date_range": ["2023-12-11 07:56:32", "2023-12-12 07:56:32"],
        #     # "date_order": "desc",
        #     # "owner_id": ["o0xgrf3f8ort2v7"],
        #     # "created_by_id": ["yuatx5ktbwva33n"],
        #     # "participants": ["o0xgrf3f8ort2v7"],
        #     # "user_id": "gzu4781ukw16eyc",
        #     "classification": "subordinate",
        #     "status": [1, 2, 3, 4],
        #     "page": 1,
        #     "size": 100,
        #     "subordinate_uid": [sysuser.id for sysuser in subordinate_list]
        # }
        # total, res = ESService.querySeProjectByFilter(user_ids, **params)
        # self.dev_print(total, res)

    @unittest.skip("跳过测试")
    def test_update_sysuser_manage(self):
        sysuser_employee_list = SysUserDao.getAllSysUserEmployeeById()
        if sysuser_employee_list:
            for sysuser_employee in sysuser_employee_list:
                sysuser, employee = sysuser_employee
                if employee.leader:
                    leader_employee = TblEmployeeDao.queryEmployeeByUserId(employee.leader)
                    manage_user = SysUserDao.querySysUserByEmployeeId(leader_employee.id)
                    if manage_user:
                        update_data = {"manage_id": manage_user.id}
                        SysUserDao.updateSysUserById(sysuser.id, update_data)

    def test_sysuser_subordinate(self):
        user_id = 'bvt7lbrd3m9m90t'
        sysuser_list = SysUserDao.getSysPersonSubordinateIdById(user_id)
        for sys_user in sysuser_list:
            self.dev_print({"id": sys_user.id, "name": sys_user.display_name, "manage_id": sys_user.manage_id})

    def test_employee_subordinate(self):
        user_id = 'bvt7lbrd3m9m90t'
        sysuser_list = DataScopeDao.getEmployeeSubordinateIdById(user_id)
        for sysuser in sysuser_list:
            self.dev_print(sysuser.display_name)

    @unittest.skip("跳过测试")
    def test_sys_user_id(self):
        sys_user = SysUserDao.querySysUserByDisplayName('XiongYing Chen(陈雄应)')
        print(sys_user.id)

    @unittest.skip("跳过测试")
    def test_set_token(self):
        from datetime import datetime
        from app.utils.auth_util import JwtUtil
        from app.extensions import redis_client

        user_id = 'vx9fdlcdcbwgva9'
        jwt_util = JwtUtil('hE2J&XIcP@hHo3ICLcB@cA1NR8Vfu8qQ')

        sso_user = {}
        role_users = SysRoleUserDao.querySysRolesByUserId(user_id)
        roles = [role_user.role_id for role_user in role_users]
        sso_user['roles'] = roles

        timestamp = datetime.now().timestamp()
        sso_user['timestamp'] = timestamp
        token = jwt_util.createToken(user_id, timestamp)
        # SSO登陆信息写入Redis缓存, key techadmin:online:userid
        print(token)
        redis_client.updateOnlineUser(user_id, sso_user, 86400)

    @unittest.skip("跳过测试")
    def test_db_session(self):
        from app.models import db
        from app.extensions import executor
        import concurrent.futures
        import time
        from app.controllers.service.dashboard_service import SeProjectTaskMinePendingTask

        for _ in range(100):
            app_db = db.get_app()
            task_list, user_id = [], 'bvt7lbrd3m9m90t'
            dashboard_service = [
                SeProjectTaskMinePendingTask
            ]
            task_list.extend(dashboard_service)

            data = None
            futures = [executor.submit(task, app_db, user_id) for task in task_list]
            for future in concurrent.futures.as_completed(futures):
                data = future.result()

            self.dev_print(data)

        time.sleep(60)

    def test_se_project_all_record(self):
        record_tu_list = SeProjectRecordDao.getPublishProjectRecord('2bamthd9sbmuven')
        self.dev_print(record_tu_list)

    def test_all_superiors(self):
        user_id = 'o0xgrf3f8ort2v7'
        sysuser_list = DataScopeDao.getAllSuperiorsByUserId(user_id)
        for sysuser in sysuser_list:
            self.dev_print(sysuser.display_name)

    def test_crm_assgin(self):
        crm_assigner_list = CrmViewsDao.queryAssignerByEmail("fengxiangyang@Hillstonenet.com")
        for assigner in crm_assigner_list:
            employee_department = TblEmployeeDao.getEmployeeJoinDepartmentDByEmail(assigner[3])
            if not employee_department:
                continue

            employee, department = employee_department
            assign_sysuser = SysUserDao.querySysUserByEmployeeId(assigner[3])
            if not assign_sysuser:
                sys_user = SysUserDao.querySysUserByEmployeeId(employee.id)
                if sys_user:
                    assigner_user_id = sys_user.id
                else:
                    schema = SysUserSchema(only=['id', 'display_name', 'employee_id'])
                    sys_user = schema.load({"display_name": employee.name, "employee_id": employee.id})
                    assigner_user_id = SysUserDao.addSysUserByEmployee(sys_user)
            else:
                assigner_user_id = assign_sysuser.id

            user_name = f'{employee.name}-{department.name}-{employee.position}'
            owner = {
                "id": assigner_user_id,
                "internal_email": employee.email,
                "user_name": user_name,
            }
            self.dev_print(owner)

