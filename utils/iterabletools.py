#!/usr/bin/env python

import operator
from itertools import *

def ilen(it):
    """Return the length of an iterable.
    
    For some, you do not know the length of an
    iterable until you iterate through it.
    
    CAUTION: Some iterables may be infinite or be
    "consumed" and need to be reset!
    
    >>> ilen(range(7))
    7
    """   
    return sum(1 for _ in it)
    
def runlength_enc(xs):
    """Return a run-length encoded version of the stream, xs.
    
    The resulting stream consists of (count, x) pairs.
    
    >>> ys = runlength_enc('AAABBCCC')
    >>> next(ys)
    (3, 'A')
    >>> list(ys)
    [(2, 'B'), (3, 'C')]
    """
    return ((ilen(gp),x) for x,gp in groupby(xs))

def runlength_dec(xs):
    """Expand a run-length encoded stream.
    
    Each element of xs is a pair, (count, x).
    
    >>> ys = runlength_dec(((3, 'A'), (2, 'B')))
    >>> next(ys)
    'A'
    >>> ''.join(ys)
    'AABB'
    >>> demo_runlength_dec()
    0 0 1 1 1 5
    """
    return chain.from_iterable(repeat(x,n) for n,x in xs)

def runlength_consumer(a, mask):
    """Apply run-length with consumer feature."""
    RLE = runlength_enc(mask)
    for n,v in RLE:
        print n,v
        if v==0:
            print "consume",n
            consume(a,n)
            consume(mask,n)
        else:
            print "no consume"    

def runlength_blocks(data):
    """Return run-length encoded blocks of input data.
    
    The result consists of (count, length, value) tuples.
    
    >>> runlength_blocks([1,1,1,1,0,0,0,0,0,1,1,1,0,0])
    [[0, 3, 1], [4, 8, 0], [9, 11, 1], [12, 13, 0]]
    """
    itemgetter = operator.itemgetter
    blocks = [map(itemgetter(0), itemgetter(0, -1)(list(g))) + [k] for k, g in groupby(enumerate(data), itemgetter(1))]
    return blocks

def dedupe_adjacent(alist):
    """Return list with adjacent duplicates removed.
    
    >>> dedupe_adjacent( [0, 0, 1, 1, 1, 5] )
    [0, 1, 5]
    """
    return [k for k,g in groupby(alist)]

def take(n, iterable):
    """Return first n items of the iterable as a list.
    
    >>> RLD = runlength_dec(((3, 'A'), (15, 'B'))) # ilen is 18
    >>> take(4, RLD)
    ['A', 'A', 'A', 'B']
    """
    return list(islice(iterable, n))

def tabulate(function, start=0):
    "Return function(0), function(1), ..."
    return imap(function, count(start))

def consume(iterator, n):
    "Advance the iterator n-steps ahead. If n is none, consume entirely."
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)

def nth(iterable, n, default=None):
    """Returns the nth item or a default value.
    
    >>> RLD = runlength_dec(((3, 'A'), (5, 'B'))) # ilen is 8
    >>> nth(RLD, 2) # two things consumed! (see next call)
    'A'
    >>> nth(RLD, 2)
    'B'
    """
    return next(islice(iterable, n, None), default)

def quantify(iterable, pred=bool):
    """Count how many times the predicate is true.
    
    >>> is_divisible_by_3 = lambda i: i % 3 == 0
    >>> quantify( xrange(14), is_divisible_by_3 ) # btw, zero counts!
    5
    
    >>> is_palindrome = lambda x: str(x) == str(x)[::-1]
    >>> #            yes      yes     nope   (Eric is not a palindrome)
    >>> quantify( ['radar', 'level', 'Eric'], is_palindrome )
    2
    
    >>> import re; fname = '/tmp/file_one.txt'
    >>> is_matched = lambda pat : bool(re.match(pat, fname))
    >>> pats = ['.*stupid.*', '.*one.*', '.*dumb.*']
    >>> quantify(pats, is_matched) # count matches
    1
    """
    return sum(imap(pred, iterable))

def padnone(iterable):
    """Returns the sequence elements and then returns None indefinitely.

    Useful for emulating the behavior of the built-in map() function.
    """
    return chain(iterable, repeat(None))

def ncycles(iterable, n):
    """Returns the sequence elements n times.
    
    >>> for s in ncycles(xrange(3), 2): print s,
    0 1 2 0 1 2
    
    >>> for s in ncycles('ABC', 3): print s,
    A B C A B C A B C
    """
    return chain.from_iterable(repeat(tuple(iterable), n))

def prod(iterable):
    "Multiply elements of iterable."
    return reduce(operator.mul, iterable, 1)

def dotproduct(vec1, vec2):
    "Dot product."
    return sum(imap(operator.mul, vec1, vec2))

