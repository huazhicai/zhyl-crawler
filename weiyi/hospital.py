# -*- coding:utf-8 -*-
from lxml import etree
import requests
from math import ceil
from requests.exceptions import RequestException
from urllib.parse import quote
from pymongo import MongoClient
from fake_useragent import UserAgent
import time
from datetime import datetime
from utils.logger import getLogger
from weiyi.config.config import MONGO_HOST, MONGO_DB

ua = UserAgent()
HEADERS = {'User-Agent': ua.random}
logger = getLogger('hospital')


class Base(object):
    def __init__(self):
        super().__init__()

        mongo_client = MongoClient(MONGO_HOST)
        db = mongo_client[MONGO_DB]

        self.weiyi_hospital = db['weiyi_hospital']
        self.hospital_link_cache = db['hospital_link_cache']
        self.weiyi_department = db['weiyi_department']
        self.department_link_cache = db['department_link_cache']
        self.weiyi_doctor = db['weiyi_doctor']
        self.doctor_link_cache = db['doctor_link_cache']

        self.host = 'https://www.guahao.com'
        self.data = {}

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = super(Base, cls).__new__(cls)
        return cls._instance

    def init(self):
        pass

    def add_update_time(self):
        now = datetime.now()
        update_time = now.strftime('%Y-%m-%d %H:%M:%S')
        self.data['update_time'] = update_time

    def get_one_page(self, url):
        try:
            time.sleep(1)  # 减缓爬取速度，防止ip
            # print(url)
            response = requests.get(url, headers=HEADERS)
            if response.status_code == 200:
                return response.text
            logger.warning(f'error{url}, {response.status_code}')
            return ''
        except RequestException as e:
            logger.warning(e)
            return ''

    def save_to_mongo(self, collection):
        try:
            collection.update_one({'_id': self.data['_id']}, {'$set': self.data}, upsert=True)
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
        for province in provinces.json()[:-2]:   # 去除香港澳门
            if not province['value'].isdigit(): continue
            citys_url = self.host + '/json/white/area/citys?provinceId={}'.format(province['value'])
            citys = requests.get(citys_url, headers=HEADERS).json()
            for city in citys:
                if not city['value'].isdigit(): continue
                url = self.host + f'/hospital/{province["value"]}/{quote(province["text"])}/{city["value"]}/{quote(city["text"])}'
                yield url

    def get_total_pages(self, url):
        """获取城市医院列表总页数"""
        html = self.get_one_page(url)
        doc = etree.HTML(html)
        hospital_total = doc.xpath('//*[@id="J_ResultNum"]/text()')
        if not hospital_total: 
            logger.waring(f'get total pages error: {url}')
            pages = 1
        else:
            pages = ceil(eval(hospital_total[0]) / 10)
        return pages

    def get_hospital_link(self, url):
        """获取索引页面医院的链接"""
        html = self.get_one_page(url)
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


class HospitalInfo(Base):
    def __init__(self):
        super().__init__()
        self.section_links = []
        self.data.clear()

    def get_departments(self, doc):
        items = doc.xpath('//*[@id="departments"]/div[2]/ul/li')
        departments = []
        for item in items:
            department = ''.join(item.xpath('./label/text()')).strip()
            sections = [{'section_name': ''.join(section.xpath('./a/text()')).strip(),
                         'section_link': ''.join(section.xpath('./a/@href')).strip(),
                         'doctor_num': ''.join(section.xpath('./em/text()')).strip()}
                        for section in item.xpath('./p/span')]
            self.section_links.extend(item.xpath('./p/span/a/@href'))
            departments.append({
                'department': department,
                'sections': sections
            })
        self.data['departments'] = departments

    def get_hospital_info(self, url):
        html = self.get_one_page(url)
        doc = etree.HTML(html)
        self.get_departments(doc)
        p = lambda x: ''.join(doc.xpath(x)).strip()
        self.data['hospital'] = p('//*[@id="g-cfg"]/div[2]/section/div[1]/div[2]/h1/strong/a/text()')
        self.data['province'] = p('//*[@id="g-breadcrumb"]/a[2]/text()')
        self.data['city'] = p('//*[@id="g-breadcrumb"]/a[3]/text()')
        self.data['class'] = p('//*[@id="g-cfg"]/div[2]/section/div[1]/div[2]/h1/h3[1]/span/text()')
        self.data['address'] = p('//*[@id="g-cfg"]/div[2]/section/div[1]/div[2]/div[1]/span/text()')
        self.data['phone'] = p('//*[@id="g-cfg"]/div[2]/section/div[1]/div[2]/div[2]/span/text()')
        intro_link = p('//*[@id="g-cfg"]/div[2]/section/div[1]/div[2]/div[3]/span/a/@href')
        if not intro_link:
            self.data['introduction'] = p('//*[@id="g-cfg"]/div[2]/section/div[1]/div[2]/div[3]/span/text()')
        else:
            self.data['introduction'] = self.get_hospital_introduction(intro_link)

    def get_hospital_introduction(self, url):
        html = self.get_one_page(url)
        doc = etree.HTML(html)
        introduce = ''.join(doc.xpath('//*[@id="g-cfg"]/div[3]/div/div/div/div/div/pre/text()'))
        return introduce

    def load_hospital_link_from_mongo(self):
        for data in self.hospital_link_cache.find():
            yield data

    def remove_hospital_link_from_mongo(self, data):
        for section_link in self.section_links:  # 缓存科室url
            self.department_link_cache.update_one({'_id': section_link}, {'$set': {'_id': section_link}}, upsert=True)
        self.section_links.clear()
        self.data.clear()
        self.hospital_link_cache.delete_one(data)

    def start(self):
        for data in self.load_hospital_link_from_mongo():
            self.data.update(data)
            self.get_hospital_info(data['_id'])
            self.add_update_time()
            self.save_to_mongo(self.weiyi_hospital)
            self.remove_hospital_link_from_mongo(data)


if __name__ == '__main__':
    HospitalLinkCache().start()
    instance = HospitalInfo()
    instance.start()
