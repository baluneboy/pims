#!/usr/bin/env python

import os
import glob
import datetime
import pandas as pd
from dateutil.parser import parse

from pims.files.filter_pipeline import FileFilterPipeline, MatchSensorAxRoadmap, MatchSensorPad
from pims.utils.pimsdateutil import datetime_to_roadmap_fullstub, datetime_to_ymd_path
from ugaudio.explore import minmax_stats, show_pad_minmax

_TWODAYSAGO = str(datetime.datetime.now().date() - datetime.timedelta(days=2))


def show_missing_roadmaps(end, start=None, sensor='121f03ten', axis='s', base_path='/misc/yoda/www/plots/batch'):
    """show what spgs roadmap PDFs are missing (just the hour part for a given day)"""
    if start is None:
        start = parse(end) - datetime.timedelta(days=7)
    for d in pd.date_range(start, end):
        print d.date(), sensor, 'spg' + axis, " > ",
        day_dir = os.path.dirname(datetime_to_roadmap_fullstub(d))
    
        # initialize processing pipeline (no file list as input yet)
        ffp = FileFilterPipeline(MatchSensorAxRoadmap(sensor, axis))
        
        # apply processing pipeline (now ffp is callable)
        # LIKE /misc/yoda/www/plots/batch/year2018/month01/day25/2018_01_25_00_00_00.000_121f04ten_spgs_roadmaps500.pdf
        day_files = glob.glob(os.path.join(day_dir, '*_%s_*roadmaps*.pdf' % sensor))
        if len(day_files) == 0:
            print 'MISSING---',
        else:
            for f in ffp(day_files):
                hh = f.split('_')[3]
                print hh,
        print ''


def show_padfiles_minmax(end, start=None, sensor='121f03', base_path='/misc/yoda/pub/pad'):
    """show file-by-file, per-axis min/max values for PAD data files"""
    
    if sensor.startswith('121f0'):
        subdir_prefix = 'sams2_accel_'
    elif sensor.startswith('es0'):
        subdir_prefix = 'samses_accel_'
    else:
        error('sensor was expected to start with 121f0 or es0')
        
    if start is None:
        start = parse(end) - datetime.timedelta(days=7)
    for d in pd.date_range(start, end):
        #print d.date(), sensor, "has",
        sensor_dir = os.path.join(datetime_to_ymd_path(d), subdir_prefix + sensor)
    
        # initialize processing pipeline (no file list as input yet)
        ffp = FileFilterPipeline(MatchSensorPad(sensor))
        
        # apply processing pipeline (now ffp is callable)
        # LIKE /misc/yoda/pub/pad/year2018/month01/day18/sams2_accel_121f03/2018_01_18_23_45_05.487+2018_01_18_23_54_44.137.121f03.header
        day_files = glob.glob(os.path.join(sensor_dir, '*.%s' % sensor))
        print '{:<10s} {:<10s} {:>5d} files'.format(str(d.date()), sensor, len(day_files))
        if len(day_files) > 0:
            for f in day_files:
                num_pts, max_mg_vals = minmax_stats(f)
                if any(max_mg_vals > 100):
                    #s = '{:>90s}'.format(os.path.basename(f))
                    s = '{:>158s}'.format(f)
                    #show_pad_minmax(num_pts, max_mg_vals)
                    n = '{:,}'.format(num_pts)
                    s += "\n{:>48s} pts w/max(abs(xyz)) in mg:".format(n)
                    s += "{:9.3f} {:9.3f} {:9.3f}".format(*max_mg_vals)
                    print s
                #print ''
        
        
def show_missing_quasisteady_estimates(end, start=None):
    """show what QS products are missing (ZBOT estimates CSV files and/or PDFs)"""
    #/misc/yoda/www/plots/batch/year2017/month12/day13/2017_12_13_00_00_00_ossbtmf_gvt3_historical_time-shifted_quasi-steady_estimate.pdf
    #/misc/yoda/www/plots/batch/year2017/month12/day13/2017_12_13_00_00_00_ossbtmf_gvt3_historical_time-shifted_quasi-steady_estimate.csv    
    if start is None:
        start = parse(end) - datetime.timedelta(days=7)
    
    for d in pd.date_range(start, end):
        pad_day_dir = datetime_to_ymd_path(d)
        bat_day_dir = os.path.dirname(datetime_to_roadmap_fullstub(d))
        zbot_pad_files = glob.glob(os.path.join(pad_day_dir, 'samses_accel_es09/*.header'))
        pdf_day_files = glob.glob(os.path.join(bat_day_dir, '*_ossbtmf_gvt3_historical_time-shifted_quasi-steady_estimate.pdf'))
        csv_day_files = glob.glob(os.path.join(bat_day_dir, '*_ossbtmf_gvt3_historical_time-shifted_quasi-steady_estimate.csv'))
        num_pad = len(zbot_pad_files)
        num_pdf = len(pdf_day_files)
        num_csv = len(csv_day_files)
        if num_pad > 0:
            if num_pdf == 0 or num_csv == 0:
                print '%s %d %d %d' % (d.date(), len(pdf_day_files), len(csv_day_files), len(zbot_pad_files))

def show_pad_tally(end, start=None, sensor='121f03', base_path='/misc/yoda/pub/pad'):
    """show how many PAD header files are on server"""
    
    if sensor.startswith('121f0'):
        subdir_prefix = 'sams2_accel_'
    elif sensor.startswith('es0'):
        subdir_prefix = 'samses_accel_'
    else:
        error('sensor was expected to start with 121f0 or es0')
        
    if start is None:
        start = parse(end) - datetime.timedelta(days=7)
    for d in pd.date_range(start, end):
        print d.date(), sensor, "   PADs  > ",
        sensor_dir = os.path.join(datetime_to_ymd_path(d), subdir_prefix + sensor)
        print sensor_dir, 
    
        # initialize processing pipeline (no file list as input yet)
        ffp = FileFilterPipeline(MatchSensorPad(sensor))
        
        # apply processing pipeline (now ffp is callable)
        # LIKE /misc/yoda/pub/pad/year2018/month01/day18/sams2_accel_121f03/2018_01_18_23_45_05.487+2018_01_18_23_54_44.137.121f03.header
        day_files = glob.glob(os.path.join(sensor_dir, '*%s.header' % sensor))
        if len(day_files) == 0:
            print 'MISSING---',
        else:
            print len(day_files), 'files',
        print ''    


if __name__ == "__main__":
    #end = _TWODAYSAGO
    suffix = 'one'
    for end in pd.date_range('2018-01-20', '2018-01-29'):
        for sensor in ['121f02', '121f03', '121f04', '121f05', '121f08', 'es09']:
            #print end.date()
            show_missing_roadmaps(end, start=end, sensor=sensor+suffix)
            #print '------------------'
            #print '------------------'
            #show_pad_tally(end, sensor=sensor)
        print '----------------------------------------------'

    #python -c 'from pims.files.missing_roadmaps import show_missing_roadmaps; sensor="es09one"; end="2018-01-29"; start="2018-01-28"; show_missing_roadmaps(end, start, sensor=sensor);'    