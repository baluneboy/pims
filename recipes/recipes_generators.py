#!/usr/bin/env python

import random
from collections import deque

# A generator to get datetimes (every 5 minutes start on 31-Dec-2012)
def nextFiveMinutes():
    import datetime
    dtm = datetime.datetime(2012, 12, 31, 22, 0, 0) - datetime.timedelta(minutes=5)
    while 1:
        dtm += datetime.timedelta(minutes=5)
        yield (dtm)

def generateDummyData():
    # Generate dummy data
    nd = nextFiveMinutes()
    num = 5
    some_dates = [nd.next() for i in range(0,num)] #get 20 dates
    y_values = [random.randint(1,100) for i in range(0,num)] # get dummy y data
    return some_dates, y_values

def randomwalk_generator():
    last, rand = 1, random.random() # initialize candidate elements
    while rand > 0.1:               # threshhold terminator
        print '*',                  # display the rejection
        if abs(last-rand) >= 0.4:   # accept the number
            last = rand             # update prior value
            yield rand              # return AT THIS POINT
        rand = random.random()      # new candidate
    yield rand

def fibonacciFirstNish(n):
    """Fibonacci numbers generator, first n-ish"""
    a, b, counter = 0, 1, 0
    while True:
        if (counter > n): return
        yield a
        a, b = b, a + b
        counter += 1

# We have to take care when we use this iterator, that a termination criterium is used!
def fibonacci():
    """Fibonacci numbers generator"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

class SimpleCircularBuffer(object):
    
    def __init__(self, data=[0,1,2]):
        data.reverse()
        self._data = deque(data, maxlen=len(data))

    def rot_get(self, num_rot=1):
        """rotate num_rot times and return current element"""
        self._data.rotate(num_rot)
        return self._data[-1]
    
    def get(self):
        return self.rot_get(num_rot=0)

some_dates, y_values = generateDummyData()
for d,y in zip(some_dates, y_values):
    print 'date = %s, y-value = %d' % (d, y)

f = fibonacciFirstNish(5)
for x in f:
    print x,
print

f = fibonacci()

counter = 0
for x in f:
    print x,
    counter += 1
    if (counter > 10): break 
print


