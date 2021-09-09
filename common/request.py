# -*- coding:utf-8 -*-
import logging
import requests
from retrying import retry

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_ua():
    from fake_useragent import UserAgent
    return {'User-Agent': UserAgent().random}


@retry(stop_max_attempt_number=4, wait_random_min=2000, wait_random_max=5000)
def request(url, mode):
    logger.info(url)
    response = requests.get(url, headers=get_ua(), timeout=10)
    if response.status_code != 200:
        raise Exception('unexpected status_code %s ' % response.status_code)
    if mode == 'json':
        return response.json()
    return response.text


def get_one_page(url, mode='text'):
    try:
        return request(url, mode)
    except Exception as e:
        logger.error(f'{url}\n{e}')
        return None
