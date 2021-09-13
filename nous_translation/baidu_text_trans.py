# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document

import requests
import random
from hashlib import md5
from retrying import retry
from common.data_stream import csv_reader, load_json, write_row_csv
from utils import has_letter
from baidu import translate


appid = '20210901000932905'
appkey = 'XBRtzLpsN4fd0iMARa7o'
# appid= '20210901000933121'
# appkey = '3DHhlTmafpIObsR_9OXZ'


# For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`


endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path


# Generate salt and sign
def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


salt = random.randint(32768, 65536)

# Build request
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
# TRANSLATION_FILE = 'file/baidu.csv'
TRANSLATION_FILE = 'new/translation.csv'
EN_2_ZH = {}


@retry(stop_max_attempt_number=4, wait_random_min=2000, wait_random_max=6000)
def translate_bak(text, from_lang='en', to_lang='zh'):
    # sign = make_md5(appid + text + str(salt) + appkey)
    # payload = {'appid': appid, 'q': text, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}
    #
    # # Send request
    # r = requests.post(url, params=payload, headers=headers)
    # result = r.json()
    # print(result)
    result = translate(text)

    if result:
        print('result: ', result)
        chinese = result[-1]
        write_row_csv(TRANSLATION_FILE, [text, chinese])
        EN_2_ZH[text] = chinese
        return chinese

    return text + ' [translate failed]'


def load_local_translation():
    for row in csv_reader(TRANSLATION_FILE):
        EN_2_ZH[row[0].strip().lower()] = row[1]


def baidu_query(text):
    text = text.lower().strip()
    if not EN_2_ZH:
        load_local_translation()
    if not has_letter(text):
        return text
    return EN_2_ZH.get(text) or translate(text)


if __name__ == '__main__':
    # print(baidu_query('Hello'))
    translate('amyotrophic lateral sclerosis')