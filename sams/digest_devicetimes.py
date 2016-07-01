#!/usr/bin/env python

import os
import sys
import datetime
import subprocess
from itertools import combinations
import pandas as pd

from pims.utils.pimsdateutil import doytimestr_to_datetime, datetime_to_doytimestr

MAX_ABS_DELTA_KU = 2
SOUND_DEVICES = ['122-f02', '122-f03', '122-f04', '122-f07', '121f02rt', '121f03rt', '121f04rt', '121f05rt', '121f08rt']

# input parameters
defaults = {
#                comma-sep values for plus groups    
'groups':       '122-f07+121f04rt,122-f02+122-f03+Ku_AOS,122-f02+121f03rt,122-f04+121f02rt+121f05rt',
'gmtoffset':    '0', # hour offset from this system clock's time and GMT (like -4 or -5 for Eastern time)
}
parameters = defaults.copy()

# check for reasonableness of parameters entered on command line
def parametersOK():
    """check for reasonableness of parameters entered on command line"""    

    # get gmt offset (hours)
    parameters['gmtoffset'] = int(parameters['gmtoffset'])
    if parameters['gmtoffset'] not in [0, -4, -5]:
        print 'Unexpected gmtoffset %d' % parameters['gmtoffset']
        return False

    # split out the groups into lists
    tmplist = parameters['groups'].split(',')
    parameters['groups'] = [ g.split('+') for g in tmplist]

    return True # all OK; otherwise, return False somewhere above

def printUsage():
    """print short description of how to run the program"""
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def OLD_COMBO_STYLE_digest_file(txt_file='/misc/yoda/www/plots/user/sams/status/sensortimes.txt'):
    """digest device times file"""
    
    host_now = datetime.datetime.now() + datetime.timedelta(hours=parameters['gmtoffset'])
    
    # build delta_dict: {  deviceN:  (timestr, datetime_of_timestr, deltasec_bigtime_host, deltasec_this_machine) }
    # ...could be like: { '122-f03': ('2015:154:12:07:16', datetime.datetime(2015, 6, 3, 12, 7, 16), -284.0, -276.62259) }
    # ...could be like: { 'butters': ('2015:154:12:12:00', datetime.datetime(2015, 6, 3, 12, 12   ),    0.0,    7.37741) }
    # ...could be like: { 'es03rt':  ('yyyy:ddd:hh:mm:ss', None,                                       None,       None)  }
    delta_dict = {}
    with open(txt_file, 'r') as f:
        parsing = False
        for line in f.readlines():
            
            if line.startswith('end'):
                parsing = False
                
            if parsing:
                timestr, device, suffix = line.rstrip('\n').split(' ')
                try:
                    dtm = doytimestr_to_datetime(timestr)
                    if suffix.lower() == 'host':
                        host = device
                        dtm_host = dtm
                    delta_host = (dtm - dtm_host).total_seconds()
                    my_delta = (dtm - host_now).total_seconds()
                    #print '%s %s %.1f %.1f' % (datetime_to_doytimestr(dtm)[:-7], device, delta_host, my_delta)
                    delta_dict[device] = (datetime_to_doytimestr(dtm)[:-7], dtm, delta_host, my_delta)
                except:
                    #print timestr, device, None, None
                    delta_dict[device] = (timestr, None, None, None)
                    
            if line.startswith('begin'):
                parsing = True
                
    #for k, v in delta_dict.iteritems():
    #    print k, v

    grp_count = 0
    grp_time = datetime.datetime.now()
    #err_devs = []
    for g in parameters['groups']:
        grp_count += 1
        combo_count = 0
        for c in combinations(g, 2):
            combo_count += 1
            print 'Group', grp_count, 'Combo', combo_count, ':', c
            print c[0], delta_dict[c[0]]
            print c[1], delta_dict[c[1]]
            print 'delta for (device1 - device2) = %.1f seconds' % (delta_dict[c[0]][1] - delta_dict[c[1]][1]).total_seconds()
            print 'delta for (device1 - bt_host) = %.1f seconds' % (delta_dict[c[0]][2])
            print 'delta for (device1 - my_host) = %.1f seconds' % (delta_dict[c[0]][3])
            print
            
            delta_dev1_dev2 = (delta_dict[c[0]][1] - delta_dict[c[1]][1]).total_seconds()
            delta_dev1_bthost = delta_dict[c[0]][2]
            
            flagstr = 'ERROR'
            if abs(delta_dev1_dev2) < 3:
                if (9 < delta_dev1_bthost) and (delta_dev1_bthost < 18):
                    flagstr = 'OKAY'
                else:
                    flagstr = 'WARN'
                    
            #now,group,combo,device1,device2,delta_dev1_dev2,delta_dev1_bthost,delta_dev1_myhost,delta_dev2_bthost,delta_dev2_myhost,timestr1,dtm1,timestr2,dtm2,flagstr               
            row = '\n%s,%d,%d,%s,%s,%.1f,%.1f,%.1f,%.1f,%.1f,%s,%s,%s,%s,%s' % (
                grp_time.strftime('%Y-%m-%d %H:%M:%S'),
                grp_count,
                combo_count,
                c[0],
                c[1],
                delta_dev1_dev2,
                delta_dev1_bthost,
                delta_dict[c[0]][3],
                delta_dict[c[1]][2],
                delta_dict[c[1]][3],
                delta_dict[c[0]][0],
                delta_dict[c[0]][1],
                delta_dict[c[1]][0],
                delta_dict[c[1]][1],
                flagstr
            )
            append2csv(row)

        print '-' * 11
        
    ## keep last few entries
    #df = csv_to_lastfew_dataframe()
    
    # write to csv
    df.to_csv('/misc/yoda/www/plots/user/sams/status/digest.csv', index=False)

