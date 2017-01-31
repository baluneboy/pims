#!/usr/bin/env python

from operator import itemgetter

# Here's an easy way to sort
foo = [1, 2, 9, 3]
bar = ['one', 'two', 'nine', 'three']
perm = sorted(xrange(len(foo)), key=lambda x:foo[x])

# This generates a list of permutations - the value in perm[i] is the
# index of the ith smallest value in foo. Then, you can access both lists in order:
for p in perm:
    print "%s: %s" % (foo[p], bar[p])
#-------------------------------------

# Also, using sorted and itemgetter to sort by item in position 0, then position 2
data = [(9, 'zabc', 121),(12, 'abc', 231),(12, 'kabc', 148), (0, 'xabc',221)]
sorted_data = sorted(data, key=itemgetter(0,2))
sort2_data =  sorted(data, key=itemgetter(0,1))
print 'unsorted                        ', data
print '  sorted by pos 0, then by pos 2', sorted_data
print '  sorted by pos 0, then by pos 1', sort2_data