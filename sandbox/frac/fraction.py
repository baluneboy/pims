#!/usr/bin/env python

# fraction.py
# Walker M. White (wmw2)
# October 7, 2012
"""Module with a simple Fraction class.

This module shows off operator overloading.  This allows
us to define complex mathematical objects.

This version of Fraction uses fields.  Therefore, we
cannot enforce our invariants."""

import math


def gcd(a, b):
    """Returns: Greatest common divisor of x and y.

    Precondition: x and y are integers."""
    assert type(a) == int, `x` + ' is not an int'
    assert type(b) == int, `y` + ' is not an int'
    while b != 0:
        t = b
        b = a % b
        a = t
    return a


class Fraction(object):
    """Instance a fraction n/d

    Attributes:
        numerator: must be an int
        denominator: must be an int > 0"""

    def __init__(self, n=0, d=1):
        """Constructor: Creates a new Fraction n/d

        Precondition: n an int, d > 0 an int."""
        assert type(n) == int, `n` + ' is not an int'
        assert type(d) == int, `d` + ' is not an int'
        assert d > 0, `d` + ' is not positive'

        self.numerator = n
        self.denominator = d

    def __str__(self):
        """Returns: this Fraction as a string 'n/d'"""
        return str(self.numerator) + '/' + str(self.denominator)

    def __repr__(self):
        """Returns: unambiguous representation of Fraction"""
        return str(self.__class__) + '[' + str(self) + ']'

    def __mul__(self, other):
        """Returns: Product of self and other as a new Fraction

        Does not modify contents of self or other

        Precondition: other is a Fraction"""
        assert type(other) == Fraction
        top = self.numerator * other.numerator
        bot = self.denominator * other.denominator
        return Fraction(top, bot)

    def __add__(self, other):
        """Returns: Sum of self and other as a new Fraction

        Does not modify contents of self or other

        Precondition: other is a Fraction"""
        assert type(other) == Fraction
        bot = self.denominator * other.denominator
        top = (self.numerator * other.denominator +
               self.denominator * other.numerator)
        return Fraction(top, bot)

    def __eq__(self, other):
        """Returns: True if self, other are equal Fractions.
        False if not equal, or other not a Fraction"""
        if type(other) != Fraction:
            return False

        # Cross multiply
        left = self.numerator * other.denominator
        rght = self.denominator * other.numerator
        return left == rght

    def __ne__(self, other):
        """Returns: False if self, other are equal Fractions.
        True if not equal, or other not a Fraction"""
        return not self == other

    def __cmp__(self, other):
        """Returns: a negative integer if self < other,
        zero if self == other,
        a positive integer if self > other

        Used to implement comparison operations.

        Precondition: other is a Fraction."""
        assert type(other) == Fraction
        # Cross multiply
        left = self.numerator * other.denominator
        rght = self.denominator * other.numerator
        return left - rght

    def reduce(self):
        """Normalizes this fraction so that numerator
        and denominator have no common divisors."""
        g = gcd(self.numerator, self.denominator)
        self.numerator = self.numerator / g
        self.denominator = self.denominator / g