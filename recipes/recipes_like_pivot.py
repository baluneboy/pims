#!/usr/bin/env python

from itertools import groupby, islice
from operator import itemgetter
from collections import defaultdict

def get_demo_data():
    data = [('Apple',      'Coles',      1.50),
            ('Apple',      'Woolworths', 1.60),
            ('Apple',      'IGA',        1.70),
            ('Banana',     'Coles',      0.50),
            ('Banana',     'Woolworths', 0.60),
            ('Banana',     'IGA',        0.70),
            ('Cherry',     'Coles',      5.00),
            ('Peach',       'Coles',      2.00),
            ('Peach',       'Woolworths', 2.10),
            ('Kiwi', 'IGA',        10.00)]
    return data

def demo_like_pivot():
    data = get_demo_data()
    stores = sorted(set(row[1] for row in data))
    # probably splitting this up in multiple lines would be more readable
    pivot = ((fruit, defaultdict(lambda: None, (islice(d, 1, None) for d in data))) for fruit, data in groupby(sorted(data), itemgetter(0)))
    
    print '-'*44
    print 'Fruit'.ljust(12), '\t'.join(stores)
    print '-'*44
    for fruit, prices in pivot:
        print fruit.ljust(12), '\t'.join(str(prices[s]) for s in stores)
    print '-'*44

if __name__ == "__main__":
    demo_like_pivot()