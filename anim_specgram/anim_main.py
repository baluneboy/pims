"""
Matplotlib Animation Example

author: Jake Vanderplas
email: vanderplas@astro.washington.edu
website: http://jakevdp.github.com
license: BSD
Please feel free to use and modify this, but keep the above information. Thanks!
"""

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation


def setup_fig():
    """first set up the figure, the axis, and the plot element we want to animate"""
    fig = plt.figure()
    ax = plt.axes(xlim=(0, 2), ylim=(-2, 2))
    line, = ax.plot([], [], lw=2)
    return fig, ax, line


def animate(i, the_line):
    """animation function (this is called sequentially)"""
    x = np.linspace(0, 2, 1000)
    y = np.sin(2 * np.pi * (x - 0.01 * i))
    the_line.set_data(x, y)
    return the_line,


# setup figure
fig, ax, line = setup_fig()
# line.set_data([], [])  # FIXME not sure we need this?

# call the animator
anim = animation.FuncAnimation(fig, animate, fargs=(line, ), frames=200, interval=20, blit=False)

plt.show()
