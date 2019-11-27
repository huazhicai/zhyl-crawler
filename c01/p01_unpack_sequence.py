#!/usr/bin/env python
"""
Topic: unpacking sequence
Desc :
"""

p = (4, 5)
x, y = p
print(x, y)

data = ['ACME', 50, 91.1, (2012, 12, 21)]
# name, shares, price, date = data
# name, shares, price, (year, mon, day) = data

s = 'Hello'
a, b, c, d, e = s

_, shares, price, _ = data
