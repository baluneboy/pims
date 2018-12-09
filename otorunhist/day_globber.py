#!/usr/bin/env python

"""A handler for globbing a day's worth of files.

This module provides classes for glob file iteration over year/month/day subdirs.

"""

import os
import dateutil.parser as parser


class DayGlobber(object):
    """dg = DayGlobber(date, basedir, subdir)

    A class for for glob file iteration over year/month/day subdirs.
    """

    def __init__(self, basedir, datestr, subdir, fileglobpat='*'):
        self.basedir = basedir
        self.date = parser.parse(datestr).date()
        # self.ymdpart = ymdpart
        self.subdir = subdir
        self.fileglobpat = fileglobpat

    @property
    def basedir(self):
        return self.__basedir

    @basedir.setter
    def basedir(self, s):
        try:
            assert os.path.isdir(s)
        except TypeError:
            raise TypeError('basedir must be a string')
        except AssertionError:
            raise Exception('basedir must be a string that represents an existing directory')
        finally:
            self.__basedir = s

    @property
    def subdir(self):
        return self.__subdir

    @subdir.setter
    def subdir(self, s):
        try:
            assert isinstance(s, str)
        except TypeError:
            raise TypeError('subdir must be a string')
        finally:
            self.__subdir = s

    def __str__(self):
        s = self.__class__.__name__
        s += ' %s' % self.date
        s += ' %s' % self.basedir
        s += ' %s' % self.subdir
        return s



if __name__ == '__main__':

    d = '2017-01-02'
    dg = DayGlobber('/tmp', d, '/tmp')
    print dg
    print dg.fileglobpat
