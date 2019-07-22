#!/usr/bin/env python

import math

def roundup100(x):
	"""return integer value for x rounded up to next hundred"""
	return int(math.ceil(x / 100.0)) * 100

def roundup_int(x, m):
	"""return integer value for x rounded up to next multiple of m"""
	return int(math.ceil(x / float(m))) * m
