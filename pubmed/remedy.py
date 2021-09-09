# -*- coding:utf-8 -*-
import csv
from extractor import extractor_group, SAMPLE_FILE
from config import title_2_factor


def csv_reader(file):
    with open(file, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            yield row


def write_row_csv(filename, row, mode='a', newline=''):
    with open(filename, mode, newline=newline) as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(row)


def write_rows_csv(filename, rows, mode='a', newline=''):
    with open(filename, mode, newline=newline) as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerows(rows)


def clean_sample():
    seen = set()
    rows = []
    with open(SAMPLE_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] not in seen:
                seen.add(row[0])
                rows.append(row)
        rows.sort(key=lambda x: x[0])
        chunk = []
        for row in rows:
            chunk.append(row)
            if len(chunk) == 10000:
                write_rows_csv(clean_file, chunk)
                chunk.clear()
        write_rows_csv(clean_file, chunk)


def dedup_sample(file):
    seen = set()
    chunk = []
    for row in csv_reader(file):
        title = row[1]
        if title not in seen:
            seen.add(title)
            chunk.append(row)
        if len(chunk) == 10000:
            write_rows_csv(clean_file, chunk)
    write_rows_csv(clean_file, chunk)


def other_title_2_factor():
    other_2_factor = {}
    for row in csv_reader('new_journal_impact_factor.csv'):
        other_2_factor.update({title: row[3] for title in row[5:]})
    return other_2_factor


def compare_all(title):
    for other_title in other_2_factor.keys():
        source_title = title.split(' ')
        refer_title = other_title.split(' ')
        if len(source_title) == len(refer_title):
            if all(source_title[i].startswith(refer_title[i]) for i in range(len(source_title))):
                return other_2_factor[other_title]
    return '0.000'
    # if len(title.split(' ')) == len(other_title.split(' ')):


def match_title_for_factor():
    global other_2_factor
    other_2_factor = other_title_2_factor()
    for row in csv_reader('clean_samples.csv'):
        journal_title = row[1].lower()
        factor = title_2_factor.get(journal_title) or other_2_factor.get(journal_title)
        # factor = other_2_factor.get(journal_title)
        # if not factor:
        #     factor = compare_all(journal_title)
        # row[-1] = factor or '0.000'
        row.append(factor or '0.000')
        row.append(factor)
        write_row_csv('new_new_samples.csv', row)


if __name__ == '__main__':
    # clean_sample()
    clean_file = 'clean.csv'
    # dedup_sample(SAMPLE_FILE)
    match_title_for_factor()
