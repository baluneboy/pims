#!/usr/bin/env python

from sympy.abc import rho, phi

import numpy as np
from sympy import sin, cos, Matrix, Symbol, Transpose
from sympy import pprint, symbols, eye


def symbolic_rotation_matrix(yaw_deg, pitch_deg, roll_deg):
    """

    EXAMPLE
    yaw_deg = 90;
    pitch_deg = 0;
    roll_deg = 0;
    m = symbolic_rotation(yaw_deg, pitch_deg, roll_deg)

    """

    Y, P, R = symbols('Y P R', integer=False)

    Rz = Matrix([[cos(Y), -sin(Y), 0], [sin(Y), cos(Y), 0], [0, 0, 1]])
    Ry = Matrix([[cos(P), 0, sin(P)], [0, 1, 0], [-sin(P), 0, cos(P)]])
    Rx = Matrix([[1, 0, 0], [0, cos(R), -sin(R)], [0, sin(R), cos(R)]])

    M = Transpose(Rz*Ry*Rx)  # need transpose to get PIMS M_NEWoverA matrix

    # matrix, M (above) is equal to PIMS M_NEWoverA matrix
    # SEE PIMS INC3 REPORT, p. 134 Eq. E.1-3
    # left multiply a vector in SSA to get that vector in NEW coords:
    # v_NEW = M * v_A %% NOTE A is short for SSA here

    # Scale factor to convert input angles from degrees to radians
    sf = np.pi / 180.0

    # YAW FIRST
    a = M.subs(Y, yaw_deg*sf)

    # PITCH SECOND
    b = a.subs(P, pitch_deg*sf)

    # ROLL THIRD (LAST)
    m = b.subs(R, roll_deg*sf)  # this has our 3 rotations substituted in

    return m

if __name__ == '__main__':
    ydeg, pdeg, rdeg = 90.0, -20.0, 11.234
    m = symbolic_rotation_matrix(ydeg, pdeg, rdeg)
    pprint(m)
