#!/usr/bin/env python

import re
import warnings

def method_1(*args):
    return 'method 1'

def method_2(*args):
    return 'method 2'

def method_3(*args):
    return 'method 3'


my_pats = {}
my_pats[ re.compile('^(.*), (.*) Handover US to RS$') ] = method_1
my_pats[ re.compile('^(.*), (.*) Free Drift for Docking \(Prog on DC-1\) Start$') ] = method_2
my_pats[ re.compile('^(.*), (.*) Free Drift for Docking \(Prog on DC-1\) Cease$') ] = method_3
my_pats[ re.compile('^(.*), (.*) Mnvr to Post-Docking LVLH TEA Start$') ] = method_1
my_pats[ re.compile('^(.*), (.*) Mnvr to Post-Docking LVLH TEA Cease$') ] = method_2
my_pats[ re.compile('^(.*), (.*) Handover RS to US Momentum Management$') ] = method_3
my_pats[ re.compile('^(.*), (.*) Plot gvt3 Start$') ] = method_1
my_pats[ re.compile('^(.*), (.*) Plot gvt3 Cease$') ] = method_2
my_pats[ re.compile('^(.*), (.*) Plot gvt3 Ceas.$') ] = method_3


def execute_method_for(str):
    
    # Match each regex on the string
    matches = ( (regex.match(str), f) for regex, f in my_pats.iteritems() )

    # Filter out empty matches, and extract groups
    matches = ( (match.groups(), f) for match, f in matches if match is not None )


    # Apply all the functions
    outputs = []
    for args, f in matches:
        out = f(*args)
        outputs.append(out)
        
     # FIXME for multiple matches we are only returning first such match
    if len(outputs) > 1:
        warnings.warn("Found multiple matches mapping line to function.")
        outputs = outputs[0]
        
    return outputs


if __name__ == "__main__":
    
    lines = [
            '23-Dec-2015, 08:19 Handover US to RS',
            '23-Dec-2015, 10:27 Free Drift for Docking (Prog on DC-1) Start',
            '23-Dec-2015, 10:49 Free Drift for Docking (Prog on DC-1) Cease',
            '23-Dec-2015, 10:49 Mnvr to Post-Docking LVLH TEA Start',
            '23-Dec-2015, 11:11 Mnvr to Post-Docking LVLH TEA Cease',
            '23-Dec-2015, 11:37 Handover RS to US Momentum Management',
            '23-Dec-2015, 08:00 Plot gvt3 Start',
            '23-Dec-2015, 12:00 Plot gvt3 Cease',  
    ]
    
    for line in lines:
        outputs = execute_method_for(line)
        print line, outputs