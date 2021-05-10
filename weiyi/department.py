# -*- coding:utf-8 -*-
import time
from lxml import etree
from weiyi.hospital import Base


class DepartmentInfo(Base):
    def __init__(self):
        super().__init__()
        self.data.clear()
        self.doctors = []
        self.doctor_links = []

    def load_link_from_mongo(self):
        for data in self.department_link_cache.find():
            yield data

    def clear(self):
        self.doctor_links.clear()
        self.data.clear()
        self.doctors.clear()

    def remove_link_from_mongo(self, data):
        for doctor_link in self.doctor_links:  # 缓存医生url
            self.doctor_link_cache.update_one({'_id': doctor_link}, {'$set': {'_id': doctor_link}}, upsert=True)
        self.clear()
        self.department_link_cache.delete_one(data)

    def get_index_page_doctor_info(self, url, page=1):
        """更多医生，另一页"""
        html = self.get_one_page(url + f'?pageNo={page}')
        doc = etree.HTML(html)
        items = doc.xpath('//*[@id="g-cfg"]//div[@class="list"]/div')
        for item in items:
            self.doctors.append({'name': ''.join(item.xpath('./div[1]/dl/dt/a//text()')).strip(),
                                 'title': ''.join(item.xpath('./div[1]/dl/dt/text()')).strip(),
                                 'doctor_link': ''.join(item.xpath('./div[1]/dl/dt/a/@href')).strip(),
                                 'good_at': ''.join(item.xpath('./div[2]/text()')).strip(), })
            self.doctor_links.append(''.join(item.xpath('./div[1]/dl/dt/a/@href')).strip())

        next_page = doc.xpath('//*[@id="g-cfg"]//a[@class="next J_pageNext_gh"]/@href')
        if next_page:
            page += 1
            self.get_index_page_doctor_info(url, page)

    def get_doctor_info(self, doc):
        url = ''.join(doc.xpath('//*[@id="anchor"]/div[2]/div[12]/a/@href')).strip()
        if not url:
            items = doc.xpath('//*[@id="anchor"]/div[2]/div')
            for item in items:
                self.doctors.append({'name': ''.join(item.xpath('./dl/dt/a/text()')).strip(),
                                     'title': ''.join(item.xpath('./dl/dt/span/text()')).strip(),
                                     'doctor_link': ''.join(item.xpath('./dl/dt/a/@href')).strip(),
                                     'good_at': ''.join(item.xpath('./dl/dd/p/text()')).strip(), })
        else:
            self.get_index_page_doctor_info(url)
        self.data['doctors'] = self.doctors

    def get_department_info(self, url):
        html = self.get_one_page(url)
        doc = etree.HTML(html)
        self.data['_id'] = url
        self.data['department'] = ''.join(
            doc.xpath('//*[@id="g-cfg"]/div[1]/div[2]/div/div[1]/div/h1/strong/text()')).strip()
        introduction = doc.xpath('//*[@id="g-cfg"]/div[1]/div[2]/div/div[1]/div/div[2]/span/a/text()')
        self.get_doctor_info(doc)
        if not introduction:
            self.data['introduction'] = ''.join(
                doc.xpath('//*[@id="g-cfg"]/div[1]/div[2]/div/div[1]/div/div[2]/span/text()')).strip()
        else:
            self.data['introduction'] = ''.join(introduction).strip()

    def start(self):
        for data in self.load_link_from_mongo():
            self.get_department_info(data['_id'])
            self.save_to_mongo(self.weiyi_department)
            self.remove_link_from_mongo(data)
            time.sleep(1)


if __name__ == '__main__':
    instance = DepartmentInfo()
    url = 'https://www.guahao.com/department/2b94ac5e-2d68-4095-90ae-9790b86d5615000?isStd='
    instance.get_department_info(url)
