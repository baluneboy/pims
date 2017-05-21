#!/usr/bin/env python

import numpy as np
from math import atan2, sqrt, sin, cos


def symbolic_eulerangles_from_rotation_matrix(m):
    """
    EXAMPLE
    yaw_deg = 90;
    pitch_deg = 0;
    roll_deg = 0;
    m = symbolic_rotation(yaw_deg, pitch_deg, roll_deg)
    [Ydeg, Pdeg, Rdeg] = symbolic_eulerangles_from_rotation_matrix(m)

    """

    # Scale factor to convert input angles from radians to degrees
    sf = 180.0 / np.pi

    # Extract first angle
    roll = atan2(m[1,2], m[2,2])
    Rdeg = roll * sf

    # Intermediate calc [sidesteps gimbal lock situation?]
    #  see /Users/ken/matlab/euler-angles1.pdf
    c2 = sqrt(m[0,0]^2 + m[0,1]^2)

    # Extract second angle
    pitch = atan2(-m[0,2], c2)
    Pdeg = pitch * sf

    # Two more intermediate calc
    s1 = sin(roll)
    c1 = cos(roll)

    # Extract third angle
    yaw = atan2( s1*m[2,0] - c1*m[1,0], c1*m[1,1] - s1*m[2,1] )
    Ydeg = yaw * sf

    return Ydeg, Pdeg, Rdeg

if __name__ == '__main__':
    m = np.arange(9).reshape(3, 3)
    print m
    Ydeg, Pdeg, Rdeg = symbolic_eulerangles_from_rotation_matrix(m)
    print Ydeg, Pdeg, Rdeg