def digest_file(txt_file='/misc/yoda/www/plots/user/sams/status/sensortimes.txt'):
    """digest device times file"""
    
    host_now = datetime.datetime.now() + datetime.timedelta(hours=parameters['gmtoffset'])
    
    #########################################################
    ### FIRST PASS GETS HOST DELTA AND JUST KU DELTA AS NONE
    #                                                                                      None INITIALLY for last in tuple
    #                                                                                      V
    # build delta_dict: {  deviceN:  (timestr, datetime_of_timestr, deltasec_bigtime_host, deltasec_ku) }
    # ...could be like: { '122-f03': ('2015:154:12:07:16', datetime.datetime(2015, 6, 3, 12, 7, 16), -284.0, None) }
    # ...could be like: { 'butters': ('2015:154:12:12:00', datetime.datetime(2015, 6, 3, 12, 12   ),    0.0, None) }
    delta_dict = {}
    with open(txt_file, 'r') as f:
        parsing = False
        for line in f.readlines():
            
            if line.startswith('end'):
                parsing = False
                
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
                    #print '%s %s %.1f %.1f' % (datetime_to_doytimestr(dtm)[:-7], device, delta_host, delta_ku)
                    delta_dict[device] = (datetime_to_doytimestr(dtm)[:-7], dtm, delta_host, delta_ku)
                except:
                    #print timestr, device, None, None
                    delta_dict[device] = (timestr, None, None, None)
                    
            if line.startswith('begin'):
                parsing = True

    #########################################################
    ### SECOND PASS GETS KU DELTA VALUES
    #
    ku_time = delta_dict['Ku_AOS'][1]

    # dummy record for machine [jimmy] that is doing digesting
    delta_ku = (host_now - ku_time).total_seconds()
    delta_host = (host_now - dtm_host).total_seconds()
    #print "digester", datetime_to_doytimestr(host_now)[:-7], delta_host, delta_ku,
    row = "\n%s,%s,%.1f,%.1f" % ("digester", datetime_to_doytimestr(host_now)[:-7], delta_host, delta_ku)
    
    # now iterate to get other delta_ku's
    any_bad_delta_ku = False
    for key in sorted(delta_dict):
        dtm = delta_dict[key][1]
        delta_ku = (dtm - ku_time).total_seconds()
        if abs(delta_ku) > MAX_ABS_DELTA_KU and (key in SOUND_DEVICES):
            any_bad_delta_ku = True
        delta_host = delta_dict[key][2]
        #print key, datetime_to_doytimestr(dtm)[:-7], delta_host, delta_ku,
        row += "\n%s,%s,%.1f,%.1f" % (key, datetime_to_doytimestr(dtm)[:-7], delta_host, delta_ku)
        
    append2csv(row, csv_files=['/misc/yoda/www/plots/user/sams/status/digest.csv'])
    
    # if any bad delta ku, then play very alarmed sound; otherwise, mild europa
    if any_bad_delta_ku:
        p = subprocess.Popen(['play', '/home/pims/Music/very_alarmed.mp3'])
    else:
        now = datetime.datetime.now()
        if now.minute == 0:
            p = subprocess.Popen(['play', '/home/pims/Music/mild_europa.mp3'])
        elif now.minute == 30:
            p = subprocess.Popen(['play', '/home/pims/Music/halfhourchime.mp3'])

def append2csv(row, csv_files=['/misc/yoda/www/plots/user/sams/status/devicedigest.csv', '/misc/yoda/www/plots/user/sams/status/digest.csv']):
    for csv_file in csv_files:
        fd = open(csv_file, 'a')
        fd.write(row)
        fd.close()

def csv_to_lastfew_dataframe(n=4, csv_file='/misc/yoda/www/plots/user/sams/status/digest.csv'):
    df = pd.read_csv(csv_file)
    lastfew = sorted(pd.unique(df['now']))[-n:]
    df_recentfew = df[df['now'].isin(lastfew)]
    df_recentfew = df_recentfew.sort(['now', 'group', 'combo'], ascending=[False, True, True])
    return df_recentfew

def show_params():
    print 'GMT Offset = %d' % parameters['gmtoffset']
    grp_count = 0
    print 'GROUPS'
    for g in parameters['groups']:
        grp_count += 1
        combo_count = 0
        for c in combinations(g, 2):
            combo_count += 1
            print 'Group', grp_count, 'Combo', combo_count, ':', c
        print '-' * 11

def main(argv):
    """describe what this routine does here"""
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parametersOK():
            #show_params()
            digest_file()
            return 0
    printUsage()  

if __name__ == '__main__':
    sys.exit(main(sys.argv))
    