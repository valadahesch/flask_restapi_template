import os
import io
import requests
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import json

from docxtpl import DocxTemplate
from datetime import datetime
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
# from docx2pdf import convert
import tempfile


# import win32com.client as win32
# import pythoncom
def generate_bar_chart(title, categories, values):
    plt.rcParams['font.sans-serif'] = ["SimHei"]
    plt.figure()
    plt.bar(categories, values)
    plt.title(title)

    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)
    plt.close()
    return img_stream


# 生成饼图
def generate_pie_chart(title, labels, sizes):
    plt.rcParams['font.sans-serif'] = ["SimHei"]
    plt.figure()
    explode = (0, 0.1)  # 仅"爆炸"第2部分
    plt.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
    plt.title(title)

    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)
    plt.close()
    return img_stream


class OFFICEUtil:

    def __init__(self):
        pass

    def renderTheInspectionReportTemplate(self, record_list, task, org_name, start_date, contrast, oss_util):
        """
        巡检模板数据写入（写入设备信息）
        """
        if record_list is None:
            return False
        # 数据处理
        chinese_numbers = {
            "1": "一季", "2": "二季", "3": "三季", "4": "四季"
        }
        monthly_dic = {"01": "一月", "02": "二月", "03": "三月", "04月": "四月", "05": "五月", "06": "六月", "07": "七月",
                       "08": "八月", "09": "九月", "10": "十月", "11": "十一月", "12": "十二月"}
        inspection_type = task.inspection_type.split("-")
        now = datetime.now()
        if len(inspection_type) != 3:
            month = start_date.month
            quarter = (month - 1) // 3 + 1
            inspection_type = ['q', str(start_date.year), str(quarter)]

        # 季度参数
        timing_separation = ''
        if inspection_type:
            if inspection_type[0] == 'q':
                timing_separation = "%s年第%s度" % (inspection_type[1], chinese_numbers[inspection_type[2]])
            else:
                timing_separation = "%s年第%s度" % (inspection_type[1], monthly_dic[inspection_type[2]])


        under_warranty = 0  # 在保数量
        over_insured = 0  # 过保数量
        table_id = 1  # 序号ID
        device_model = {}  # 各设备型号数量
        software_version = {}  # 各软件版本数量

        compare_main_baseconfig = []  # 主备配置一致性
        password_policy = []  # 口令长度与复杂度
        admin_lockout_duration = []  # 账号锁定策略
        unsafe_interface = []  # 关闭不安全的管理方式
        admin_host = []  # 配置可信主机

        logging_status = []  # 查看事件、告警、配置、操作、威胁日志是否开启
        log_threat = []  # Threat安全威胁日志分析
        log_alarm = []  # 告警日志分析
        all_passrlue = []  # 检查是否有全通策略

        for record in record_list:
            record['table_id'] = table_id
            if record['device_model'] in device_model:
                device_model[record['device_model']] += 1
            else:
                device_model[record['device_model']] = 1

            if record['software_version'] in software_version:
                software_version[record['software_version']] += 1
            else:
                software_version[record['software_version']] = 1

            # 安全评估-1、配置检查
            device_name = "_".join([record['device_name'], record['device_sn']])
            if record['compare_main_baseconfig'] and record['compare_main_baseconfig'] != '""':
                abnormal = ",".join(json.loads(record['compare_main_baseconfig']))
                compare_main_baseconfig.append(":".join([device_name, abnormal]))
            if record['password_policy']:
                password_policy.append(device_name)
            if record['admin_lockout_duration']:
                admin_lockout_duration.append(device_name)
            if record['unsafe_interface']:
                unsafe_interface.append(device_name)
            if record['admin_host']:
                admin_host.append(device_name)

            # 安全评估-2、安全日志分析,3、策略规范性
            if record['logging_status'] and 'off' in record["logging_status"].lower():
                logging_status.append(device_name)
            if record["log_threat"]:
                suggest = device_name + "检测到TOP10威胁类型：" + "{{威胁类型}}"

                log_threat.append(suggest)
            if record["log_alarm"]:
                log_alarm.append(":".join([device_name, record['log_alarm']]))
            if record["all_passrlue"]:
                all_passrlue.append(":".join([device_name, record['all_passrlue'].strip().replace("\n", ",").replace("+", "")]))

            record["date_tag"] = timing_separation

            if now >= start_date:
                over_insured += 1
            else:
                under_warranty += 1
            table_id += 1

        # 获取文件路径
        abspath = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(abspath, "default_docx/XX客户XXXX年XX季度巡检报告.docx")
        font_path = os.path.join(abspath, "font/simhei.ttf")
        fm.fontManager.addfont(font_path)

        over_chart_stream = generate_pie_chart('设备许可过保比例', ['在保', '过保'], [under_warranty, over_insured])
        product_chart_stream = generate_bar_chart('各型号设备数量', device_model.keys(), device_model.values())
        software_chart_stream = generate_bar_chart('软件版本统计', software_version.keys(), software_version.values())

        # 初始化模板对象
        tpl = DocxTemplate(path)  # 打开word文件

        context = {
            "company": org_name,
            "year": inspection_type[1],
            "quarter": chinese_numbers[inspection_type[2]] if inspection_type[0] == 'q' else monthly_dic[inspection_type[2]],
            "report_date": start_date.strftime("%Y-%m-%d"),
            "record_list": record_list,
            "quarterly_list": record_list if contrast else [],
            "under_warranty": under_warranty,
            "over_insured": over_insured,
            "set_number": len(record_list),
            "normal_number": "{{normal_number}}",
            "abnormal_number": "{{abnormal_number}}",
            "timing_separation": timing_separation,
            # "external_str": "{{external_str}}",
            "for_start": "{%tr for row in external_list %}",
            "for_due": "{%tr endfor %}",
            "row_id": "{{row.id}}",
            "row_name": "{{row.device_name}}",
            "row_sn": "{{row.device_sn}}",
            "row_occurrence_time": "{{row.occurrence_time}}",
            "row_concrete_issue": "{{row.concrete_issue}}",
            "row_solution": "{{row.solution}}",
            "row_risk_grade": "{{row.risk_grade}}",
            "over_chart": InlineImage(tpl, over_chart_stream, width=Mm(150)),
            "product_chart": InlineImage(tpl, product_chart_stream, width=Mm(150)),
            "software_chart": InlineImage(tpl, software_chart_stream, width=Mm(150)),
            "compare_main_baseconfig_equipment": "、".join(compare_main_baseconfig),
            "compare_main_baseconfig_suggest": "以上设备配置存在差异，请检查确认是否正常" if compare_main_baseconfig else '',
            "password_policy_equipment": "、".join(password_policy),
            "password_policy_suggest": "以上设备口令长度或复杂度不符合安全要求，建议设置口令长度至少8位、至少1个大写字母、1个小写字母、1个数字和1个特殊字符" if password_policy else '',
            "admin_lockout_duration_equipment": "、".join(admin_lockout_duration),
            "admin_lockout_duration_suggest": "以上设备账号锁定策略不符合安全要求，建议锁定时间为2分钟及以上" if admin_lockout_duration else '',
            "unsafe_interface_equipment": "、".join(unsafe_interface),
            "unsafe_interface_suggest": "以上设备存在不安全的管理方式，建议在接口配置中关闭" if unsafe_interface else '',
            "admin_host_equipment": "、".join(admin_host),
            "admin_host_suggest": "以上设备可信主机配置不符合安全要求，建议删除0.0.0.0/0、::/0网段，细化可信可信管理主机地址" if admin_host else '',
            "logging_status_equipment": "、".join(logging_status),
            "logging_status_suggest": "以上设备存在事件日志、告警日志、配置日志、操作日志、威胁日志未开启的情况" if logging_status else '',
            "log_threat_equipment": "、".join(log_threat),
            "log_threat_suggest": " 请持续关注以上攻击拦截情况，若存在非误报的持续攻击动作，建议添加黑名单或安全策略对IP进行封禁" if log_threat else '',
            "log_alarm_equipment": "、".join(log_alarm),
            "log_alarm_suggest": "以上设备存在异常告警日志：xxxx" if log_alarm else '',
            "all_passrlue_equipment": "、".join(all_passrlue),
            "all_passrlue_suggest": "请根据业务访问需求细化安全策略并删除全通策略" if all_passrlue else ''
        }

        # 开始宣誓数据到模板文件中
        tpl.render(context=context)
        with tempfile.TemporaryDirectory() as temp_dir:
            path_html = temp_dir + "/巡检报告.docx"
            tpl.save(path_html)
            with open(path_html, 'rb') as file_stream:
                # 文件上传-上传历史记录
                file_meta = {
                    "ContentType": "docx",
                    "ContentDisposition": f"attachment; filename={org_name}_巡检报告_{task.id}.docx"
                }
                _id = oss_util.uploadFileStream(file_stream, "tech-attachment", file_meta, task.report_file_id)
        return _id

    def summaryOfInspectionDocuments(self, report_id, summary_id, task_id, org_name, external, total, oss_util):
        """
        写入巡检文件总结信息
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = temp_dir + '/巡检报告模板.docx'
            output_path = temp_dir + '/巡检报告.docx'

            # 异常设备数量
            abnormal = len(external['external_list'])
            normal = total - abnormal

            for record in external['external_list']:
                record['id'] = int(record['id']) + 1
                device = record['device_name_sn'].split("_")
                record['device_name'] = device[0]
                record['device_sn'] = device[1]

            data, _ = oss_util.getObject("tech-attachment", report_id)

            with open(input_path, 'wb') as file:
                file.write(data)
                file.close()

            # 初始化模板对象
            tpl = DocxTemplate(input_path)  # 打开word文件

            context = {
                # "external_str": external['_str'],
                "normal_number": normal,
                "abnormal_number": abnormal,
                "external_list": external['external_list']
            }

            # 开始宣誓数据到模板文件中
            tpl.render(context=context)
            tpl.save(output_path)

            with open(output_path, 'rb') as file:
                # data = file.read()
                # file.close()
                # # 文件上传-上传历史记录
                file_meta = {
                    "ContentType": "docx",
                    "ContentDisposition": f"attachment; filename={org_name}_巡检报告_{task_id}.docx"
                }
                _id = oss_util.uploadFileStream(file, "tech-attachment", file_meta, summary_id)
        return _id

    def convertToPDFFile(self, report_id, task, org_name, oss_util):
        """
        第一次写入模板文件转换为PDF
        """
        # 下载文件
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = temp_dir + "/巡检报告.docx"
            output_path = temp_dir + '/巡检报告.pdf'

            data, _ = oss_util.getObject("tech-attachment", report_id)

            with open(input_path, 'wb+') as file:
                file.write(data)
                file.seek(0)
                file.close()

            # # 初始化com库
            # pythoncom.CoInitialize()
            # # 创建word应用程序实例
            # word_app = win32.gencache.EnsureDispatch('Word.Application')
            # # 设置应用程序可见性为False （不显示word界面）
            # word_app.Visible = False
            #
            # try:
            #     # 打开word文档
            #     doc = word_app.Documents.Open(input_path)
            #     # 保存为PDF
            #     doc.SaveAs(output_path, FileFormat=17)
            #     doc.Close()
            #     return True
            # except Exception as e:
            #     print(e)
            #     return ''
            # finally:
            #     word_app.Quit()
            #     # 在程序结束前取消初始化COM库
            #     pythoncom.CoUninitialize()

            # convert(input_path)

            with open(output_path, 'rb') as file_stream:
                # 文件上传-上传历史记录
                file_meta = {
                    "ContentType": "application/pdf",
                    "ContentDisposition": f"attachment; filename={org_name}_巡检报告_{task.id}.pdf"
                }
                _id = oss_util.uploadFileStream(file_stream, "tech-attachment", file_meta, task.preview_file_id)
            return _id

    def convertToPDFFileV2(self, report_id, task, org_name, oss_util):
        """
        第一次写入模板文件转换为PDF
        """
        # 下载文件
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = temp_dir + f'/{task.preview_file_id}.pdf'

            file_data, _ = oss_util.getObject("tech-attachment", report_id)

            convert_url = 'http://10.86.248.49:9980/lool/convert-to/pdf'
            files = {'data': (f'{task.preview_file_id}.docx', file_data, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            response = requests.post(convert_url, files=files)

            if response.status_code == 200:
                # 文件上传-上传历史记录
                file_meta = {
                    "ContentType": "application/pdf",
                    "ContentDisposition": f"inline; filename={org_name}_巡检报告_{task.preview_file_id}.pdf"
                }
                pdf_file_obj = io.BytesIO(response.content)
                _id = oss_util.uploadFileStream(pdf_file_obj, "tech-attachment", file_meta, task.preview_file_id)
            return _id