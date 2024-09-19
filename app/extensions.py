import grpc

from app.config import *
from flask_debugtoolbar import DebugToolbarExtension
from flask_assets import Environment
from flask_caching import Cache
from app.utils.auth_util import JwtUtil, Passport
from app.utils.logger_util import createLogger
from app.utils.redis_util import RedisClient
from app.utils.api_util import CasbinPolicyUtil
from app.utils.aliyun import AliyunUtil
from app.utils.oss import OSSUtil, AliyunOSSUtil
from app.utils.apollo import ApolloUtil
from app.utils.http_api import *
from app.utils.ps_inspection import OFFICEUtil, ProcessingCompressionUtil
from elasticsearch import Elasticsearch
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool

grpc_channel = None
if ServerConfig.get('grpc_server'):
    grpc_server = ServerConfig.get('grpc_server')
    if grpc_server:
        grpc_channel = grpc.insecure_channel(grpc_server.get('target'))

assets_env = Environment()

debug_toolbar = DebugToolbarExtension()

redis_client = RedisClient()

cache = Cache()

jwt_util = JwtUtil(ServerConfig.get('secret') if ServerConfig.get('secret') else None)

sso_util = Passport(SsoConfig["id"], SsoConfig["secret"])

logger = createLogger(LogConfig)

permission = CasbinPolicyUtil(grpc_channel)

aliyun_util = AliyunUtil(AliyunConfig['tac_devops_etl']['access_key'], AliyunConfig['tac_devops_etl']['access_secret'])

oss_util = OSSUtil(InspurConfig['tac-ccc']['access_key'], InspurConfig['tac-ccc']['access_secret'])

oss_aliyun_util = AliyunOSSUtil(AliyunConfig['oss']['access_key'], AliyunConfig['oss']['access_secret'])

apollo_util = ApolloUtil(ApolloConfig['server_url'], ApolloConfig['app_id'])

executor = ThreadPoolExecutor(8)

message_gw = MessageGateway(TacApiConfig['server_url'])

tac_api = TacApi(TacApiConfig['server_url'])

qywx_api = QyWxApi(QyWxConfig['corp_id'], QyWxConfig['corp_secret'])

crm_api = CrmHttpAPI(CrmConfig['app_id'], CrmConfig['app_secret'], CrmConfig['server_url'])

opensearch_api = AliyunOpenSearch(OpensearchAliConfig['access_key'], OpensearchAliConfig['access_secret'])

aiask_api = AiAsk(AiAskConfig['api_key'])

es_util = Elasticsearch(
    ESConfig['hosts'], http_auth=(ESConfig['username'], ESConfig['password']),
    max_retries=3, retry_on_timeout=True,  retry_on_status=(500, 502, 503, 504)
)

es_aliyun_util = Elasticsearch(
    AliyunESConfig['hosts'], http_auth=(AliyunESConfig['username'], AliyunESConfig['password']),
    max_retries=3, retry_on_timeout=True,  retry_on_status=(500, 502, 503, 504)
)
db_engine = create_engine(SQLConfig['database'], pool_size=5,
                          pool_timeout=30, pool_pre_ping=False, pool_recycle=15*60)

cloudlab_db_engine = create_engine(SQLConfig['database'], poolclass=NullPool)

DBSession = scoped_session(sessionmaker(bind=cloudlab_db_engine))

office_util = OFFICEUtil()

procession_compression_util = ProcessingCompressionUtil()
