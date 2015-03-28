#!/usr/bin/env python

################################################################################
"""For cases where you need to choose from a very large number of possibilities,
you can create a dictionary mapping case values to functions to call. For
example:"""

def function_1():
    return "one"

def function_2():
    return "two"

# a "large" number of choices (here just 2 though)    
functions = {
    'a': function_1,
    'b': function_2, 
    #'c': self.method_1,
}

values = ['b', 'a']
for value in values:
    func = functions[value]
    print "%s() = %s" % (func.__name__, func())
print '-' * 44


################################################################################
"""Perhaps more pythonic way to do switch/case, you can create a class to handle
dispatching by using getattr to retrieve methods with a particular name. For
example:"""
class MyClass(object):

    def _a(self):
        print "A"

    def _b(self):
        print "B"

    def dispatch(self, value):
        method_name = '_' + str(value)
        try:
            method = getattr(self, method_name)
        except AttributeError:
            print method_name, "not found"
        else:
            method()
            
mc = MyClass()
mc.dispatch('a')
mc.dispatch('b')