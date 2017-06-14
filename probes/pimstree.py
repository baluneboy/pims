#!/usr/bin/env python

"""PIMS Trees"""

import os
import re
from json2html import json2html
import pandas as pd

from pims.utils.gists import tree, add_tree_value
from pims.files.utils import filter_filenames
from pims.utils.pimsdateutil import datetime_to_ymd_path, unix2dtm
from pims.files.filter_pipeline import FileFilterPipeline, MatchSensorAxRoadmap, BigFile
from pims.patterns.probepats import _ROADMAP_PDF_BLANKS_PATTERN, _OSSBTMF_ROADMAP_PDF_FILENAME_PATTERN
from pims.database.samsquery import query_pimsmap_roadmap, get_roadmap_data_record, do_insert_pimsmap_roadmap


class PimsTree(object):
    """description"""

    def __init__(self, *args, **kwargs):
        """Constructor for PimsTree"""

        pass


class NextTree(object):
    """description"""

    def __init__(self, *args, **kwargs):
        """Constructor for NextTree"""

        pass


class ThirdTree():
    """describe"""

    def __init__(self, *args, **kwargs):
        """Constructor for ThirdTree"""

        pass


def get_day_roadmap_pdf_files(base_dir, day, basename_pat):
    """return list of all roadmap PDFs for a given day"""
    day_dir = datetime_to_ymd_path(day, base_dir=base_dir)
    pattern = '.*' + basename_pat
    return list(filter_filenames(day_dir, re.compile(pattern).match))


def get_day_sensor_axis_roadmap_pdf_files(day_roadmap_pdf_files, sensor, axis):
    """return list of roadmap spg files for given day, sensor and axis"""
    # FIXME empirically determine good threshold value for min_bytes arg in BigFile
    if sensor == 'ossbtmf':
        ffp = FileFilterPipeline(BigFile(min_bytes=20))        
    else:
        ffp = FileFilterPipeline(MatchSensorAxRoadmap(sensor, axis), BigFile(min_bytes=20))
    return list(ffp(day_roadmap_pdf_files))


def get_loop_params(parameters):
    dir_name = parameters['dir_name']
    start_date = parameters['first_day']
    end_date = parameters['last_day']
    sensors = parameters['sensors']
    if sensors == ['ossbtmf']:
        axes = ['3']
        basename_pat = _OSSBTMF_ROADMAP_PDF_FILENAME_PATTERN
    else:
        axes = parameters['axes']
        basename_pat = _ROADMAP_PDF_BLANKS_PATTERN.replace('SENSOR', '.*').replace('PLOT', '.*').replace('AXIS', '\w')
    date_range = pd.date_range(start=start_date, end=end_date)
    return dir_name, start_date, end_date, sensors, axes, basename_pat, date_range


def get_roadmap_sensor_tree(parameters):
    dir_name, start_date, end_date, sensors, axes, basename_pat, date_range = get_loop_params(parameters)
    sensor_tree = tree()    
    for day in date_range:
        day_pdf_files = get_day_roadmap_pdf_files(dir_name, day, basename_pat)
        for sensor in sensors:
            for axis in axes:
                pdf_files = get_day_sensor_axis_roadmap_pdf_files(day_pdf_files, sensor, axis)
                sensor_tree[sensor][day.strftime('%Y-%m-%d')][axis] = [os.path.basename(f) + ' ' + unix2dtm(os.path.getmtime(f)).strftime('%H:%M:%S') for f in pdf_files]
    return sensor_tree


def bname_in_roadmap_recs(fname, roadmap_recs):
    bname = os.path.basename(fname)
    return bname in roadmap_recs['name'].values


def get_fs(fname):
    bname = os.path.basename(fname)    
    return float(bname.split('_')[8].lstrip('roadmaps').rstrip('.pdf'))


def get_pdf_file_status(f, roadmap_recs):
    bname = os.path.basename(f)
    tstamp = unix2dtm(os.path.getmtime(f)).strftime('%H:%M:%S')
    fsstr = '%.2f' % get_fs(f)
    is_roadmap_rec = bname_in_roadmap_recs(f, roadmap_recs)
    if is_roadmap_rec:
        query_str = 'insert; not needed for pimsmap.roadmap (twss)'
        data_record = None
    else:
        # get eight-tuple data_record like following:
        # ('2017_04_02_16_00_00.000_121f03_spgs_roadmaps500.pdf', 3, 2, 2017, 4, 2, 500.000, '2017-04-02')
        query_str, data_record = get_roadmap_data_record(bname)
    return bname, tstamp, query_str, data_record


def get_roadmap_day_tree(parameters):
    dir_name, start_date, end_date, sensors, axes, basename_pat, date_range = get_loop_params(parameters)    
    day_tree = tree()    
    for sensor in sensors:
        for day in date_range:
            day_pdf_files = get_day_roadmap_pdf_files(dir_name, day, basename_pat)
            if parameters['more_details']:
                roadmap_recs = query_pimsmap_roadmap(day, sensor)
                for axis in axes:
                    pdf_files = get_day_sensor_axis_roadmap_pdf_files(day_pdf_files, sensor, axis)
                    #day_tree[day.strftime('%Y-%m-%d')][sensor][axis] = [os.path.basename(f) + ' ' + unix2dtm(os.path.getmtime(f)).strftime('%H:%M:%S') + ' ' + '%.2f' % get_fs(f) + ' ' + str(bname_in_roadmap_recs(f, roadmap_recs)) + ' ' + 'insertstr' for f in pdf_files]
                    day_sensor_axis = list()
                    for f in pdf_files:
                        bname, tstamp, query_str, data_record = get_pdf_file_status(f, roadmap_recs)
                        if parameters['do_insertion'] and data_record:
                            prefix = 'do'
                            do_insert_pimsmap_roadmap(data_record)
                        else:
                            prefix = 'NO'
                        day_sensor_axis.append(' '.join([bname, tstamp, prefix, query_str]))
                    day_tree[day.strftime('%Y-%m-%d')][sensor][axis] = day_sensor_axis
            else:
                for axis in axes:
                    pdf_files = get_day_sensor_axis_roadmap_pdf_files(day_pdf_files, sensor, axis)
                    day_tree[day.strftime('%Y-%m-%d')][sensor][axis] = [os.path.basename(f) + ' ' + unix2dtm(os.path.getmtime(f)).strftime('%H:%M:%S') for f in pdf_files]
    return day_tree


def get_roadmap_tree(parameters):
    if parameters['order_by_day']:
        roadmap_tree = get_roadmap_day_tree(parameters)
    else:
        roadmap_tree = get_roadmap_sensor_tree(parameters)
    return roadmap_tree


def write_html(json_str):
    html_str = json2html.convert(json_str)
    with open("/misc/yoda/www/plots/user/pims/roadmap_probe.html", "w") as html_file:
        html_file.write( _HEADER + html_str + _FOOTER )         
