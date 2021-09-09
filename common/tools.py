# -*- coding:utf-8 -*-


_formats = {
    'y-m-d': '{d.year}-{d.month}-{d.day}',
    'y/m/d': '{d.year}/{d.month}/{d.day}',
    'nyr': '{d.year}年{d.month}月{d.day}日'
}


class Date(object):
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day

    def __format__(self, code):
        if code == '':
            code = 'y-m-d'
        fmt = _formats[code]
        return fmt.format(d=self)


def singleton(cls):
    _instance = {}

    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton


def timethis(func):
    import time
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, (end - start)/60)
        return result

    return wrapper
