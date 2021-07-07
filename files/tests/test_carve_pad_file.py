import os
import pytest
import tempfile
import shutil
import datetime
from pims.files.utils import carve_pad_file, files_differ
from ugaudio.load import pad_read, pad_readall
from pims.files.utils import rezero_pad_file

REF_DIR = os.path.dirname(__file__)


def read_num_recs(pad_file, num_recs):
    """return array with first num_recs records from pad_file"""
    # FIXME we are assuming 4 floats (t,x,y,z) per sample (per record)
    return pad_read(pad_file, count=num_recs*4)


def rezero_was_success(pad_file, rate):
    """return True if pad_file was reset to start time with zero"""
    a = read_num_recs(pad_file, 2)  # read first 2 records
    if not (pytest.approx(a[0][0], 0.001) == 0.0):
        return False
    delta = a[1][0] - a[0][0]
    return pytest.approx(delta, 0.001) == (1.0 / rate)


def simple_rezero_was_success(bname):
    """return Tre if a simple rezero_pad_file was success; otherwise, False"""
    pad_file = os.path.join(os.path.dirname(__file__), bname)
    rate = 500.0
    with tempfile.NamedTemporaryFile(prefix=bname) as temp_file:
        shutil.copyfile(pad_file, temp_file.name)
        rezero_pad_file(temp_file.name, rate)
        ref_file = os.path.join(REF_DIR, bname + '.rezeroed5recs')
        temp_file.flush()
        result = not files_differ(ref_file, temp_file.name)
    return result


def simple_carve_was_success(prefix):
    """return True if a simple carve_pad_file was success; otherwise, False"""
    pad_file = os.path.join(os.path.dirname(__file__), prefix)
    prev_grp_stop = datetime.datetime(2020, 10, 6, 0, 0, 0, 4000)
    rate = 500.0
    new_prefix = prefix.replace('+', '-')
    with tempfile.NamedTemporaryFile(prefix=new_prefix) as temp_file:
        shutil.copyfile(pad_file, temp_file.name)
        new_pad_file = carve_pad_file(temp_file.name, prev_grp_stop, rate)
        ref_file = os.path.join(REF_DIR, new_prefix + '.carved3recs')
        temp_file.flush()
        # print('files_differ is', files_differ(ref_file, temp_file.name), 'and it should be False')
        result = not files_differ(ref_file, new_pad_file)
        # no_plus_in_name =
    shutil.rmtree('/tmp/quarantined')
    return result


def test_rezero_pad_file():
    bname = '2020_04_01_00_05_13.393+2020_04_01_00_15_13.404.121f03'
    was_rezero_ok = simple_rezero_was_success(bname)
    assert was_rezero_ok is True


def test_carve_pad_file_not_renamed():
    prefix = '2020_10_06_00_00_00.000-2020_10_06_00_00_00.008.121f99'
    was_carve_ok = simple_carve_was_success(prefix)
    assert was_carve_ok is True


def test_carve_pad_file_with_rename():
    prefix = '2020_10_06_00_00_00.000+2020_10_06_00_00_00.008.121f00'
    was_carve_ok = simple_carve_was_success(prefix)
    assert was_carve_ok is True


if __name__ == '__main__':
    pass
    # pad_file = '/home/pims/dev/programs/python/pims/files/tests/2020_10_06_00_00_00.000-2020_10_06_00_00_00.008.121f00.carved3recs'
    # # pad_file = '/home/pims/dev/programs/python/pims/files/tests/2020_10_06_00_00_00.000-2020_10_06_00_00_00.008.121f99.carved3recs'
    # a = pad_readall(pad_file)
    # print(a)
    #
    # rezero_pad_file(pad_file, 500.0)
    #
    # a = pad_readall(pad_file)
    # print(a)
    #
    # raise SystemExit

    # prefix = '2020_10_06_00_00_00.000-2020_10_06_00_00_00.008.121f99'
    # prefix = '2020_10_06_00_00_00.000+2020_10_06_00_00_00.008.121f00'
    # was_carve_ok = simple_carve_was_success(prefix)
    # print(was_carve_ok)



    # prev_grp_stop, rate = datetime.datetime(2020, 10, 6, 0, 0, 0, 4000), 500.0
    # pad_file1 = '/tmp/2020_10_06_00_00_00.000-2020_10_06_00_00_00.008.121f55'
    # new_pad_file = carve_pad_file(pad_file1, prev_grp_stop, rate)
    #
    # pad_file2 = '/tmp/2020_10_06_00_00_00.000+2020_10_06_00_00_00.008.121f33'
    # new_pad_file = carve_pad_file(pad_file2, prev_grp_stop, rate)
