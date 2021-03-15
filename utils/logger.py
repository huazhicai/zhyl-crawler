# -*- coding: utf-8 -*-
import logging, os
import logging.config

output_list = ['file', 'console', 'error_handler']

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%Y-%m-%d %H:%M:%S"
        },
        'simple': {
            # 'format': '%(levelname)s %(message)s'
            'format': '[%(name)s:%(lineno)s] %(levelname)s  %(message)s'
        },
        'error_format': {
            'format': '[%(name)s:%(lineno)s] %(levelname)s  %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            # 如果没有使用并发的日志处理类，在多实例的情况下日志会出现缺失, some problem
            # 'class': 'cloghandler.ConcurrentRotatingFileHandler',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 30,
            'delay': True,
            'filename': os.path.join(os.path.dirname(__file__), 'log/project_log.txt'),

            'formatter': 'verbose'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            # 'formatter': 'simple',
            'stream': 'ext://sys.stdout',
        },
        "error_handler": {
            "class": "logging.StreamHandler",
            "level": 'ERROR',
            "formatter": "error_format",
            "stream": "ext://sys.stderr"
        }
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file', 'error_handler'],
            'level': 'DEBUG'
        },
    }
})


def getLogger(module_name):
    return logging.getLogger(module_name)
