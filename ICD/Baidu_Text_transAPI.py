# -*- coding: utf-8 -*-

# This code shows an example of text translation from English to Simplified-Chinese.
# This code runs on Python 2.7.x and Python 3.x.
# You may install `requests` to run this code: pip install requests
# Please refer to `https://api.fanyi.baidu.com/doc/21` for complete api document

import requests
import random
import json
from hashlib import md5

# Set your own appid/appkey.
from retrying import retry

appid = '20210901000932905'
appkey = 'XBRtzLpsN4fd0iMARa7o'

# For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
from_lang = 'en'
to_lang = 'zh'

endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path


# query = '(((4-nitrophenyl)amino)(2,2,4,4-tetramethyl thiochroman-6-yl)amino) methane-1-thione'


# Generate salt and sign
def make_md5(s, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


salt = random.randint(32768, 65536)

# Build request
headers = {'Content-Type': 'application/x-www-form-urlencoded'}


@retry(stop_max_attempt_number=10, wait_random_min=4000, wait_random_max=9000)
def bd_trans(text):
    sign = make_md5(appid + text + str(salt) + appkey)
    payload = {'appid': appid, 'q': text, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()

    # Show response
    # print(json.dumps(result, indent=4, ensure_ascii=False))
    # return json.dumps(result, indent=4, ensure_ascii=False)
    return result


from utils import csv_reader, write_row_csv, write_rows_csv, write_dict_csv

seen = set()
start_row = 11114


def load_src():
    count = 0
    for row in csv_reader('nounsword.csv'):
        count += 1
        if count < start_row:
            continue
        ret = bd_trans(row[0])
        print(ret)
        trans = ret.get('trans_result')
        write_row_csv('trans_word.csv', trans[0].values())


load_src()