#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt

# import numpy as np
# import matplotlib.pyplot as plt
#
# prop_cycle = plt.rcParams['axes.prop_cycle']
# colors = prop_cycle.by_key()['color']
#
# lwbase = plt.rcParams['lines.linewidth']
# thin = lwbase / 2
# thick = lwbase * 3
#
# fig, axs = plt.subplots(nrows=2, ncols=2, sharex=True, sharey=True)
# for icol in range(2):
#     if icol == 0:
#         lwx, lwy = thin, lwbase
#     else:
#         lwx, lwy = lwbase, thick
#     for irow in range(2):
#         for i, color in enumerate(colors):
#             axs[irow, icol].axhline(i, color=color, lw=lwx)
#             axs[irow, icol].axvline(i, color=color, lw=lwy)
#
#     axs[1, icol].set_facecolor('k')
#     axs[1, icol].xaxis.set_ticks(np.arange(0, 10, 2))
#     axs[0, icol].set_title('line widths (pts): %g, %g' % (lwx, lwy),
#                            fontsize='medium')
#
# for irow in range(2):
#     axs[irow, 0].yaxis.set_ticks(np.arange(0, 10, 2))
#
# fig.suptitle('Colors in the default prop_cycle', fontsize='large')
#
# plt.show()


def demo_step_plot():

    x = np.arange(1, 7, 0.4)
    y0 = np.sin(x)
    y = y0.copy() + 2.5

    # fig, axs = plt.subplots()

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

    plt.axhline(2.0, 3.0, 4.0, color='firebrick')

    plt.show()


def demo2():
    t = np.arange(-1, 2, .01)
    s = np.sin(2 * np.pi * t)

    plt.plot(t, s, alpha=0.5, color='blue')

    # Draw horizontal lines at y=0.5 that spans the middle half of the axes
    plt.hlines(y=[1e-12, 1e-9], xmin=[0.25, 1e-2], xmax=[0.75, 1e0], linewidth=2.0, alpha=0.95, color='red')

    # plt.axis([-1, 2, -1, 2])

    plt.xscale('log')
    plt.yscale('log')

    plt.show()


if __name__ == '__main__':

    demo2()
    raise SystemExit

    demo_step_plot()
