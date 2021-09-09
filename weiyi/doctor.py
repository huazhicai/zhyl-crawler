# -*- coding:utf-8 -*-
from lxml import etree

from weiyi.deduplicate import clean_data
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
        self.doctor_link_cache.delete_one(data)

    def get_doctor_info(self, url):
        html = self.get_one_page(url)
        if not html: return
        doc = etree.HTML(html)
        p = lambda x: ''.join(doc.xpath(x)).strip()
        self.data['_id'] = url
        self.data['hospital'] = p('//*[@id="g-breadcrumb"]/a[4]/text()')
        # self.data['department'] = p('//*[@id="g-breadcrumb"]/a[5]/text()')
        self.data['name'] = p('//*[@id="g-cfg"]/div[2]/div/div[1]/div[2]/h1/strong/text()')
        self.data['title'] = p('//*[@id="g-cfg"]/div[2]/div/div[1]/div[2]/h1/span/text()')
        self.data['keywords'] = p('//*[@id="g-cfg"]//div[@class="keys"]/a/text()')
        self.data['good_at'] = p('//*[@id="expertFeature"]/@value')
        self.data['introduction'] = p('//*[@id="g-cfg"]//div[@class="about"]/input/@value')
        self.data['visit_departments'] = [''.join(item.xpath('.//text()')).strip() for item in
                                          doc.xpath('//*[@id="card-hospital"]/div/p')]
        clean_data(self.data)

    def update_one(self, url):
        self.data['_id'] = url
        self.get_doctor_info(url)
        self.add_update_time()
        self.save_to_mongo(self.weiyi_doctor)

    def start(self):
        for data in self.load_link_from_mongo():
            try:
                self.get_doctor_info(data['_id'])
            except Exception as e:
                print(e)

            self.add_update_time()
            self.save_to_mongo(self.weiyi_doctor)
            try:
                self.remove_link_from_mongo(data)
            except Exception as e:
                print(e)


if __name__ == '__main__':
    url = 'https://www.guahao.com/expert/125982907829083000'
    instance = DoctorInfo()
    instance.get_doctor_info(url)
