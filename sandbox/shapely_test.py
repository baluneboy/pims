#!/usr/bin/env python

from shapely.geometry import Point
from functools import partial
import pyproj
from shapely.ops import transform

point1 = Point(9.0, 50.0)

print point1

project = partial(
    pyproj.transform,
    pyproj.Proj(init='epsg:4326'),
    pyproj.Proj(init='epsg:32632'))

point2 = transform(project, point1)
print point2
