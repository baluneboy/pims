#!/usr/bin/python

import fortune

fortunes_file = '/Users/ken/dev/programs/python/pims/sandbox/data/fortunes/fortunes'
print fortune.get_random_fortune(fortunes_file)