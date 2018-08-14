#!/usr/bin/env python

import numpy as np
from mayavi import mlab
from pims.kinematics.rotation import ypr_to_3_rotation_matrices, change_of_basis_to_ypr


ZTEXT = 0.85
CS_SPACING = 1.75  # coordinate system spacing


def show_4_coord_sys(y, p, r):
    """
    [ xA        [ xS      [  a   b   c      [ xS     [ a*xS + b*yS + c*zS
      yA   = M *  yS    =    d   e   f    *   yS   =   d*xS + e*yS + f*zS
      zA ]        zS ]       g   h   i  ]     zS ]     g*xS + h*yS + i*zS ]
    """

    np.set_printoptions(formatter={'float': lambda x: ' {0:+0.1f} '.format(x)})
    a, b, c = ypr_to_3_rotation_matrices(y, p, r)
    # print '\nfirst independent rotation matrix'
    # print a
    # print '\nsecond independent rotation matrix'
    # print b
    # print '\nthird independent rotation matrix'
    # print c
    
    objs = []

    v = np.identity(3)

    # ----------------------------------------------------------------------------------------
    x = 3.0 * CS_SPACING

    # X-axis arrow
    obj = mlab.quiver3d(x, 0.0, 0.0, v[0,0], v[0,1], v[0,2],
                        line_width=3, color=(1.0, 0.0, 0.0), colormap='hsv',
                        scale_factor=0.8, mode='arrow', resolution=25)
    objs.append(obj)

    # Y-axis arrow
    obj = mlab.quiver3d(x, 0.0, 0.0, v[1,0], v[1,1], v[1,2],
                        line_width=3, color=(0.0, 1.0, 0.0), colormap='hsv',
                        scale_factor=0.8, mode='arrow', resolution=25)
    objs.append(obj)

    # Z-axis arrow
    obj = mlab.quiver3d(x, 0.0, 0.0, v[2,0], v[2,1], v[2,2],
                        line_width=3, color=(0.0, 0.0, 1.0), colormap='hsv',
                        scale_factor=0.8, mode='arrow', resolution=25)
    objs.append(obj)

    mlab.text3d(x, 0, ZTEXT, 'A', scale=0.15)

    # ----------------------------------------------------------------------------------------
    x -= CS_SPACING

    v = np.matmul(np.linalg.inv(a), v)

    # X-axis arrow
    obj = mlab.quiver3d(x, 0.0, 0.0, v[0,0], v[0,1], v[0,2],
                        line_width=3, color=(1.0, 0.0, 0.0), colormap='hsv',
                        scale_factor=0.8, mode='arrow', resolution=25)
    objs.append(obj)

    # Y-axis arrow
    obj = mlab.quiver3d(x, 0.0, 0.0, v[1,0], v[1,1], v[1,2],
                        line_width=3, color=(0.0, 1.0, 0.0), colormap='hsv',
                        scale_factor=0.8, mode='arrow', resolution=25)
    objs.append(obj)

    # Z-axis arrow
    obj = mlab.quiver3d(x, 0.0, 0.0, v[2,0], v[2,1], v[2,2],
                        line_width=3, color=(0.0, 0.0, 1.0), colormap='hsv',
                        scale_factor=0.8, mode='arrow', resolution=25)
    objs.append(obj)

    mlab.text3d(x, 0, ZTEXT, 'B', scale=0.15)

    # ----------------------------------------------------------------------------------------
    x -= CS_SPACING

    v = np.matmul(np.linalg.inv(b), v)

    # X-axis arrow
    obj = mlab.quiver3d(x, 0.0, 0.0, v[0,0], v[0,1], v[0,2],
                        line_width=3, color=(1.0, 0.0, 0.0), colormap='hsv',
                        scale_factor=0.8, mode='arrow', resolution=25)
    objs.append(obj)

    # Y-axis arrow
    obj = mlab.quiver3d(x, 0.0, 0.0, v[1,0], v[1,1], v[1,2],
                        line_width=3, color=(0.0, 1.0, 0.0), colormap='hsv',
                        scale_factor=0.8, mode='arrow', resolution=25)
    objs.append(obj)

    # Z-axis arrow
    obj = mlab.quiver3d(x, 0.0, 0.0, v[2,0], v[2,1], v[2,2],
                        line_width=3, color=(0.0, 0.0, 1.0), colormap='hsv',
                        scale_factor=0.8, mode='arrow', resolution=25)
    objs.append(obj)

    mlab.text3d(x, 0, ZTEXT, 'C', scale=0.15)

    # ----------------------------------------------------------------------------------------
    x -= CS_SPACING

    v = np.matmul(np.linalg.inv(c), v)

    # X-axis arrow
    obj = mlab.quiver3d(x, 0.0, 0.0, v[0,0], v[0,1], v[0,2],
                        line_width=3, color=(1.0, 0.0, 0.0), colormap='hsv',
                        scale_factor=0.8, mode='arrow', resolution=25)
    objs.append(obj)

    # Y-axis arrow
    obj = mlab.quiver3d(x, 0.0, 0.0, v[1,0], v[1,1], v[1,2],
                        line_width=3, color=(0.0, 1.0, 0.0), colormap='hsv',
                        scale_factor=0.8, mode='arrow', resolution=25)
    objs.append(obj)

    # Z-axis arrow
    obj = mlab.quiver3d(x, 0.0, 0.0, v[2,0], v[2,1], v[2,2],
                        line_width=3, color=(0.0, 0.0, 1.0), colormap='hsv',
                        scale_factor=0.8, mode='arrow', resolution=25)
    objs.append(obj)

    mlab.text3d(x, 0, ZTEXT, 'S', scale=0.15)

    return objs


def demo(a, b, c, d, e, f, g, h, i):

    mlab.figure(bgcolor=(1, 1, 1), fgcolor=(0, 0, 0), size=(1200, 900))

    yaw, pitch, roll = change_of_basis_to_ypr(a, b, c, d, e, f, g, h, i, show_matrix=True)

    title = 'yaw, pitch, roll = %.1f,  %.1f,  %.1f' % (yaw, pitch, roll)
    objs = show_4_coord_sys(yaw, pitch, roll)
    mlab.title(title, size=0.25, height=0.92)

    # set camera params
    cam = objs[0].scene.camera
    cam.position = [7.4, 4.1, 4.2]
    cam.focal_point = [3.30, 0.01, 0.13]
    cam.view_angle = 30.0
    cam.view_up = [0.0, 0.0, 1.0]
    cam.clipping_range = [1.9, 13.6]
    cam.compute_view_plane_normal()

    mlab.show()


if __name__ == '__main__':

    print """
Enter the change of basis matrix, M, that gets us from sensor coordinates to SSA coordinates
where a, b, c, ... g, h, i describe the components of SSA in terms of sensor coords:

[ xA        [ xS      [  a   b   c      [ xS     [ a*xS + b*yS + c*zS
  yA   = M *  yS    =    d   e   f    *   yS   =   d*xS + e*yS + f*zS
  zA ]        zS ]       g   h   i  ]     zS ]     g*xS + h*yS + i*zS ]
    """
    str_arr = raw_input().split(' ')
    arr = [float(num) for num in str_arr]
    yaw, pitch, roll = change_of_basis_to_ypr(*arr)
    print 'this yields yaw, pitch, roll =', yaw, pitch, roll

    objs = demo(*arr)
