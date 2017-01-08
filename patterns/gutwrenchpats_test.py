import re
import pytest

my_regex = re.compile("<this is where the magic (doesn't)? happen(s)?>")

@pytest.mark.parametrize('test_str', [
    "an easy test that I'm sure will pass",
    "a few things that may trip me up",
    "a really pathological, contrived example",
    "something from the real world?",
])
def test_my_regex(test_str):
     assert my_regex.match(test_str) is not None
