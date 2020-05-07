#!/usr/bin/env python

import math


def is_power_of_two(n):
    """Return True if n is a power of two."""
    if n <= 0:
        return False
    else:
        return n & (n - 1) == 0


def roundup100(x):
	"""return integer value for x rounded up to next hundred"""
	return int(math.ceil(x / 100.0)) * 100


def roundup_int(x, m):
	"""return integer value for x rounded up to next multiple of m"""
	return int(math.ceil(x / float(m))) * m
