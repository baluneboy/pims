#!/usr/bin/env python3

import datetime
from pathlib import Path
from pims.pad.padutils import pad_fullfilestr_to_start_stop


if __name__ == "__main__":

    rate = 500.0
    pth = Path('/home/pims/data/dummy_pad/year2020/month04/day05/sams2_accel_121f03')
    for p in sorted(pth.glob('*.121f03')):
        f_start, f_stop = pad_fullfilestr_to_start_stop(p.name)
        f_pts = p.stat().st_size // 16
        c_stop = f_start + datetime.timedelta(seconds=(f_pts-1)/rate)
        print(p.name, f_start, f_stop, c_stop, p.stat().st_size // 16)
