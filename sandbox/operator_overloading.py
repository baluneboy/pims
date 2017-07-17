#!/usr/bin/env python

# One way to think of overloading is that we use the same thing in different ways depending on what we're dealing with
# or...operator overloading lets the operator do different operations depending on the type of its arguments.

# --------------------------------------------------------------------------------------------------------------------
# Example #1 - an example of using the "+" operator to do int addition (a mathematical sum)
#              HERE WE USE PLUS SYMBOL/OPERATOR FOR INT ADDITION
a = 1  # an int will be the 1st argument in the addition operation we do below
b = 2  # an int will be the 2nd argument in the addition operation we do below

# This block of comments applies to the single line of code below, which is: c = a + b
# OPERATION: add 2 ints
# OPERATOR : plus symbol (this, you will see in Example #2, is what gets "overloaded")
# RESULT   : sum (or "integer sum" to put it better)
# ARGUMENTS: 2 ints (first argument is a, second argument is b)
c = a + b

print "The sum of 2 integers a and b is: %d" % c


# --------------------------------------------------------------------------------------------------------------------
# Example #2 - an example of operator overloading the "+" operator/symbol to do string concatenation
#              HERE WE USE PLUS SYMBOL/OPERATOR FOR STRING CONCATENATION
first_name = 'Eric'     # string
last_name = 'Cartman'   # string

# This block of comments applies to the line of code below, which is: full_name = first_name + last_name
# OPERATION: concatenate 2 strings
# OPERATOR : plus symbol (this got "overloaded" - it's not addition here; for strings it's concatenation)
# RESULT   : concatenation
# ARGUMENTS: 2 strings: first_name and last_name
full_name = first_name + last_name

print "The concatenation of 2 strings here is %s" % full_name
