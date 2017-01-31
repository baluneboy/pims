#!/usr/bin/env python

import os
import cPickle as pickle

def fileSaveSet(fname, s):
    """ save set to file, fname """
    file = open(fname, 'w')
    pickle.dump(s, file)
    file.close()

def fileLoadSet(fname):
    """ return set loaded from file """
    file = open(fname, 'r')
    s = pickle.load(file)
    file.close()
    return s

def demoDaySet():
    import num2word
    fname = '/tmp/trash.p'
    myList = [ ('one',1), ('two',2) ]
    s = set(myList)
    
    print s
    fileSaveSet(fname, s)
    del s
    
    for x in range(9):
        s = fileLoadSet(fname)
        s.add( (num2word.to_card(x), x) )
        print s
        fileSaveSet(fname, s)
        del s
    
if __name__ == "__main__":
    demoDaySet()
