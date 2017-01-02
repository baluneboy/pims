#!/usr/bin/env python

import os
import re
import ConfigParser
from dateutil import parser

from pims.nautilus.handbookme import MyCommand, run_timeout_cmd, alert
from pims.patterns.dirnames import _SENSORCHECKDIR_PATTERN
from pims.nautilus.popstrings import _POPCONFIG_MFILE_FMT_STR

# map plot type to a disposal class
disposal_map = {'powspecdens': PowerSpectralDensityDisposal }

# a sensor pair to check
class CheckSensorPair(object):
    """a sensor pair to check"""
    
    def __init__(self, config_ini_file):
        self.dir = os.path.dirname(config_ini_file)
        self.config_ini_file = config_ini_file
        self.popconfig_mfile = os.path.join(self.dir, 'popconfig.m')
        config = ConfigParser.ConfigParser()
        config.read(self.config_ini_file)
        self.start = parser.parse( config.get('GmtRange', 'start') )
        self.stop = parser.parse( config.get('GmtRange', 'stop') )
        self.host1 = config.get('Sensors', 'host1')                
        self.sensor1 = config.get('Sensors', 'sensor1')
        self.host2 = config.get('Sensors', 'host2')                
        self.sensor2 = config.get('Sensors', 'sensor2')
        self.plot_params = dict( config.items('PlotParams') )
        print self.plot_params
        
    def __str__(self):
        s = 'CheckSensorPair\n'
        s += '%s is START GMT\n' % self.start
        s += '%s is STOP GMT\n'  % self.stop
        s += '%s on %s vs. %s on %s\n' % (self.sensor1, self.host1, self.sensor2, self.host2)
        return s

    # /home/pims/dev/programs/bash/matlaboverlaypsd3.bash "2016-03-30 10:50:00" "2016-03-30 11:00:00" tweek 121f03 mr-hankey 121f04 /misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Check_Sensor_DD-MON-YEAR
    def get_bash_command(self):
        s = '/home/pims/dev/programs/bash/matlaboverlaypsd3.bash '
        s += '"%s" "%s" ' % (self.start, self.stop)
        s += '%s %s %s %s %s' % (self.host1, self.sensor1, self.host2, self.sensor2, self.dir)
        return s
    
    def write_popconfig_mfile(self):
        if os.path.exists(self.popconfig_mfile):
            print '%s already exists' % self.popconfig_mfile
            bln_ok = False
        else:
            startstr = self.start.strftime("%d-%b-%Y,%H:%M:%S.000")
            stopstr = self.stop.strftime("%d-%b-%Y,%H:%M:%S.000")
            fmtstr = _POPCONFIG_MFILE_FMT_STR
            s = fmtstr % (self.dir, self.sensor1, self.sensor2, startstr, stopstr)
            with open(self.popconfig_mfile, 'w') as f:
                f.write(s)
            bln_ok = True
        return bln_ok

# create stub for config.ini
def create_config_ini(config_file):
    """create stub for config.ini"""
    with open(config_file, 'w') as f:     
        f.write('[GmtRange]\n')
        f.write("start = '2016-03-30 10:50:00'\n")
        f.write("stop  = '2016-03-30 11:00:00'\n")
        f.write('\n')
        f.write('[Sensors]\n')
        f.write('host1   = tweek\n')
        f.write('sensor1 = 121f03\n')
        f.write('host2   = mr-hankey\n')
        f.write('sensor2 = 121f04\n')

# take action from nautilus script based on curdir
def main(curdir):
    """take action from nautilus script based on curdir"""
    
    # Strip off uri prefix
    if curdir.startswith('file:///'):
        curdir = curdir[7:]

    # Verify curdir matches pattern (this works even in build subdir, which is a good thing)
    match = re.search( re.compile(_SENSORCHECKDIR_PATTERN), curdir )

    ########################################################################################
    # this is where we do branching based on if we have properly named curdir and config.ini
    if match:
  
        try:
            
            dir_date = parser.parse(match.group('date')).date()
            
            # get/process config file
            config_file = os.path.join(curdir, 'config.ini')
            if os.path.exists(config_file):
                # config.ini exists
                csp = CheckSensorPair(config_file); raise SystemExit
                wrote_ok = csp.write_popconfig_mfile()
                if not wrote_ok:
                    msg = 'did not write popconfig.m okay, maybe it existed already?'
                else:
                    cmd = csp.get_bash_command()
                    print cmd
                    return_code, elapsed_sec = run_timeout_cmd(cmd, timeout_sec=999)
                    if return_code == 0:
                        msg = str(csp)
                    else:
                        msg = 'bad return code from %s' % cmd
            else:
                # config.ini does NOT exist
                create_config_ini(config_file)
                msg = '%s did NOT exist here, so created an example for you' % os.path.basename(config_file)
        
        except Exception, name:
            msg = name
    
    else:
        
        msg = 'ABORT: ignore non-matching dirname'

    response = alert( '%s' % msg ) # 1 for "OK", 2 for "Show Log", otherwise -4 (for eXited out)

#main('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Sensor_Check_2016-04-01')
#raise SystemExit

if __name__ == "__main__":
    # Get nautilus current uri and take action in main func
    curdir = os.environ.get('NAUTILUS_SCRIPT_CURRENT_URI', os.curdir)
    main(curdir)


