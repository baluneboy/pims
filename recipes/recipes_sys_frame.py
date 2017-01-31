# use sys._getframe() -- it returns a frame object, whose attribute
# f_code is a code object, whose attribute co_name is the name:
import sys
this_function_name = sys._getframe().f_code.co_name

# the frame and code objects also offer other useful information:
this_line_number = sys._getframe().f_lineno; print this_line_number

this_filename = sys._getframe().f_code.co_filename
print this_filename

# also, by calling sys._getframe(1), you can get this information
# for the *caller* of the current function.  So you can package
# this functionality up into your own handy functions:
def whoami():
    import sys
    return sys._getframe(1).f_code.co_name

me  = whoami()
print me

# this uses argument 1, because the call to whoami is now frame 0.
# and similarly:
def callersname():
    import sys
    return sys._getframe(2).f_code.co_name

him = callersname()
print him