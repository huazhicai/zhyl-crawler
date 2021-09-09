# -*- coding:utf-8 -*-
import requests
import time

from math import ceil
from datetime import datetime
from urllib.parse import quote
from pymongo import MongoClient
from fake_useragent import UserAgent
from pprint import pprint
from retrying import retry
from lxml import etree

from common.logger import getLogger
from weiyi.config.config import MONGO_HOST, MONGO_DB, random_ua

logger = getLogger(__name__)


def get_ua():
    try:
        return {'User-Agent': UserAgent().random}
    except:
        return {'User-Agent': random_ua()}


class Base(object):
    def __init__(self):
        super().__init__()

        mongo_client = MongoClient(MONGO_HOST)
        db = mongo_client[MONGO_DB]

        self.hospitals_col = db['weiyi_hospital']
        self.hospital_link_col = db['hospital_link']
        self.department_col = db['weiyi_department']
        self.department_link_col = db['department_link']
        self.doctor_col = db['weiyi_doctor']
        self.doctor_link_col = db['doctor_link']

        self.host = 'https://www.guahao.com'
        self.data = {}

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Base, cls).__new__(cls)
        return cls._instance

    def add_update_time(self):
        now = datetime.now()
        update_time = now.strftime('%Y-%m-%d %H:%M:%S')
        self.data['update_time'] = update_time

    @retry(stop_max_attempt_number=3, wait_random_min=1000, wait_random_max=5000)
    def _request(self, url):
        response = requests.get(url, headers=get_ua(), stream=True, timeout=5)
        if response.status_code != 200:
            raise Exception('unexpected status_code %s !' % response.status_code)
        return response.text

    def get_one_page(self, url):
        try:
            # time.sleep(random.randint(1, 2))  # 减缓爬取速度，防止ip
            time.sleep(1)  # 减缓爬取速度，防止ip
            return self._request(url)
        except Exception as e:
            logger.error(f'{url}\n{e}')
            # logger.error(f'{url}', exc_info=True)

    def save_to_mongo(self, collection):
        try:
            collection.update_one({'_id': self.data['_id']}, {'$set': self.data}, upsert=True)
            pprint(self.data)
            print('\n')
        except Exception as e:
            print(e)

    @property
    def has_hospital_link_cache(self):
        return self.hospital_link_cache.find_one()

    @property
    def has_department_link_cache(self):
        return self.department_link_cache.find_one()

    @property
    def has_doctor_link_cache(self):
        return self.doctor_link_cache.find_one()

    def has_link_cache(self):
        return self.has_hospital_link_cache or self.has_department_link_cache or self.has_doctor_link_cache


class HospitalLinkCache(Base):
    """提取医院uri存入mongo,断点续爬"""

    def __init__(self):
        super().__init__()
        self.data.clear()

    def get_province_citys(self):
        province_url = self.host + '/json/white/area/provinces'
        provinces = requests.get(province_url)
        for province in provinces.json()[:-2]:  # 去除香港澳门
            if not province['value'].isdigit(): continue
            citys_url = self.host + '/json/white/area/citys?provinceId={}'.format(province['value'])
            citys = requests.get(citys_url, headers=get_ua()).json()
            for city in citys:
                if not city['value'].isdigit(): continue
                url = self.host + f'/hospital/{province["value"]}/{quote(province["text"])}/{city["value"]}/{quote(city["text"])}'
                yield url

    def get_total_pages(self, url, pages=0):
        """获取城市医院列表总页数"""
        html = self.get_one_page(url)
        if not html: return pages
        doc = etree.HTML(html)
        hospital_total = doc.xpath('//*[@id="J_ResultNum"]/text()')
        if hospital_total:
            pages = ceil(eval(hospital_total[0]) / 10)
        return pages

    def get_hospital_link(self, url):
        """获取索引页面医院的链接"""
        html = self.get_one_page(url)
        if not html: raise Exception('get hospital link failed!')
        doc = etree.HTML(html)
        hospital_url = doc.xpath('//*[@id="g-cfg"]/div[1]/div[3]/ul/li/a/@href')
        return hospital_url

    def start(self):
        if self.has_link_cache():
            return
        logger.info('Starting!')
        for city_index_url in self.get_province_citys():
            for page in range(1, self.get_total_pages(city_index_url) + 1):
                index_url = city_index_url + f'/p{page}'
                for link in self.get_hospital_link(index_url):
                    self.data['_id'] = link
                    self.save_to_mongo(self.hospital_link_cache)
