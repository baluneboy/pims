#!/usr/bin/env python

class First(object):
    def __init__(self):
        super(First, self).__init__()
        print "first"
    def method_one(self):
        print "method from %s" % self.__class__.__name__

class Second(object):
    def __init__(self):
        super(Second, self).__init__()
        print "second"
    def method_two(self):
        print "this is a method from %s" % self.__class__.__name__

class Third(Second, First):
    def __init__(self):
        super(Third, self).__init__()
        print "that's it"
        
x = Third()
x.method_one()
x.method_two()