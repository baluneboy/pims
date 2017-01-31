#!/usr/bin/env python

import os
import shelve

def write_shelve(dbfile, d):
    s = shelve.open(dbfile)
    for key in d:
        s[key] = d[key]
    s.close()

def read_shelve(dbfile):
    d = shelve.open(dbfile)
    return d

if __name__ == "__main__":
    dbfile = '/tmp/test_shelf.db'
    #d = { 'an_int': 10, 'a_float':9.5, 'some_string':'Sample data' }
    #write_shelve(dbfile, d)
    x = read_shelve(dbfile)
    print x