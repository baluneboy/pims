#!/usr/bin/env python

import operator
import pandas as pd
from pims.utils.pimsdateutil import doytimestr_to_datetime, datetime_to_doytimestr

class TimeTuple(tuple):

    def __init__(self, b):
        super(TimeTuple, self).__init__(tuple(b))
    
    def __sub__(self, other):
        return tuple(map(operator.sub, self, other))

#x = TimeTuple( (1, 2, 7) )
#y = TimeTuple( (1, float('NaN'), 3) )
#print x-y
#print y-x
#raise SystemExit
    
def OLDtextfile_to_dataframe(txt_file):
    delta_dict1 = {}
    delta_dict2 = {}
    with open(txt_file, 'r') as f:
        parsing = False
        delta_dict = delta_dict1
        for line in f.readlines():
            
            if line.startswith('end'):
                parsing = False

            if line.startswith('middle'):
                delta_dict = delta_dict2
                continue
            
            # this relies on bigtime (butters) host entry being first in order to get delta_host info
            if parsing:
                timestr, device, suffix = line.rstrip('\n').split(' ')
                try:
                    dtm = doytimestr_to_datetime(timestr)
                    if suffix.lower() == 'host':
                        host = device
                        dtm_host = dtm
                    delta_host = (dtm - dtm_host).total_seconds()
                    delta_ku = None
                    delta_dict[device] = (datetime_to_doytimestr(dtm)[:-7], dtm, delta_host, delta_ku)
                except:
                    #print timestr, device, None, None
                    delta_dict[device] = (timestr, None, None, None)
                    
            if line.startswith('begin'):
                parsing = True
    
    df = pd.DataFrame(delta_dict1.items())
    print df
    return delta_dict1, delta_dict2

def textfile_to_dataframe(txt_file):
    inds_one, tups_one = [], []
    inds_two, tups_two = [], []
    with open(txt_file, 'r') as f:
        parsing = False
        inds, tups = inds_one, tups_one # start with one
        for line in f.readlines():
            
            if line.startswith('end'):
                parsing = False

            if line.startswith('middle'):
                inds, tups = inds_two, tups_two # switch to two
                continue
            
            # this relies on bigtime (butters) host entry being first in order to get delta_host info
            if parsing:
                timestr, device, suffix = line.rstrip('\n').split(' ')
                inds.append(device)
                try:
                    dtm = doytimestr_to_datetime(timestr)
                    if suffix.lower() == 'host':
                        host = device
                        dtm_host = dtm
                    delta_host = (dtm - dtm_host).total_seconds()
                    delta_ku = float('NaN')
                    tups.append( TimeTuple( (dtm, delta_host, delta_ku)))
                except:
                    tups.append( TimeTuple( (float('NaN'), float('NaN'), float('NaN'))))
                    
            if line.startswith('begin'):
                parsing = True
    
    delta_dict = {
        'one': pd.Series(tups_one, index=inds_one),
        'two': pd.Series(tups_two, index=inds_two)
        }
    df = pd.DataFrame(delta_dict)
    return df

txt_file = '/misc/yoda/www/plots/user/sams/status/sensortimes.txt'
df = textfile_to_dataframe(txt_file)
delta_series = df['two'] - df['one']
print delta_series
print delta_series['122-f02']
#print dd1
#print '--------------'
#print dd2