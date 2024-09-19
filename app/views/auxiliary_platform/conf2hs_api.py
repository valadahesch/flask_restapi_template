import datetime
import json
import io
import pandas as pd
import chardet
import openpyxl
import xlwt

from flask import Blueprint, session, jsonify, current_app
from flask_restful import Resource
from flask_restful.reqparse import RequestParser
from app.utils.func_util import prepare_args_for_parser
from werkzeug.datastructures import FileStorage
from app.extensions import oss_util, permission, logger, executor
from app.enums.auxiliary_enum import getExportItems
from app.enums.permission_enum import p_list
from app.controllers.schema import SysAttachmentSchema, Conf2HsSchema
from app.controllers.dao import SysAttachmentDao, AuxiliaryConf2HSDao
from app.utils.api_util import Api, AppResponse, AppException
from conf2hs import factory, get_brand
from Configure_Conversion_SDK.Configure_Conversion import Mywin
from app.models import db

conf2hs_app = Blueprint('conf2hs', __name__, url_prefix='/api/auxiliary/conf2hs')
conf2hs_api = Api(conf2hs_app)


@conf2hs_api.resource('/brands')
class Brands(Resource):

    # @permission.check(p_list['p_online_tools_conf2hs'])
    def get(self):
        """
        获取商列表
        :return:
        """
        data = {"list": []}
        manufacturer_list = Mywin.manufacturer_list()
        for k, v in manufacturer_list.items():
            data["list"].append({"key": k, "label": v})
        return jsonify(AppResponse(data))


conf2hs_items_parser = RequestParser()
conf2hs_items_parser.add_argument('brand_name', location='args', type=str, required=True)


@conf2hs_api.resource('/brand/items')
class BrandItems(Resource):

    # @permission.check(p_list['p_online_tools_conf2hs'])
    def get(self):
        """
        获取版本、模块、导出选项
        :return:
        """
        parser_args = prepare_args_for_parser(conf2hs_items_parser.copy())
        params = parser_args.parse_args()

        models = []
        operation_change_list = Mywin.operation_change_list()
        for k, v in operation_change_list.items():
            models.append({"key": k, "label": v})

        export = []
        export_option_list = Mywin.export_option_list()
        for k, v in export_option_list.items():
            export.append({"key": k, "label": v})

        data = {
            "version": [],
            "models": models,
            "export": export
        }
        return jsonify(AppResponse(data))


brans_transform_parser = RequestParser()
brans_transform_parser.add_argument('file', location='files', type=FileStorage)
brans_transform_parser.add_argument('brand_name', location='form', type=str, required=True)
brans_transform_parser.add_argument('brand_version', location='form', type=str)
brans_transform_parser.add_argument('models', location='form', type=str)
brans_transform_parser.add_argument('export', location='form', type=str, required=True)
brans_transform_parser.add_argument('description', location='form', type=str, required=True)


