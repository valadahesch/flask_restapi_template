# 数据库规范
1.采用26个英文字母(区分大小写)和0-9的自然数(经常不需要)加上下划线'_'组成，命名简洁明确，多个单词用下划线'_'分隔  
2.全部小写命名，禁止出现大写  
3.禁止使用数据库关键字  
4.表名称不应该取得太长，一般不超过三个英文单词  
5.用单数形式表示名称  
6.表必须填写描述信息  
7.数据库字符集：utf8mb4，排序规则：utf8mb4_general_ci   
8.字段命名使用完整名称，禁止缩写  
9.表中字段是另外一张表的主键，则为表名_id  
10.能转化的最好转化，同样节约空间、提高查询性能  
11.避免使用NULL字段  
12.表必须定义主键，默认为ID，整型自增  

# Python规范
1.模块尽量使用小写命名，首字母保持小写  
2.类名使用驼峰命名风格，首字母大写  
3.函数名使用驼峰命名风格，首字母小写  
4.变量名尽量小写， 多个单词，用下划线隔开  
5.常量名全大写， 多个单词，使用下划线隔开  

# 项目规范  
```text
-app 应用模块
    -controller 控制层模块
        -response 响应数据结构化
        -schema 序列化和反序列化
    -models 模型文件夹
    -enums 枚举字段
    -views 蓝图模块
        -sys_manage 系统管理模块
    -utils 工具函数
    __init__.py 创建应用函数
    config.py 默认配置文件
    extensions.py 插件初始化
-doc 文档文件
-test 测试模块
-logs 日志文件
config.json 配置文件
manage.py 项目启动文件
requirements.txt 依赖文件
```
日志记录： 调用 `app.extensions.logger` 对象，默认输出到console和logs/目录（缓存30天）下，可配置阿里云日志服务  
注册路由： 遍历app.views目录下的 *_api.py 的模块，蓝图名以*_app 命名，后自动注册路由，示例  
```Python
from flask import Blueprint
from app.utils.api_util import Api
auth_app = Blueprint('auth', __name__, url_prefix='/api/auth')
auth_api = Api(auth_app)
```
数据库： 使用`flask_sqlalchemy`, 数据库模型调用`app.models.db`  
```text
数据库controller方法命名：
增（addXxxByXx)、删（deleteXxxByXx)、改（updateXxxByXx)、查（queryXxxByXx）、关联多表查（getXxxByXxx)、不定参数查（queryXxxByFilter)

增返回创建的ID、删返回空（异常直接抛出）、改返回空（异常抛出）、查（返回数据库对象）  
示例：  
@staticmethod
@clearcache
def addBusinessLead(new_lead: BusinessLead) -> str:
    exist = BusinessLeadController.queryBusinessLeadById(new_lead.id)
    if exist:
        raise AppException("创建失败，线索ID已创建")

    db.session.add(new_lead)
    db.session.commit()

    return new_lead.id
```
生成模型命令：  `flask-sqlacodegen "$sql_url" --flask --tables sys_user --outfile app/models/temp.py`  
权限设计： [Casbin RBAC](https://casbin.org/zh/docs/get-started), 模型：[casbin_model.conf](app/utils/conf/casbin_model.conf), 策略数据库： pymysql://$url/techadmin.casbin
缓存方式： 本地静态cache（加快查询速度，本地） + 数据库缓存（持久层数据，变更频率低） + 系统session（系统会话数据，外部redis） + 自定义（外部redis）。   
```text
1.系统静态cache通过调用`app.extensions.cache`  
2.数据库缓存(key models:{models}:$arg...) 在数据库查询函数添加装饰器 `@cacheable`（models—>json），返回models对象 
3.系统session调用 `flask.seesion`  
4.自定义redis缓存通过 `app.extensions.redis_client`
```
请求参数： 使用[flask_restful.reqparse.RequestParser](https://flask-restful.readthedocs.io/en/latest/reqparse.html)，示例
```Python
from flask_restful.reqparse import RequestParser
parser = RequestParser()
parser.add_argument('subsystem', location='args', type=str, nullable=True, required=True)
```  
接口swagger: [techadmin.json](doc/swagger/techadmin.json), 访问`/doc/swagger`接口查看  
响应结构：配置在`app.controllers.response`中， 接口函数中使用@marsh_response结构化响应数据  



