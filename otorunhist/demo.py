#!/usr/bin/env python

import datetime
import decimal
import numpy as np
# from main import plotnsave_daterange_histpad, plotnsave_monthrange_histpad, save_range_of_months
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import cPickle as pkl


class FatArray(object):

    def __init__(self, num_freqs):
        self.data = np.empty((num_freqs, 3), dtype=float)
        self.data[:] = np.nan
        self.capacity = 500
        self.size = 0

    def update(self, depth):
        for r in depth:
            self.add(r)

    def add(self, x):
        if self.size == self.capacity:
            self.capacity *= 2
            newdata = np.zeros((self.capacity,))
            newdata[:self.size] = self.data
            self.data = newdata

        self.data[self.size] = x
        self.size += 1

    def finalize(self):
        data = self.data[:self.size]
        return np.reshape(data, newshape=(len(data)/5, 5))


def demo_eng_units():
    for n in (10 ** e for e in range(-1, -8, -1)):
        d = decimal.Decimal(str(n))
        print d.to_eng_string()
    x = decimal.Decimal(str(11334264123))
    print x.to_eng_string()


def demo_plotnsave_monthrange_histpad():
    start = datetime.date(2017, 1, 1)
    stop = datetime.date(2017, 3, 1)
    plotnsave_monthrange_histpad(start, stop, sensor='121f03')


def demo_save_range_of_months():
    # FIXME this has to be able to step year boundaries!
    year = 2018
    month1 = 4
    month2 = 11
    save_range_of_months(year, month1, month2, sensor='121f05')


def demo_plotnsave_daterange_histpad():
    #start = datetime.date(2016, 1, 1)
    #stop = datetime.date(2016, 3, 31)
    start = datetime.date(2018, 1, 18)
    stop = datetime.date(2018, 11, 30)    
    stop = datetime.date(2018, 1, 22)    
    plotnsave_daterange_histpad(start, stop, sensor='121f05')


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


def get_log10_data_and_exts(raw_data):
    """return log10(raw_data) and min & max"""
    data = np.log10(raw_data)
    return data, np.nanmin(data), np.nanmax(data)


def get_log10_bins():
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
    return np.zeros(n, dtype='int64')


def demo_running_log10_hist(pickle_files, tag, ax_cols=None):
    """running histogram of log10(data)"""

    # define our columns
    col_defs = {0: 'x', 1: 'y', 2: 'z', 3: 'v'}

    # handle columns (axes) we want to process
    # NOTE: for rss(x,y,z), use ax_cols = [3, ]; idx=3 is fourth (last) column
    if ax_cols is None:
        ax_cols = [0, 1, 2, 3]

    # get hard-coded bin values
    bin_edges, bin_centers, bin_width, num_bins = get_log10_bins()

    # initialize running values for counting out-of-bound values & total count
    # NOTE: each of the following has a count for each ax_col
    count_out_bounds, total_count = my_zeros(len(ax_cols)), my_zeros(len(ax_cols))

    # initialize running values for histogram(s)
    hist_counts = my_zeros((num_bins - 1, len(ax_cols)))

    # iterate over date-ranged, processed OTO count pickle files
    for pickle_file in pickle_files:

        with open(pickle_file, 'rb') as handle:
            my_dict = pkl.load(handle)

        fidx = my_dict['fidx']
        fat_array = my_dict['fat_array']
        # files = my_dict['files']
        # freqs = my_dict['freqs']
        # start = my_dict['start']
        # stop = my_dict['stop']
        # sensor = my_dict['sensor']

        if tag not in fidx.keys():
            print 'tag = %s not among keys in %s' % (tag, pickle_file)
            continue  # to next file since this one's missing tag

        v = fidx[tag]
        raw_data = fat_array[np.array(v)]

        # iterate over axes (columns)
        for c in ax_cols:

            # now working with log10(raw_data) in column c
            data, data_min, data_max = get_log10_data_and_exts(raw_data[:, :, c])

            # update counts (per-axis)
            non_nan_data = data[~np.isnan(data)]  # one way of suppressing annoying warnings
            count_out_bounds[c] += ((non_nan_data < bin_edges[0]) | (non_nan_data >= bin_edges[-1])).sum()
            hist_counts[:, c] += np.histogram(data, bin_edges)[0]  # idx=0 bc no need for 2nd return value
            total_count[c] += np.count_nonzero(~np.isnan(data))

            print "{:s}-axis (col={:d}) had {:,} good + {:,} outbounds = {:,} total".format(col_defs[c], c,
                                                                                            sum(hist_counts[:, c]),
                                                                                            count_out_bounds[c],
                                                                                            total_count[c])

    # FIXME this is where we output spreadsheet like product for Gateway
    # # display just for ax_col = 3 (all)
    # for k, left_edge in enumerate(bin_edges[:-1]):
    #     print hist_counts[k, 3], bin_edges[k], bin_edges[k + 1]

    return

    # TODO this is where we use matplotlib's separate boxplot stats vs. plot parts to do plotting based on cumsum pctile

    # csum = np.cumsum(hist_counts, dtype=float)

    fig, ax = plt.subplots()

    # Plot the histogram heights against integers on the x axis
    ax.bar(bin_edges[:-1], hist_counts, width=1)
    plt.xlim(min(bin_edges), max(bin_edges))

    # # Set the ticks to the center of the bins (bars)
    # ax.set_xticks(bin_edges)
    #
    # # Set the xticklabels to a string that tells us what the bin edges were
    # ax.set_xticklabels(['{} - {}'.format(bin_edges[i], bin_edges[i + 1]) for i, j in enumerate(hist_counts)])

    # Set the ticks to the center of the bins (bars)
    ax.set_xticks(bin_centers)

    # Set the xticklabels to bin_centers
    ax.set_xticklabels(['{:0g}'.format(i) for i in bin_centers])

    plt.show()


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


if __name__ == '__main__':

    # gf = FatArray()
    # for i in xrange(140*92*3):
    #     gf.update([i])
    #
    # print len(gf.data)
    # gf.finalize()
    # print len(gf.data)
    #
    # raise SystemExit

    # demo_pickle_save()
    # raise SystemExit

    pickle_files = ['/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-01_2016-01-02_121f03_sleep_all_wake_otorunhist.pkl',
                    '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-03_2016-01-04_121f03_sleep_all_wake_otorunhist.pkl']
    demo_running_log10_hist(pickle_files, 'sleep', ax_cols=None)
    raise SystemExit

    demo_rigged_full_month_fat_array()
    # demo_kde()
    # demo_rigged_elementwise_count_ignore_nans()
    # demo_eng_units()
    # demo_save_range_of_months()
    # demo_plotnsave_daterange_histpad()