@conf2hs_api.resource('/brand/transform')
class BrandTransform(Resource):

    # @permission.check(p_list['p_online_tools_conf2hs'])
    def post(self):
        """
        解析配置文件
        :return:
        """
        data = {}
        parser_args = prepare_args_for_parser(brans_transform_parser.copy())
        params = parser_args.parse_args()

        models = params["models"].split(',')
        export = params["export"].split(',')
        file_storage = params.pop("file")
        filename = file_storage.filename
        schema_data = {
            "file_name": filename, "models": json.dumps(models),
            "brand_name": params.get("brand_name"),
            "brand_version": params.get("brand_version"),
            "created_by_id": session["user_id"], "export": json.dumps(export),
            "result": 'running', "description": params.get("description")
        }
        schema = Conf2HsSchema()
        schema_data = schema.load(schema_data)
        _id = AuxiliaryConf2HSDao.addConf2Hs(schema_data)

        file_byte = file_storage.read()
        file_storage.stream.seek(0)

        file_meta = {
            "ContentType": file_storage.content_type,
            "ContentDisposition": f"attachment; filename={filename}"
        }
        attachment_id1 = oss_util.uploadFileStream(file_storage, "tech-attachment", file_meta)
        attachment = {
            "id": attachment_id1, "file_name": filename, "file_size": len(file_byte),
            "related_object": "online_conf2hs", "related_object_id": _id,
            "created_by_id": session["user_id"], "file_type": file_storage.content_type
        }
        schema = SysAttachmentSchema()
        attachment = schema.load(attachment)
        SysAttachmentDao.addAttachment(attachment)

        db_app = db.get_app()
        user_id = session["user_id"]

        # def transform(**kwargs):
        #     brand = factory(brand_name=kwargs.get("brand_name"))
        #     try:
        #         result = chardet.detect(file_byte)
        #         file_bytesio = io.BytesIO(file_byte)
        #         file_obj = io.TextIOWrapper(file_bytesio, encoding=result['encoding'])
        #         brand.extract(file_obj, models)
        #         brand.transform_load()
        #
        #         if 'translation' in export:
        #             translation_filename = f'{filename.split(".")[0]}_配置翻译.txt'
        #             config_translation = brand.get_config_translation()
        #
        #             res_byte = config_translation.encode('gbk')
        #             byte_io = io.BytesIO(res_byte)
        #             file_meta = {
        #                 "ContentType": "txt",
        #                 "ContentDisposition": f"attachment; filename={translation_filename}"
        #             }
        #             attachment_id2 = oss_util.uploadFileStream(byte_io, "tech-attachment", file_meta)
        #
        #             attachment = {
        #                 "id": attachment_id2, "file_name": translation_filename, "file_size": len(res_byte),
        #                 "related_object": "online_conf2hs", "related_object_id": _id,
        #                 "created_by_id": user_id, "file_type": "txt"
        #             }
        #             schema = SysAttachmentSchema()
        #             attachment = schema.load(attachment)
        #             with db_app.app_context():
        #                 SysAttachmentDao.addAttachment(attachment)
        #
        #         if 'comparison' in export:
        #             df_data = {}
        #             excel_buffer = io.BytesIO()
        #             comparison_filename = f'{filename.split(".")[0]}_配置对比.xlsx'
        #             config_comparison = brand.get_config_comparison()
        #             for model, value in config_comparison.items():
        #                 df = pd.DataFrame(value, columns=['源厂商配置', '山石配置'])
        #                 df_data[model] = df
        #
        #             with pd.ExcelWriter(excel_buffer, engine='xlsxwriter', mode='xlsx') as writer:
        #                 for sheet, df in df_data.items():
        #                     df.to_excel(writer, index=False, sheet_name=sheet)
        #
        #             excel_binary_data = excel_buffer.getvalue()
        #             excel_buffer.seek(0)
        #             file_meta = {
        #                 "ContentType": "xlsx",
        #                 "ContentDisposition": f"attachment; filename={comparison_filename}"
        #             }
        #             attachment_id3 = oss_util.uploadFileStream(excel_buffer, "tech-attachment", file_meta)
        #             attachment = {
        #                 "id": attachment_id3, "file_name": comparison_filename, "file_size": len(excel_binary_data),
        #                 "related_object": "online_conf2hs", "related_object_id": _id,
        #                 "created_by_id": user_id, "file_type": "xlsx"
        #             }
        #             schema = SysAttachmentSchema()
        #             attachment = schema.load(attachment)
        #             with db_app.app_context():
        #                 SysAttachmentDao.addAttachment(attachment)
        #
        #         if 'traffic' in export:
        #             from conf2hs.source import TrafficPkt
        #             df_data = {}
        #             excel_buffer = io.BytesIO()
        #             traffict_filename = f'{filename.split(".")[0]}_打流表.xlsx'
        #             tp = TrafficPkt(brand.model_db)
        #             policy_ip = tp.generate_policy_ip()
        #             for model, value in policy_ip.items():
        #                 df = pd.DataFrame(value, columns=[
        #                     'ID', '源地址', '目标地址', '服务', '源转换为', '目的转换为', '策略描述', '源区域', '目标区域', '启用状态', '动作'
        #                 ])
        #                 df_data[model] = df
        #
        #             with pd.ExcelWriter(excel_buffer, engine='xlsxwriter', mode='xlsx') as writer:
        #                 workbook = writer.book
        #                 workbook.add_format({"text_wrap": True})
        #                 for sheet, df in df_data.items():
        #                     df.to_excel(writer, index=False, sheet_name=sheet)
        #
        #             excel_binary_data = excel_buffer.getvalue()
        #             excel_buffer.seek(0)
        #             file_meta = {
        #                 "ContentType": "xlsx",
        #                 "ContentDisposition": f"attachment; filename={traffict_filename}"
        #             }
        #             attachment_id3 = oss_util.uploadFileStream(excel_buffer, "tech-attachment", file_meta)
        #             attachment = {
        #                 "id": attachment_id3, "file_name": traffict_filename, "file_size": len(excel_binary_data),
        #                 "related_object": "online_conf2hs", "related_object_id": _id,
        #                 "created_by_id": user_id, "file_type": "xlsx"
        #             }
        #             schema = SysAttachmentSchema()
        #             attachment = schema.load(attachment)
        #             with db_app.app_context():
        #                 SysAttachmentDao.addAttachment(attachment)
        #
        #         with db_app.app_context():
        #             AuxiliaryConf2HSDao.updateConf2HsById(_id, {"result": "successful"})
        #     except Exception as e:
        #         logger.error(f"BrandTransform Exception: {repr(e)}")
        #         with db_app.app_context():
        #             AuxiliaryConf2HSDao.updateConf2HsById(_id, {"result": "failed", "failed_reason": str(e)})
        #
        #     finally:
        #         brand.end_clear()

        def output_xls(policy,bytes_io,filename):
            #添加datatime和xlwt
            print('正在生成Excle适用的配置信息...\n')
            print('发现' + str(len(policy) - 1) + '条策略！\n')
            # filename = 'policy_ip_for_sendpkt-' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.xls'
            workbook = xlwt.Workbook(encoding='ascii')
            sheet = workbook.add_sheet('policy-ip', cell_overwrite_ok=True)  # 创建工作簿
            # sheet_lite =workbook.add_sheet('policy-ip_lite',cell_overwrite_ok=True)#创建工作簿
            r = 1  # 起始行
            print('文件创建成功:' + filename + '\n正在写入数据...\n')
            style = xlwt.easyxf('align: wrap on')  # 设置单元格自动换行
            title = ['ID', '源地址', '目标地址', '服务', '源转换为', '目的转换为', '策略描述', '源区域', '目标区域',
                     '启用状态',
                     '动作']  # 表格头
            # self.sum_list.append(title)
            tn = 0  # 起始列
            for t in title:  # 写入表头
                sheet.write(0, tn, t)
                # sheet_lite.write(0,tn,t)
                tn += 1
            for prow in policy:
                sheet.write(r, 0, prow[0])
                sheet.write(r, 1, prow[1], style)
                sheet.write(r, 2, prow[2], style)
                sheet.write(r, 3, prow[3], style)
                sheet.write(r, 4, prow[4], style)
                sheet.write(r, 5, prow[5], style)
                sheet.write(r, 6, prow[6], style)
                sheet.write(r, 7, prow[7], style)
                sheet.write(r, 8, prow[8], style)
                sheet.write(r, 9, prow[9], style)
                sheet.write(r, 10, prow[10], style)
                r += 1
            print(filename + ' 写入完成！\n')
            workbook.save(bytes_io)
            print(filename + ' 保存完成！\n正在打开...\n')
            # webbrowser.open(filename)
            print('打流表配置信息写入完成！\n')
            print('\n该配置信息可以用于流量工具进行测试，请根据策略方向手动筛选需要测试的内容。\n')
            # return workbook.save(bytes_io)

        def transform(**kwargs):
            try:
                my_win = Mywin(file_byte, kwargs.get("brand_name"), '')
                if 'config_conversion' in export:
                    translation_filename = f'{filename.split(".")[0]}_配置翻译.txt'
                    config_translation = my_win.sum_outconfig()
                    res_byte = config_translation.encode('gbk')
                    byte_io = io.BytesIO(res_byte)
                    file_meta = {
                        "ContentType": "txt",
                        "ContentDisposition": f"attachment; filename={translation_filename}"
                    }
                    attachment_id2 = oss_util.uploadFileStream(byte_io, "tech-attachment", file_meta)
                    attachment = {
                        "id": attachment_id2, "file_name": translation_filename, "file_size": len(res_byte),
                        "related_object": "online_conf2hs", "related_object_id": _id,
                        "created_by_id": user_id, "file_type": "txt"
                    }
                    schema = SysAttachmentSchema()
                    attachment = schema.load(attachment)
                    with db_app.app_context():
                        SysAttachmentDao.addAttachment(attachment)

                if 'compare_config' in export:
                    pass

                if 'output_traffic_excle' in export:
                    from conf2hs.source import TrafficPkt
                    traffict_filename = f'{filename.split(".")[0]}_打流表.xlsx'
                    config_transexcel=my_win.output_traffic_excle()
                    excel_buffer = io.BytesIO()
                    output_xls(config_transexcel,excel_buffer,traffict_filename)

                    excel_binary_data = excel_buffer.getvalue()
                    excel_buffer.seek(0)

                    file_meta = {
                        "ContentType": "xlsx",
                        "ContentDisposition": f"attachment; filename={traffict_filename}"
                    }
                    attachment_id3 = oss_util.uploadFileStream(excel_buffer, "tech-attachment", file_meta)
                    attachment = {
                        "id": attachment_id3, "file_name": traffict_filename, "file_size": len(excel_binary_data),
                        "related_object": "online_conf2hs", "related_object_id": _id,
                        "created_by_id": user_id, "file_type": "xlsx"
                    }
                    schema = SysAttachmentSchema()
                    attachment = schema.load(attachment)
                    with db_app.app_context():
                        SysAttachmentDao.addAttachment(attachment)

                with db_app.app_context():
                    AuxiliaryConf2HSDao.updateConf2HsById(_id, {"result": "successful"})

                my_win.remove_db()

            except Exception as e:
                logger.error(f"BrandTransform Exception: {repr(e)}")
                with db_app.app_context():
                    AuxiliaryConf2HSDao.updateConf2HsById(_id, {"result": "failed", "failed_reason": str(e)})

        executor.submit(transform, brand_name=params["brand_name"])

        data["id"] = _id
        return jsonify(AppResponse(data))


