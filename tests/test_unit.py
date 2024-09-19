import os
import datetime
import unittest

from datetime import datetime


class TestUnit(unittest.TestCase):

    def dev_print(self, *args):
        if self.env == 'dev':
            print(*args)

    def setUp(self):
        self.env = os.environ.get('APP_ENV', 'dev')

    def tearDown(self):
        pass

    def test_nanoid(self):
        from app.utils.func_util import nanoId
        nano_id = nanoId()
        self.dev_print(nano_id)

    def test_numberid(self):
        from app.utils.func_util import numberId
        number_id = numberId()
        self.dev_print(number_id)

    def test_re(self):
        import re
        reg_str = ':role_id:$role_id:user_id:$user_id'
        all_arg = re.findall(r'(?:\$(.*?)(?:\:|$))', reg_str)
        self.dev_print(all_arg)

    def test_sso_schema(self):
        from app.controllers.schema import SysUserSchema
        from app.controllers.response import SSOUser

        sso_user = {
            'UserID': '2cc1bfee-b67e-402f-9ac2-ae885703d75d', 'UserName': 'zcding@Hillstonenet.com',
            'DisplayName': 'Zhicheng Ding(丁智成)', 'FirstName': 'Zhicheng', 'LastName': 'Ding',
            'NickName': 'zcding', 'Birthday': None, 'UserType': 0, 'CompanyName': '山石网科通信技术股份有限公司',
            'Mobile': '18855055162', 'Email': 'zcding@Hillstonenet.com', 'TimeDiff': 480, 'OEMBrand': '',
            'Language': 'zh-cn', 'first_login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        sso_user = SSOUser(**sso_user).to_dict()
        sso_user['first_login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        user_schema = SysUserSchema()
        sys_user = user_schema.load(sso_user)
        self.dev_print(sys_user)

        user_schema = SysUserSchema(only=['id', 'user_name', 'email'])
        sys_user_dict = user_schema.dumps(sys_user)
        self.dev_print(sys_user_dict)

        user_schema = SysUserSchema(exclude=['id', 'user_name', 'email'])
        sys_user_dict = user_schema.dump(sys_user)
        self.dev_print(sys_user_dict)

    def test_jwt_util(self):
        from app.utils.auth_util import JwtUtil
        from app.config import ServerConfig
        jwt_util = JwtUtil(ServerConfig.get('secret') if ServerConfig.get('secret') else None)

        timestamp = datetime.now().timestamp()
        token = jwt_util.createToken("yuatx5ktbwva33n", timestamp)
        self.dev_print(token)

        user_id = jwt_util.loadsToken(token).get('userid')
        timestamp = jwt_util.loadsToken(token).get('timestamp')
        self.dev_print(user_id, timestamp)

    def test_apollo(self):
        from app.utils.apollo import ApolloUtil
        from app.config import ApolloConfig
        apollo_util = ApolloUtil(ApolloConfig['server_url'], ApolloConfig['app_id'])
        email_cc = apollo_util.getValue("sales_manager")
        self.dev_print(email_cc)

    def test_es(self):
        from app.controllers import ESService
        account = ESService.queryCrmAccountByAccountId('00190000028MXjiAAG')
        self.dev_print(account)
        user = ESService.queryCrmSystemUserByUserId('2FB1AF7E-B213-49D2-A4D1-89F3F79D462E')
        self.dev_print(user)
        res = ESService.querySeWorkByProjectId('mz23yzr8hvy7jas')
        self.dev_print(res)
        res = ESService.queryCrmAccountByAccountName("湛江市坡头区人民医院")
        self.dev_print(res)
        total, res = ESService.querySysResource('', 'HA(高可用性)AP模', 1, 10)
        self.dev_print(res)
        res = ESService.querySeProjectByProjectId('5rqn3sj7ijw5s80')
        self.dev_print(res)

    @unittest.skip("跳过测试")
    def test_message_gw(self):
        from app.extensions import message_gw
        from app.utils.http_api.msg_template import SeWorkProjectEmail

        template = SeWorkProjectEmail()
        template.update({
            "id": "vxmb4t69ttwk6gu", "project_number": "BJ25QJZ8D6", "subject": "渠道培训",
            "owner_name": "zcding", "created_by_name": "zcding",
            "created_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

        message_gw.push(target="zcding@hillstonenet.com", template=template)

    def test_qywx_api(self):
        from app.extensions import qywx_api
        session = qywx_api.code2Session('8Vyy-Uy1tfBWZWW-mraEXeDnaimifh3U4_IDY5K37w')
        print(session)

