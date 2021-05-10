# -*- coding:utf-8 -*-
import time

from lxml import etree
from weiyi.hospital import Base


class DoctorInfo(Base):
    def __init__(self):
        super().__init__()
        self.data.clear()

    def load_link_from_mongo(self):
        for data in self.doctor_link_cache.find():
            yield data

    def remove_link_from_mongo(self, data):
        self.data.clear()
        self.department_link_cache.delete_one(data)

    def get_doctor_info(self, url):
        html = self.get_one_page(url)
        doc = etree.HTML(html)
        self.data['_id'] = url
        self.data['hospital'] = ''.join(doc.xpath('//*[@id="g-breadcrumb"]/a[4]/text()')).strip()
        self.data['department'] = ''.join(doc.xpath('//*[@id="g-breadcrumb"]/a[5]/text()')).strip()
        self.data['name'] = ''.join(doc.xpath('//*[@id="g-cfg"]/div[2]/div/div[1]/div[2]/h1/strong/text()')).strip()
        self.data['title'] = ''.join(doc.xpath('//*[@id="g-cfg"]/div[2]/div/div[1]/div[2]/h1/span/text()')).strip()
        self.data['keywords'] = ''.join(doc.xpath('//*[@id="g-cfg"]//div[@class="keys"]/a/text()')).strip()
        self.data['good_at'] = ''.join(doc.xpath('//*[@id="expertFeature"]/@value')).strip()
        self.data['intro'] = ''.join(doc.xpath('//*[@id="g-cfg"]//div[@class="about"]/span/p/text()')).strip()
        self.data['visit_departments'] = [''.join(item.xpath('.//text()')).strip() for item in
                                          doc.xpath('//*[@id="card-hospital"]/div/p')]

    def start(self):
        for data in self.load_link_from_mongo():
            self.get_doctor_info(data['_id'])
            self.save_to_mongo(self.weiyi_doctor)
            self.remove_link_from_mongo(data)
            time.sleep(1)


if __name__ == '__main__':
    url = 'https://www.guahao.com/expert/125982907829083000'
    instance = DoctorInfo()
    instance.get_doctor_info(url)
