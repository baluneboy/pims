#!/usr/bin/python

from collections import Counter


# return Counter object with tally for occurrences of words in a list
def tally_occurrences_of_words_list(words_list):
    """return Counter object with tally for occurrences of words in a list
    
    >>> cnt = tally_occurrences_of_words_list(['red', 'blue', 'red', 'green', 'blue', 'blue'])
    >>> cnt
    Counter({'blue': 3, 'red': 2, 'green': 1})
    """
    cnt = Counter()
    for word in words_list:
        cnt[word] += 1
    return cnt


# return list of tuples (word, tally) for N most common lower-cased words words in file named fname
def find_n_most_common_words_in_file(fname, n=10):
    """return list of tuples (word, tally) for N most common lower-cased words words in file named fname
    
    >>> fname = '/Volumes/serverHD2/data/temp/hamlet.txt'
    >>> c = find_n_most_common_words_in_file(fname, n=6)
    >>> c
    [('the', 2499), ('in', 1140), ('not', 995), ('and', 993), ('from', 784), ('to', 767)]
    """   
    import re
    # get list of "words" from file contents, each converted to lower case
    words = re.findall(r'\w+', open(fname).read().lower())
    return Counter(words).most_common(n)

    
# A Counter is a dict subclass for counting hashable objects. It is an unordered
# collection where elements are stored as dictionary keys and their counts are
# stored as dictionary values. Counts are allowed to be any integer value
# including zero or negative counts.
#
# Elements are counted from an iterable OR can be initialized from another mapping (or counter):
#
# c = Counter()                           # a new, empty counter
# c = Counter('gallahad')                 # a new counter from an iterable
# c = Counter({'red': 4, 'blue': 2})      # a new counter from a mapping
# c = Counter(cats=4, dogs=8)             # a new counter from keyword args
#
# Counter objects have a dictionary interface except that they return a zero
# count for missing items instead of raising a KeyError:
#
# c = Counter(['eggs', 'ham'])
# c['bacon']                              # count of a missing element is zero
#
# HOWEVER, setting a count to zero does not remove an element from a counter. Use del to remove it entirely:
#
# c['sausage'] = 0                        # counter entry with a zero count
# del c['sausage']                        # del actually removes the entry
#
# Counter objects support three methods beyond those available for all dictionaries:
#
# DEMO METHOD
# elements() # returns iterator over elements repeating each as many times as
#              its count, BUT elements are returned in arbitrary order AND if
#              an element's count  is less than one, elements() will ignore it
#              SIMILAR to rude.m (run length vector en/decoder in MATLAB)
#
# c = Counter(a=4, b=2, c=0, d=-2)
# list(c.elements())
# ['a', 'a', 'a', 'a', 'b', 'b']
#
# DEMO METHOD
# most_common([n]) # returns list of the n most common elements and their counts from the most common to the least
#                    if n is omitted or None, most_common() returns all elements in the counter AND elements with
#                    equal counts are ordered arbitrarily
#
# Counter('abracadabra').most_common(3)
# [('a', 5), ('r', 2), ('b', 2)]
#
# DEMO METHOD
# subtract([iterable-or-mapping]) # elements are subtracted from an iterable or from another mapping (or counter)
#                                   this is like dict.update() but subtracts counts instead of replacing them
#                                   both inputs and outputs may be zero or negative
#
# c = Counter(a=4, b=2, c=0, d=-2)
# d = Counter(a=1, b=2, c=3, d=4)
# c.subtract(d)
# c
# Counter({'a': 3, 'b': 0, 'c': -3, 'd': -6})
#
# The usual dictionary methods are available for Counter objects except for two
# which work differently for counters.
#
# fromkeys(iterable)            # this class method is not implemented for Counter objects
# update([iterable-or-mapping]) # elements are counted from an iterable or added-in from another mapping (or counter)
#                                 this is like dict.update() but adds counts instead of replacing them ALSO, the
#                                 iterable is expected to be a sequence of elements, not a sequence of (key, value) pairs.
#
# Common patterns for working with Counter objects:
#
# sum(c.values())                 # total of all counts
# c.clear()                       # reset all counts
# list(c)                         # list unique elements
# set(c)                          # convert to a set
# dict(c)                         # convert to a regular dictionary
# c.items()                       # convert to a list of (elem, cnt) pairs
# Counter(dict(list_of_pairs))    # convert from a list of (elem, cnt) pairs
# c.most_common()[:-n-1:-1]       # n least common elements
# c += Counter()                  # remove zero and negative counts
#
# Several mathematical operations are provided for combining Counter objects to
# produce multisets (counters that have counts greater than zero). Addition and
# subtraction combine counters by adding or subtracting the counts of
# corresponding elements. Intersection and union return the minimum and maximum
# of corresponding counts. Each operation can accept inputs with signed counts,
# but the output will exclude results with counts of zero or less.
#
# c = Counter(a=3, b=1)
# d = Counter(a=1, b=2)
# c + d                       # add two counters together:  c[x] + d[x]
# Counter({'a': 4, 'b': 3})
#
# c - d                       # subtract (keeping only positive counts)
# Counter({'a': 2})
#
# c & d                       # intersection:  min(c[x], d[x]) # MIN of each element
# Counter({'a': 1, 'b': 1})
#
# c | d                       # union:  max(c[x], d[x])        # MAX of each element
# Counter({'a': 3, 'b': 2})        


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