def flatten(listOfLists):
    """Flatten one level of nesting.
    
    >>> LOL = [ [1,2], ['A','B'], ['Judy',5] ]
    >>> list(flatten(LOL))
    [1, 2, 'A', 'B', 'Judy', 5]
    """
    return chain.from_iterable(listOfLists)

def repeatfunc(func, times=None, *args):
    """Repeat calls to func with specified arguments.
       or does it? can you have kwargs before args??
    """
    if times is None:
        return starmap(func, repeat(args))
    return starmap(func, repeat(args, times))

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def grouper(n, iterable, fillvalue=None):
    """grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx
    
    >>> demo_grouper()
    [[0 1 2] [3 4 5] [6 7 8] [ 9 10 11] None None None]
    """
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def roundrobin(*iterables):
    "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
    # Recipe credited to George Sakkis
    pending = len(iterables)
    nexts = cycle(iter(it).next for it in iterables)
    while pending:
        try:
            for next in nexts:
                yield next()
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))

def powerset(iterable):
    """powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    
    >>> [ x for x in powerset([1,2,3]) ]
    [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))

def unique_everseen(iterable, key=None):
    """List unique elements, preserving order. Remember all elements ever seen.
    
    >>> [ x for x in unique_everseen('AAAABBBCCDAABBB') ]
    ['A', 'B', 'C', 'D']
    >>> [ x for x in unique_everseen('ABBCcAD', key=str.lower) ]
    ['A', 'B', 'C', 'D']
    """
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

def unique_justseen(iterable, key=None):
    """List unique elements, preserving order. Remember only the element just seen.
    
    >>> [ x for x in unique_justseen('AAAABBBCCDAABBB') ]
    ['A', 'B', 'C', 'D', 'A', 'B']
    >>> [ x for x in unique_justseen('ABBCcAD', key=str.lower) ]
    ['A', 'B', 'C', 'A', 'D']
    """
    return imap(next, imap(operator.itemgetter(1), groupby(iterable, key)))

def iter_except(func, exception, first=None):
    """ Call a function repeatedly until an exception is raised.

    Converts a call-until-exception interface to an iterator interface.
    Like __builtin__.iter(func, sentinel) but uses an exception instead
    of a sentinel to end the loop.

    Examples:
        bsddbiter = iter_except(db.next, bsddb.error, db.first)
        heapiter = iter_except(functools.partial(heappop, h), IndexError)
        dictiter = iter_except(d.popitem, KeyError)
        dequeiter = iter_except(d.popleft, IndexError)
        queueiter = iter_except(q.get_nowait, Queue.Empty)
        setiter = iter_except(s.pop, KeyError)

    """
    try:
        if first is not None:
            yield first()
        while 1:
            yield func()
    except exception:
        pass

def random_product(*args, **kwds):
    "Random selection from itertools.product(*args, **kwds)."
    pools = map(tuple, args) * kwds.get('repeat', 1)
    return tuple(random.choice(pool) for pool in pools)

def random_permutation(iterable, r=None):
    "Random selection from itertools.permutations(iterable, r)."
    pool = tuple(iterable)
    r = len(pool) if r is None else r
    return tuple(random.sample(pool, r))

def random_combination(iterable, r):
    "Random selection from itertools.combinations(iterable, r)."
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(xrange(n), r))
    return tuple(pool[i] for i in indices)

def random_combination_with_replacement(iterable, r):
    "Random selection from itertools.combinations_with_replacement(iterable, r)."
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.randrange(n) for i in xrange(r))
    return tuple(pool[i] for i in indices)

def demo_runlength_dec( counts=[2, 3, 1], vals=[0, 1, 5] ):
    """Demonstrate run_length functions."""
    # default values: get two zeros, three ones, and then one five
    ys = runlength_dec( ( zip(counts,vals) ) )
    # iterable ready to roll...gets consumed by iteration though!
    for y in ys: print y,

def demo_grouper():
    import numpy as np
    a = np.arange(12).reshape((4,3))
    for g in grouper(7, a):
        print np.asarray(g)


def group_iterable_by_predicate(iterable, is_start):
    """Group an iterable by a predicate.
    
    >>> demo_group_iterable_by_predicate()
    grp: 04, grp: 05, 06, 07, 08, 09, grp: 10, 11, 12, 13, 14, grp: 15,
    """
    def _pairwise2(iterable):
        a, b = tee(iterable)
        return izip(a, chain(b, [next(b, None)]))

    pairs = _pairwise2(iterable)

    def extract(current, lookahead, pairs=pairs, is_start=is_start):
        yield current
        if is_start(lookahead):
            return
        for current, lookahead in pairs:
            yield current
            if is_start(lookahead):
                return

    for start, lookahead in pairs:
        gen = extract(start, lookahead)
        yield gen
        for _ in gen:
            pass

def demo_group_iterable_by_predicate():
    for gen in group_iterable_by_predicate(xrange(4, 16), lambda x: x % 5 == 0):
        print 'grp:',
        for n in gen:
            print '%02d,' % n,

if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
