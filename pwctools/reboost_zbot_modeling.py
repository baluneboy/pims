import datetime
import warnings
import numpy as np
import pandas as pd
from scipy import interpolate
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def round_seconds(dtm):
    """return datetime rounded to nearest second"""
    if dtm.microsecond >= 500_000:
        dtm += datetime.timedelta(seconds=1)
    dtm = dtm.replace(microsecond=0)
    return dtm.replace(second=np.round(dtm.second))


def sdn2dtm(sdn):
    """return array of datetimes converted from MATLAB serial datenum format"""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', UserWarning)  # FIXME for nanoseconds warning
        return pd.to_datetime(sdn-719529, unit='D').to_pydatetime()


def dtm2sdn(dt):
    """return array of MATLAB-like serial datenums converted from datetime"""
    mdn = dt + datetime.timedelta(days=366)
    frac_seconds = (dt-datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0)).seconds / (24.0 * 60.0 * 60.0)
    frac_microseconds = dt.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0)
    return mdn.toordinal() + frac_seconds + frac_microseconds


def generate_time_array(m1, m2):
    """generate new time step values based on endpoints, t1 & t4, and start of subset, t2

       begin_superset                   begin_subset         end_subset                     end_superset
       t1                               t2                   t3                             t4
       -p*dt          ... -2*dt, -1*dt, 0*dt, 1*dt...                                       q*dt

    """
    # time step
    t2 = m2[0, 0]
    t3 = m2[-1, 0]
    dt = m2[1, 0] - m2[0, 0]

    # marked points
    t1 = m1[0, 0]
    t4 = m1[-1, 0]

    # integer number of time steps to endpoints, nearest seconds...crude stuff
    p = np.floor((t2 - t1) / dt)
    q = np.floor((t4 - t2) / dt)
    t_before = np.arange(t2-dt, m1[0, 0], -dt)[::-1]
    t_after = np.arange(t3+dt, m1[-1, 0], dt)

    # 3 piecewise time chunks
    tnew = np.append(np.append(t_before, m2[:, 0]), t_after)

    return tnew


def get_fake_superset():
    """return data for longer, superset which has less frequent samples, e.g. 5-hour span every 16 seconds"""
    t1 = 729529 + np.arange(0, 13, 2)
    x1 = 0.1 * np.exp(-t1 / 3.0)
    y1 = np.exp(-t1 / 3.0)
    z1 = 10.0 * np.exp(-t1 / 3.0)
    return np.column_stack([t1, x1, y1, z1])


def get_fake_subset():
    """return data for subset"""
    # shorter subset of data that we will add to longer superset (more frequent time steps); e.g. 20-minute span
    # note: we will add only at appropriate/common time steps and nowhere else so this has to be a subset of time range
    t2 = 729529 + np.arange(3.8, 8.3, 0.2)
    x2 = 1 * np.sin(2 * np.pi * 0.3 * t2)
    y2 = 10 * np.sin(2 * np.pi * 0.3 * t2)
    z2 = 100 * np.sin(2 * np.pi * 0.3 * t2)
    return np.column_stack([t2, x2, y2, z2])


def read_csv(csv_file):
    """return numpy array, txyz, read from CSV file"""
    return np.genfromtxt(csv_file, delimiter=',')


