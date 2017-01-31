#!/usr/bin/env python

import re
import pytest

from pims.patterns.probepats import _ROADMAP_PDF_FILENAME_PATTERN

my_regex = re.compile(_ROADMAP_PDF_FILENAME_PATTERN)

@pytest.mark.parametrize('test_str', [
'2017_01_01_16_00_00.000_121f03one_spgs_roadmaps142.pdf',
'2017_01_01_16_00_00.000_121f03two_spgx_roadmaps142.pdf',
'2017_01_01_16_00_00.000_121f03uno_spgy_roadmaps142.pdf',
'2017_01_01_16_00_00.000_121f03dos_spgz_roadmaps140.pdf',
'2017_01_01_16_00_00.000_121f03ten_gvtm_roadmaps141.pdf',
'2017_01_01_16_00_00.000_121f05_spgs_roadmaps144.pdf',
'2017_01_01_16_00_00.123_121f08_spgx_roadmaps198.pdf',
])

def test_my_regex(test_str):
     assert my_regex.match(test_str) is not None

# SEE /home/pims/dev/programs/python/pims/patterns/tests/readme.txt