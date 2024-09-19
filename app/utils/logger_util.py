import logging
import logging.config
import os

LogsDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../logs')
LogPath = os.path.join(LogsDir, 'runlog.log')


LoggingDic = {
    'version': 1,
    'formatters': {
        'rawformatter': {
            'format': '%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d : %(message)s'
        },
        'aliyunformatter': {
            'format': '%(message)s'
        }
    },
    'handlers': {
        'console_streamHandler': {
            'class': 'logging.StreamHandler',
            'formatter': 'rawformatter',
            'stream': 'ext://sys.stdout'
        },
        'console_fileHandler': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'rawformatter',
            'filename': LogPath,
            'interval':  1,
            'when': 'D',
            'backupCount': 30,
            'encoding': 'utf8'
        }
    },
    'loggers': {}
}


class FileFilter(logging.Filter):
    def filter(self, record):
        if record.filename in ['role_manager.py']:
            return False
        return True


def createLogger(log_config, name='root'):
    if not os.path.isdir(LogsDir):
        os.mkdir(LogsDir)

    LoggingDic['loggers'][name] = {
        'handlers': ["console_streamHandler", "console_fileHandler"],
        'level': log_config.get('level') if log_config.get('level') else 'DEBUG',
        'propagate': True
    }

    if 'aliyun_sls' in log_config:
        aliyun_sys = log_config['aliyun_sls']
        LoggingDic['handlers']['sls_handler'] = {
            '()': 'aliyun.log.QueuedLogHandler',
            'formatter': 'aliyunformatter',
            'end_point': aliyun_sys['end_point'],
            'access_key_id': aliyun_sys['access_key_id'],
            'access_key': aliyun_sys['access_key'],
            'project': aliyun_sys['project'],
            'log_store': aliyun_sys['log_store']
        }
        LoggingDic['loggers'][name]['handlers'].append('sls_handler')

    logging.config.dictConfig(LoggingDic)
    logging.getLogger('netmiko').setLevel(logging.ERROR)
    logging.getLogger('paramiko').setLevel(logging.ERROR)
    logging.getLogger('paramiko.transport').setLevel(logging.ERROR)
    app_logger = logging.getLogger(name)

    return app_logger
