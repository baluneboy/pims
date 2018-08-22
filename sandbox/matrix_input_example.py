import json
import numpy
import sys

data = numpy.array(json.loads(sys.argv[1]))
# do you calculation
print data

# Now you can run on the command line

# python matrix_input_example.py '[[1,0,0],[0,1,0],[0,0,1]]'


print """

Enter the change of basis matrix from sensor to SSA coordinates
like this:
xA = M * xS

where M =
a b c
d e f
g h i

enter like this '[[a,b,c],[d,e,f],[g,h,i]]'

"""
