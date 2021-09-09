# -*- coding:utf-8 -*-
import json
import copy

EN_2_ZH = {}
container = []

ZH_FILE = 'file/icd_zh.json'
EN_FILE = 'file/icd_en.json'


def load_json(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def recursion(data):
    if isinstance(data, dict):
        for key, value in data.items():
            container.append(key.lower())
            recursion(value)
    elif isinstance(data, list):
        for item in data:
            recursion(item)
    else:
        container.append(data.lower())


def en_map_zh():
    en_data = load_json(EN_FILE)
    recursion(en_data)
    en_list = copy.copy(container)

    container.clear()
    zh_data = load_json(ZH_FILE)
    recursion(zh_data)
    zh_list = container

    assert len(en_list) == len(zh_list)
    EN_2_ZH.update(dict(zip(en_list, zh_list)))


def icd_query(text):
    if not EN_2_ZH: en_map_zh()
    return EN_2_ZH.get(text.strip().lower())


if __name__ == '__main__':
    print(icd_query('Certain infectious or parasitic diseases'))
    print(icd_query('Cholera'))
