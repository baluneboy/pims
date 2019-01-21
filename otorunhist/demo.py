#!/usr/bin/env python

import os
import datetime
import decimal
import numpy as np
# from main import plotnsave_daterange_histpad, plotnsave_monthrange_histpad, save_range_of_months
from scipy.stats import gaussian_kde
# import matplotlib.pyplot as plt
# import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import pandas as pd
import cPickle as pkl
from main import get_log10rms_bins, get_log10_data_and_extrema
from pims.signal.rounding import roundup100, roundup_int
from pims.utils.pimsdateutil import datetime_to_ymd_path

from ugaudio.load import padread
from pims.files.filter_pipeline import FileFilterPipeline, BigFile, PadDaySensorHours, HeaderMatchesSensorRateCutoffPad

import glob
import pandas as pd


AXMAP = {'x': 0, 'y': 1, 'z': 2, 'v': 3}


def demo_rigged_elementwise_max_ignore_nans():
    zero = np.empty((5, 3))
    zero[:] = -np.inf

    one = np.arange(15).reshape((5, 3))

    two = one.copy()
    two[1][:] = [-3, -4, -5]

    three = one.copy()
    three[2][:] = [66, 77, 88]

    four = np.empty((5, 3))
    four[:] = np.nan
    four[0][:] = [0, 0, 0]
    four[1][:] = [0, np.nan, 0]
    four[2][:] = [np.nan, 0, np.nan]
    four[3][:] = [333, 334, np.nan]

    five = one.copy()
    five[-1][:] = [120, 130, 140]

    print one; np.fmax(zero, one, out=zero); print zero; print '-'*22
    print two; np.fmax(zero, two, out=zero); print zero; print '-'*22
    print three; np.fmax(zero, three, out=zero); print zero; print '-'*22
    print four; np.fmax(zero, four, out=zero); print zero; print '-'*22
    print five; np.fmax(zero, five, out=zero); print zero; print '-'*22


def demo_rigged_elementwise_sum_ignore_nans():

    zero = np.zeros((4, 3), dtype=float)
    print zero; print '-' * 22

    one = np.arange(60).reshape((5, 4, 3)).astype(float)
    this_sum1 = np.nansum(one, axis=0)
    print this_sum1
    # print zero.shape
    # print this_sum1.shape
    np.nansum(np.dstack((zero, this_sum1)), axis=2, out=zero); print zero; print '-'*22

    two = one.copy()
    two[1][:] = -1.0
    print '*'*10; print two; print '#'*10
    this_sum2 = np.nansum(two, axis=0)
    print '='*10; print this_sum2; print '~'*10
    np.nansum(np.dstack((zero, this_sum2)), axis=2, out=zero); print zero; print '-'*22


def demo_rigged_full_month_fat_array():

    from main import get_date_range

    freqs = np.logspace(0, np.log(100)/np.log(10), 4)
    num_freqs = len(freqs)  # always this num freqs

    start, stop = datetime.datetime(2016, 1, 5), datetime.datetime(2016, 1, 6)
    delta = stop - start
    num_days = delta.days + 1

    files = ['one', 'two', 'three', 'four', 'five']
    num_files = len(files)

    fat_month = np.empty((num_files, num_freqs, 3), dtype=float)
    fat_month[:] = np.nan

    for c, f in enumerate(files):

        # load this file's Fx3 array
        file_array = np.random.randn(num_freqs, 3)

        fat_month[:][:][c] = file_array
        print fat_month
        print '-'*22

    # np.nansum(np.dstack((zero, this_sum2)), axis=2, out=zero); print zero; print '-'*22


def demo_hist2d():
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    xedges = [0, 1, 3, 5]
    yedges = [0, 2, 3, 4, 6]

    x = np.random.normal(2, 1, 100)
    y = np.random.normal(1, 1, 100)
    H, xedges, yedges = np.histogram2d(x, y, bins=(xedges, yedges))
    H = H.T  # Let each row list bins with common y range.

    fig = plt.figure(figsize=(7, 3))
    ax = fig.add_subplot(131, title='imshow: square bins')
    plt.imshow(H, interpolation='nearest', origin='low',
               extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])

    ax = fig.add_subplot(132, title='pcolormesh: actual edges',
                         aspect='equal')
    X, Y = np.meshgrid(xedges, yedges)
    ax.pcolormesh(X, Y, H)
    plt.show()


