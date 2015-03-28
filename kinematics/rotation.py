#!/usr/bin/env python

import math
import numpy as np

def rotation_matrix(roll, pitch, yaw, invert=0):
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