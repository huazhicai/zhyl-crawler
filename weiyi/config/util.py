# -*- coding:utf-8 -*-
from pprint import pprint

from pymongo import MongoClient


def parse_url(url):
    if '?' in url:
        i = url.index('?')
        return url[:i]
    else:
        return url


def clean_url():
    collection = db['doctor_link_cache']
    for data in collection.find():
        data['_id'] = parse_url(data['_id'])
        new_col.update_one({'_id': data['_id']}, {'$set': data}, upsert=True)
        print(data)


def connect():
    for data in collection.find():
        _id = data['_id']
        clean_data(data)
        collection.delete_one({'_id': _id})


def clean_data(data):
    import re
    try:
        data['_id'] = parse_url(data['_id'])
        pattern = re.compile('[\t\n\r\s]+')
        data['keywords'] = re.sub(pattern, ',', data['keywords'])
        new = [re.sub(pattern, '', ele) for ele in data['visit_departments']]
        data['visit_departments'] = new
        data['introduction'] = data['introduction'].strip('<p>').strip('</p>')
    except Exception as e:
        print(e)


def update_data(doc, collection):
    collection.update_one({'_id': doc['_id']}, {'$set': doc}, upsert=True)


def get_doctor_link():
    col = db.weiyi_department
    new_col = db.new_url
    for data in col.find():
        for ele in data['doctors']:
            doc = {'_id': parse_url(ele['doctor_link'])}
            new_col.update_one(doc, {'$set': doc}, upsert=True)
            print(doc)


if __name__ == '__main__':
    client = MongoClient('10.0.108.14:27017')
    db = client.web_crawler_aiit_zhyl
    # collection = db.weiyi_doctor
    collection = db.weiyi_doctor
    new_col = db.new_url

    # clean_url()
    # connect()
    get_doctor_link()