def demo_violinplot():

    sns.set(style="whitegrid")

    # Load the example dataset of brain network correlations
    df = sns.load_dataset("brain_networks", header=[0, 1, 2], index_col=0)

    # Pull out a specific subset of networks
    used_networks = [1, 3, 4, 5, 6, 7, 8, 11, 12, 13, 16, 17]
    used_columns = (df.columns.get_level_values("network")
                    .astype(int)
                    .isin(used_networks))
    df = df.loc[:, used_columns]

    # Compute the correlation matrix and average over networks
    corr_df = df.corr().groupby(level="network").mean()
    corr_df.index = corr_df.index.astype(int)
    corr_df = corr_df.sort_index().T

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 6))

    # Draw a violinplot with a narrower bandwidth than the default
    sns.violinplot(data=corr_df, palette="Set3", bw=.2, cut=1, linewidth=1)

    # Finalize the figure
    ax.set(ylim=(-.7, 1.05))
    sns.despine(left=True, bottom=True)

    plt.show()


def demo_pickle_save():

    # a = {'hello': 'world', 'bye': 4}
    #
    pickle_file = '/tmp/myfile.pkl'
    # with open(pickle_file, 'wb') as handle:
    #     pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)
    #
    # with open(pickle_file, 'rb') as handle:
    #     b = pickle.load(handle)
    #
    # print a == b
    # print type(a), type(b)

    fat_array = np.arange(24).reshape((2, 3, 4))
    fidx = np.array([1, 2, 3, 9])
    files = ['one', 'two']

    my_dict = dict()
    my_dict['fat_array'] = fat_array
    my_dict['fidx'] = fidx
    my_dict['files'] = files

    with open(pickle_file, 'wb') as handle:
        pkl.dump(my_dict, handle, protocol=pkl.HIGHEST_PROTOCOL)

    # Here is one that loads it.

    with open(pickle_file, 'rb') as handle:
        new_dict = pkl.load(handle)

    print np.all(new_dict['fat_array'] == my_dict['fat_array'])
    print new_dict['fidx'] == my_dict['fidx']
    print new_dict['files'] == my_dict['files']


def get_data():
    L = list()
    L.append(np.array([[[-5.00, -5.01, -5.02, -5.03],
                        [-5.04, -5.05, -5.06, -5.07],
                        [-5.08, -5.09, -5.10, -55.11]],

                       [[-5.12, -5.13, -5.14, -5.15],
                        [-5.16, -5.17, -5.18, -5.19],
                        [-5.20, -5.21, -5.22, -5.23]]]))

    L.append(np.array([[[-6.00, -6.01, -6.02, -6.03],
                        [-6.04, -6.05, -6.06, -6.07],
                        [-6.08, -6.09, -6.10, -6.11]],

                       [[-6.12, -6.13, -6.14, -6.15],
                        [-6.16, -6.17, -6.18, -66.19],
                        [-6.20, -6.21, -6.22, -66.23]]]))

    L.append(np.array([[[-7.00, -7.01, -7.02, -7.03],
                        [-7.04, -7.05, -7.06, -7.07],
                        [-7.08, -7.09, -7.10, -7.11]],

                       [[-7.12, -7.13, -7.14, -77.15],
                        [-7.16, -7.17, -7.18, -77.19],
                        [-7.20, -7.21, -7.22, -77.23]]]))

    return [10.0**i for i in L]

# ---------------------------------------------------------------------------------------------

def get_log10_data_and_exts(raw_data):
    """return log10(raw_data) and min & max"""
    data = np.log10(raw_data)
    return data, np.nanmin(data), np.nanmax(data)


