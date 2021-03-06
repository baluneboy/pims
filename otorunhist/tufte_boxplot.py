#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt


def demo_iss_req_steps():

    m = np.array([
        [0.0088, 0.0098, 0.0110, 1.8000e-006],
        [0.0110, 0.0124, 0.0139, 1.8000e-006],
        [0.0139, 0.0156, 0.0175, 1.8000e-006],
        [0.0175, 0.0197, 0.0221, 1.8000e-006],
        [0.0221, 0.0248, 0.0278, 1.8000e-006],
        [0.0278, 0.0313, 0.0351, 1.8000e-006],
        [0.0351, 0.0394, 0.0442, 1.8000e-006],
        [0.0442, 0.0496, 0.0557, 1.8000e-006],
        [0.0557, 0.0625, 0.0702, 1.8000e-006],
        [0.0702, 0.0787, 0.0891, 1.8000e-006],
        [0.0891, 0.1000, 0.1122, 1.8000e-006],
        [0.1122, 0.1250, 0.1413, 2.2500e-006],
        [0.1413, 0.1600, 0.1778, 2.8800e-006],
        [0.1778, 0.2000, 0.2239, 3.6000e-006],
        [0.2239, 0.2500, 0.2818, 4.5000e-006],
        [0.2818, 0.3150, 0.3548, 5.6700e-006],
        [0.3548, 0.4000, 0.4467, 7.2000e-006],
        [0.4467, 0.5000, 0.5623, 9.0000e-006],
        [0.5623, 0.6300, 0.7079, 1.1340e-005],
        [0.7079, 0.8000, 0.8913, 1.4400e-005],
        [0.8913, 1.0000, 1.1220, 1.8000e-005],
        [1.1220, 1.2500, 1.4130, 2.2500e-005],
        [1.4130, 1.6000, 1.7780, 2.8800e-005],
        [1.7780, 2.0000, 2.2390, 3.6000e-005],
        [2.2390, 2.5000, 2.8180, 4.5000e-005],
        [2.8180, 3.1500, 3.5480, 5.6700e-005],
        [3.5480, 4.0000, 4.4670, 7.2000e-005],
        [4.4670, 5.0000, 5.6230, 9.0000e-005],
        [5.6230, 6.3000, 7.0790, 1.1340e-004],
        [7.0790, 8.0000, 8.9130, 1.4400e-004],
        [8.9130, 10.0000, 11.2200, 1.8000e-004],
        [11.2200, 12.5000, 14.1300, 2.2500e-004],
        [14.1300, 16.0000, 17.7800, 2.8800e-004],
        [17.7800, 20.0000, 22.3900, 3.6000e-004],
        [22.3900, 25.0000, 28.1800, 4.5000e-004],
        [28.1800, 31.5000, 35.4800, 5.6700e-004],
        [35.4800, 40.0000, 44.6700, 7.2000e-004],
        [44.6700, 50.0000, 56.2300, 9.0000e-004],
        [56.2300, 64.0000, 71.8380, 1.1520e-003],
        [71.8380, 80.6350, 90.5100, 1.4514e-003],
        [90.5100, 101.5900, 114.0400, 1.8000e-003],
        [114.0400, 128.0000, 143.6800, 1.8000e-003],
        [143.6800, 161.2700, 181.0200, 1.8000e-003],
        [181.0200, 203.1900, 228.0700, 1.8000e-003],
        [228.0700, 256.0000, 287.3500, 1.8000e-003],
        [287.3500, 322.5400, 362.0400, 1.8000e-003]])

    fig, ax = plt.subplots(figsize=(10, 7.5))

    # draw steps for ISS requirement in light, transparent blue
    plt.step(m[:, 0], m[:, 3], where='post', label='post',
             alpha=0.3, color='blue')

    # draw horizontal lines at median grms values in red
    plt.hlines(y=[3.500e-006, 2.5000e-006], xmin=[m[12, 0], m[13, 0]], xmax=[m[12, 2], m[13, 2]], linewidth=2.5,
               alpha=0.85, color='red')

    # draw lower, vertical (whisker) lines from 1st to 25th percentiles in black
    plt.vlines(x=[m[12, 1], m[13, 1]], ymin=[1e-6, 1.5e-6], ymax=[2.0e-6, 2.1e-6], linewidth=1.5,
               alpha=0.5, color='black')

    # draw upper, vertical (whisker) lines from 75th to 99th percentiles in black
    plt.vlines(x=[m[12, 1], m[13, 1]], ymin=[3.9e-6, 3e-6], ymax=[5.7e-6, 6.5e-6], linewidth=1.5,
               alpha=0.5, color='black')

    plt.xscale('log')
    plt.yscale('log')

    # this is an inset axes over the main axes to use as a legend
    ax_leg = plt.axes([0.2, 0.6, 0.2, 0.2], facecolor='white')
    plt.plot([], [])
    plt.title('Legend')

    plt.vlines(x=[10.0], ymin=[75.0], ymax=[99.0], linewidth=1.5, alpha=0.75, color='black')
    plt.hlines(y=[50.0], xmin=[ 5.0], xmax=[15.0], linewidth=2.5, alpha=0.85, color='red')
    plt.vlines(x=[10.0], ymin=[ 1.0], ymax=[25.0], linewidth=1.5, alpha=0.75, color='black')

    plt.hlines(y=[1, 25, 50, 75, 99], xmin=[10, 10, 16, 10, 10], xmax=[30, 30, 30, 30, 30], linewidth=1, color='gray', linestyle=':')

    plt.text(31, 99, '99th percentile', verticalalignment='center')
    plt.text(31, 75, '75th percentile', verticalalignment='center')
    plt.text(31, 50, 'median', verticalalignment='center')
    plt.text(31, 25, '25th percentile', verticalalignment='center')
    plt.text(31,  1, '1st percentile', verticalalignment='center')

    plt.xlim(-10, 110)
    plt.ylim(-10, 110)

    plt.xticks([])
    plt.yticks([])

    plt.show()

    # fig.savefig(out_file, pad_inches=(1.0, 1.0))  # 1-inch pad since figsize was chopped 1-inch all-around


if __name__ == '__main__':

    demo_iss_req_steps()
