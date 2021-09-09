from remedy import csv_reader, write_rows_csv, write_row_csv
import threading
import requests
from collections import Counter
from extractor import parser
from concurrent.futures import ThreadPoolExecutor

URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={}&retmode=xml'
_LOCK = threading.Lock()
CONTAINER = []

titles = set()
publish = set()
seen = set()


def start():
    for row in csv_reader(filename):
        title = row[1].strip()
        if title not in seen:
            seen.add(title)
            write_row_csv('journal_title.csv', [title])


def publish_type():
    for row in csv_reader(filename):
        publishs = row[2].split('\n')
        for i in publishs:
            name = i.strip()
            if name not in seen:
                seen.add(name)
                write_row_csv('journal_publish.csv', [name])


if __name__ == '__main__':
    # thread_num = 32
    filename = 'dedup_samples.csv'
    # start()
    publish_type()
