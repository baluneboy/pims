#!/usr/bin/env python

from samsquery import insert_pimsmap_roadmap, query_pimsmap_plottype, query_pimsmap_sensor_id

def test_insert():
    bname = '2017_05_10_00_00_00.000_121f03_spgs_roadmaps500.pdf'
    insert_pimsmap_roadmap(bname)

if __name__ == "__main__":
    test_insert()
    #for abb in ['spgs', 'spgx', 'spgy', 'spgz', 'pcss']:
    #    plottype = query_pimsmap_plottype(abb)
    #    print plottype
    #for s in ['121f02', '121f03', '121f04', '121f05', '121f08']:
    #    sensorid = query_pimsmap_sensor_id(s)
    #    print sensorid