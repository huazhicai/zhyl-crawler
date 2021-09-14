# -*- coding: utf-8 -*-
import sys
import logging
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from .handlers import ProcessRotatingFileHandler

SizeRotate = 1
TimedRotate = 2
ProcessRotate = 3

stream_handler = None
file_handlers = {}

all_loggers = set()


def _ensure_formatter(formatter, debug):
    if formatter is None:
        if debug:
            formatter = logging.Formatter('%(asctime)s - %(filename)s(line:%(lineo)d) - %(levelname)s : %(message)s')
        else:
            formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s : %(message)s')
    return formatter


def _get_file_handler(filename, rotate_type):
    global file_handlers
    if filename not in file_handlers:
        if rotate_type == SizeRotate:
            file_handler = RotatingFileHandler(filename, maxBytes=10 * 1024 * 1024, backupCount=9)
        elif rotate_type == TimedRotate:
            file_handler = TimedRotatingFileHandler(filename, when='midnight', interval=1, backupCount=9)
        elif rotate_type == ProcessRotate:
            file_handler = ProcessRotatingFileHandler(filename, encoding='utf-8')
        else:
            raise TypeError('rotate type error %s' % rotate_type)
    else:
        file_handler = file_handlers.get(filename)
    return file_handler


def get_logger(module_name, filename=None, rotate_type=SizeRotate, level=logging.INFO, formatter=None, debug=False):
    logger = logging.getLogger(module_name)
    all_loggers.add(logger)
    logger.setLevel(level)

    formatter = _ensure_formatter(formatter, debug)

    global stream_handler
    if stream_handler is None:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if filename:
        file_handler = _get_file_handler(filename, rotate_type)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_time_rotate_logger(module_name, filename, level=logging.INFO, formatter=None, debug=False):
    return get_logger(module_name, filename, TimedRotate, level, formatter, debug)


def get_process_rotate_logger(module_name, filename, level=logging.INFO, formatter=None, debug=False):
    return get_logger(module_name, filename, ProcessRotate, level, formatter, debug)