conf2hs_history_parser = RequestParser()
conf2hs_history_parser.add_argument('page', location='args', type=int, default=1)
conf2hs_history_parser.add_argument('size', location='args', type=int, default=10)
conf2hs_history_parser.add_argument('brand_name', location='args', type=str)
conf2hs_history_parser.add_argument('description', location='args', type=str)


@conf2hs_api.resource('/history')
class BrandHistory(Resource):

    # @permission.check(p_list['p_online_tools_conf2hs'])
    def get(self):
        """
        获取历史记录
        :return:
        """
        parser_args = prepare_args_for_parser(conf2hs_history_parser.copy())
        params = parser_args.parse_args()
        data = {
            "list": [], "total": 0,
            "page": int(params.get("page")), "size": int(params.get("size")),
        }

        create_by = session["user_id"]
        data["total"], history_list = AuxiliaryConf2HSDao.queryConf2HsByFilter(create_by, **params)

        manufacturer_list = Mywin.manufacturer_list()
        operation_change_list = Mywin.operation_change_list()
        export_option_list = Mywin.export_option_list()

        for history in history_list:
            schema = Conf2HsSchema()
            history = schema.dump(history)

            history["brand_name"] = manufacturer_list.get(history["brand_name"])

            models_list = []
            for operation in json.loads(history["models"]):
                models_list.append({"key": operation, "label": operation_change_list.get(operation)})
            history["models"] = models_list

            export_list = []
            for export in json.loads(history["export"]):
                export_list.append({"key": export, "label": export_option_list.get(export)})
            history["export"] = export_list

            if not history["failed_reason"]:
                history["failed_reason"] = ""

            data["list"].append(history)

        return jsonify(AppResponse(data))


