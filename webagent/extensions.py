from webagent.config import *
from webagent.utils.logger_util import createLogger
from redis import StrictRedis

redis_client = StrictRedis(
    host=RedisConfig["host"],
    port=RedisConfig.get("port") if RedisConfig.get("port") else 6379,
    password=RedisConfig["password"]
)

logger = createLogger(LogConfig)