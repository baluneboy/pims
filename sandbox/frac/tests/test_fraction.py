#!/usr/bin/env python

from unittest import TestCase
from fraction import Fraction, gcd

class TestFraction(TestCase):

    def test_worthless(self):
        n = 1
        d = 2
        f = Fraction(n, d)
        print n, d
        print f
        self.fail()

    def test_gcd(self):
        a = 36
        b = 18
        g = gcd(a, b)
        print 'a is', a, ', b is', b, ', so gcd is', g