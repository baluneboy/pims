#!/usr/bin/env python

"""
Run these tests after patterns change AND AFTER adding updates/new a test_*.py file.

    #------------------------------------------------
    for alternate test examples using unittest, see:
    ~/dev/programs/python/ugaudio/tests
    #------------------------------------------------

# THIS IS HOW TO RUN THE TESTS
cd /home/pims/dev/programs/python/pims/patterns/tests
python -B -m pytest # ALL FOUND IN THIS DIR

# OR, FOR JUST ONE FILE:
cd /home/pims/dev/programs/python/pims/patterns/tests
python -B -m pytest test_probepats.py
"""

import re
import pytest

from pims.patterns.probepats import _ROADMAP_PDF_FILENAME_PATTERN, _ROADMAP_PDF_BLANKS_PATTERN, _OSSBTMF_ROADMAP_PDF_FILENAME_PATTERN

my_regex = re.compile(_ROADMAP_PDF_FILENAME_PATTERN)

my_pat2 = _ROADMAP_PDF_BLANKS_PATTERN.replace('SENSOR', '121f02.*').replace('PLOT', 'spg').replace('AXIS', 's')
my_regex2 = re.compile(my_pat2)
my_regex3 = re.compile(_OSSBTMF_ROADMAP_PDF_FILENAME_PATTERN)

@pytest.mark.parametrize('test_str', [
'2017_01_01_16_00_00.000_121f02one_spgs_roadmaps142.pdf',
'2017_01_01_16_00_00.000_121f02two_spgs_roadmaps142.pdf',
'2017_01_01_16_00_00.000_121f02uno_spgs_roadmaps142.pdf',
'2017_01_01_16_00_00.000_121f02dos_spgs_roadmaps140.pdf',
'2017_01_01_16_00_00.000_121f02ten_gvts_roadmaps141.pdf',
'2017_01_01_16_00_00.000_121f02_spgs_roadmaps144.pdf',
'2017_01_01_16_00_00.123_121f04_spgs_roadmaps198.pdf',
])

def test_my_regex(test_str):
     assert my_regex.match(test_str) is not None
     assert my_regex2.match(test_str) is not None
     assert my_regex3.match('2016_07_01_00_ossbtmf_roadmap.pdf') is not None
