#!/usr/bin/env python

# A decorator that modifies behavior of undecorated (target) function
def myDecorator(theTarget):
    def wrapper(*args, **kwargs):
        print 'Calling function "%s" with arguments %s and keyword arguments %s' % (theTarget.__name__, args, kwargs)
        return theTarget(*args, **kwargs)
    return wrapper

@myDecorator
def myTarget(a, b):
    return a+b

if __name__ == "__main__":
    print myTarget(1,2)