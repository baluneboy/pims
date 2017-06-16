#!/usr/bin/env python

"""PIMS Trees"""

import os
import re
import json
from json2html import json2html
import pandas as pd

from pims.utils.gists import tree, add_tree_value
from pims.files.utils import filter_filenames
from pims.pad.daily_set import _TWODAYSAGO
from pims.utils.pimsdateutil import datetime_to_ymd_path, unix2dtm
from pims.files.filter_pipeline import FileFilterPipeline, MatchSensorAxRoadmap, BigFile
from pims.patterns.probepats import _ROADMAP_PDF_BLANKS_PATTERN, _OSSBTMF_ROADMAP_PDF_FILENAME_PATTERN
from pims.database.samsquery import query_pimsmap_roadmap, get_roadmap_data_record, do_insert_pimsmap_roadmap

_DEFAULTSENSORS = ['121f02', '121f03', '121f04', '121f05', '121f08']
_DEFAULTAXES = ['s']
_DEFAULTPATTERN = _ROADMAP_PDF_BLANKS_PATTERN.replace('SENSOR', '.*').replace('PLOT', '.*').replace('AXIS', '\w')


class RoadmapDayProbeTree(object):
    """A probe tree for roadmap PDF files.

    Attributes:
        dir_name:     string directory name; default: '/misc/yoda/www/plots/batch'
        start_date:   datetime start date
        end_date:     datetime end date
        sensors:      list of strings for sensors; default: ['121f02', '121f03', '121f04', '121f05', '121f08']
        axes:         list of strings for axes; default: ['s']
        pattern:      string regular expression for basename pattern of PDF files of interest
    """

    def __init__(self, start_date, end_date=_TWODAYSAGO, dir_name='/misc/yoda/www/plots/batch',
                 sensors=_DEFAULTSENSORS, axes=_DEFAULTAXES, pattern=_DEFAULTPATTERN):
        """Constructor for RoadmapDayProbeTree"""
        self.dir_name = dir_name
        self.start_date = start_date
        self.end_date = end_date
        self.sensors = sensors
        self.axes = axes
        self.pattern = pattern
        pass

    def __str__(self):
        """return this object as a string"""
        s = str(self.__class__.__name__)
        # s += '\nunder ' + self.dir_name
        # s += '\nfor files like ' + self.pattern
        s += '\nfrom   : ' + self.start_date
        s += '\nto     : ' + self.end_date
        s += '\nsensors: ' + ','.join(self.sensors)
        s += '\naxes   : ' + ','.join(self.axes)
        return s

    def __repr__(self):
        """return unambiguous representation of this object"""
        return str(self.__class__) + '[' + str(self) + ']'

    def get_roadmap_day_tree(self, more_details=False, fix_db=False):
        date_range = pd.date_range(start=self.start_date, end=self.end_date)
        day_tree = tree()
        for sensor in self.sensors:
            for day in date_range:
                day_pdf_files = self.get_day_roadmap_pdf_files(day)
                if more_details:
                    roadmap_recs = query_pimsmap_roadmap(day, sensor)
                    for axis in self.axes:
                        pdf_files = get_day_sensor_axis_roadmap_pdf_files(day_pdf_files, sensor, axis)
                        #day_tree[day.strftime('%Y-%m-%d')][sensor][axis] = [os.path.basename(f) + ' ' + unix2dtm(os.path.getmtime(f)).strftime('%H:%M:%S') + ' ' + '%.2f' % get_fs(f) + ' ' + str(bname_in_roadmap_recs(f, roadmap_recs)) + ' ' + 'insertstr' for f in pdf_files]
                        day_sensor_axis = list()
                        for f in pdf_files:
                            bname, tstamp, query_str, data_record = get_pdf_file_status(f, roadmap_recs)
                            if fix_db and data_record:
                                prefix = 'do'
                                do_insert_pimsmap_roadmap(data_record)
                            else:
                                prefix = 'NO'
                            day_sensor_axis.append(' '.join([bname, tstamp, prefix, query_str]))
                        day_tree[day.strftime('%Y-%m-%d')][sensor][axis] = day_sensor_axis
                else:
                    for axis in self.axes:
                        pdf_files = get_day_sensor_axis_roadmap_pdf_files(day_pdf_files, sensor, axis)
                        day_tree[day.strftime('%Y-%m-%d')][sensor][axis] = [os.path.basename(f) + ' ' + unix2dtm(os.path.getmtime(f)).strftime('%H:%M:%S') for f in pdf_files]
        return day_tree

    def get_day_roadmap_pdf_files(self, day):
        """return list of ALL roadmap PDFs for a given day"""
        day_dir = datetime_to_ymd_path(day, base_dir=self.dir_name)
        pattern = '.*' + self.pattern
        return list(filter_filenames(day_dir, re.compile(pattern).match))


def get_day_sensor_axis_roadmap_pdf_files(day_roadmap_pdf_files, sensor, axis):
    """return list of roadmap spg files for given day, sensor and axis"""
    # FIXME empirically determine good threshold value for min_bytes arg in BigFile
    if sensor == 'ossbtmf':
        ffp = FileFilterPipeline(BigFile(min_bytes=20))        
    else:
        ffp = FileFilterPipeline(MatchSensorAxRoadmap(sensor, axis), BigFile(min_bytes=20))
    return list(ffp(day_roadmap_pdf_files))


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

if __name__ == '__main__':
    start_date = _TWODAYSAGO
    roadmap_probe_tree = RoadmapDayProbeTree(start_date)
    print roadmap_probe_tree
    my_tree = roadmap_probe_tree.get_roadmap_day_tree()
    json_str = json.dumps(my_tree, sort_keys=True, indent=3, separators=(',', ':'))
    print json_str