@conf2hs_api.resource('/history/<history_id>')
class BrandHistoryDetail(Resource):

    # @permission.check(p_list['p_online_tools_conf2hs'])
    def get(self, history_id):
        """
        获取历史详情
        :return:
        """

        history = AuxiliaryConf2HSDao.queryConf2HsById(history_id)

        schema = Conf2HsSchema()
        data = schema.dump(history)

        data["models"] = []
        data["export"] = []
        data["attachments"] = []
        manufacturer_list = Mywin.manufacturer_list()
        data["brand_name"] = manufacturer_list.get(history.brand_name)

        operation_change_list = Mywin.operation_change_list()
        for operation in json.loads(history.models):
            data["models"].append({"key": operation, "label": operation_change_list.get(operation)})

        export_option_list = Mywin.export_option_list()
        for export in json.loads(history.export):
            data["export"].append({"key": export, "label": export_option_list.get(export)})

        if not data["failed_reason"]:
            data["failed_reason"] = ""

        attachments = SysAttachmentDao.queryAttachmentByObjectId("online_conf2hs", history_id)
        for attachment in attachments:
            data["attachments"].append({
                "id": attachment.id,
                "filename": attachment.file_name,
                "file_size": attachment.file_size,
                "file_type": attachment.file_type
            })

        return jsonify(AppResponse(data))

