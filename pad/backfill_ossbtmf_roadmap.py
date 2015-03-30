#!/usr/bin/env python
version = '$Id$'

import os
import re
import sys
import time
import logging
import logging.config
import datetime
import threading
import subprocess
import numpy as np
from dateutil import parser
from datetimeranger import DateRange
from pims.utils.commands import timeLogRun
from pims.files.log import OssbtmfBackfillRoadmapsLog
from pims.files.utils import listdir_filename_pattern
from pims.utils.pimsdateutil import datetime_to_ymd_path

_TWO_DAYS_AGO = str( datetime.datetime.now().date() - datetime.timedelta(days=2) )

# input parameters
defaults = {
'dateStart':    _TWO_DAYS_AGO, # like '2013-10-23'; see DateRange for flexibility
'dateStop':     _TWO_DAYS_AGO, # like '2013-10-27'; see DateRange for flexibility
'batch_dir':    '/misc/yoda/www/plots/batch', # where to look for JPGs needed for PDF convert
}
parameters = defaults.copy()

def params_ok(log):
    """check for reasonableness of parameters entered on command line"""
    # parse start/stop
    try:
        parameters['dateStart'] = parser.parse( parameters['dateStart'] )
        parameters['dateStop'] = parser.parse( parameters['dateStop'] )
    except ValueError, e:
        log.error('Bad input trying to parse date got ValueError: "%s"' % e.message )
        return False
    parameters['date_range'] = DateRange( parameters['dateStart'], parameters['dateStop'] )
    
    # check dir exists    
    if not os.path.exists(parameters['batch_dir']):
        log.error('Bad batch_dir %s does not exist' % parameters['batch_dir'])
        return False
    
    # inputs seem okay
    record_inputs(log)
    return True

def record_inputs(log):
    for k,v in parameters.iteritems():
        log.info( k + ':' + str(v) )
    log.info( '='*99 )
    
def print_usage():
    """print short description of how to run the program"""
    print version
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])

def get_day_files(day, batch_dir, log, ext):
    """Get list of ossbtmf roadmap 'ext' files for day."""
    fname_pattern = day.strftime('%Y_%m_%d_\d{2}_ossbtmf_roadmap.' + ext)
    pth = datetime_to_ymd_path(day, base_dir=batch_dir)
    if not os.path.exists(pth):
        log.warn('No such path %s during check for JPGs.' % pth)
        return None
    files = listdir_filename_pattern(pth, fname_pattern)
    if not files:
        log.warn('no %s files along %s' % (ext, pth))
    return files

def get_day_jpgs(day, batch_dir, log):
    """Get list of ossbtmf roadmap JPGs for day."""
    qs_dir = os.path.join(batch_dir, 'Quasi-steady')
    return get_day_files(day, qs_dir, log, 'jpg')

def get_day_pdfs(day, batch_dir, log):
    """Check for ossbtmf roadmap PDF files for day."""
    return get_day_files(day, batch_dir, log, 'pdf')

def run_backfill(day, batch_dir, jpg_files, log):
    """Convert JPGs to PDFs and move the PDFs to batch dir."""
    ymd_path = datetime_to_ymd_path(day, base_dir=batch_dir)
    count = 0
    if jpg_files:
        for jpg_file in jpg_files:
            pdf_file = jpg_file.replace('.jpg','.pdf')
            cmdstr = 'convert %s %s && mv %s %s/' % (jpg_file, pdf_file, pdf_file, ymd_path)
            timeLogRun(cmdstr, 44, log) # timeout of 44 seconds
            count += 1
    return count

def run_ike_repair(years, log):
    """Run processRoadmap.py on ike to get new PDFs into the fold"""
    # ssh ike 'cd /home/pims/roadmap && python /home/pims/roadmap/processRoadmap.py logLevel=3 mode=repair repairModTime=5 | grep nserted'
    for repair_year in years:
        log.info('Run ike repair for year %d.' % repair_year)
        cmdstr = "ssh ike 'cd /home/pims/roadmap && python /home/pims/roadmap/processRoadmap.py logLevel=3 mode=repair repairModTime=5 repairYear=%d | grep Inserted'" % repair_year
        timeLogRun(cmdstr, 900, log) # timeout of 900 seconds for 15 minutes

def backfill_ossbtmf_roadmaps(date_range, batch_dir, log):
    """
    Convert daily ossbtmf roadmap JPGs to PDFs and move for web display
    for entirety of date range.
    """
    log.info("Try backfill of ossbtmf roadmap PDFs for %s." % date_range)

    # Loop BACKWARDS in time over days in date range
    repair_years = set( (date_range.stop.year,) )
    num_days_backfilled = 0
    d = date_range.stop
    while d >= date_range.start:
        log.debug('Day %s.' % d.date())
        jpg_files = get_day_jpgs(d, batch_dir, log)
        if jpg_files:
            pdf_files = get_day_pdfs(d, batch_dir, log)
            if not pdf_files:
                log.info('Backfilling for day %s' % d.date())
                num_back_filled = run_backfill(d, batch_dir, jpg_files, log)
                repair_years.add( d.year )
                log.debug('Years %s' % repair_years)
                num_days_backfilled += 1
            else:
                log.info('NO NEED TO BACKFILL FOR DAY %s' % d.date())
        d -= datetime.timedelta(days=1)
    
    log.info('Backfilled a total of %d days.' % num_days_backfilled)
    
    # If any backfills, then do repair routine on ike
    if num_days_backfilled > 0:
        run_ike_repair(repair_years, log)
    
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
        # set up logging
        bname = os.path.splitext( os.path.basename(__file__) )[0]
        log_config_file = os.path.join('/home/pims/dev/programs/python/pims/files', bname + '_log.conf')
        logging.config.fileConfig(log_config_file)
        log = logging.getLogger('inputs')
        if params_ok(log):
            try:
                log = logging.getLogger('process')
                backfill_ossbtmf_roadmaps(parameters['date_range'], parameters['batch_dir'], log)
            except Exception, e:
                # Log error
                log.process.error( e.message )
                return -1
            # Message with time when done
            log.debug('Done %s.\n' % datetime.datetime.now() + '-'*99)
            return 0
    print_usage()  

if __name__ == '__main__':
    sys.exit(main(sys.argv))
