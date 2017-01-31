#!/usr/bin/env python

# PIVOT TABLE !!! ???

class Distros(object):
   def __init__(self, name, h_p_d, tendency, releases):
       self.name = name
       self.h_p_d = h_p_d
       self.tendency = tendency
       self.releases = releases
   def __repr__(self):
       return "<Distro: %s, %d, %s, %d>" % (self.name, self.h_p_d, self.tendency, self.releases)

distros = [
           Distros('Ubuntu', 2075, '+', 13),
           Distros('Mint', 1547, '=', 10),
           Distros('Fedora', 1460, '+', 14),
           Distros('Debian', 1143, '+', 10),
           Distros('OpenSuse', 1135, '+', 26)
          ]

from pivottable import PivotTable, Sum, GroupBy
pt = PivotTable()
pt.rows = distros
pt.xaxis = "name"
pt.yaxis = [
        {'attr':'h_p_d', 'label':'Hits per distro', 'aggr':Sum},
        {'attr':'tendency', 'label':'Tendency', 'aggr':Sum},
        {'attr':'releases', 'label':'Releases', 'aggr':Sum}]

print pt.yaxis.Sum

for a in pt.result:
   print a

#help(pt)