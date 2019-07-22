#!/usr/bin/env python

import os
import re
import sys
import json
import numpy as np
from mayavi import mlab
from pims.kinematics.rotation import ypr_to_3_rotation_matrices, rotation_matrix_to_ypr


# input parameters
defaults = {
    'sensor': None,            # string for start date
    'sensor_location': None,   # string for stop date
    'date_str': None,          # string for date, typically for when sensor was moved
    'rot_mat': None,           # string form of rotation matrix
    'text_pos_z': '0.85',      # string for z-position of label text that hovers above each coord sys
    'cs_spacing': '1.75',      # coordinate system spacing along the display's x-axis
    'top_dir': '/misc/yoda/www/plots/user/handbook/source_docs',  # parent directory under which subdir/output_file goes
}
parameters = defaults.copy()


def parameters_ok():
    """check for reasonableness of parameters entered on command line"""

    for param in ['sensor_location', 'sensor']:
        if parameters[param] is None:
            print 'ABORT BECAUSE NO ' + param + ' SPECIFIED (None)'
            return False
        elif not isinstance(parameters[param], str):
            print 'ABORT BECAUSE ' + param + ' IS NOT A STRING'
            return False

    if parameters['date_str'] is None:
        print 'ABORT BECAUSE date_str IS None'
        return False
    if not re.match('^\d{4}-\d{2}-\d{2}$', parameters['date_str']):
        print 'date_str %s does not match expected pattern (YYYY-MM-DD)' % parameters['date_str']
        return False

    if parameters['rot_mat'] is None:
        print 'ABORT BECAUSE rot_mat is None'
        return False
    try:
        parameters['rot_mat'] = np.array(json.loads(parameters['rot_mat']))
    except Exception, e:
        print 'ABORT WHILE TRYING TO JSON PARSE MATRIX FROM rot_mat BECAUSE ' + e.message
        return False

    for param in ['text_pos_z', 'cs_spacing']:
        try:
            parameters[param] = float(parameters[param])
        except Exception, e:
            print 'ABORT WHILE TRYING TO CAST ' + param + ' AS FLOAT BECAUSE ' + e.message
            return False

    if not os.path.exists(parameters['top_dir']):
        print 'ABORT BECAUSE TOP DIR ' + parameters['top_dir'] + ' DOES NOT EXIST'
        return False

    return True  # all OK; otherwise, return False above


def print_usage():
    """print short description of how to run the program"""
    print 'usage: %s [options]' % os.path.abspath(__file__)
    print '       options (and default values) are:'
    for i in defaults.keys():
        print '\t%s=%s' % (i, defaults[i])


def draw_coord_sys_with_text(x, v, objs, zpos, label):
    """draw coord sys glpyhs at x-position with text/title label hovering at zpos"""

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

    return objs


def show_4_coord_sys(y, p, r, cs_spacing, txt_zpos):
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
    x = 3.0 * cs_spacing  # this is how mayavi defaults, we will put first coord sys glyphs furthest along X
    objs = draw_coord_sys_with_text(x, v, objs, txt_zpos, 'A')

    # first rotation about Z-axis (yaw) --------------------------------------------------------------------------------
    x -= cs_spacing  # move inward to origin along X for next coord sys glyphs
    v = np.matmul(np.linalg.inv(a), v)
    objs = draw_coord_sys_with_text(x, v, objs, txt_zpos, 'B')

    # second rotation about Y'-axis (pitch) ----------------------------------------------------------------------------
    x -= cs_spacing  # move inward to origin along X for next coord sys glyphs
    v = np.matmul(np.linalg.inv(b), v)
    objs = draw_coord_sys_with_text(x, v, objs, txt_zpos, 'C')

    # third rotation about X''-axis (roll) -----------------------------------------------------------------------------
    x -= cs_spacing  # move inward to origin along X for next coord sys glyphs
    v = np.matmul(np.linalg.inv(c), v)
    objs = draw_coord_sys_with_text(x, v, objs, txt_zpos, 'S')

    return objs


def build_output_filename(sensor, loc, date_str, top_dir):
    #/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Sensor_Check_121f02_RMS_Console_2018-07-11
    bname = 'hb_vib_vehicle_Sensor_Check_' + '_'.join([sensor, loc.replace(' ', '_'), date_str]) + '.png'
    return os.path.join(top_dir, bname)


def show_results(yaw, pitch, roll, cs_spacing, txt_zpos):

    # TODO save figure for configuration management purposes (filename convention sensor, location, date, etc.)
    # TODO add annotations on the figure for sensor, location and date [DATE OF WHAT?]

    mlab.figure(bgcolor=(1, 1, 1), fgcolor=(0, 0, 0), size=(1200, 900))

    title = 'yaw, pitch, roll = %.1f,  %.1f,  %.1f' % (yaw, pitch, roll)
    objs = show_4_coord_sys(yaw, pitch, roll, cs_spacing, txt_zpos)
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


def run(m, sensor, sensor_loc, cs_spacing, txt_zpos):
    """create plots and gather data from start to stop date (results into output_dir)"""

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

    y, p, r = rotation_matrix_to_ypr(m)
    print 'this yields yaw, pitch, roll =', y, p, r
    show_results(y, p, r, cs_spacing, txt_zpos)


def main(argv):
    """get command line arguments (or defaults) and run processing"""
    # parse command line
    for p in argv[1:]:
        pair = p.split('=')
        if 2 != len(pair):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if parameters_ok():
            run(parameters['rot_mat'],
                parameters['sensor'], parameters['sensor_location'],
                parameters['cs_spacing'],
                parameters['text_pos_z'],
                )
            return 0
    print_usage()


if __name__ == '__main__':
    sys.exit(main(sys.argv))
