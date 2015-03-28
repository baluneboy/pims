#!/usr/bin/env python

from StringIO import StringIO
example_url = '/home/pims/dev/programs/python/pims/sandbox/slist3traces.ascii'
stringio_obj = StringIO(file(example_url).read())
st = read(stringio_obj)

print st