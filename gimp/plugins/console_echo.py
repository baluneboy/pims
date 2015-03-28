#! /usr/bin/env python
from gimpfu import *

def echo(*args):
	"""Print the arguments on standard output"""
	print "echo:", args

register(
  "console_echo", "", "", "", "", "",
  #"<Toolbox>/Xtns/Languages/Python-Fu/Test/_Console Echo", "",
  "<Image>/_Xtns/_Console Echo", "",
  [
  (PF_STRING, "arg0", "argument 0", "test string"),
  (PF_INT,    "arg1", "argument 1", 100          ),
  (PF_FLOAT,  "arg2", "argument 2", 1.2          ),
  (PF_COLOR,  "arg3", "argument 3", (0, 0, 0)    ),
  ],
  [],
  echo
  )

main()