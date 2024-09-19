import json
import logging
from pyapollo.apollo_client import ApolloClient


class ApolloUtil:
    data_map = {}

    def __init__(self, server_url, app_id):
        """
        使用AK&SK初始化账号Client
        """
        file_filter = FileFilter()
        apollo_logger = logging.getLogger('pyapollo.apollo_client')
        apollo_logger.addFilter(file_filter)

        self.client = ApolloClient(app_id, config_server_url=server_url, cycle_time=600)
        self.client.start()

    def getValue(self, key):
        value = self.client.get_value(key)
        if value:
            try:
                json_object = json.loads(value)
                return json_object

            except Exception:
                return value

        return


class FileFilter(logging.Filter):
    def filter(self, record):
        if record.filename in ['apollo_client.py']:
            return False
        return True
