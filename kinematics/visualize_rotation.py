#!/usr/bin/env python

import sys
import json
import numpy as np
from mayavi import mlab
from pims.kinematics.rotation import ypr_to_3_rotation_matrices, rotation_matrix_to_ypr

ZTEXT = 0.85
CS_SPACING = 1.75  # coordinate system spacing


def OBSOLETE_show_4_coord_sys(y, p, r):
    """
    save file with screenshot of visualization that shows sequence of 3 rotations for config mgmt purposes
    """

    # set print options (in case we need)
    np.set_printoptions(formatter={'float': lambda x: ' {0:+0.1f} '.format(x)})

    # convert sequence of 3 rotations to the 3 successive rotation matrices for yaw, pitch, then roll
    a, b, c = ypr_to_3_rotation_matrices(y, p, r)
    # print '\nfirst independent rotation matrix'
    # print a
    # print '\nsecond independent rotation matrix'
    # print b
    # print '\nthird independent rotation matrix'
    # print c

    # initialize VTK objects list
    objs = []

    # matrix of 3 original basis vectors that represents SSA before we apply any rotations
    v = np.identity(3)

    # no rotation yet, just show SSA as-is -----------------------------------------------------------------------------
    x = 3.0 * CS_SPACING  # this is how mayavi defaults, we will put first coord sys glyphs furthest along X

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

    # first rotation about Z-axis (yaw) --------------------------------------------------------------------------------
    x -= CS_SPACING  # move inward to origin along X for next coord sys glyphs

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

    # second rotation about Y'-axis (pitch) ----------------------------------------------------------------------------
    x -= CS_SPACING  # move inward to origin along X for next coord sys glyphs

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

    # third rotation about X''-axis (roll) -----------------------------------------------------------------------------
    x -= CS_SPACING  # move inward to origin along X for next coord sys glyphs

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


def draw_coord_sys_with_text(x, v, objs, zpos, label):
    """draw coord sys glpyhs at x-position with text/title hovering at zpos"""

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

    mlab.text3d(x, 0, zpos, label, scale=0.15)

    return x, v, objs


def show_4_coord_sys(y, p, r):
    """
    save file with screenshot of visualization that shows sequence of 3 rotations for config mgmt purposes
    """

    # set print options (in case we need)
    np.set_printoptions(formatter={'float': lambda x: ' {0:+0.1f} '.format(x)})

    # convert sequence of 3 rotations to the 3 successive rotation matrices for yaw, pitch, then roll
    a, b, c = ypr_to_3_rotation_matrices(y, p, r)
    # print '\nfirst independent rotation matrix'
    # print a
    # print '\nsecond independent rotation matrix'
    # print b
    # print '\nthird independent rotation matrix'
    # print c

    # initialize VTK objects list
    objs = []

    # no rotation yet, just show SSA as-is -----------------------------------------------------------------------------
    # matrix of 3 original basis vectors that represents SSA before we apply any rotations
    v = np.identity(3)
    x = 3.0 * CS_SPACING  # this is how mayavi defaults, we will put first coord sys glyphs furthest along X
    x, v, objs = draw_coord_sys_with_text(x, v, objs, ZTEXT, 'A')

    # first rotation about Z-axis (yaw) --------------------------------------------------------------------------------
    x -= CS_SPACING  # move inward to origin along X for next coord sys glyphs
    v = np.matmul(np.linalg.inv(a), v)
    x, v, objs = draw_coord_sys_with_text(x, v, objs, ZTEXT, 'B')

    # second rotation about Y'-axis (pitch) ----------------------------------------------------------------------------
    x -= CS_SPACING  # move inward to origin along X for next coord sys glyphs
    v = np.matmul(np.linalg.inv(b), v)
    x, v, objs = draw_coord_sys_with_text(x, v, objs, ZTEXT, 'C')

    # third rotation about X''-axis (roll) -----------------------------------------------------------------------------
    x -= CS_SPACING  # move inward to origin along X for next coord sys glyphs
    v = np.matmul(np.linalg.inv(c), v)
    x, v, objs = draw_coord_sys_with_text(x, v, objs, ZTEXT, 'S')

    return objs


def show_results(yaw, pitch, roll):

    # TODO save figure for configuration management purposes (filename convention sensor, payload, date, etc.)

    mlab.figure(bgcolor=(1, 1, 1), fgcolor=(0, 0, 0), size=(1200, 900))

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

    # ~/dev/programs/python/pims/kinematics/visualize_rotation.py '[[ 0, -1, 0], [ 1,  0, 0], [0, 0, 1]]' # 90, 0, 0
    # ~/dev/programs/python/pims/kinematics/visualize_rotation.py '[[ 0,  1, 0], [-1,  0, 0], [0, 0, 1]]' #-90, 0, 0
    # ~/dev/programs/python/pims/kinematics/visualize_rotation.py '[[-1,  0, 0], [ 0, -1, 0], [0, 0, 1]]' #180, 0, 0
    # ~/dev/programs/python/pims/kinematics/visualize_rotation.py '[[0.5, -0.70710677, 0.5], [0.5, 0.70710677, 0.5], [-0.70710677, 0.0, 0.70710677]]' #45, 45, 0

    print """
The input change of basis matrix, M, takes us from sensor coordinates to SSA coordinates
where a, b, c, ... g, h, i describe the components of SSA in terms of sensor coords like so:

[ xA        [ xS      [  a   b   c      [ xS     [ a*xS + b*yS + c*zS
  yA   = M *  yS    =    d   e   f    *   yS   =   d*xS + e*yS + f*zS
  zA ]        zS ]       g   h   i  ]     zS ]     g*xS + h*yS + i*zS ]
    """

    m = np.array(json.loads(sys.argv[1]))
    y, p, r = rotation_matrix_to_ypr(m)
    print 'this yields yaw, pitch, roll =', y, p, r
    show_results(y, p, r)
