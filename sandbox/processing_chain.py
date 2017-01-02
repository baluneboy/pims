class ProcessingPipeline(object):

    def __init__(self, *functions, **kwargs):
        self.functions = functions
        self.data = kwargs.get('data') # makes this callable

    def __call__(self, data):
        return ProcessingPipeline(*self.functions, data=data)

    def __iter__(self):
        data = self.data
        for func in self.functions:
            data = func(data)
        return data

#####################################################
# A FEW (VERY SIMPLE) OPERATORS, OF DIFFERENT TYPES #
#####################################################

# Operator type #1 = a multiplier class
class Multiplier(object):
    def __init__(self, by):
        self.by = by
    def __call__(self, data):
        for x in data:
            yield x * self.by

# Operator type #2 = an add function
def add(data, y):
    for x in data:
        yield x + y

# Operator type #3 = a square lambda function
from functools import partial
by2 = Multiplier(by=2)
sub1 = partial(add, y=-1)
square = lambda data: ( x*x for x in data )

# Initialize processing pipeline (no data input yet)
pp = ProcessingPipeline(square, sub1, by2)

# Apply processing pipeline input #1 (now pp is callable)
inp1 = range(10)
print list(pp(inp1))

# Apply processing pipeline input #2 (pp is callable again with new input data)
inp2 = range(-3, 4)
print list(pp(inp2))
