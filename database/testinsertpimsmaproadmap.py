#!/usr/bin/env python

from unittest import TestCase
import datetime
from pims.database.samsquery import get_roadmap_data_record
from pims.probes.roadmap_probe import bname_in_roadmap_recs, query_pimsmap_roadmap


class TestInsertPimsmapRoadmap(TestCase):

    def get_result(self, bname):
        query_str, data_record = get_roadmap_data_record(bname)
        print query_str, data_record
        return query_str, data_record

    def test_query_pimsmap_roadmap(self):
        day = datetime.datetime(2017, 6, 10)
        sensor = '121f03'
        roadmap_recs = query_pimsmap_roadmap(day, sensor)
        print roadmap_recs
        return False

    def test_bname_in_roadmap_recs(self):
        day = datetime.datetime(2017, 6, 10)
        sensor = '121f03one'
        roadmap_recs = query_pimsmap_roadmap(day, sensor)
        for ax in ['s', 'x', 'y', 'z']:
            f = '/misc/yoda/www/plots/batch/year2017/month06/day10/2017_06_10_00_00_00.000_121f03one_spg' + ax + '_roadmaps142.pdf'
            is_roadmap_rec = bname_in_roadmap_recs(f, roadmap_recs)
            print is_roadmap_rec, f
            self.assertTrue(is_roadmap_rec, '%s NOT DETECTED' % f)

    def test_good_bname(self):
        bname = '2017_06_10_00_00_00.000_121f03ten_spgs_roadmaps500.pdf'
        query_str, data_record = self.get_result(bname)
        print data_record
        return query_str, data_record

    def test_bad_bname(self):
        bname = '2017_01_01_16_00_00.000_121f0X_spgs_roadmaps142.pdf'
        #                                     ^
        #                                    BAD
        self.assertRaises(IndexError, self.get_result, bname)

    def test_one_bname(self):
        bname = '2017_01_01_16_00_00.000_121f03one_spgs_roadmaps142.pdf'
        query_str, data_record = self.get_result(bname)
        return query_str, data_record

    def test_ten_bname(self):
        bname = '2017_01_01_16_00_00.000_121f03ten_spgs_roadmaps142.pdf'
        query_str, data_record = self.get_result(bname)
        return query_str, data_record
