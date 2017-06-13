from unittest import TestCase
from pims.database.samsquery import insert_pimsmap_roadmap


class TestInsertPimsmapRoadmap(TestCase):

    def get_result(self, bname):
        result = insert_pimsmap_roadmap(bname)
        return result

    def test_good_bname(self):
        bname = '2017_01_01_16_00_00.000_121f03_spgs_roadmaps142.pdf'
        result = self.get_result(bname)
        return result

    def test_bad_bname(self):
        bname = '2017_01_01_16_00_00.000_121f0X_spgs_roadmaps142.pdf'
        #                                     ^
        #                                    BAD
        self.assertRaises(IndexError, self.get_result, bname)

    def test_one_bname(self):
        bname = '2017_01_01_16_00_00.000_121f03one_spgs_roadmaps142.pdf'
        result = self.get_result(bname)
        return result

    def test_ten_bname(self):
        bname = '2017_01_01_16_00_00.000_121f03ten_spgs_roadmaps142.pdf'
        result = self.get_result(bname)
        return result
