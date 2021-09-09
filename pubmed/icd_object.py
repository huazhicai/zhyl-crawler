from lxml.etree import HTML
from icd_crawler import get_one_page


class ICDItem:
    def __init__(self, item):
        self._id = item['ID']
        self.name = self.parser(item['html'])
        self.is_adopted_child = item['isAdoptedChild']
        self.is_leaf = item['isLeaf']

        self.children = {}
        self.leaf = []

        if not self.is_leaf:
            self.get_children()

    def parser(self, html):
        doc = HTML(html)
        ele = ''.join(doc.xpath('//a/text()')).strip()
        return self._id + ' ' + ele

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



