import os
import json
import redis

from datetime import timedelta

abspath = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(abspath, '../config/config.json'), 'r', encoding="utf-8") as f:
    Config = json.load(f)

ServerConfig = Config['server']
AliyunConfig = Config['aliyun']
InspurConfig = Config['inspur']
SQLConfig = ServerConfig['sql']
SessionConfig = ServerConfig['session']
SsoConfig = ServerConfig['sso']
LogConfig = ServerConfig['log']
RedisConfig = ServerConfig['redis']
ESConfig = Config['elasticsearch']
AliyunESConfig = Config['elasticsearch_aliyun']
ApolloConfig = Config['apollo']
CrmConfig = Config['crm']
TacApiConfig = Config['tac_api']
KvmConfig = Config['kvm']
KafkaConfig = Config['kafka']
EmailConfig = Config['email']
StConfig = Config['st']
OtherConfig = Config['other']
QyWxConfig = Config['qywx']
OpensearchAliConfig = Config['opensearch_ali']
AiAskConfig = Config["aiask"]


class Config(object):
    TEMPLATES_AUTO_RELOAD = True
    JSON_AS_ASCII = False
    ASSETS_DEBUG = True
    LOG_LEVEL = "DEBUG"
    SITE_DOMAIN = "linktest.hillstonenet.com"
    API_DOMAIN = "linkapitest.tac.hillstonenet.com"
    TRACE_ENDPOINT = "http://tracing-analysis-dc-sh.aliyuncs.com/adapt_c1w9rriv36@abcd270e26d717e_c1w9rriv36@53df7ad2afe8301/api/otlp/traces"
    SECRET_KEY = ServerConfig.get('secret') if ServerConfig.get('secret') else os.urandom(24)

    # 数据库链接配置: 数据类型://登录账号:登录密码@数据库主机IP:数据库访问端口/数据库名称
    if 'database' in SQLConfig:
        SQLALCHEMY_DATABASE_URI = SQLConfig['database']
    if 'binds' in SQLConfig:
        SQLALCHEMY_BINDS = SQLConfig['binds']

    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    # 设置mysql的错误跟踪信息显示
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 打印每次模型操作对应的SQL语句
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 15,
        'max_overflow': 5,
        'pool_timeout': 10,
        'pool_recycle': 2*3600,
        'pool_pre_ping': True
    }

    if 'cache' in RedisConfig:
        CACHE_TYPE = RedisConfig['cache']['type'] if RedisConfig['cache'].get('type') else 'simple'
        if CACHE_TYPE == 'redis':
            CACHE_DEFAULT_TIMEOUT = 3600*12
            CACHE_REDIS_HOST = '127.0.0.1'
            CACHE_KEY_PREFIX = "techadmin:cache:"

    if 'session' in RedisConfig:
        # 服务器session缓存
        SESSION_TYPE = "redis"
        SESSION_REDIS_HOST = RedisConfig['session']['host']
        SESSION_REDIS_PORT = RedisConfig['session']['port'] if RedisConfig['session'].get('port') else 6379
        SESSION_REDIS_PASSWORD = RedisConfig['session']['password'] if RedisConfig['session'].get('password') else None
        # 如果设置session的生命周期是否是会话期, 为True，则关闭浏览器session就失效
        SESSION_PERMANENT = False
        PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
        # 是否对发送到浏览器上session的cookie值进行加密
        SESSION_USE_SIGNER = False
        # 保存到redis的session数的名称前缀
        SESSION_KEY_PREFIX = "techadmin:session:"
        # session保存数据到redis时启用的链接对象
        SESSION_REDIS = redis.Redis(
            host=SESSION_REDIS_HOST, port=SESSION_REDIS_PORT, password=SESSION_REDIS_PASSWORD, db=1
        )

    if 'global' in RedisConfig:
        SERVER_REDIS_HOST = RedisConfig['global'].get('host')
        SERVER_REDIS_PORT = RedisConfig['global'].get('port') if RedisConfig['global'].get('port') else 6379
        SERVER_REDIS_PASSWORD = RedisConfig['global'].get('password') if RedisConfig['global'].get('password') else None


class ProdConfig(Config):
    ENV = 'prod'
    SITE_DOMAIN = "link.hillstonenet.com"
    API_DOMAIN = "linkapi.hillstonenet.com"
    DISABLEPATH = ['ping_api.py', 'conversion_api.py']


class DevConfig(Config):
    with open(os.path.join(abspath, '../doc/swagger/techadmin.json'), 'r', encoding="utf-8") as f:
        techadmin_swagger = json.load(f)

    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PROFILER_ENABLED = True
    ENV = 'dev'
    DEBUG = True
    SWAGGER_CONFIG = {
        "headers": [],
        "specs": [{
            "endpoint": 'apispec_1',
            "route": '/techadmin.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }],
        "static_url_path": "/flasgger_static",
        # "static_folder": "static",  # must be set by user
        "swagger_ui": True,
        "specs_route": "/doc/swagger",
        "tags": techadmin_swagger['tags'],
        "openapi": techadmin_swagger['openapi'],
        "info": techadmin_swagger['info'],
        "paths": techadmin_swagger['paths']
    }


class TestConfig(Config):
    ENV = 'test'
    DEBUG = True
    TESTTING = True
    WTF_CSRF_ENABLED = False
