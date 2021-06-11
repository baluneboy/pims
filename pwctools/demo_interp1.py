import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt


def generate_time_array(m1, m2):
    """generate new time step values based on endpoints, t1 & t4, and start of subset, t2

       begin_superset                   begin_subset         end_subset                     end_superset
       t1                               t2                   t3                             t4
       -p*dt          ... -2*dt, -1*dt, 0*dt, 1*dt...                                       q*dt

    """
    # time step
    dt = np.round(m2[1, 0] - m2[0, 0], decimals=6)

    # marked points
    t1, t4 = m1[0, 0], m1[-1, 0]
    t2 = m2[0, 0]

    # integer number of time steps to endpoints
    p = np.ceil((t2 - t1) / dt)
    q = np.ceil((t4 - t2) / dt)

    return np.arange(t2-(p-1)*dt, t2+q*dt, dt)


def get_superset():
    """return data for longer, superset which has less frequent samples, e.g. 5-hour span every 16 seconds"""
    t1 = 729529 + np.arange(0, 13, 2)
    x1 = 0.1 * np.exp(-t1 / 3.0)
    y1 = np.exp(-t1 / 3.0)
    z1 = 10.0 * np.exp(-t1 / 3.0)
    return np.column_stack([t1, x1, y1, z1])


def get_subset():
    """return data for subset"""
    # shorter subset of data that we will add to longer superset (more frequent time steps); e.g. 20-minute span
    # note: we will add only at appropriate/common time steps and nowhere else so this has to be a subset of time range
    t2 = 729529 + np.arange(3.8, 8.3, 0.2)
    x2 = 1 * np.sin(2 * np.pi * 0.3 * t2)
    y2 = 10 * np.sin(2 * np.pi * 0.3 * t2)
    z2 = 100 * np.sin(2 * np.pi * 0.3 * t2)
    return np.column_stack([t2, x2, y2, z2])

def demo_main():
    # get two Mx4 arrays (txyz) for superset and for subset (M is different for each array = number of time steps)
    m1 = get_superset()
    m2 = get_subset()

    # use a grid to create new set of time step values
    tnew = generate_time_array(m1, m2)

    # get columnwise interpolation object for the superset
    f = interpolate.interp1d(m1[:, 0], m1[:, 1:], axis=0)

    # interpolate to get new superset on time step values that will mesh with subset
    xyz3 = f(tnew)
    m3 = np.column_stack([tnew, xyz3])

    # verify subset with new time step values have proper length
    tsup = np.round(tnew, decimals=6)
    tsub = np.round(m2[:, 0], decimals=6)
    mask_subset = (tsup >= tsub[0]) & (tsup <= tsub[-1])
    if len(tnew[mask_subset]) != m2.shape[0]:
        raise RuntimeError('interpolated array size does not mesh with subset size')

    # add subset values onto new, interpolated (main) array
    m3[mask_subset, 1:] += m2[:, 1:]

    # plot
    h = plt.plot(m1[:, 0], m1[:, 2], 'bs', m3[:, 0], m3[:, 2], 'r-', m3[:, 0], m3[:, 2], 'ro')
    h[0].set_markersize(8)

    plt.show()


if __name__ == '__main__':
    demo_main()
