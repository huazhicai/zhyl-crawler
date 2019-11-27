def drop_first_last(grades):
    first, *middle, last = grades
    return avg(middle)


record = ('Dave', 'dave@example.com', '773-555-1212', '847-555-1212')
name, email, *phone_numbers = record
print(phone_numbers)  # ['773-555-1212', '847-555-1212']

*trailing_qtrs, current_qtr = sales_record
trailing_avg = sum(trailing_qtrs) / len(trailing_qtrs)
avg_comparison(trailing_avg, current_qtr)

records = [
    ('foo', 1, 2),
    ('bar', 'hello'),
    ('foo', 3, 4),
]


def do_foo(x, y):
    print('foo', x, y)


def do_bar(s):
    print('bar', s)


# 获取可变长元组序列
for tag, *args in records:
    if tag == 'foo':
        do_foo(*args)
    elif tag == 'bar':
        do_bar(*args)

record = ('ACME', 50, 123.45, (12, 18, 2012))
name, *_, (*_, year) = record

items = [1, 10, 7, 4, 5, 9]
head, *tail = items


# 递归算法
def sum(items):
    head, *tail = items
    return head + sum(tail) if tail else head
