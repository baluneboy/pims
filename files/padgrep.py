#!/usr/bin/env python

from pims.pad.create_header_dict import parse_header  # FIXME old [but trusted] code


# FIXME move this function to where it's home should be?
def merge_two_dicts(x, y):
    """return merge of 2 dicts"""
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def find_pad_keys(pad_hdr, float_keys):
    """return pad fields that match float_keys; e.g. SampleRate or CutoffFreq"""
    return {k: float(pad_hdr[k]) for k in float_keys}


def find_pad_subfields(pad_hdr, field, subfield):
    """return pad subfield that match key; e.g. SampleRate or CutoffFreq"""
    new_field = '_'.join([field, subfield])
    subdict2 = {new_field: pad_hdr[field][subfield]}
    return subdict2


def get_hdr_dict_fs_fc_loc_ssa(hdr_file):
    """return dict with header file SampleRate, CutoffFreq and DataCoordinateSystem's name"""
    ph = parse_header(hdr_file)
    fs_fc = find_pad_keys(ph, ['SampleRate', 'CutoffFreq'])
    ssa = find_pad_subfields(ph, 'DataCoordinateSystem', 'name')
    loc = find_pad_subfields(ph, 'SensorCoordinateSystem', 'comment')
    merge1 = merge_two_dicts(fs_fc, ssa)
    return merge_two_dicts(merge1, loc)


def demo_grep():
    hdr_file = '/Users/ken/Downloads/pad/2018_06_13_15_06_10.361-2018_06_13_15_06_24.359.121f04.header'
    hdr_file = '/misc/yoda/pub/pad/year2018/month06/day13/sams2_accel_121f04/2018_06_13_15_06_10.361-2018_06_13_15_06_24.359.121f04.header'
    print get_hdr_dict_fs_fc_loc_ssa(hdr_file)


if __name__ == '__main__':
    demo_grep()
