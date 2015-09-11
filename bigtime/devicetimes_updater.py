#!/usr/bin/env python

import datetime
#import operator
#import pandas as pd
#from pims.lib.typedlist import TypedList
#from pims.lib.transformeddict import TransformedDict
from pims.utils.pimsdateutil import doytimestr_to_datetime, datetime_to_doytimestr

class DeviceDict(dict):

    def __init__(self, *args, **kwargs):
        self.timestamp = datetime.datetime.now()
        self.filename = kwargs.pop('filename', None)
        self.begin = kwargs.pop('begin', None)
        if self.filename:
            super(DeviceDict, self).__init__()
            self.from_file()
        else:
            super(DeviceDict, self).__init__(*args)
    
    def __sub__(self, other):
        return len(self) - len(other)

    def get_host_time(self):
        the_time = [ value for key, value in self.items() if key[1].lower().startswith('host') ]
        if len(the_time) == 1:
            return the_time[0]
        else:
            return None

    def get_ku_time(self):
        the_time = [ value for key, value in self.items() if key[0].lower().startswith('ku_aos') ]
        if len(the_time) == 1:
            return the_time[0]
        else:
            return None
    
    def get_dh_dk(self):
        host_time = self.get_host_time()
        ku_time = self.get_ku_time()
        for k, v in self.iteritems():
            dh = (v - host_time).total_seconds()
            dk = (v - ku_time).total_seconds()
            self[k] = (v, dh, dk)
            
    def from_file(self):
        delims = {'begin': 'middle', # from begin to middle
                  'middle': 'end'}   # from middle to end
        endstr = delims[self.begin]
        with open(self.filename, 'r') as f:
            parsing = False
            for line in f.readlines():
                
                if line.startswith(endstr):
                    parsing = False

                if parsing:
                    timestr, device, category = line.rstrip('\n').split(' ')
                    dtm = doytimestr_to_datetime(timestr)
                    self[(device, category)] = dtm

                if line.startswith(self.begin):
                    parsing = True

def demo_deltas():
    txt_file = '/tmp/sensortimesTest.txt'
    dd1 = DeviceDict(filename=txt_file, begin='begin')
    dd2 = DeviceDict(filename=txt_file, begin='middle')
    
    for devdict in [dd1, dd2]:
        devdict.get_dh_dk()
        for k, v in devdict.iteritems():
            print devdict.timestamp, v, k
        print '- - - - - - - - - - - - - -'
    
    devices = list( set(dd1.keys()).union(set(dd2.keys())) )
    for dev in devices:
        if dd1.has_key(dev) and dd2.has_key(dev):
            dt = (dd2[dev][0] - dd1[dev][0]).total_seconds()
            print dev, dd2[dev][1], dd2[dev][2], dt

demo_deltas()
raise SystemExit

class OBSOLETE_DeviceTime(object):
    
    def __init__(self, timestr, device, category):
        self.timestr = timestr
        self.device = device
        self.category = category
        self.dtm = doytimestr_to_datetime(timestr)
    
    def __str__(self):
        s = '%s: %s' % (self.__class__.__name__, self.dtm)
        s += ' %s' % self.device
        s += ' %s' % self.category
        return s

class OBSOLETE_DeviceList(TypedList):
    
    _delims = {'begin': 'middle',
               'middle': 'end'}
       
    def __init__(self, *args, **kwargs):
        self.devices = set()
        self.filename = kwargs.pop('filename', None)
        self.begin = kwargs.pop('begin', None)
        if self.filename:
            super(DeviceList, self).__init__(DeviceTime)
            self._append_from_file()
        else:
            self.filename = None
            super(DeviceList, self).__init__(DeviceTime, *args)

    def __setitem__(self, i, v):
        self.check(v)
        self.list[i] = v
        self.devices.add( v.device )

    def insert(self, i, v):
        self.check(v)
        self.list.insert(i, v)
        self.devices.add( v.device )
        
    def _append_from_file(self):
        self.end = self._delims[self.begin]
        with open(self.filename, 'r') as f:
            parsing = False
            for line in f.readlines():
                
                if line.startswith(self.end):
                    parsing = False

                if parsing:
                    timestr, device, category = line.rstrip('\n').split(' ')
                    self.append( DeviceTime(timestr, device, category) )

                if line.startswith(self.begin):
                    parsing = True
    
    def __str__(self):
        s = '%s with %d members of %s' % (self.__class__.__name__, len(self), self.oktypes)
        for devtime in self:
            s += '\n%s' % str(devtime)
        return s

###device_list1 = DeviceList(filename='/tmp/sensortimesTest.txt', begin='begin') # empty container for many DeviceTime(s)
###device_list2 = DeviceList(filename='/tmp/sensortimesTest.txt', begin='middle') # empty container for many DeviceTime(s)
###print device_list1
###print device_list2
###print sorted( device_list2.devices.union(device_list1.devices) )
####device_list1.to_dict(1)
####device_list2.to_dict(2)
###raise SystemExit

class OBSOLETE_TimeTuple(tuple):

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
                timestr, device, category = line.rstrip('\n').split(' ')
                try:
                    dtm = doytimestr_to_datetime(timestr)
                    if category.lower() == 'host':
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
                timestr, device, category = line.rstrip('\n').split(' ')
                inds.append(device)
                try:
                    dtm = doytimestr_to_datetime(timestr)
                    if category.lower() == 'host':
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

#txt_file = '/misc/yoda/www/plots/user/sams/status/sensortimes.txt'
txt_file = '/tmp/sensortimesTest.txt'
df = textfile_to_dataframe(txt_file)
delta_series = df['two'] - df['one']
print delta_series
print delta_series['122-f02']
#print dd1
#print '--------------'
#print dd2