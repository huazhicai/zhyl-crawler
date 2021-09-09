# -*- coding:utf-8 -*-
from lxml import etree

from weiyi.link_cache import Base


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
        if not html: return
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
        if not html: return
        doc = etree.HTML(html)
        introduce = ''.join(doc.xpath('//*[@id="g-cfg"]/div[3]/div/div/div/div/div/pre/text()'))
        return introduce

    def load_hospital_link(self):
        for data in self.hospital_link_col.find():
            yield data

    def save_departments_link(self):
        for section_link in self.section_links:  # 缓存科室url
            self.department_link_col.update_one({'_id': section_link}, {'$set': {'_id': section_link}}, upsert=True)
        self.section_links.clear()

    def remove_hospital_link(self, data):
        for section_link in self.section_links:  # 缓存科室url
            self.department_link_col.update_one({'_id': section_link}, {'$set': {'_id': section_link}}, upsert=True)
        self.section_links.clear()
        self.data.clear()
        self.hospital_link_col.delete_one(data)

    def update_one(self, url):
        self.data['_id'] = url
        self.get_hospital_info(url)
        self.add_update_time()
        self.save_to_mongo(self.hospitals_col)

    def start(self, url=None):
        # logger.info('Start HospitalInfo')
        for data in self.load_hospital_link():
            self.data['_id'] = data['_id']
            self.get_hospital_info(data['_id'])
            self.add_update_time()
            self.save_to_mongo(self.hospitals_col)
            self.remove_hospital_link(data)


if __name__ == '__main__':
    # HospitalLinkCache().start()
    instance = HospitalInfo()
    instance.start()
