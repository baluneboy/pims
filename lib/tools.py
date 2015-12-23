#!/usr/bin/env python
"""
Some hopefully useful classes and functions.
"""
from collections import MutableMapping, MutableSet
import inspect
import re
import operator

class TransformedDict(MutableMapping):
    """
    A dictionary that applies an arbitrary key-altering
    function before accessing the keys.
    """

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        # key transform code goes here
        return key

class LowerKeysTransformedDict(TransformedDict):
    """Transform keys to lowercase."""
    def __keytransform__(self, key):
        return key.lower()

class OrderedSet(MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)

# one way to return variable name
def varname(p):
    """one way to return variable name"""
    for line in inspect.getframeinfo(inspect.currentframe().f_back)[3]:
          m = re.search(r'\bvarname\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)', line)
          if m:
            return m.group(1)

# return True if x is "inrange"; else False
def inrange(x, min, max, lower_closed=True, upper_closed=False):
    """return True if x is "inrange"; else False"""
    if lower_closed:
        mincmp = operator.le
    else:
        mincmp = operator.lt
    if upper_closed:
        maxcmp = operator.ge
    else:
        maxcmp = operator.gt
    #return (min is None or min <= x) and (max is None or max >= x)
    return (min is None or mincmp(min,x)) and (max is None or maxcmp(max, x))

#for x in range(-5,5,1):
#    print x, inrange(x, -2, 2, upper_closed=True)
#raise SystemExit

def demo():
    d = LowerKeysTransformedDict( [ ('Test', 1), ('camelCase', 'dogma') ] )
    d['piNg'] = 'pong'
    for k,v in d.iteritems():
        print k, v
    
    assert d.get('TEST') is d['test']   # free get
    assert 'TeSt' in d                  # free __contains__
                                        # free setdefault, __eq__, and so on

if __name__ == "__main__":
    demo()