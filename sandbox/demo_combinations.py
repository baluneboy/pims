#!/usr/bin/env python

from itertools import combinations

iterable = [4, 1, 2, 3]

for r in range(1, len(iterable) + 1):
    count = 0
    print 'combinations of length %d' % r
    for c in combinations(iterable, r):
        count += 1
        print count, c
