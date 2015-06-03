#!/usr/bin/env python

import sys
import datetime

from pims.utils.pimsdateutil import doytimestr_to_datetime, datetime_to_doytimestr

#digest_devicetimes tshs=es03rt,es05rt,es06rt groups=122-f02+121f03rt+121f04rt,122-f03+121f05rt,122-f04+121f02rt+121f08rt gmtoffset=0

# input parameters
defaults = {
'tshs':         'es03rt,es05rt,es06rt',    # comma-sep values for non-grouped devices (TSHs)
'groups':       '122-f02+121f03rt+121f04rt,122-f03+121f05rt,122-f04+121f02rt+121f08rt', # comma-sep values for plus groups
'gmtoffset':    '0',                       # hour offset from this system clock time and GMT (like -4 for Eastern time)
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
    
    # split tshs string into list
    parameters['tshs'] = parameters['tshs'].split(',')

    # split groups string into list
    tmplist = parameters['groups'].split(',')
    parameters['groups'] = []
    for grp in [ g.split('+') for g in tmplist ]:
        d = {}
        d[grp[0]] = grp[1:]
        parameters['groups'].append(d)

    return True # all OK; otherwise, return False somewhere above

def printUsage():
    """print short description of how to run the program"""
    print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def digest_file(txt_file='/misc/yoda/www/plots/user/sams/status/sensortimes.txt'):
    """digest device times file"""
    
    host_now = datetime.datetime.now() + datetime.timedelta(hours=parameters['gmtoffset'])
    
    with open(txt_file, 'r') as f:
        parsing = False
        for line in f.readlines():
            
            if line.startswith('end'):
                parsing = False
                
            if parsing:
                timestr, device, suffix = line.rstrip('\n').split(' ')
                try:
                    dtm = doytimestr_to_datetime(timestr)
                    if suffix == 'host':
                        host = device
                        dtm_host = dtm
                    delta_host = (dtm - dtm_host).total_seconds()
                    my_delta = (dtm - host_now).total_seconds()
                    print '%s %s %.1f %.1f' % (datetime_to_doytimestr(dtm)[:-7], device, delta_host, my_delta)
                except:
                    print timestr, device, None, None
                    
            if line.startswith('begin'):
                parsing = True

def show_params():
    print 'TSHs'
    print parameters['tshs']
    print 'Groups'
    for g in parameters['groups']:
        print g
    print 'GMT Offset'
    print parameters['gmtoffset']    

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
            show_params()
            digest_file()
            return 0
    printUsage()  

if __name__ == '__main__':
    sys.exit(main(sys.argv))