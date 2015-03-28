#! /usr/bin/env python

from gimpfu import *
import re

def hasComments(s):
	"""return true if matches "^\d+$"; otherwise, return false"""
	pattern = re.compile('^\d+$')
	if pattern.match(s):
		return False # only digits found
	return True

def showLayerNames(*args):
	"""Print names of layers on standard output"""
	img = args[0]
	all_layers = img.layers
	print "number of layers:", len(all_layers)
	for l in all_layers:
		if hasComments(l.name):
			print "HAS COMMENTS:", l.name
			l.visible = True
		else:
			print "NO  COMMENTS:", l.name
			l.visible = False
			img.remove_layer(l)

register(
  "python_fu_showLayerNames", "", "", "", "", "",
  #"<Toolbox>/Xtns/Languages/Python-Fu/Test/_Console Echo", "",
  "<Image>/_Xtns/_showLayerNames", "",
  [
  (PF_STRING, "arg0", "argument 0", "press OK button now"),
  ],
  [],
  showLayerNames
  )

main()