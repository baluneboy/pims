#!/usr/bin/env python

import warnings

def fxn():
    warnings.warn("deprecated", DeprecationWarning)

def demo():
    with warnings.catch_warnings():
        rxstr = 'divide by zero.*'
        warnings.filterwarnings("ignore", message=rxstr)
        # here is code that might issue warning we want to suppress
        warnings.warn('divide by zero encountered in divide')


def demo2():
    with warnings.catch_warnings(record=True) as w:
        # Cause all warnings to always be triggered.
        warnings.simplefilter("ignore") # ignore or always
        # Trigger a warning.
        fxn()
        fxn()
        # Verify some things
        assert len(w) == 2
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "deprecated" in str(w[-1].message)
    print w

demo2()