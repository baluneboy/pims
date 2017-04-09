#!/usr/bin/env python

import sys
import numpy as np
from sympy import pprint, symbols
from sympy.matrices import *
from transformations import identity_matrix, rotation_matrix, concatenate_matrices, euler_from_matrix
from transformations import euler_matrix, is_same_transform, scale_matrix, shear_matrix, random_rotation_matrix
from transformations import decompose_matrix, compose_matrix, random_vector, vector_product, translation_matrix
from transformations import angle_between_vectors, _AXES2TUPLE
import contextlib

@contextlib.contextmanager
def printoptions(*args, **kwargs):
    original = np.get_printoptions()
    np.set_printoptions(*args, **kwargs)
    try:
        yield
    finally:
        np.set_printoptions(**original)

def print_hstack(I, Rz, Rzy, Rzyx):
    D = np.hstack((I.transpose()[:3,:3], Rz.transpose()[:3,:3], Rzy.transpose()[:3,:3], Rzyx.transpose()[:3,:3]))
    print np.array_str(D, precision=1, suppress_small=True)


np.set_printoptions(precision=1, suppress=True, formatter={'float': '{: 0.1f}'.format})
origin, xaxis, yaxis, zaxis = [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]
I = identity_matrix()

xA, yA, zA = symbols('xA yA zA'); VA = Matrix([xA,yA,zA])
x1, y1, z1 = symbols('x1 y1 z1'); V1 = Matrix([x1,y1,z1])
x2, y2, z2 = symbols('x2 y2 z2'); V2 = Matrix([x2,y2,z2])
xS, yS, zS = symbols('xS yS zS'); VS = Matrix([xS,yS,zS])

count = 0
four_angles = range(0, 360, 90)
for y in four_angles:
    for p in four_angles:
        for r in four_angles:
            count += 1
            ypr = [ y, p, r ]
            gamma, beta, alpha = [ a * np.pi/180.0 for a in ypr ]

            Rz = rotation_matrix(gamma, zaxis)            
            Ry = rotation_matrix(beta, yaxis)
            Rx = rotation_matrix(alpha, xaxis)
            
            Rzy = concatenate_matrices(Rz, Ry)
            Rzyx = concatenate_matrices(Rz, Ry, Rx)
            
            # TODO in order to use each rotation matrix for step-by-step illustration
            #      we need to work with upper-left 3x3 of transposed matrix for each of
            #      these in order:
            #      I    to show starting state
            #      Rz   yields YAW result
            #      Rzy  yields YAW + PITCH result
            #      Rzyx yields YAw + PITCH + ROLL (final) result
            
            if True: #y == 90 and p + r == 0:
                print u'\ncount = %02d:  ' % count, 'yaw = %3d, pitch = %3d, roll = %3d\n' % (ypr[0], ypr[1], ypr[2]) 
                M = Matrix(np.rint(Rzyx[:3,:3].transpose()))
                #pprint(M)
                pprint(M*VA)
                #print_hstack(I, Rz, Rzy, Rzyx)
            
            else:
                continue

        
            
            # FIXME better document that for YPR sequence, use:
            #       first 3 args: (gamma, beta, alpha), then 'rzyx'
            #       to rotate around zaxis, then yaxis, and xaxis last
            #Re = euler_matrix(gamma, beta, alpha, 'rzyx') 
            #print is_same_transform(Rzyx, Re)

            # FIXME empirically shown that need transpose here to work with PIMS SSA xform
            #       C'mon man! get your maths on and show this analytically
            #M = np.matrix.transpose(Re)
