#!/usr/bin/env python

import sys
import numpy as np
from sympy.matrices import Matrix
from sympy import pprint, symbols, eye
from transformations import rotation_matrix, concatenate_matrices
#from transformations import euler_matrix, is_same_transform

#I = eye(4)

def print_hstack(I, Rz, Rzy, Rzyx):
    """print horizontal stackof the rotation matrices left-to-right for yaw, then pitch, then roll"""
    D = np.hstack((I.transpose()[:3,:3], Rz.transpose()[:3,:3], Rzy.transpose()[:3,:3], Rzyx.transpose()[:3,:3]))
    print np.array_str(D, precision=1, suppress_small=True)

def rint_3x3_transpose(R):
    """return Matrix object that corresponds to 3x3 Rotation matrix after been transposed to work with PIMS SSA xform""" 
    return Matrix(np.rint(R[:3,:3].transpose()))

def simple_str(x, new_sub):
    """return string for given axis-component and subscript, like xS = """
    return '%s = ' % new_sub + '%3s' % str(x).replace('1.0*', '')

def get_new_axes_str(R, V, new_sub):
    """return new axes alignment given Rotation matrix and starting orientation (VA) and new subscript"""
    M = rint_3x3_transpose(R)
    xyzN = M*V
    xstr = 'x' + simple_str(xyzN[0], new_sub)
    ystr = 'y' + simple_str(xyzN[1], new_sub)
    zstr = 'z' + simple_str(xyzN[2], new_sub)
    return '%s, %s, %s' % (xstr, ystr, zstr)

def show_all_xforms():
    #np.set_printoptions(precision=1, suppress=True, formatter={'float': '{: 0.1f}'.format})
    origin, xaxis, yaxis, zaxis = [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]
    xA, yA, zA = symbols('xA yA zA'); VA = Matrix([xA, yA, zA])
    
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
                            
                str1 = get_new_axes_str(Rz,   VA, '1') # YAW to go from group A to group 1
                str2 = get_new_axes_str(Rzy,  VA, '2') # YAW then PITCH to go from group A to group 2
                strS = get_new_axes_str(Rzyx, VA, 'S') # YAW, PITCH, then ROLL to go from group A to group S
                
                #print_hstack(I, Rz, Rzy, Rzyx)
                print 'count = %02d:  ' % count, 'yaw = %3d, pitch = %3d, roll = %3d -> %s -> %s -> %s' % (ypr[0], ypr[1], ypr[2],
                                                                                                           str1, str2, strS)
                
                # to go directly from input of yaw, pitch, roll [deg] -> (gamma, beta, alpha) [radians], use this:
                #Re = euler_matrix(gamma, beta, alpha, 'rzyx') # order needed for next line to be True
                #print is_same_transform(Rzyx, Re)             # YPR sequence needs args as shown here
                #Me = rint_3x3_transpose(Re) # this is what we'd use to correspond to Rzyx used above

if __name__ == '__main__':
    show_all_xforms() 