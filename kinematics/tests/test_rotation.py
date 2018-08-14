#!/usr/bin/env python

import unittest
import numpy as np
from kinematics.rotation import is_rotation_matrix, rotation_matrix_to_ypr


class TestIsRotationMatrix(unittest.TestCase):

    def test_is_rotation_matrix(self):
        m = np.identity(3)
        self.assertTrue(is_rotation_matrix(m))

    def test_is_rotation_matrix_badarg(self):
        x = 1.0
        self.assertRaises(AttributeError, is_rotation_matrix, x)

    def test_rotation_matrix_simple(self):
        m = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.assertTrue(is_rotation_matrix(m))


class TestTaitBryanAngles(unittest.TestCase):

    def test_rotation_matrix_yaw_only(self):
        m1, y1, p1, r1 = np.array([[ 0, -1, 0], [ 1,  0, 0], [0, 0, 1]]),  90.0, 0.0, 0.0
        m2, y2, p2, r2 = np.array([[ 0,  1, 0], [-1,  0, 0], [0, 0, 1]]), -90.0, 0.0, 0.0
        m3, y3, p3, r3 = np.array([[-1,  0, 0], [ 0, -1, 0], [0, 0, 1]]), 180.0, 0.0, 0.0
        ms = [m1, m2, m3]
        yprs = [(y1, p1, r1), (y2, p2, r2), (y3, p3, r3)]
        for m, ypr in zip(ms, yprs):
            yaw, pitch, roll = rotation_matrix_to_ypr(m)
            self.assertEqual((yaw, pitch, roll), ypr)


if __name__ == '__main__':
    unittest.main(verbosity=2)
