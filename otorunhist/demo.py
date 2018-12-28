#!/usr/bin/env python

import datetime
import decimal
import numpy as np
# from main import plotnsave_daterange_histpad, plotnsave_monthrange_histpad, save_range_of_months
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt


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

    # demo_stack()
    # raise SystemExit

    demo_rigged_full_month_fat_array()
    # demo_kde()
    # demo_rigged_elementwise_count_ignore_nans()
    # demo_eng_units()
    # demo_save_range_of_months()
    # demo_plotnsave_daterange_histpad()