def demo_get_log10_bins():
    """return logarithmic bin width, edges, centers and count"""
    grms_min, grms_max = 1.0e-9, 1.0  # yes, hard coded
    data_min = np.log10(grms_min)
    data_max = np.log10(grms_max)
    bin_width = 0.01  # this is in log10 domain
    bin_edges = np.arange(data_min, data_max + bin_width, bin_width)
    bin_centers = [i + bin_width / 2.0 for i in bin_edges[:-1]]
    num_bins = len(bin_edges)
    return bin_edges, bin_centers, bin_width, num_bins


def my_zeros(n):
    """return array of zeros with shape n (use either scalar or tuple for shape)"""
    return np.zeros(n, dtype='float64')


def demo_sum_otorunhist_pickle_files(pickle_files, tag, axs='xyzv'):
    """Return summed otorunhist/tag data from pickle files generated by save_otorunhist_pickle_file routine.

     Good for grand boxplot (percentile) info on log10(grms) data.
     """

    # define our columns
    ax_cols = [AXMAP[i] for i in axs]

    # get hard-coded RMS bin values
    log10rms_bin_edges, log10rms_bin_centers, log10rms_bin_width, num_log10rms_bins = get_log10rms_bins()

    # FIXME find a better way to get num_freqs without having to peek (load) first pickle file
    with open(pickle_files[0], 'rb') as fh:
        tmp_dict = pkl.load(fh)
    num_freqs = len(tmp_dict['freqs'])

    # initialize running values for histogram(s)
    hist_counts = my_zeros((len(ax_cols), len(log10rms_bin_centers), num_freqs))
    csum_pct = my_zeros((len(ax_cols), len(log10rms_bin_centers), num_freqs))

    # iterate over date-range, processed OTO count pickle files
    for pickle_file in pickle_files:

        with open(pickle_file, 'rb') as handle:
            my_dict = pkl.load(handle)

        fat_array = my_dict['fat_array']  # ndarray   972x46x4: type `float64`, ~(1 Mb)
        fidx = my_dict['fidx']            # dict      n=3 << ex/ sleep, wake and all
        # taghours = my_dict['taghours']    # dict      n=3 << ex/ sleep, wake and all
        # files = my_dict['files']          # list      n=972
        # freqs = my_dict['freqs']          # ndarray   46x1: 46 elems, type `float64`
        # sensor = my_dict['sensor']        # str       ex/ 121f03
        # start = my_dict['start']          # date      ex/ 2016-01-01
        # stop = my_dict['stop']            # date      ex/ 2016-01-07

        if tag not in fidx.keys():
            print 'tag = %s not among keys in %s' % (tag, pickle_file)
            continue  # to next file since this one's missing tag

        # get v array of file (i.e. time) indexes
        v = fidx[tag]
        raw_data = fat_array[np.array(v)]  # shape: (num_times_this_tag, num_freqs, num_axes)

        print pickle_file

        # iterate over input for axes (columns), ax_cols to get counts
        for idx, c in enumerate(ax_cols):

            # let's get it so we are working with log10(raw_data) from this column, c
            data, data_min, data_max = get_log10_data_and_extrema(raw_data[:, :, c])  # this ax data shape is: (num_times_this_tag, num_freqs)

            # update counts (per-axis)
            hist_counts[idx] += np.apply_along_axis(lambda a: np.histogram(a, log10rms_bin_edges)[0], 0, data)

    # print np.max(sum(sum(hist_counts)))

    # now get cumulative sum percentage (to later pluck percentiles from)
    for idh, k in enumerate(ax_cols):
        top = np.cumsum(hist_counts, axis=1, dtype='float64')[idh]
        bot = np.sum(hist_counts, axis=1, dtype='float64')[idh]
        csum_pct[idh] = 100.0 * np.true_divide(top, bot, out=np.zeros_like(top, dtype='float64'), where=(bot != 0))

    return hist_counts, csum_pct


