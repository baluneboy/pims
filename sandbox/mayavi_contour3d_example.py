import numpy as np
from mayavi import mlab
fig = mlab.figure(1, size=(400, 400), bgcolor=(1, 1, 1), fgcolor=(0, 0, 0))
x, y, z = np.ogrid[-10:10:20j, -10:10:20j, -10:10:20j]
s = np.sin(x*y*z)/(x*y*z)
mlab.contour3d(s)

mlab.view(42, 73, 104, [79,  75,  76])

mlab.show()
