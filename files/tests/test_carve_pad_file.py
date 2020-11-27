import os
import pytest
import tempfile
import shutil
import datetime
from pims.files.utils import carve_pad_file


def simple_carve():
    pad_file = '2020_10_06_00_00_00.000-2020_10_06_00_00_00.008.121f00'
    prev_grp_stop = datetime.datetime(2020, 10, 6, 0, 0, 0, 4000)
    rate = 500.0
    with tempfile.TemporaryDirectory() as dirpath:
        tmp_file = os.path.join(dirpath, pad_file)
        shutil.copyfile(pad_file, tmp_file)
        carve_pad_file(tmp_file, prev_grp_stop, rate)
        # shutil.rmtree(dirpath)
        pass


def test_carve_pad_file():
    # dd bs=8192 iflag=skip_bytes skip=32 if=/tmp/carveme.txt of=/tmp/carveme.new
    simple_carve()
    assert 1 == 1


if __name__ == '__main__':
    simple_carve()