def demo_masked(csum_pct, log10rms_bin_centers, pctile):

    # use shape to tile rms bin center values for plucking via mask
    num_f, num_r, num_a = csum_pct.shape  # num of: freqs, rms and axes
    rms_tiles = np.tile(log10rms_bin_centers.reshape(-1, 1), (num_f, 1, num_a))

    # mask off/out RMS values where cumsum percentage is strictly less than percentile value
    log10rms_values = np.ma.masked_where(csum_pct < pctile, rms_tiles)  # keep at/above pctile

    # create outer list, one outer list element for each axis
    log10rms_values_at_pctile = list()
    for ax in log10rms_values:
        # inner list for this axis holds 1st RMS value where percentile meets/beats pctile (or None if all masked out)
        values_for_this_ax = list()
        for fr in ax.T:
            rms_list = list(fr.compressed())
            values_for_this_ax.append(next(iter(rms_list), None))
        log10rms_values_at_pctile.append(values_for_this_ax)

    return log10rms_values_at_pctile



def demo_manual_boxplot(sensor, start, stop, tag, ax_cols, bin_centers, hist_counts, total_count, count_out_bounds, nice_freqs=True):

    num_freqs = len(bin_centers)

    # fake data to get stats as placeholder
    np.random.seed(19841211)
    data = np.random.lognormal(size=(4, num_freqs), mean=123, sigma=4.56)
    labels = 'A' * num_freqs

    # compute the boxplot stats
    stats = cbook.boxplot_stats(data, labels=labels)

    # After we've computed the stats, we can go through and change anything. Just to prove it, I'll
    # set the median of each set to the median of all the data, and double the means

    for n in range(len(stats)):
        stats[n]['whishi'] = np.float64(5)
        stats[n]['q3'] = np.float64(4)
        stats[n]['med'] = np.float64(3)
        stats[n]['q1'] = np.float64(2)
        stats[n]['whislo'] = np.float64(1)
        # -----------------------------------
        stats[n]['label'] = 'A'
        stats[n]['mean'] = np.nan
        stats[n]['cilo'] = -np.inf
        stats[n]['cihi'] = np.inf
        stats[n]['fliers'] = np.array([np.nan, ])
        stats[n]['iqr'] = np.nan

    # print list(stats[0])  # ['label', 'mean', 'iqr', 'cilo', 'cihi', 'whishi', 'whislo', 'fliers', 'q1', 'med', 'q3']

    font_size = 10  # fontsize

    fig, ax = plt.subplots(figsize=(10, 7.5))

    ax.bxp(stats, showfliers=False)

    title_str = 'One-Third Octave Band RMS Acceleration Summary'
    title_str += '\nSensor: %s, Tag: %s' % ('sensor', tag.upper())
    title_str += '\nGMT %s through %s' % (start.strftime('%Y-%m-%d'), stop.strftime('%Y-%m-%d'))
    ax.set_title(title_str, fontsize=font_size)

    plt.xlabel('Frequency (Hz)')
    plt.ylabel('RMS Acceleration  $log_{10}(g)$')

    # Set the ticks to indexes of freqs
    ax.set_xticks(range(1, num_freqs + 1))

    # Set xticklabels
    if nice_freqs:
        # custom xticklabels interpolated to "nice" frequencies
        locs, labels = plt.xticks()
        freq_ticks = [0.01, 0.1, 1, 10.0, 100.0]
        locs_new = np.interp(freq_ticks, np.concatenate(bin_centers).ravel(), locs)
        plt.xticks(locs_new, freq_ticks)

    else:
        # set the xticklabels to bin_centers with rotated text
        ax.set_xticklabels(['{:0g}'.format(i) for i in bin_centers.ravel()])
        plt.xticks(rotation=90)

    plt.show()

# ---------------------------------------------------------------------------------------------

def demo_vertical_boxplot():

    df = pd.DataFrame({'Freq':   [1,   2,   3,      4,   5],
                       'Score1': [100, 150, 110,    180, 125],
                       'Score2': [200, 210, np.nan, 125, 293],
                       'Score3': [50,  35,  200,    100, 180]})
    tdf = df.set_index('Freq').T
    print tdf
    tdf.boxplot()
    plt.show()


