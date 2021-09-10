# coding=utf-8
import http.client
import hashlib
import urllib
import random
import json
import os
import requests
from retrying import retry
from queue import Queue
from common.data_stream import csv_reader, write_row_csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from common.tools import timethis
from utils import has_letter


appid = '20210901000932905'  # 濉啓浣犵殑appid
secretKey = 'XBRtzLpsN4fd0iMARa7o'  # 濉啓浣犵殑瀵嗛挜
headers = {'Content-Type': 'application/x-www-form-urlencoded'}

salt = random.randint(32768, 65536)
NOUNS_Q = Queue()
finish_single = object()
SRC_FILE = 'new/nouns.csv'
DEST_FILE = 'new/translation.csv'


def load_nouns():
    saved_nouns = set()
    if os.path.exists(DEST_FILE):
        saved_nouns = {row[0].lower() for row in csv_reader(DEST_FILE)}

    for row in csv_reader(SRC_FILE):
        noun = row[3].lower().strip()
        if noun not in saved_nouns:
            NOUNS_Q.put(row[3].lower().strip())


@retry(stop_max_attempt_number=4, wait_random_min=2000, wait_random_max=6000)
def vertical_translate(q, fromLang='en', toLang='zh', domain='medicine'):
    httpClient = None
    myurl = '/api/trans/vip/fieldtranslate'
    sign = appid + q + str(salt) + domain + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&domain=' + domain + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response鏄疕TTPResponse瀵硅薄
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        print(result)
        return [val for val in result['trans_result'][0].values()]
    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()


@retry(stop_max_attempt_number=4, wait_random_min=2000, wait_random_max=6000)
def translate(q, fromLang='en', toLang='zh', domain='medicine'):
    if not has_letter(q):
        return [q, q]

    url = 'https://fanyi-api.baidu.com/api/trans/vip/fieldtranslate'
    sign = appid + q + str(salt) + domain + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    payload = {
        'q': q,
        'from': fromLang,
        'to': toLang,
        'appid': appid,
        'salt': salt,
        'domain': domain,
        'sign': sign,
    }
    response = requests.post(url, params=payload, headers=headers)
    result = response.json()

    if not result.get('trans_result'):
        print(result)
        NOUNS_Q.put(q)
        return None
    return [val for val in result['trans_result'][0].values()]


@timethis
def main(thread_num):
    load_nouns()
    with ThreadPoolExecutor(thread_num) as executor:
        all_task = []
        print(NOUNS_Q.qsize())
        while not NOUNS_Q.empty():
            noun = NOUNS_Q.get()
            if noun is finish_single: break
            all_task.append(executor.submit(translate, noun))

        for future in as_completed(all_task):
            row = future.result()
            print(row)
            if row:
                write_row_csv('new/translation.csv', row)


if __name__ == '__main__':
    q = 'amyotrophic lateral sclerosis'
    main(1)
    # translate(q)
