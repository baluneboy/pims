#!/usr/bin/env python

import math
import numpy as np

def rotation_matrix(roll, pitch, yaw, invert=True):
    """convert roll, pitch, yaw into a 3x3 float32 rotation matrix, inverting if requested
    examples:
    ---------
    [ x'                           [ x
      y'   = rotationMatrix(...) *   y
      z' ]                           z ]
    
    [x' y' z'] = [x y z] * transpose(rotationMatrix(...))
    
    [ x0' y0' z0'   = [ x0 y0 z0  
      x1' y1' z1'   =   x1 y1 z1   * transpose(rotationMatrix(...))
      x2' y2' z2'   =   x2 y2 z2
       .   .   .         .  .  .
      xn' yn' zn' ] =   xn yn zn ]
    """
    r = roll * math.pi/180 # convert to radians
    p = pitch * math.pi/180
    w = yaw * math.pi/180
    cr = math.cos(r)
    sr = math.sin(r)
    cp = math.cos(p)
    sp = math.sin(p)
    cw = math.cos(w)
    sw = math.sin(w)

    # use numpy array
    rot = np.array(( [      cp*cw,          cp*sw,      -sp  ],
                     [ sr*sp*cw-cr*sw, sr*sp*sw+cr*cw, sr*cp ],
                     [ cr*sp*cw+sr*sw, cr*sp*sw-sr*cw, cr*cp ] ), np.float32)

    # invert is the same as transpose for any rotation matrix
    if invert:
        rot = np.transpose(rot)
    return rot


def is_rotation_matrix(m):
    """Checks if a matrix is a valid rotation matrix."""
    rt = np.transpose(m)
    should_be_identity = np.dot(rt, m)
    eye = np.identity(3, dtype=m.dtype)
    n = np.linalg.norm(eye - should_be_identity)
    return n < 1e-6


def rotation_matrix_to_euler_angles(m):
    """Calculates rotation matrix to Euler angles."""
    assert (is_rotation_matrix(m))

    sy = math.sqrt(m[0, 0] * m[0, 0] + m[1, 0] * m[1, 0])

    singular = sy < 1e-6

    if not singular:
        x = math.atan2(m[2, 1], m[2, 2])
        y = math.atan2(-m[2, 0], sy)
        z = math.atan2(m[1, 0], m[0, 0])
    else:
        x = math.atan2(-m[1, 2], m[1, 1])
        y = math.atan2(-m[2, 0], sy)
        z = 0

    return np.array([z, y, x]) * 180.0 / np.pi


def demo():
    m = np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    yaw, pitch, roll = rotation_matrix_to_euler_angles(m)
    print "rotation_matrix_to_euler_angles(m)", yaw, pitch, roll
    print "rotation_matrix(roll, pitch, yaw)", rotation_matrix(roll, pitch, yaw)


if __name__ == '__main__':
    demo()
