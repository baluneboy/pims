#!/usr/bin/env python

import mayavi
from mayavi import mlab
from mayavi.modules.grid_plane import GridPlane
import numpy as np
from kinematics.rotation import ypr_to_3_rotation_matrices

np.set_printoptions(formatter={'float': lambda x: '{0:+0.2f}'.format(x)})
a, b, c = ypr_to_3_rotation_matrices(-90.0, 0.0, 0.0)
print a
print b
print c


CS_SPACING = 1.75  # coordinate system spacing

def plot_4_coords():

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

    mlab.text3d(x, 0, 1, 'A', scale=0.15)

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

    mlab.text3d(x, 0, 1, 'B', scale=0.15)

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

    mlab.text3d(x, 0, 1, 'C', scale=0.15)

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

    mlab.text3d(x, 0, 1, 'S', scale=0.15)

    return objs


def demo():
    mlab.figure(bgcolor=(1, 1, 1), fgcolor=(0, 0, 0), size=(1200, 900))
    objs = plot_4_coords()
    # mlab.orientation_axes()
    # gp = GridPlane()
    # gp.grid_plane.axis = 'y'
    mlab.show()


if __name__ == '__main__':
    demo()
