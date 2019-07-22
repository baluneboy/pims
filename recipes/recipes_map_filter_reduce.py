#!/usr/bin/env python

"""Consider map and filter methodology."""


import numpy as np


def area(r):
    """return area of circle with radius r"""
    return np.pi * (r ** 2)


def demo_1(radii):
    """method 1 does not use map, it fully populates in a loop NOT AS GOOD FOR LARGER DATA SETS"""
    areas = []
    for r in radii:
        a = area(r)  # populate list one-by-one in for loop
        areas.append(a)
        print a


def demo_2(radii):
    """method 2 uses map to create iterator, which applies area function to each element of radii
     it can sometimes be better to use iterator, esp. for large lists"""
    area_iter = map(area, radii)  # returns iterator over area applied to each radius
    for a in area_iter:
        print a


def demo_one_map():
    """compare with/out using map"""
    radii = [2, 5, 7.1, 0.3, 10]
    demo_1(radii)
    demo_2(radii)


def demo_two_map():
    """use map to convert temps en masse"""
    # example using map
    temps_c = [("Berlin", 29), ("Cairo", 36), ("Buenos Aires", 19),
               ("Los Angeles", 26), ("Tokyo", 27), ("New York", 28),
               ("London", 22), ("Beijing", 32)]

    # lambda to return tuple with calculated deg. F converted from deg. C
    c2f = lambda city_tmp: (city_tmp[0], (9.0/5.0)*city_tmp[1] + 32)

    print list(map(c2f, temps_c))


def demo_one_filter():
    """use filter to keep only data from list that are strictly above average"""
    data = [1.3, 2.7, 0.8, 4.1, 4.3, -0.1]
    avg = np.mean(data)
    print "average value is:", avg

    # create iterator that filters to keep only above average data
    above_avg_iter = filter(lambda x: x > avg, data)  # returns iterator for data above the avg

    print "values strictly above average are:", list(above_avg_iter)


if __name__ == '__main__':
    demo_one_filter()
