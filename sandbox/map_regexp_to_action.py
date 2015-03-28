#!/usr/bin/env python

import re

def function_1(i1, i2):
    i1 = int(i1)
    i2 = int(i2)
    print 'action for two integers: %d and %d' % (i1, i2)
    
def function_2(s1, s2):
    print 'action for two strings:  %s and %s' % (s1, s2)

map_regexp_action = {}
map_regexp_action[re.compile('action_int12 (\d+) (\d+)')] = function_1
map_regexp_action[re.compile('action_str12 (\w+) (\w+)')] = function_2
   
def execute_function_for(str):
    #Match each regex on the string
    matches = (
        (regex.match(str), f) for regex, f in map_regexp_action.iteritems()
    )

    #Filter out empty matches, and extract groups
    matches = (
        (match.groups(), f) for match, f in matches if match is not None
    )

    #Apply all the functions
    for args, f in matches:
        f(*args)
        
execute_function_for('action_int12 7 9')
execute_function_for('action_str12 quick silver')