#!/usr/bin/env python

from operator import itemgetter

# sort list based on tuple elements [1], then [0]
tuples = [(1,"z",5), (2,"x",9), (3,"y",7), (2,"y",7), (3,"y",9)]
sorted_tuples = sorted(tuples, key=itemgetter(1,0))
print tuples
print sorted_tuples

# remove duplicates based on tuple elements [0] and [1], then sorted based on elements [1], then [0]
non_dup_tuples = dict(((x[0], x[1]), x) for x in tuples).values()
sorted_non_dup_tuples = sorted(non_dup_tuples, key=itemgetter(1,0))
print non_dup_tuples
print sorted_non_dup_tuples