def demo_hist_hexbin():
    """
    hexbin is an axes method or pyplot function that is essentially
    a pcolor of a 2-D histogram with hexagonal cells.  It can be
    much more informative than a scatter plot; in the first subplot
    below, try substituting 'scatter' for 'hexbin'.
    """

    import numpy as np
    import matplotlib.pyplot as plt

    np.random.seed(0)
    n = 100000
    x = np.random.standard_normal(n)
    y = 2.0 + 3.0 * x + 4.0 * np.random.standard_normal(n)
    xmin = x.min()
    xmax = x.max()
    ymin = y.min()
    ymax = y.max()

    fig, axs = plt.subplots(ncols=2, sharey=True, figsize=(7, 4))
    fig.subplots_adjust(hspace=0.5, left=0.07, right=0.93)
    ax = axs[0]
    hb = ax.hexbin(x, y, gridsize=50, cmap='viridis')
    ax.axis([xmin, xmax, ymin, ymax])
    ax.set_title("Hexagon binning")
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label('counts')

    ax = axs[1]
    hb = ax.hexbin(x, y, gridsize=50, bins='log', cmap='viridis')
    ax.axis([xmin, xmax, ymin, ymax])
    ax.set_title("With a log color scale")
    cb = fig.colorbar(hb, ax=ax)
    cb.set_label('log10(N)')

    plt.show()


def demo_rigged_elementwise_count_ignore_nans():

    #                            T  F  3
    one = np.arange(60).reshape((5, 4, 3)).astype(float)
    one[(one > 1.0) & (one < 10.0)] = np.nan
    print one
    print np.count_nonzero(~np.isnan(one), axis=0)


def demo_kde():

    plt.style.use('seaborn-white')

    mean = [0, 0]
    cov = [[1, 1], [1, 2]]
    x, y = np.random.multivariate_normal(mean, cov, 10000).T

    # fit an array of size [Ndim, Nsamples]
    data = np.vstack([x, y])
    kde = gaussian_kde(data)

    # evaluate on a regular grid
    xgrid = np.linspace(-3.5, 3.5, 40)
    ygrid = np.linspace(-6, 6, 40)
    Xgrid, Ygrid = np.meshgrid(xgrid, ygrid)
    Z = kde.evaluate(np.vstack([Xgrid.ravel(), Ygrid.ravel()]))

    # Plot the result as an image
    plt.imshow(Z.reshape(Xgrid.shape),
               origin='lower', aspect='auto',
               extent=[-3.5, 3.5, -6, 6],
               cmap='Blues')
    cb = plt.colorbar()
    cb.set_label("density")
    plt.show()


def demo_stack():
    arrays = [np.random.randn(4, 3) for _ in range(10)]
    print np.stack(arrays, axis=0).shape
    print np.stack(arrays, axis=1).shape
    print np.stack(arrays, axis=2).shape


