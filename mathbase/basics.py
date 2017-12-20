#!/usr/bin/env python

import math


def round2ten(a):
    """return value rounded to multiple of ten"""
    return int(round(a, -1))


def round_down(x, m):
    """return value of x rounded down to multiple of m"""    
    return x - (x%m)


def round_up(x, m):
    """return value of x rounded up to multiple of m"""        
    return (int(math.floor(x / m)) + 1) * m


def demo():
    for v in range(65740, 65860, 10):
        print v / 10.0, round2ten(v/10.0)


if __name__ == '__main__':
    demo()