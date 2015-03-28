#!/usr/bin/env python

from inspect import stack

class Foo(object):

    def _method_a(self):
        methodstr = stack()[0][3]
        classstr = self.__class__.__name__
        filestr = __file__
        print 'This introspective message is coming from...'
        print '{label1:<12}: {methodstr}\n{label2:<12}: {classstr}\n{label3:<12}: {filestr}'.format(
            label1='method',
            label2='class',
            label3='module(file)',
            methodstr=methodstr,
            classstr=classstr,
            filestr=filestr
        )

f = Foo()
f._method_a()