def demo_jury_rig_pickle_file():

    # freqs[10] is   0.10065 Hz
    # freqs[20] is   1.00665 Hz
    # freqs[30] is  10.0665  Hz
    # freqs[40] is 102.275   Hz

    pickle_file = '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-08_2016-01-14_121f03_sleep_all_wake_otorunhist.pkl'
    with open(pickle_file, 'rb') as handle:
        my_dict = pkl.load(handle)

    fat_array = my_dict['fat_array']  # ndarray   972x46x4: type `float64`, ~(1 Mb)
    fidx = my_dict['fidx']            # dict      n=3 << ex/ sleep, wake and all
    taghours = my_dict['taghours']    # dict      n=3 << ex/ sleep, wake and all
    files = my_dict['files']          # list      n=972
    freqs = my_dict['freqs']          # ndarray   46x1: 46 elems, type `float64`
    sensor = my_dict['sensor']        # str       ex/ 121f03
    start = my_dict['start']          # date      ex/ 2016-01-01
    stop = my_dict['stop']            # date      ex/ 2016-01-07

    v = fat_array[:, :, 3]

    # v[:, 10][0:99] = 1e-6
    # v[:, 10][100:399] = 1e-7
    # v[:, 10][400:599] = 1e-8
    # v[:, 10][600:899] = 10 ** (-7.5)
    # v[:, 10][900:] = 10 ** (-5.5)
    #
    # v[:, 20][0:199] = 10 ** (-8.5)
    # v[:, 20][200:399] = 10 ** (-8.2)
    # v[:, 20][400:499] = 10 ** (-7.5)
    # v[:, 20][500:899] = 10 ** (-6.5)
    # v[:, 20][900:] = 10 ** (-6.0)
    #
    # v[:, 30][0:99] = 1e-7
    # v[:, 30][100:399] = 1e-8
    # v[:, 30][400:599] = 1e-6
    # v[:, 30][600:899] = 10 ** (-6.5)
    # v[:, 30][900:] = 10 ** (-8.5)
    #
    # v[:, 40][0:199] =   10 ** (-7.5)
    # v[:, 40][200:399] = 10 ** (-6.2)
    # v[:, 40][400:499] = 10 ** (-5.5)
    # v[:, 40][500:899] = 10 ** (-4.5)
    # v[:, 40][900:] =    10 ** (-8.9)

    v[:, 10][0:199] = 10 ** (-8.5)
    v[:, 10][200:399] = 10 ** (-7.0)
    v[:, 10][400:599] = 10 ** (-5.5)
    v[:, 10][600:799] = 10 ** (-4.0)
    v[:, 10][800:] = 10 ** (-2.5)

    v[:, 20][0:199] = 10 ** (-8.5)
    v[:, 20][200:399] = 10 ** (-8.2)
    v[:, 20][400:499] = 10 ** (-7.5)
    v[:, 20][500:899] = 10 ** (-6.5)
    v[:, 20][900:] = 10 ** (-6.0)

    v[:, 30][0:199] = 10 ** (-7.5)
    v[:, 30][200:399] = 10 ** (-6.0)
    v[:, 30][400:599] = 10 ** (-4.5)
    v[:, 30][600:799] = 10 ** (-4.0)
    v[:, 30][800:] = 10 ** (-3.5)

    v[:, 40][0:199] =   10 ** (-7.5)
    v[:, 40][200:399] = 10 ** (-6.2)
    v[:, 40][400:499] = 10 ** (-5.5)
    v[:, 40][500:899] = 10 ** (-4.5)
    v[:, 40][900:] =    10 ** (-8.9)

    fat_array[:, :, 3] = v
    my_dict['fat_array'] = fat_array
    new_pickle_file = pickle_file.replace('.pkl', '.pkl.dummy')
    with open(new_pickle_file, 'wb') as handle:
        pkl.dump(my_dict, handle, protocol=pkl.HIGHEST_PROTOCOL)
    print 'wrote %s' % new_pickle_file


def demo_look_jury_rig_pickle_file():

    # freqs[10] is   0.10065 Hz
    # freqs[20] is   1.00665 Hz
    # freqs[30] is  10.0665  Hz
    # freqs[40] is 102.275   Hz

    pickle_file = '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-08_2016-01-14_121f03_sleep_all_wake_otorunhist.pkl.dummy'
    with open(pickle_file, 'rb') as handle:
        my_dict = pkl.load(handle)

    fat_array = my_dict['fat_array']  # ndarray   972x46x4: type `float64`, ~(1 Mb)
    fidx = my_dict['fidx']            # dict      n=3 << ex/ sleep, wake and all
    taghours = my_dict['taghours']    # dict      n=3 << ex/ sleep, wake and all
    files = my_dict['files']          # list      n=972
    freqs = my_dict['freqs']          # ndarray   46x1: 46 elems, type `float64`
    sensor = my_dict['sensor']        # str       ex/ 121f03
    start = my_dict['start']          # date      ex/ 2016-01-01
    stop = my_dict['stop']            # date      ex/ 2016-01-07

    print fat_array.shape
    print fidx.keys()


def demo_step_plot():

    x = np.arange(1, 7, 0.4)
    y0 = np.sin(x)
    y = y0.copy() + 2.5

    plt.step(x, y, label='pre (default)')

    y -= 0.5
    plt.step(x, y, where='mid', label='mid')

    y -= 0.5
    plt.step(x, y, where='post', label='post')

    y = np.ma.masked_where((y0 > -0.15) & (y0 < 0.15), y - 0.5)
    plt.step(x, y, label='masked (pre)')

    plt.legend()

    plt.xlim(0, 7)
    plt.ylim(-0.5, 4)

    plt.show()


