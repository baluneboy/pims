#!/usr/bin/env python

import os
import sys
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from dateutil import parser, relativedelta
from pims.config.conf import get_db_params
from pims.lib.niceresult import NiceResult
from pims.pad.daily_set import _TWODAYSAGO
from pims.utils.pimsdateutil import datetime_to_ymd_path
from pims.database.pimsquery import get_mams_bias_cal

_SCHEMA, _UNAME, _PASSWD = get_db_params('pimsquery')

# input parameters
defaults = {
'day':  _TWODAYSAGO,   # string for day of interest, e.g. '2017-03-22'
}
parameters = defaults.copy()

# EXAMPLE QUERY (on stan) WITHOUT THE date_format PART
# select from_unixtime(time),97.5-((ascii(substring(packet,26,1))*256+ascii(substring(packet,25,1)))/512) AS mpcs1,97.5-((ascii(substring(packet,48,1))*256+ascii(substring(packet,47,1)))/512) AS mpcs2 from housek where time >= unix_timestamp('2017-03-25 00:00:00') and time < unix_timestamp('2017-03-26 00:00:00') order by time asc;

def query_mams_temps(day, table='housek', schema='pims', host='stan', user=_UNAME, passwd=_PASSWD):
    """return dataframe of mpcs1 and mpcs2 temperatures on desired day"""
    constr = 'mysql://%s:%s@%s/%s' % (user, passwd, host, schema)
    d2 = day + relativedelta.relativedelta(days=1)
    t1 = day.strftime('%Y-%m-%d 00:00:00')
    t2 = d2.strftime('%Y-%m-%d 00:00:00')
    query_str = "select date_format(from_unixtime(time),'%%%%Y-%%%%m-%%%%d %%%%H:%%%%i:%%%%S'),97.5-((ascii(substring(packet,26,1))*256+ascii(substring(packet,25,1)))/512) AS mpcs1,97.5-((ascii(substring(packet,48,1))*256+ascii(substring(packet,47,1)))/512) AS mpcs2 from %s where time >= unix_timestamp('%s') and time < unix_timestamp('%s') order by time asc;" % (table, t1, t2)
    #print query_str
    engine = create_engine(constr, echo=False)
    df = pd.read_sql_query(query_str, con=engine)
    return df

def query_mams_bias_cal(last=10):
    df = get_mams_bias_cal(last=last)
    print df
    
def parameters_ok():
    """check for reasonableness of parameters"""    

    try:
        parameters['day'] = parser.parse( parameters['day'] ).date()
    except Exception, e:
        print 'could not get day input as date object: %s' % e.message
        return False
    
    return True # all OK; otherwise, return False somewhere above

def print_usage():
    """print helpful text how to run the program"""
    #FIXME with git keyword sub via following:
    # http://stackoverflow.com/questions/11534655/git-keyword-substitution-like-those-in-subversion
    #print version << BETTER GO AT THIS???
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def plot_data(df, day):
    if len(df) == 0:
        # if query did not return results (so empty dataframe, df), then plot "no data" textbox
        plt.text(0.5, 0.5, "no data", size=50, rotation=30, ha='center', va='center',
                 bbox=dict(boxstyle='round',
                           ec=(1.0, 0.5, 0.5),
                           fc=(1.0, 0.8, 0.8),
                          )
                )
    else:
        axes = df[['mpcs2','mpcs1']].plot(subplots=True, figsize=(11,8.5), colormap='jet_r')
        for a in axes:
            a.xaxis.grid(True, which="both")
            a.yaxis.grid(True)
            a.tick_params(labelsize=8)    
        plt.setp(axes[1].get_xticklabels(), rotation=45, horizontalalignment='right')    
    
    plt.suptitle('MAMS Temps on GMT %s' % day.strftime('%Y-%m-%d'))
    #plt.show()

    pth = datetime_to_ymd_path(day, base_dir='/misc/yoda/www/plots/batch')    
    if os.path.isdir(pth):
        fname = os.path.join(pth, day.strftime('%Y-%m-%d_mams_temps') + '.pdf')
        plt.savefig(fname, dpi=80, format='pdf')
        print 'wrote %s' % fname
    else:
        print 'directory not found %s' % pth
    
def process_data(params):
    """process data with parameters here (after we checked them earlier)"""
       
    # get dataframe of day's worth of results from Eric's query to plot 2 mams temps (mpcs1 and mpcs2)
    df = query_mams_temps(params['day'])

    df.columns = ['GMT', 'mpcs1', 'mpcs2']
    df = df.set_index(['GMT']) # I think this helps with datetime on xlabels?
    #print df
    
    plot_data(df, params['day'])
    
    # FIXME with better status/code output logic
    if len(df) > 0:
        # plot results and return zero (success) code
        return 0
    else:
        # plot blank and return failure code (2 for now)
        return 2

def play_catchup():
    """get plots since 01-Jan-2017"""
    start_date = datetime.datetime(2017, 1,  1).date()
    end_date =   datetime.datetime(2017, 3, 26).date()
    date_range = pd.date_range(start=start_date, end=end_date)
    params = {}
    for d in date_range:
        params['day'] = d.date()
        process_data(params)
        plt.close('all')

def main(argv):
    """describe main routine here"""
    
    # parse command line
    for p in sys.argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parameters_ok():
            nr = NiceResult(process_data, parameters)
            nr.do_work()
            result = nr.get_result()
            return result # result is zero for unix success
        
    print_usage()  

if __name__ == '__main__':
    """run main with cmd line args and return exit code"""
    sys.exit(main(sys.argv))
    #query_mams_bias_cal(last=10)
