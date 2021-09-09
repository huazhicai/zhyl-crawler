# coding: utf-8
from concurrent.futures.thread import ThreadPoolExecutor
import json
from lxml.etree import HTML
from utils import get_one_page


class ICDItem:
    def __init__(self, item):
        self._id = item['ID']
        self.name = self.parser(item['html'])
        self.is_adopted_child = item['isAdoptedChild']
        self.is_leaf = item['isLeaf']

        self.children = {}
        self.leaf = []
        # self.icode = ''

        if not self.is_leaf:
            self.get_children()

    def parser(self, html):
        doc = HTML(html)
        self.icode = ''.join(doc.xpath('//span/text()'))
        ele = ''.join(doc.xpath('//a/text()')).strip()
        if self.icode:
            return self.icode + ' ' + ele
        return ele

    def get_children(self):
        url = child_url.format(self._id)
        children = get_one_page(url)
        for ele in children:
            child = ICDItem(ele)
            if child.is_leaf:
                self.leaf.append(child.export())
            else:
                self.children.update(child.export())

    def export(self):
        if self.is_leaf:
            return self.name
        if self.leaf:
            return {self.name: self.leaf}
        return {self.name: self.children}


def start(item):
    result.append(ICDItem(dict(item)))


def sort_result():
    new_doc = {}
    ret = sorted(result, key=lambda x: x.icode)
    for item in ret:
        new_doc.update(item.export())
    return new_doc


def save_to_json(data):
    with open(save_as, 'w') as f:
        json.dump(data, f)


def main(url):
    global result
    result = []
    data = get_one_page(url)
    with ThreadPoolExecutor(thread_num) as executor:
        for item in data:
            args = ((key, value) for key, value in item.items())
            executor.submit(start, args)
    sort_data = sort_result()
    save_to_json(sort_data)


if __name__ == '__main__':
    thread_num = 3  # 大于4就有401
    # icd_10
    # root_url = 'https://icd.who.int/browse10/2019/en/JsonGetRootConcepts?useHtml=true'
    # child_url = 'https://icd.who.int/browse10/2019/en/JsonGetChildrenConcepts?ConceptId={}&useHtml=true&showAdoptedChildren=true'
    # save_as = 'file/icd_2019.json'

    # icd_11
    root_url = 'https://icd.who.int/browse11/l-m/en/JsonGetRootConcepts?useHtml=true'
    child_url = 'https://icd.who.int/browse11/l-m/en/JsonGetChildrenConcepts?ConceptId={}&useHtml=true&showAdoptedChildren=true'
    save_as = 'file/icd_11.json'

    main(root_url)
