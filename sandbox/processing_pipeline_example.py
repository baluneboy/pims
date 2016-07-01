#!/usr/bin/env python

class ProcessingPipeline(object):
    def __init__(self, *functions, **kwargs):
        self.functions = functions
        self.data = kwargs.get('data')
    def __call__(self, data):
        return ProcessingPipeline(*self.functions, data=data)
    def __iter__(self):
        data = self.data
        for func in self.functions:
            data = func(data)
        return data

def demo_few():
    # a few (very simple) operators, of different kinds
    class Multiplier(object):
        def __init__(self, by):
            self.by = by
        def __call__(self, data):
            for x in data:
                yield x * self.by
    
    def add(data, y):
        for x in data:
            yield x + y
    
    from functools import partial
    by2 = Multiplier(by=2)
    sub1 = partial(add, y=-1)
    square = lambda data: ( x*x for x in data )
    
    pp = ProcessingPipeline(square, sub1, by2)
    
    print list(pp(range(10)))
    print list(pp(range(-3, 4)))

if __name__ == '__main__':
    demo_few()