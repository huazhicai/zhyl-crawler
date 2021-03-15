# -*- coding:utf-8 -*-
import cchardet
from retrying import retry
from requests import request, RequestException

from config.user_agent import get_ua
from logger import getLogger

logger = getLogger('component')


@retry(stop_max_attempt_number=3, retry_on_result=lambda x: x is None, wait_fixed=2000)
def downloader(url, method=None, header=None, timeout=None, binary=False, **kwargs):
    logger.info(f'Scraping {url}')
    _header = {'User-Agent': get_ua()}
    _maxTimeout = timeout if timeout else 3
    _headers = header if header else _header
    _method = "GET" if not method else method
    try:
        response = request(method=_method, url=url, headers=_headers, **kwargs)
        encoding = cchardet.detect(response.content)['encoding']
        if response.status_code == 200:
            return response.content if binary else response.content.decode(encoding)
        elif 200 < response.status_code < 400:
            logger.info(f"Redirect_URL: {response.url}")
        logger.error('Get invalid status code %s while scraping %s', response.status_code, url)
    except RequestException as e:
        logger.error(f'Error occurred while scraping {url}, Msg: {e}', exc_info=True)


if __name__ == '__main__':
    print(downloader("https://www.baidu.com/", "GET"))
