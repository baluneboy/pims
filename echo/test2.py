#!/usr/bin/env python

import pickle

from myring import retrieve, SECRETSDB_FILE

# Load or create secrets database:
with open(SECRETSDB_FILE) as f:
    db = pickle.load(f)
if db == {}: raise IOError

### Test (put your code here) ###
print 'username', retrieve('username')
print 'password7', retrieve('password7')
