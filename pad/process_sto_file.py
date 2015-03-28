#!/usr/bin/env python

import sys
from pims.pad.amp_kpi import convert_sto2xlsx

#stofile = '/misc/yoda/www/plots/batch/padtimes/2014_032-062_msg_cir_fir.sto'
#stofile = '/misc/yoda/www/plots/batch/padtimes/2014_077-091_cir_fir_pwr_sams.sto'
#stofile = '/misc/yoda/www/plots/batch/padtimes/2014_077-092_cir_fir_pwr_sams2min.sto'
#stofile = '/misc/yoda/www/plots/user/sams/playback/er34_msg_cir_fir.sto'
#stofile = '/misc/yoda/www/plots/user/sams/playback/er34_msg_cir_firX.sto'
#stofile = '/misc/yoda/www/plots/user/sams/playback/er34_msg_cir_fir_JanFeb.sto'
#stofile = '/misc/yoda/www/plots/user/sams/kpi/2014_04_sams_monthly_kpi.sto'

# process sto file to get amp kpi spreadsheet
def process_amp_kpi(stofile):
    """process sto file to get amp kpi spreadsheet"""
    
    # Open input stofile and figure out what GMT day range
    
    # process stofile
    convert_sto2xlsx(stofile)
    
    # EITHER do per-file dataframe with column appending (and necessary row trim/pad)
    # OR do the next block of code (BUT do not do both)

    ### # for each of grouped.csv files
    ###     # pad rows with zeros for missing days so we have one for each day of "this" month
    ###     #
    ###     
    ###     # trim first day of "next" month
    ###     #
    ### 
    ### # subprocess LIKE: "paste -d, *grouped.csv > 2014_04_grouped_pasted.csv"
    ### #
    
    # subprocess to zip all EXCEPT for final product spreadsheet
    #
    
if __name__ == "__main__":
    process_amp_kpi( sys.argv[1] )   
