#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
from progressbar import ProgressBar

def demo1():
	pbar = ProgressBar().start()
	for i in xrange(100):
		time.sleep(0.1)
		pbar.update(i+1)
	pbar.finish()

if __name__ == '__main__':
	demo1()