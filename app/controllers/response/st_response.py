from marshmallow import fields, validate, validates_schema
from app.controllers.response.response_schema import ResponseSchema

# /api/search/site_list


class StSites(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Search.info'
    accendant = fields.Str(metadata={"label": "站点维护人"}, load_default="")
    create_time = fields.Str(metadata={"label": "站点添加时间"})
    description = fields.Str(metadata={"label": "站点功能或使用描述"}, load_default="", allow_none=True)
    id = fields.Integer(metadata={"label": "站点唯一id"})
    parent_id = fields.Int(metadata={"label": "站点父级id,用于数据结构化"}, allow_none=True)
    site_name = fields.Str(metadata={"label": "站点名称，用于前端显示"})
    site_url = fields.Str(metadata={"label": "访问站点的链接"}, load_default="", allow_none=True)
    type = fields.Str(metadata={"label": "站点的类型：path/url"}, load_default="path", allow_none=True)
    zindex = fields.Int(metadata={"label": "相同父级id下，用于数据显示排序"}, allow_none=True)


class StSitesList(ResponseSchema):
    list = fields.List(fields.Nested(StSites(unknown="exclude")), required=True, data_key="list")


# /api/search/overview


class StOverViewSource(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Search.info'
    key = fields.Str(metadata={"label": "主键"})
    name = fields.Str(metadata={"label": "显示名"})
    total = fields.Int(metadata={"label": "查询结果数量"})


class StOverViewSourceList(ResponseSchema):
    list = fields.List(fields.Nested(StOverViewSource(unknown="exclude")), required=True, data_key="list")


class StOverViewNext(ResponseSchema):
    __subsystem__ = 'System'
    __object__ = 'Search.info'
    id = fields.Integer(required=False, metadata={"label": "来源对应的id"})
    name = fields.String(required=False, metadata={"label": "来源名称"})
    total = fields.Integer(required=False, metadata={"label": "该来源的搜索结果计数"})


class StOverView(ResponseSchema):
    next = fields.Nested(StOverViewNext, required=False, metadata={"label": "来源的下一个id"})
    source = fields.List(fields.Nested(StOverViewSource), required=True, metadata={"label": "来源"})


# /api/search/detail


class StDetailSchemaOne(ResponseSchema):
    customer = fields.Str(required=True, metadata={"label": "最终客户"})
    data_time = fields.Str(required=True, metadata={"label": "数据发布时间"})
    meiguang = fields.Boolean(required=True, metadata={"label": "是否为镁光产品"})
    product_name = fields.Str(required=True, metadata={"label": "产品名称"})
    service_deadline = fields.Str(required=True, metadata={"label": "服务截至时间"})
    sn = fields.Str(required=True, metadata={"label": "序列号"})


class StDetailSchemaTwo(ResponseSchema):
    author = fields.Str(required=True, metadata={"label": "作者"})
    content = fields.Str(required=True, metadata={"label": "内容"})
    date = fields.Str(allow_none=True, metadata={"label": "文章日期"}, default="日期")
    id = fields.Str(required=True, metadata={"label": "文章id"})
    internal = fields.Boolean(required=True, metadata={"label": ""})
    title = fields.Str(required=True, metadata={"label": "文章标题"})
    url = fields.URL(required=True, metadata={"label": "文章链接"})


class StDetailList(ResponseSchema):
    list = fields.List(fields.Dict(), required=True, metadata={"label": ""})
    style = fields.Str(required=True, metadata={"label": ""})
    total = fields.Integer(required=True, metadata={"label": "条目"})


class StDetailSchema(ResponseSchema):
    @validates_schema
    def validate_list(self, data, **kwargs):
        for key in data:
            if key != "origin":
                list_data = data.get(key)['list']
                if list_data:
                    for item in list_data:
                        if not isinstance(item, dict):
                            raise ValueError('Invalid data structure in list')
                        if 'customer' in item:
                            StDetailSchemaOne().load(item)
                        else:
                            StDetailSchemaTwo().load(item)
                origin_data = data.get(key)
                if origin_data:
                    StDetailList().load(origin_data)
    kb = fields.Dict(allow_none=True, metadata={"label": "知识库"})
    case = fields.Dict(allow_none=True, metadata={"label": "case系统"})
    idocs = fields.Dict(allow_none=True, metadata={"label": "文档"})
    s = fields.Dict(allow_none=True, metadata={"label": "销售部站点"})
    hillstone_university = fields.Dict(allow_none=True, metadata={"label": "山石大学"})
    fr = fields.Dict(allow_none=True, metadata={"label": "FR"})
    bugzilla = fields.Dict(allow_none=True, metadata={"label": "bug系统"})
    dms = fields.Dict(allow_none=True, metadata={"label": "dms"})
    device_info = fields.Dict(allow_none=True, metadata={"label": "设备信息"})
    origin = fields.Str(required=True, metadata={"label": "搜索来源"})

