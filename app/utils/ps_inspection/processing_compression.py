import zipfile
import json
from distutils.version import LooseVersion


class ProcessingCompressionUtil:

    def __init__(self):
        self.start_version = "1.0"
        self.end_version = "1.3"

        self.fields = [
            "hostname", "product_name", "sn", "version", "uptime", "feature", "plat_expiration", "cp_memory",
            "dp_memory", "throughput", "env_pssum_status", "env_fan_status", "module_status", "alg", "ha",
            "logging_status", "log_threat ", "log_event", "clock", "compare_main_baseconfig", "password_policy",
            "admin_lockout_duration", "unsafe_interface", "admin_host", "logging_status", "log_threat", "log_alarm",
            "all_passrlue", "ha_group", "synced", "poor"
        ]
        self.fields_dict = {
            "ha": ["ha_status"], "session": ["max_session", "rampup_session"],
            "cpu": ["cpu_24h_max", "env_cpu_temperature"],
            "rate": ["route使用率", "policy使用率", "service使用率", "address使用率", "dnat使用率", "snat使用率"]
        }

    def unzipTheFile(self, file_storage):
        # 获取文件处理
        zip_file = zipfile.ZipFile(file_storage)
        file_list = zip_file.namelist()

        json_file = zip_file.open(file_list[0])

        report_data = json.loads(json.loads(json_file.read()))
        zip_file.close()

        # source_version, target_version = zip([report_data["report_version"]["struct_version"].split("."),
        #                                       struct_version.split(".")])
        #
        # if source_version[0][0] > target_version[0][0] or source_version[0][1] > target_version[0][1]:
        if not self.version_in_range(report_data["report_version"]["struct_version"]):
            return [False, {"start": self.start_version, "end": self.end_version}]

        dataInfo = []
        for data in report_data["report_data"]:
            for key, values in self.fields_dict.items():
                if key not in data:
                    data[key] = {}
                for val in values:
                    if val not in data[key]:
                        data[key][val] = ''
            for key in self.fields:
                if key not in data:
                    data[key] = ''

            dataInfo.append(data)

        return [True, dataInfo]

    def version_in_range(self, version):
        """
        比较版本是否超过支持范围
        """
        ver = LooseVersion(version)
        min_ver = LooseVersion(self.start_version)
        max_ver = LooseVersion(self.end_version)

        return min_ver <= ver <= max_ver
