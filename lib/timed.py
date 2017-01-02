#!/usr/bin/python

import time
import timeit

def timed(method):

    def timed(*args, **kw):        
        
        start_time = timeit.default_timer()
        result = method(*args, **kw)
        stop_time = timeit.default_timer()
        num_sec = stop_time - start_time
        
        timed_str = '%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, num_sec)
        
        return result, timed_str

    return timed

def demo():
    class Foo(object):
        
        @timed
        def foo(self, a=2, b=3):
            time.sleep(0.2)
            print 'Foo.foo'
    
    @timed
    def f1():
        time.sleep(1)
        print 'f1'
        return ('a string from f1', ['dog', 'cat'])
    
    @timed
    def f2(a):
        time.sleep(2)
        print 'f2', a
        return 'output from f2 is this string showing double its input = %d' % (2*a)
    
    @timed
    def f3(a, *args, **kw):
        time.sleep(0.3)
        print 'f3', args, kw
        # no output from f3
        
    out1 = f1()
    out2 = f2(14)
    out3 = f3(42, 43, foo=2)
    outFoo = Foo().foo()
    
    # results
    print "RESULTS:"
    print out1
    print out2
    print out3
    print outFoo

if __name__ == '__main__':
    demo()