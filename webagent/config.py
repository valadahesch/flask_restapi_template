import os
import json

abspath = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(abspath, '../config/config.json'), 'r', encoding="utf-8") as f:
    Config = json.load(f)

ServerConfig = Config['server']
RedisConfig = ServerConfig['redis']["global"]
LogConfig = ServerConfig['log']