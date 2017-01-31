#!/usr/bin/env python

class A(object):
    def __init__(self, x, y, flag=None):
        print "Constructor A was called with x = %f and y = %f and flag of %s" % (x, y, flag)

class B(A):
    def __init__(self, *args, **kwargs):
        super(B,self).__init__(*args, **kwargs)
        print "Constructor B was called"

class C(B):
    def __init__(self, *args, **kwargs):
        super(C,self).__init__(*args, **kwargs)
        print "Constructor C was called"

#b = B(1,2)
c = C(4,5,flag='see')