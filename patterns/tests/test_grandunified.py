#!/usr/bin/env python

import re
import pytest

from pims.patterns.handbookpdfs import _TIGDUR_PATTERN

my_regex = re.compile(_TIGDUR_PATTERN)

@pytest.mark.parametrize('test_str', [
'abc TIG 16:28:00 DUR 21 min 11 sec, not',
'abc TIG 16:28:00 DUR 21:00 not',
])

def test_my_regex(test_str):
     assert my_regex.match(test_str) is not None
