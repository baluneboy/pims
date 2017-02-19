#!/usr/bin/env python

import resource
 
list1 = []
list2 = []
for j in range(1,10):
    for i in range(0,1000000):
        list1.append('abcdefg')
    print resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
# set the first list to be an empty list
list1=[]
for j in range(1,10):
    for i in range(0,1000000):
        list2.append('abcdefg')
    print resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