def plot_txyz(txyz):
    """produce 3-panel subplots for x-, y-, and z-axis vs. time"""

    # plot z-axis
    ax3 = plt.subplot(313)
    plt.plot(sdn2dtm(txyz[:, 0]), txyz[:, 3])

    # plot x-axis
    ax1 = plt.subplot(311, sharex=ax3)
    plt.plot(sdn2dtm(txyz[:, 0]), txyz[:, 1])

    # plot y-axis
    ax2 = plt.subplot(312, sharex=ax3)
    plt.plot(sdn2dtm(txyz[:, 0]), txyz[:, 2])

    # make xy-axes tick labels invisible
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)

    # major ticks every hour
    fmt_hourly = mdates.HourLocator(interval=1)
    ax3.xaxis.set_major_locator(fmt_hourly)

    # minor ticks every 30 minutes
    fmt_half_hour = mdates.MinuteLocator(interval=30)
    ax3.xaxis.set_minor_locator(fmt_half_hour)

    # text in the x axis will be displayed in 'HH:MM' format.
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # set time axis limits, round to nearest hour
    tmin = np.datetime64(sdn2dtm(txyz[0, 0]), 'h')
    tmax = tmin + np.timedelta64(5, 'h')
    ax3.set_xlim(tmin, tmax)

    # format the coords message box, i.e. the numbers displayed as the cursor moves across axes in interactive GUI
    ax3.format_xdata = mdates.DateFormatter('%H:%M:%S')
    ax3.format_ydata = lambda x: f'{x:.2f}'
    ax3.grid(True)
    ax2.grid(True)
    ax1.grid(True)

    # rotates and right aligns the x labels, and moves the bottom of the axes up to make room for them
    fig = ax3.figure
    fig.autofmt_xdate()

    ax3.set_xlabel('Start GMT ' + sdn2dtm(txyz[0, 0]).strftime('%Y-%m-%d') + '/HH:MM')
    plt.show()


def combine_signals(m1, m2):
    """combine two Mx4 arrays (txyz), superset and subset; M is different for each array = number of time steps"""

    # use a grid to create new set of time step values based on superset and subset times
    tnew = generate_time_array(m1, m2)

    # get column-wise interpolation object for the superset
    f = interpolate.interp1d(m1[:, 0], m1[:, 1:], axis=0)

    # interpolate to get new superset on time step values that will mesh with subset
    xyz3 = f(tnew)
    m3 = np.column_stack([tnew, xyz3])

    # find index where we will add 2 signals together
    idx = np.where(m3[:, 0] >= m2[0, 0])[0][0]

    # now combine interpolated superset at subset's time steps with the subset itself
    m3[idx:idx+m2.shape[0], 1:] += m2[:, 1:]

    # np.savetxt("c:/temp/foo.csv", m3, delimiter=",")

    # plot
    h = plt.plot(m1[:, 0], m1[:, 1], 'bs', m3[:, 0], m3[:, 1], 'r.', m3[:, 0], m3[:, 1], 'r-')
    h[0].set_markersize(4)
    h[1].set_markersize(6)

    plt.show()


def main():
    """read superset (quasi-steady) and subset (reboost) with differing sample rates and time steps and combine them"""

    # read day's worth of quasi-steady estimate data for day of reboost
    csv_file1 = "G:/handbook/source_docs/hb_vib_vehicle_Progress_67P_Reboost_2017-11-02/2017_11_02_00_00_00_ossbtmf_gvt3_historical_time-shifted_quasi-steady_estimate.csv"
    m1 = read_csv(csv_file1)

    # read short reboost period to capture those dynamics
    csv_file2 = "G:/handbook/source_docs/hb_vib_vehicle_Progress_67P_Reboost_2017-11-02/reboost.csv"
    m2 = read_csv(csv_file2)

    # actually, we will keep only a subset of the quasi-steady superset on reboost day between hours 00 thru 05
    d2 = round_seconds(sdn2dtm(m2[0, 0]))
    d1 = datetime.datetime(2017, 11, 2, 0, 0, 0)
    d4 = datetime.datetime(2017, 11, 2, 5, 0, 0)
    mask_5hours = (m1[:, 0] >= dtm2sdn(d1)) & (m1[:, 0] <= dtm2sdn(d4))
    m1 = m1[mask_5hours, :]

    # d1, d2 = datetime.datetime(2011, 10, 10, 0, 0, 0), datetime.datetime(2011, 10, 11)
    # dr = pd.date_range(d1, d2, freq='10s')
    # for d in dr:
    #     print(d)

    # run interpolation routine to combine the 2 signals
    combine_signals(m1, m2)


if __name__ == '__main__':
    main()
