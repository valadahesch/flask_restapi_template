import logging
import logging.config
import os

LogsDir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../logs')
LogPath = os.path.join(LogsDir, 'webagent.log')


LoggingDic = {
    'version': 1,
    'formatters': {
        'rawformatter': {
            'format': '%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d : %(message)s'
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


def createLogger(log_config, name='root'):
    if not os.path.isdir(LogsDir):
        os.mkdir(LogsDir)

    LoggingDic['loggers'][name] = {
        'handlers': ["console_streamHandler", "console_fileHandler"],
        'level': log_config.get('level') if log_config.get('level') else 'DEBUG',
        'propagate': True
    }

    logging.config.dictConfig(LoggingDic)
    app_logger = logging.getLogger(name)
    return app_logger
