#!/usr/bin/env python
version = '$Id$'

# TODO
# make this screen let like /usr/share/screenlets/MailCheck? NO, filled/killed BIG, FRONT window

import os
import re
import sys
import time
import datetime
from dateutil import parser, relativedelta
import subprocess
from recipes_configobj import GeneralConfig
from collections import deque
import threading
from daemon import runner
import numpy as np

# input parameters
defaults = {
             'output_dir': '/data/samscheck', # output path
             'summary':  [],                  # list summary
             'details':  [],                  # list details
             'config_file': '/home/pims/dev/programs/python/config/mysql.cfg', # config file for queries
             'refresh_minutes': '1',          # how often to refresh
}
parameters = defaults.copy()

def get_app_name():
    base = os.path.basename(sys.argv[0])
    return os.path.splitext(base)[0]

def get_obj(class_name, *args):
    object = globals()[class_name]
    return object(*args)

def moving_average(iterable, n=3):
    # moving_average([40, 30, 50, 46, 39, 44]) --> 40.0 42.0 45.0 43.0
    # http://en.wikipedia.org/wiki/Moving_average
    it = iter(iterable)
    d = deque(itertools.islice(it, n-1))
    d.appendleft(0)
    s = sum(d)
    for elem in it:
        s += elem - d.popleft()
        d.append(elem)
        yield s / float(n)

