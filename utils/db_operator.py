# -*- coding:utf-8 -*-
from utils import logger
from utils.tools import singleton
from pymongo import MongoClient

logger = logger.getLogger('db_operator')


@singleton
class HandleMongo(object):
    def __init__(self, host=None, db=None):
        assert host and db
        self.host = host
        self._db = db
        self.client = None
        self.db = None

    def connect(self):
        try:
            self.client = MongoClient(self.host)
            self.db = self.client[self._db]
        except:
            logger.error('Server not available, Check your uri!')

    def get_state(self):
        return self.client is not None and self.db is not None

    def check_state(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.get_state():
                return func(*args, **kwargs)
            else:
                self.connect()
                return func(*args, **kwargs)

        return wrapper

    @reconnect
    def insert_one(self, collection, document):
        ret = self.db[collection].insert_one(document)
        return ret.inserted_id

    @reconnect
    def insert_many(self, collection, document):
        ret = self.db[collection].insert_many(document)
        return ret.inserted_id

    @reconnect
    def find_one(self, collection, condition=None, data_field=None):
        if data_field:
            ret = self.db[collection].find_one(condition, data_field)
        else:
            ret = self.db[collection].find_one(condition)
        return ret

    @reconnect
    def find(self, collection, condition, column=None):
        if column is None:
            return self.db[collection].find(condition)
        else:
            return self.db[collection].find(condition, column)

    @reconnect
    def update_one(self, collection, condition, data, upsert=True):
        try:
            self.db[collection].update_one(condition, {'$set': data}, upsert=upsert)
        except:
            logger.warning('update fail!')

    @reconnect
    def update_many(self, collection, document, data_set):
        ret = self.db[collection].update_many(document, data_set)
        return ret

    def close(self):
        if self.db:
            self.db.client.close()
            self.db = None