def demo_boxplot_width_setter():
    np.random.seed(42)
    a = np.cumsum(np.random.rayleigh(150, size=(50, 8)), axis = 1)
    fig, ax = plt.subplots()

    positions = np.logspace(-0.1, 2.6, 8)

    w = 0.1
    width = lambda p, w: 10**(np.log10(p) + w/2.0) - 10**(np.log10(p) - w/2.0)

    ax.boxplot(a, positions=positions, widths=width(positions, w))
    ax.set_xscale('log')
    plt.show()


def file_trapz(pad_file, fs, sec=10.0):

    # read data from PAD file into Tx4 array
    a = padread(pad_file)

    # toss out time column
    a = np.delete(a, 0, axis=1)

    # demean signal
    b = a - a.mean(axis=0)

    # determine how many time steps (dt) we will integrate over (how many delta t's)
    dt = 1.0 / fs
    nt = int(np.ceil(sec / dt))

    # print b.shape
    # print 'nt', nt

    # fabricate a depth dimension for deep array, which is to be filled in with PAD block(s)
    nd = roundup_int(b.shape[0], nt) / nt

    # build a slightly bigger array than we need by appending to what we read from file just a bit
    total_rows = nd * nt
    num_blank_rows = total_rows - b.shape[0]
    deep_array = np.vstack((b, np.nan*np.ones((num_blank_rows, 3))))

    # the above vstack of NaNs allows us to reshape nicely for integration along the proper dimension
    deep_array = deep_array.reshape((nd, -1, 3))

    # TODO for part (A) of Gateway, we would not delete deep_array's last element [ we would for part (B) though ]

    # if we had to add blank (NaN) rows, then let's delete deep_array's last, INCOMPLETE element now
    if num_blank_rows != 0:
        deep_array = np.delete(deep_array, -1, axis=0)

    # return trapezoidal integration over time (nominally, 100sec)
    return np.trapz(deep_array, dx=dt, axis=1)


def file_trapz_some_pad_files(start, end, sensor, fs, fc, hours):

    fsums = list()
    for d in pd.date_range(start, end):
        print d.date(), sensor, " > ",
        day_dir = datetime_to_ymd_path(d)

        # initialize processing pipeline (no file list as input yet)
        ffp = FileFilterPipeline(HeaderMatchesSensorRateCutoffPad(sensor, fs, fc),
                                 PadDaySensorHours(d.strftime('%Y-%m-%d'), sensor, hours),
                                 BigFile(min_bytes=2*1024*1024))

        # apply processing pipeline (now ffp is callable)
        glob_pat = os.path.join(day_dir, '*_*_%s/*.%s' % (sensor, sensor))
        day_files = glob.glob(glob_pat)
        if len(day_files) == 0:
            print 'MISSING---',
        else:
            c = 0
            # work with files we want to keep
            for pad_file in ffp(day_files):
                fsums.append(file_trapz(pad_file, fs, sec=10.0))
                c += 1
            print 'processed %d files' % c,
        print ''

    return np.concatenate(fsums, axis=0)


