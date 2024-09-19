from alibabacloud_ccc20200701.client import Client as CCC20200701Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ccc20200701 import models as ccc20200701_models
from alibabacloud_tea_util import models as util_models


class AliyunUtil:
    instance_id = 'hillstone'
    endpoint = 'ccc.cn-shanghai.aliyuncs.com'

    def __init__(self, access_key_id: str, access_key_secret: str):
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(access_key_id=access_key_id, access_key_secret=access_key_secret)
        config.endpoint = self.endpoint
        self.client = CCC20200701Client(config)

    def listCallDetailRecords(self, **kwargs):
        list_call_detail_records_request = ccc20200701_models.ListCallDetailRecordsRequest(
            instance_id='hillstone',
            page_number=kwargs.get("page"),
            page_size=kwargs.get("size"),
            start_time=kwargs.get("start_time"),
            end_time=kwargs.get("end_time"),
            contact_id=kwargs.get("contact_id"),
            agent_id=kwargs.get("agent_id"),
            skill_group_id=kwargs.get("skill_group_id"),
            calling_number=kwargs.get("calling_number"),
            called_number=kwargs.get("called_number")
        )
        runtime = util_models.RuntimeOptions()

        resp = self.client.list_call_detail_records_with_options(list_call_detail_records_request, runtime)
        body = resp.to_map()['body']
        if body['Code'] == 'OK':
            return body["Data"]

    def listUsers(self, **kwargs) -> None:
        list_users_request = ccc20200701_models.ListUsersRequest(
            instance_id='hillstone',
            search_pattern=kwargs.get("name_pattern"),
            page_number=kwargs.get("page"),
            page_size=kwargs.get("size")
        )
        runtime = util_models.RuntimeOptions()

        resp = self.client.list_users_with_options(list_users_request, runtime)
        body = resp.to_map()['body']
        if body['Code'] == 'OK':
            return body["Data"]



