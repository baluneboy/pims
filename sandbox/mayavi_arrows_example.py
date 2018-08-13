from mayavi import mlab
import numpy as np
import colorsys


def color(theta, phi):
    while(phi < 0):
        phi += 2.0*np.pi
    h = phi / (2.0 * np.pi)
    s = 1
    v = 1.0 - 0.9999999*(theta / np.pi)
    #print("h = {}, s = {}, v ={}".format(h,s,v))
    return colorsys.hsv_to_rgb(h,s,v)


def plot_nice():
    x = np.array([0.,1.,2.,3.])
    y = np.array([0.,0.,0.,0.])
    z = np.array([0.,0.,0.,0.])

    phi   = np.linspace(0,np.pi/2.0,x.shape[0])
    theta = phi

    u = np.sin(theta) * np.cos(phi)
    v = np.sin(theta) * np.sin(phi)
    w = np.cos(theta)

    objs = []

    for i in range(x.shape[0]):
        r,g,b = color(theta[i], phi[i])
        #print("R: {}, G: {}, B: {}".format(r,g,b))
        print 'locs:', x[i], y[i], z[i],
        print 'comps:', u[i], v[i], w[i]
        obj = mlab.quiver3d(x[i], y[i], z[i], u[i], v[i], w[i],
                line_width=3, color=(r,g,b), colormap='hsv',
                scale_factor=0.8, mode='arrow',resolution=25)
        objs.append(obj)

    return objs


mlab.figure(bgcolor=(1, 1, 1))
objs = plot_nice()
mlab.show()
print len(objs)