if __name__ == '__main__':

    # monthly results go here:
    # /misc/yoda/www/plots/batch/results/transient/year2020/month11/2020-11-01_2020-11-30_121f03006_sleep_transient.pkl
    #
    # # pickle save file sums (fsums) array
    # out_name = get_transient_pickle_filename(start, stop, sensor, taghours)
    # pickle_file = os.path.join(out_pth, out_name)
    #
    # my_dict = dict()
    # my_dict['fsums'] = fsums
    # my_dict['start'] = start
    # my_dict['stop'] = stop
    # my_dict['sensor'] = sensor
    # my_dict['taghours'] = taghours
    #
    # with open(pickle_file, 'wb') as handle:
    #     pkl.dump(my_dict, handle, protocol=pkl.HIGHEST_PROTOCOL)
    #
    # print 'saved %s' % pickle_file

    # SLEEP FILES ONLY
    start, end = '2016-01-01', '2016-02-29'
    sensor = '121f03006'
    fs, fc = 142.0, 6.0
    hours = [(0, 4)]
    fsums = file_trapz_some_pad_files(start, end, sensor, fs, fc, hours)
    print fsums.shape
    print fsums

    # pad_file = '/misc/yoda/pub/pad/year2019/month01/day01/sams2_accel_121f03006/2019_01_01_00_06_20.862-2019_01_01_00_37_06.939.121f03006'
    # pad_file = '/misc/yoda/pub/pad/year2019/month01/day01/sams2_accel_121f03006/2019_01_01_03_10_57.369+2019_01_01_03_14_56.306.121f03006'
    # fsum = file_trapz(pad_file, fs)
    # print fsum
    # print fsum.shape

    # demo_iss_req_steps()
    # demo_boxplot_width_setter()
    raise SystemExit


    # demo_jury_rig_pickle_file()
    # demo_look_jury_rig_pickle_file()
    # raise SystemExit

    #                                 AbyRbyF
    # csum_pct = np.arange(24).reshape((2, 3, 4))
    # log10rms_bin_centers = np.arange(0.11, 0.33, 0.11)

    from main import sum_otorunhist_pickle_files, get_log10rms_bins

    dummy_pickle_files = ['/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-01_2016-01-07_121f03_sleep_all_wake_otorunhist.pkl.dummy',
                    '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-08_2016-01-14_121f03_sleep_all_wake_otorunhist.pkl.dummy']

    hist_counts, csum_pct = sum_otorunhist_pickle_files(dummy_pickle_files, 'all', axs='xyzv')
    log10rms_bin_edges, log10rms_bin_centers, log10rms_bin_width, num_log10rms_bins = get_log10rms_bins()

    print csum_pct
    print log10rms_bin_centers
    print '@' * 33

    # build list for percentiles' RMS values
    percentile_stats = list()
    pctiles = [1.0, 25.0, 50.0, 75.0, 99.0]
    for pctile in pctiles:
        log10rms_vals_for_pctile = demo_masked(csum_pct, log10rms_bin_centers, pctile)
        percentile_stats.append(log10rms_vals_for_pctile)

    # since we got 1st 2 dimensions reversed above, let's get back to AxRxF ordering here
    raf = np.array(percentile_stats)    # RxAxF is RMSxAXISxFREQ
    arf = np.transpose(raf, (1, 0, 2))  # AxRxF is AXISxRMSxFREQ
    print arf
    raise SystemExit

    pickle_files = ['/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-01_2016-01-07_121f03_sleep_all_wake_otorunhist.pkl',
                    '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-08_2016-01-14_121f03_sleep_all_wake_otorunhist.pkl']

    axs = 'xyzv'
    tag = 'sleep'
    demo_sum_otorunhist_pickle_files(pickle_files, tag, axs=axs)
    raise SystemExit

    sensor = '121f0x'
    start = datetime.datetime(1988,1,2)
    stop = datetime.datetime(1988,1,15)
    tag = 'chill'
    ax_cols = [3, ]
    with open(pickle_files[0], 'rb') as handle:
        my_dict = pkl.load(handle)

    bin_centers = my_dict['freqs']  # np.arange(0.01, 0.46 + 0.01, 0.01)
    hist_counts, total_count, count_out_bounds = None, None, None
    # hist_counts, total_count, count_out_bounds = sum_otorunhist_pickle_files(pickle_files)
    # stats = compute_otorunhist_percentiles(hist_counts, total_count, count_out_bounds)
    demo_manual_boxplot(sensor, start, stop, tag, ax_cols, bin_centers, hist_counts, total_count, count_out_bounds, nice_freqs=True)
    raise SystemExit

    demo_running_log10_hist(pickle_files, 'sleep', ax_cols=None)
    raise SystemExit

    demo_rigged_full_month_fat_array()
    # demo_kde()
    # demo_rigged_elementwise_count_ignore_nans()
    # demo_eng_units()
    # demo_save_range_of_months()
    # demo_plotnsave_daterange_histpad()
