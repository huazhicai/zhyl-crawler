import logging
import requests
import csv
import json
from retrying import retry


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_ua():
    try:
        from fake_useragent import UserAgent
        return {'User-Agent': UserAgent().random}
    except:
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}


@retry(stop_max_attempt_number=10, wait_random_min=4000, wait_random_max=9000)
def get_request(url):
    logger.info(url)
    response = requests.get(url, headers=get_ua(), timeout=10)
    if response.status_code != 200:
        raise Exception('unexpected status_code %s ' % response.status_code)
    return response.json()


def get_one_page(url):
    try:
        return get_request(url)
    except Exception as e:
        logger.error(f'{url}\n{e}')
        return []


def csv_reader(file):
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            yield row


def write_row_csv(filename, row, mode='a', newline=''):
    with open(filename, mode, newline=newline, encoding='utf-8') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(row)


def write_rows_csv(filename, rows, mode='a', newline=''):
    with open(filename, mode, newline=newline, encoding='utf-8') as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(rows)


def load_json(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def dump_json(file, doc):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(f, doc, ensure_ascii=False)


def has_letter(word):
    import re
    return re.search(r'[a-zA-Z]', word)


def reader(file):
    with open(file, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            yield line