class SamsMonitor(object):

    def __init__(self):
        self.icu = deque([], 24)
        self.ee =  deque([], 24)
        self.gse = deque([], 24)
        self.state = 'unknown'

    def append_icu(self, itd):
        self.icu.append(itd)

    def append_ee(self, etd):
        self.ee.append(etd)

    def append_gse(self, gse):
        self.gse.append(gse)

    #def worst_delta(self, deltasec_now_icu, deltasec_now_gse, deltasec_icu_gse):
    #    deltas = np.array([deltasec_now_icu, deltasec_now_gse, deltasec_icu_gse])
    #    idx = np.where( abs(deltas) == max(abs(deltas)) )
    #    return deltas[idx][0]

    def delta_seconds(self):
        #now = datetime.datetime.now()
        #deltasec_now_icu = relativedelta.relativedelta( now, self.icu[-1].icu_dtm ).seconds
        #deltasec_now_gse = relativedelta.relativedelta( now, self.gse[-1].gse_tiss_dtm ).seconds
        deltasec_icu_gse = relativedelta.relativedelta( self.icu[-1].icu_dtm, self.gse[-1].gse_tiss_dtm ).seconds
        return deltasec_icu_gse #deltasec_now_icu, deltasec_now_gse, deltasec_icu_gse

    def growl(self, title, msg, timeout_msec, icon_file):
        if not os.path.isfile(icon_file): icon_file = '/home/pims/dev/programs/python/samslogs/icons/warning.png'
        cmd = 'notify-send -t %d --icon=%s SAMSCHK_%s "%s"' % (timeout_msec, icon_file, title, msg)
        subprocess.call([cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    def update(self):
        if len(self.gse) > 0 and len(self.icu) > 0:
            gse_latest = self.gse[-1]
            icu_latest = self.icu[-1]
            if gse_latest.aos_los == 'AOS':
                deltasec_icu_gse = self.delta_seconds()
                #delta_str = '{0:>5d}s=icu_gse\n{1:>5d}s=now_gse\n{2:>5d}s=now_icu'.format(deltasec_icu_gse, deltasec_now_icu, deltasec_icu_gse)
                if abs(deltasec_icu_gse) > 30: # AOS, BUT DELTA TOO BIG
                    title = '%s_WARNING' % gse_latest.aos_los
                    msg = '%s=ICU\n%s=GSE\nBIG DELTA = %ds' % ( icu_latest.icu_dtm, gse_latest.gse_tiss_dtm, deltasec_icu_gse )
                    timeout_msec = ( ( 60 * parameters['refresh_minutes'] * 1000 ) + 250 )
                    icon_file = '/home/pims/dev/programs/python/samslogs/icons/AOS_warning.png'
                    self.growl( title, msg, timeout_msec, icon_file )
                    self.state = 'alert'
                else: # AOS, AND DELTA OKAY
                    title = '%s_okay' % gse_latest.aos_los
                    msg = '%s=ICU\n%s=GSE\ndelta = %ds' % ( icu_latest.icu_dtm, gse_latest.gse_tiss_dtm, deltasec_icu_gse )
                    timeout_msec = 5000
                    icon_file = '/home/pims/dev/programs/python/samslogs/icons/AOS_okay.png'
                    self.growl( title, msg, timeout_msec, icon_file )
                    self.state = 'okay'
            else: # NOT AOS
                title = '%s_okay' % gse_latest.aos_los
                msg = '%s=ICU\n%s=GSE' % ( icu_latest.icu_dtm, gse_latest.gse_tiss_dtm )
                timeout_msec = 5000
                icon_file = '/home/pims/dev/programs/python/samslogs/icons/LOS.png'
                self.growl( title, msg, timeout_msec, icon_file )
                self.state = 'okay'

class SimpleQueryAOS(object):
    """simple query for AOS/LOS"""
    def __init__(self, host, schema, uname, pword):
        self.host = host
        self.schema = schema
        self.uname = uname
        self.pword = pword        
        self.query = 'select GSE_tiss_time , IF(GSE_aos_los =0, \\"LOS\\",\\"AOS\\") as aos_los from RT_ICU_gse_data;'
        self.run_query()

    def __str__(self):
        self.run_query()
        return '%s,%s' % (self.gse_tiss_dtm, self.aos_los)

    def run_query(self):
        cmdQuery = 'mysql --skip-column-names -h %s -D %s -u %s -p%s --execute="%s"' % (self.host, self.schema, self.uname, self.pword, self.query)
        p = subprocess.Popen([cmdQuery], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        results, err = p.communicate()
        search_pat = re.compile('(.*)\t([AL]OS)').search
        m = search_pat(results)
        gse_tiss_time, aos_los = m.group(1,2)
        self.header = 'class, gse_tiss_dtm, aos_los'
        self.gse_tiss_dtm = parser.parse(gse_tiss_time)
        self.aos_los = aos_los
        
class QueryData(object):

    def __init__(self, sams_monitor, host, schema, uname, pword):
        self.sams_monitor = sams_monitor
        self.host = host
        self.schema = schema
        self.uname = uname
        self.pword = pword

    def run_query(self):
        cmdQuery = 'mysql --skip-column-names -h %s -D %s -u %s -p%s --execute="%s"' % (self.host, self.schema, self.uname, self.pword, self.query)
        p = subprocess.Popen([cmdQuery], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        results, err = p.communicate()
        return results, err

class IcuTelemData(QueryData):

    def __init__(self, *args):
        QueryData.__init__(self, *args)
        self.query = 'select ICU_name,ICU_timestamp,ICU_out_air_temp from RT_ICU_telem_data;'
        results, err = self.run_query()
        search_pat = re.compile('(.*)\t(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\t(.*)').search
        m = search_pat(results)
        icu_str, icu_dtm, icu_out_air_temp_str = m.group(1,2,3)
        self.header = 'class, icu_str, icu_dtm, icu_out_air_temp'
        self.icu_str = icu_str
        self.icu_dtm = parser.parse(icu_dtm)
        self.icu_out_air_temp = float(icu_out_air_temp_str)

    def __str__(self):
        return '%s, %s, %s, %f' % (self.__class__.__name__, self.icu_str, self.icu_dtm, self.icu_out_air_temp)

    def register(self):
        #parameters['summary'].append( str(self) )
        self.sams_monitor.append_icu(self)

class IcuGseData(QueryData):

    def __init__(self, *args):
        QueryData.__init__(self, *args)
        self.query = 'select ICU_name,ICU_er_drw_current,ICU_er_drw_comm,ICU_ecw_word from RT_ICU_gse_data;'
        results, err = self.run_query()
        search_pat = re.compile('(.*)\t(.*)\t(.*)\t(.*)').search
        m = search_pat(results)
        icu_str, icu_er_drw_curr_str, icu_re_drw_comm_str, icu_ecw_word_str = m.group(1,2,3,4)
        self.header = 'class, icu_str, icu_er_drw_curr, icu_re_drw_comm, icu_ecw_word'
        self.icu_str = icu_str
        self.icu_er_drw_curr = float(icu_er_drw_curr_str)
        self.icu_re_drw_comm = int(icu_re_drw_comm_str)
        self.icu_ecw_word = int(icu_ecw_word_str)

    def __str__(self):
        return '%s\n%s, %s, %f, %d, %d' % (self.header, self.__class__.__name__, self.icu_str, self.icu_er_drw_curr, self.icu_re_drw_comm, self.icu_ecw_word)

    def register(self):
        #parameters['details'].append( str(self) )
        pass

class AosGseData(QueryData):

    def __init__(self, *args):
        QueryData.__init__(self, *args)
        self.query = 'select GSE_tiss_time , IF(GSE_aos_los =0, \\"LOS\\",\\"AOS\\") as aos_los, GSE_aos_los_status from RT_ICU_gse_data;'
        results, err = self.run_query()
        search_pat = re.compile('(.*)\t([AL]OS)\t(.*)').search
        m = search_pat(results)
        gse_tiss_time, aos_los, gse_aos_los_status = m.group(1,2,3)
        self.header = 'class, gse_tiss_dtm, aos_los, gse_aos_los_status'
        self.gse_tiss_dtm = parser.parse(gse_tiss_time)
        self.aos_los = aos_los
        self.gse_aos_los_status = gse_aos_los_status

    def __str__(self):
        return '%s\n%s, %s, %s, %s' % (self.header, self.__class__.__name__, self.gse_tiss_dtm, self.aos_los, self.gse_aos_los_status)

    def register(self):
        #parameters['summary'].append( str(self) )
        self.sams_monitor.append_gse(self)

class EeGseData(QueryData):

    def __init__(self, *args):
        QueryData.__init__(self, *args)
        self.query = 'select EE_id, er_dwr_current,er_drw_comm,ecw_word from RT_EE_gse_data order by EE_id;'
        results, err = self.run_query()
        self.lines = results.split('\n')
        self.search_pat = re.compile('(122-f0[2345])\t([-+]?\d*\.\d+|\d+)\t([-+]?\d*\.\d+|\d+)\t([-+]?\d*\.\d+|\d+)').match
        self.header = 'class, ee_str, er_drw_current, er_drw_comm, ecw_word'

    def __str__(self):
        s = '%s\n' % self.header
        for line in self.lines:
            m = self.search_pat(line)
            if not m: continue
            ee_str, er_dwr_current, er_drw_comm, ecw_word = m.group(1,2,3,4)
            s += '%s, %s, %s, %d, %d\n' % (self.__class__.__name__, ee_str, float(er_dwr_current), int(er_drw_comm), int(ecw_word))
        s= s[:-1]
        return s

    def register(self):
        #parameters['details'].append( str(self) )
        pass

class EeTelemData(QueryData):

    def __init__(self, *args):
        QueryData.__init__(self, *args)
        self.query = 'select EE_id, Timestamp,baseplate_temp,plus5_volt from RT_EE_telem_data where Timestamp IS NOT NULL order by EE_id;'
        results, err = self.run_query()
        self.lines = results.split('\n')
        self.search_pat = re.compile('(122-f0[2345])\t(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\t(.*)\t(.*)').match
        self.header = 'class, ee_str, dtm_ee, baseplate_temp, plus_5v'

    def __str__(self):
        s = '%s\n' % self.header
        for line in self.lines:
            m = self.search_pat(line)
            if not m: continue
            ee_str, dtm_ee, baseplate_temp_str, plus_5v_str = m.group(1,2,3,4)
            s += '%s, %s, %s, %f, %f\n' % (self.__class__.__name__, ee_str, dtm_ee, float(baseplate_temp_str), float(plus_5v_str))
        s= s[:-1]
        return s

    def register(self):
        #parameters['summary'].append( str(self) )
        self.sams_monitor.append_ee(self)

#def parametersOK():
#    """check for reasonableness of parameters"""
#    if not os.path.exists(parameters['output_dir']):
#        print 'output_dir (%s) does not exist' % parameters['output_dir']
#        return False
#
#    if os.path.isfile(parameters['config_file']):
#        validator_file = parameters['config_file'].replace('.cfg', '.ini')
#    else:
#        print 'The config_file "%s" does not exist.' % config_file
#        return False
#
#    if os.path.isfile(validator_file):
#        parameters['validator_file'] = validator_file
#    else:
#        print 'The validator_file "%s" does not exist.' % validator_file
#        return False
#
#    try:
#        parameters['refresh_minutes'] = int(parameters['refresh_minutes'])
#    except ValueError as e:
#        print 'Expected an integer for refresh_minutes.'
#        return False
#
#    return True # all OK, returned False (above) otherwise

def get_config(config_file, validator_file):
    # get schema info to query with
    gc = GeneralConfig(config_file, validator_file)
    config = gc.config
    app_name = get_app_name()
    dconfig = config['apps'][app_name]
    host = dconfig['host']
    schema = dconfig['schema']
    uname = dconfig['uname']
    pword = dconfig['pword']
    query_list = dconfig['query_list']
    return host, schema, uname, pword, query_list

def do_query_list_from_config_file(sams_monitor, app):
    for class_name in app.query_list:
        obj = get_obj(class_name, sams_monitor, app.host, app.schema, app.uname, app.pword)
        obj.register()
    sams_monitor.update()

def show_results():

    print 'vvv BEGIN DETAILS vvv'
    for d in parameters['details']:
        print d
    print '^^^ END DETAILS ^^^'

    print '\nvvv BEGIN SUMMARY vvv'
    for line in parameters['summary']:
        print line
    print '^^^ END SUMMARY ^^^'

#class SamsDaemonApp():
#    
#    def __init__(self):
#        self.stdin_path = '/dev/null'
#        self.stdout_path = '/dev/tty'
#        self.stderr_path = '/dev/tty'
#        self.pidfile_path =  '/tmp/samsd.pid'
#        self.pidfile_timeout = 5
#        if parametersOK():
#            self.sams_monitor = SamsMonitor()
#            self.config_file = parameters['config_file']
#            self.validator_file = parameters['validator_file']
#            self.refresh_minutes = parameters['refresh_minutes']
#            self.host, self.schema, self.uname, self.pword, self.query_list = get_config(self.config_file, self.validator_file)
#    
#    def run(self):
#        app = self
#        while True:
#            do_query_list_from_config_file(self.sams_monitor, app)
#            time.sleep(60.0*self.refresh_minutes)
#
#app = SamsDaemonApp()
#daemon_runner = runner.DaemonRunner(app)
#daemon_runner.do_action()
