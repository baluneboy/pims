import os
import pytest
import tempfile
import shutil
import datetime
from pims.files.utils import carve_pad_file, files_differ


def simple_carve_was_success(prefix):
    result = False
    pad_file = os.path.join(os.path.dirname(__file__), prefix)
    ref_dir = os.path.dirname(pad_file)
    prev_grp_stop = datetime.datetime(2020, 10, 6, 0, 0, 0, 4000)
    rate = 500.0
    new_prefix = prefix.replace('+', '-')
    with tempfile.NamedTemporaryFile(prefix=new_prefix) as temp_file:
        shutil.copyfile(pad_file, temp_file.name)
        new_pad_file = carve_pad_file(temp_file.name, prev_grp_stop, rate)
        ref_file = os.path.join(ref_dir, new_prefix + '.carved3recs')
        temp_file.flush()
        # print('files_differ is', files_differ(ref_file, temp_file.name), 'and it should be False')
        result = not files_differ(ref_file, new_pad_file)
        # no_plus_in_name =
    shutil.rmtree('/tmp/quarantined')
    return result


def test_carve_pad_file_not_renamed():
    prefix = '2020_10_06_00_00_00.000-2020_10_06_00_00_00.008.121f99'
    was_carve_ok = simple_carve_was_success(prefix)
    assert was_carve_ok is True


def test_carve_pad_file_with_rename():
    prefix = '2020_10_06_00_00_00.000+2020_10_06_00_00_00.008.121f00'
    was_carve_ok = simple_carve_was_success(prefix)
    assert was_carve_ok is True


if __name__ == '__main__':
    # prefix = '2020_10_06_00_00_00.000-2020_10_06_00_00_00.008.121f99'
    # prefix = '2020_10_06_00_00_00.000+2020_10_06_00_00_00.008.121f00'
    # was_carve_ok = simple_carve_was_success(prefix)
    # print(was_carve_ok)

    prev_grp_stop, rate = datetime.datetime(2020, 10, 6, 0, 0, 0, 4000), 500.0
    pad_file1 = '/tmp/2020_10_06_00_00_00.000-2020_10_06_00_00_00.008.121f55'
    new_pad_file = carve_pad_file(pad_file1, prev_grp_stop, rate)

    pad_file2 = '/tmp/2020_10_06_00_00_00.000+2020_10_06_00_00_00.008.121f33'
    new_pad_file = carve_pad_file(pad_file2, prev_grp_stop, rate)
