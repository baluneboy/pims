#!/usr/bin/env python

from xml.dom.minidom import parse
from pims.utils.pimsdateutil import pad_fullfilestr_to_start_stop


def get_sub_field(h, field, sub_fields):
    """ get sub fields using xml parser """
    d = {}
    for k in sub_fields:
        element = h.documentElement.getElementsByTagName(field)[0]
        d[k] = str(element.getAttribute(k))
    return d


def parse_header(hdr_file):
    """ use xml parsing to build header """
    h = parse(hdr_file)
    dHeader = {'header_file': hdr_file}

    start, stop = pad_fullfilestr_to_start_stop(hdr_file)
    dHeader['TimeZero'] = start

    fields = ['SampleRate', 'CutoffFreq', 'DataQualityMeasure', 'SensorID', 'ISSConfiguration']
    for field in fields:
        dHeader[field] = str(h.documentElement.getElementsByTagName(field)[0].childNodes[0].nodeValue)

    dHeader['DataType'] = str(h.documentElement.nodeName)

    if dHeader['SensorID'] not in ['ossbtmf', 'radgse', 'ossraw']:
        dHeader['Gain'] = str(h.documentElement.getElementsByTagName('Gain')[0].childNodes[0].nodeValue)

    sub_coord = ['x', 'y', 'z', 'r', 'p', 'w', 'name', 'time', 'comment']
    dHeader['SensorCoordinateSystem'] = get_sub_field(h, 'SensorCoordinateSystem', sub_coord)
    dHeader['DataCoordinateSystem'] = get_sub_field(h, 'DataCoordinateSystem', sub_coord)
    dHeader['GData'] = get_sub_field(h, 'GData', ['format', 'file'])

    if dHeader['SensorID'] == 'ossraw':
        dHeader['ElementsPerRec'] = 6
    elif dHeader['SensorID'] == 'radgse':
        dHeader['ElementsPerRec'] = 14
    else:
        dHeader['ElementsPerRec'] = 4

    return dHeader


def get_sams_simple_header(hdr_file):
    hdr = parse_header(hdr_file)
    hdr['data_cols'] = hdr.pop('ElementsPerRec')
    hdr['tzero'] = hdr.pop('TimeZero')
    hdr['sensor'] = hdr.pop('SensorID')
    hdr['fs'] = float(hdr.pop('SampleRate'))
    hdr['fc'] = float(hdr.pop('CutoffFreq'))
    hdr['system'] = hdr.pop('DataType').split('_')[0]
    scs = hdr.pop('SensorCoordinateSystem')
    dcs = hdr.pop('DataCoordinateSystem')
    hdr['location'] = scs['comment']
    hdr['coord_sys'] = dcs['name']
    hdr['xyz_coords'] = [float(v) for v in [scs['x'], scs['y'], scs['z']]]
    hdr['rpy_orient'] = [float(v) for v in [dcs['r'], dcs['p'], dcs['w']]]

    # dict comprehension for keeping only the keys (and values) we want
    keeps = ['data_cols', 'tzero', 'sensor', 'fs', 'fc', 'system', 'location', 'coord_sys', 'xyz_coords', 'rpy_orient']
    return {k: hdr[k] for k in keeps}


def demo_hdr():
    """read/parse PAD header file"""
    hdr_file = 'G:/data/pad/year2020/month04/day05/sams2_accel_121f03/2020_04_05_00_05_15.785+2020_04_05_00_15_15.803.121f03.header'
    hdr = get_sams_simple_header(hdr_file)
    for k, v in hdr.items():
        print(k, v)


if __name__ == '__main__':
    demo_hdr()
