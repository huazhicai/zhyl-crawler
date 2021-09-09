import logging
from pprint import pprint

import requests
from concurrent.futures import ThreadPoolExecutor
from lxml import etree
from retrying import retry

from config import user_agent, random_ua

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_ua():
    # try:
    #     from fake_useragent import UserAgent
    #     return {'User-Agent': UserAgent().random}
    # except:
    return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}


@retry(stop_max_attempt_number=5, wait_random_min=3000, wait_random_max=5000)
def get_request(url):
    logger.info(url)
    response = requests.get(url, headers=get_ua(), timeout=10)
    if response.status_code != 200:
        raise Exception('unexpected status_code %s ' % response.status_code)
    # logger.info('post success')
    return response.json()


def get_one_page(url):
    try:
        return get_request(url)
    except Exception as e:
        logger.error(f'{url}\n{e}')
        return []


def get_children(ele):
    if ele['isLeaf']:
        return parser(ele['html'])
    children_item = get_one_page(leaf_url.format(ele['ID']))
    doc_ele = {}
    list_ele = []
    for item in children_item:
        children = get_children(item)
        if isinstance(children, dict):
            doc_ele.update(children)
        else:
            list_ele.append(children)
    return doc_ele or list_ele


def parser(html):
    doc = etree.HTML(html)
    _id = ''.join(doc.xpath('//a/@data-id')).strip()
    ele = ''.join(doc.xpath('//a/text()')).strip()
    return _id + ele


def main(url):
    result = {}
    data = get_one_page(url)
    # with ThreadPoolExecutor(thread_num) as executor:
    # for item in data:
    #     result.update({parser(item['html']): ICDItem(item)})
    #     break

    pprint(result)


if __name__ == '__main__':
    # url = 'https://icd.who.int/browse10/2019/en#/I'
    # thread_num = 2
    # url = 'https://icd.who.int/browse10/2019/en/JsonGetRootConcepts?useHtml=true'
    leaf_url = 'https://icd.who.int/browse10/2019/en/JsonGetChildrenConcepts?ConceptId={}&useHtml=true&showAdoptedChildren=true'
    # main(url)

    print(parser(''))
