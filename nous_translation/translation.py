# -*- coding: utf-8 -*-
from icd_query import icd_query
from medical_term_query import medical_query
from baidu_text_trans import baidu_query
from common import csv_reader, write_rows_csv


def load_nouns():
    container = []
    for row in csv_reader('file/nouns.csv'):
        text = row[3].strip().lower()
        chinese = medical_query(text)
        if not chinese:
            chinese = icd_query(text)
        if not chinese:
            chinese = baidu_query(text)
        container.append([row[3], chinese or row[3]])
        # print([row[3], chinese or row[3]])
    print(len(container))
    write_rows_csv('nouns_translation.csv', container)


if __name__ == '__main__':
    load_nouns()
