import json
import time
import inspect
import re
import functools
import hashlib
import socket
import jwt
import datetime
import dateutil.parser

from datetime import date, timedelta, timezone
from nanoid import generate
from app.utils.api_util import AppException
from flask_restful import reqparse
from app.extensions import logger, cache


def cacheable(key, schema_class, many=False):
    """
    缓存数据库查询结果，数据库结果为列表时many=True，可根据函数参数动态设置key，参数标识$
    :param key: redis key
    :param schema_class: Marshmallow Schema
    :param many: Schema参数
    :return:
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            dynamic_key = key
            if '$' in dynamic_key:
                all_arg = re.findall(r'(?:\$(.*?)(?:\:|$))', dynamic_key)
                for arg in all_arg:
                    if arg in kwargs.keys():
                        if not isinstance(kwargs.get(arg), str):
                            continue
                        dynamic_key = dynamic_key.replace(f'${arg}', kwargs.get(arg))
                    else:
                        func_args = inspect.getfullargspec(func).args
                        args_value = args[func_args.index(arg)]
                        if not isinstance(args_value, str):
                            continue
                        dynamic_key = dynamic_key.replace(f'${arg}', args_value)
            if '$' in dynamic_key:
                res = func(*args, **kwargs)
            else:
                if schema_class == 'json':
                    val = cache.get(dynamic_key)
                    if val:
                        if val == 'NONE':
                            res = None
                        elif val == 'NONE_LIST':
                            res = []
                        else:
                            res = json.loads(val)
                    else:
                        res = func(*args, **kwargs)
                        if res:
                            cache.set(dynamic_key, json.dumps(res, ensure_ascii=False))
                        else:
                            if res is None:
                                cache.set(dynamic_key, 'NONE')
                            elif isinstance(res, list):
                                cache.set(dynamic_key, 'NONE_LIST')
                else:
                    val = cache.get(dynamic_key)
                    if val:
                        if val == 'NONE':
                            res = None
                        elif val == 'NONE_LIST':
                            res = []
                        else:
                            schema = schema_class()
                            res = schema.loads(val, unknown="exclude", many=many)
                    else:
                        res = func(*args, **kwargs)
                        if res:
                            schema = schema_class()
                            cache.set(dynamic_key, schema.dumps(res, ensure_ascii=False, many=many))
                        else:
                            if res is None:
                                cache.set(dynamic_key, 'NONE')
                            elif isinstance(res, list):
                                cache.set(dynamic_key, 'NONE_LIST')

            return res
        return wrapper
    return decorator


def clearcache(func):
    """
    :return:
    """

    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        cache.clear()
        return res

    return wrapper


def extract_sn(text):
    result = []
    module_reg = re.compile(r'\d+\s.*Online\s+.*?\s+(.*?)[\s|\n]')
    sn_list = module_reg.findall(text+'\n')
    if sn_list:
        result = list(set([sn.strip() for sn in sn_list if sn.strip()]))
    return result


def prepare_args_for_parser(parser):
    """ Modifies all the args of a Parser to better defaults. """
    if not isinstance(parser, reqparse.RequestParser):
        raise ValueError('Expecting a parser')
    for arg in parser.args:
        if not arg.default:
            arg.store_missing = False
            arg.help = "Error: {error_msg}. Field description: %s" % arg.help
    return parser


def str_to_bool(value):
    if value.lower() in ['true', '1', 't', 'y', 'yes']:
        return True
    elif value.lower() in ['false', '0', 'f', 'n', 'no']:
        return False
    else:
        raise ValueError(f"Invalid boolean value: {value}")


def str_to_none(value):
    if not value:
        return None
    else:
        return value


def input_filter(value):
    filter_value = value.replace("/", "\/")
    return filter_value


def validate_null(value, name):
    if not value:
        raise AppException(f"is not null")
    return value

def is_valid_date(date_str):
    """
    校验时间是否符合'yyyy-mm-dd'格式
    """
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise AppException(message='时间格式要求为:"yyyy-mm-dd" ')

def validate_half_hour(value, name):
    if not value:
        raise AppException(f"is not null")
    if int(value) % 30 != 0:
        raise AppException(f"Illegal parameter")
    return value


def to_bool_or_none(bool_str):
    if bool_str is None:
        return None
    if bool_str.lower() == "true":
        return True
    if bool_str.lower() == "false":
        return False
    raise Exception("bool str invalid.")


def timing(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        rs = func(*args, **kwargs)
        end_time = time.time()
        logger.info("函数 %s 的执行时间为：%.6f 秒" % (func.__name__, end_time - start_time))
        return rs

    return wrapper


def nanoId():
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return generate(alphabet=alphabet, size=15)


def nanoid_iterator(unique_func, size=15):
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
    while True:
        unique_id = generate(alphabet=alphabet, size=size)
        if not unique_func(unique_id):
            yield unique_id


def numberId():
    alphabet = 'ABCDFGHJKLMNPQRSTUVWXYZ0123456789'
    return generate(alphabet=alphabet, size=10)


def getIpPort(host: str):
    try:
        pattern = r'(\d+\.\d+\.\d+\.\d+):(\d+)'
        match = re.match(pattern, host)
        ip = match.group(1)
        port = match.group(2)
        return ip, port
    except:
        return "1.1.1.1", "1"
    

def scanOpenPort(host: str, port: str):
    try:
        logger.info(f"开始探测主机{host},端口{port}的连通性")
        with socket.create_connection((host, port), timeout=1):
            logger.info(f"探测主机{host},端口{port}的连通性,连通性正常")
            return True
    except Exception as error:
        logger.info(f"探测主机{host},端口{port}的连通性,无法连通,具体参考程序报错: {error}")
        return False
    

def getMd5sum(string: str) -> str:
    md5_hash = hashlib.md5()
    md5_hash.update(string.encode('utf-8'))
    md5_hex = md5_hash.hexdigest()
    return md5_hex


def getRandomString20() -> str:
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return generate(alphabet=alphabet, size=20)

def getRandomString16() -> str:
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return generate(alphabet=alphabet, size=16)

def getRandomString10() -> str:
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return generate(alphabet=alphabet, size=10)

def getRandomNumber10() -> str:
    alphabet = '0123456789'
    return generate(alphabet=alphabet, size=10)

def getDicTicketNumberID() -> str:
    current_date = datetime.datetime.now()
    formatted_date = current_date.strftime("%y%m%d")
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    number = formatted_date + generate(alphabet=alphabet, size=4)
    return number

def getCurrentTime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def getTimeDifference(start_time, end_time) -> int:
    time_difference = end_time - start_time
    seconds_difference = int(time_difference.total_seconds())
    return seconds_difference

def seconds_to_minutes_and_seconds(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes} 分钟 {remaining_seconds} 秒"

def validate_input(input_str):
    """
    校验输入字符串是否符合仅包含英文字母和数字, 并且长度不大于10位
    """
    try:
        pattern = r'^[A-Za-z0-9_-]{1,10}$'
        if re.match(pattern, input_str):
            return True
        else:
            return False
    except:
        return False

def datetimeReducedEightHour(time_str: str, time_format: str="%Y-%m-%d %H:%M:%S") -> str:
    """
    时间格式: "2024-07-01 00:00:00" 
    """
    time_obj = datetime.datetime.strptime(time_str, time_format)
    new_time_obj = time_obj - timedelta(hours=8)
    new_time_str = new_time_obj.strftime("%Y-%m-%d %H:%M:%S")
    return new_time_str

def getNearestDatetime(time_list: list, time_format: str="%Y-%m-%dT%H:%M:%S%z", 
                       return_format: str="%Y-%m-%d %H:%M:%S") -> str:
    current_time = datetime.datetime.now(timezone.utc)
    min_time_diff = float('inf')
    nearest_time = None
    for time_str in time_list:
        time_obj = datetime.datetime.strptime(time_str, time_format)
        time_diff = abs((time_obj - current_time).total_seconds())
        if time_diff < min_time_diff:
            min_time_diff = time_diff
            nearest_time = time_obj
    return  nearest_time.strftime("%Y-%m-%d %H:%M:%S")

def getNearestDatetimeAsia(time_list: list, time_format: str="%Y-%m-%dT%H:%M:%S%z", 
                           return_format: str="%Y-%m-%d %H:%M:%S") -> str:
    current_time = datetime.datetime.now()
    min_time_diff = float('inf')
    nearest_time = None
    for time_str in time_list:
        time_obj = datetime.datetime.strptime(time_str, time_format)
        time_diff = abs((time_obj - current_time).total_seconds())
        if time_diff < min_time_diff:
            min_time_diff = time_diff
            nearest_time = time_obj
    return  nearest_time.strftime("%Y-%m-%d %H:%M:%S")

class JwtTokenAuth:
    def __init__(self, secret_key: str = "hillstone_dic_cloudlab"):
        self.secret_key = secret_key

    def generateToken(self, payload):
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        token = jwt.encode({"exp": expiration_time, **payload}, self.secret_key, algorithm="HS256")
        return token

    def verifyToken(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            if "exp" in payload and datetime.datetime.utcnow() > datetime.datetime.fromtimestamp(payload["exp"]):
                return {"error": "Token has expired"}
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

class Common:
    @staticmethod
    def parseInt(obj, default=0):
        try:
            return int(obj)
        except:
            return default

    @staticmethod
    def utc2Local(utc, gmt=8):
        if isinstance(utc, date) or isinstance(utc, datetime.datetime):
            local = utc + timedelta(hours=gmt)
            return local
        elif isinstance(utc, str):
            local = dateutil.parser.parse(utc) + timedelta(hours=gmt)
            return local
        elif isinstance(utc, int):
            if len(str(utc)) > 10:
                utc = utc / 1000
            local = datetime.datetime.utcfromtimestamp(utc) + timedelta(hours=gmt)
            return local
        else:
            return None
