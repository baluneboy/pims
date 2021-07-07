class UpdateQuad(object):

    def __init__(self, ax, map_object, lons, lats):
        self.ax = ax
        self.m = map_object
        self.lons = lons
        self.lats = lats
        vmin = 0
        vmax = 1
        self.ydim, self.xdim = lons.shape
        self.z = np.zeros((self.ydim - 1, self.xdim - 1))
        levels = MaxNLocator(nbins=15).tick_values(vmin, vmax)
        cmap = plt.cm.viridis
        norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
        x, y = self.m(lons, lats)
        self.quad = self.ax.pcolormesh(x, y, self.z, alpha=0.9, norm=norm, cmap=cmap, vmin=vmin, vmax=vmax)

    def init(self):
        # print('update/init')
        self.quad.set_array(np.asarray([]))
        return self.quad

    def __call__(self, i):
        for i in range(self.ydim - 1):
            for j in range(self.xdim - 1):
                self.z[i, j] = random.random()
        self.quad.set_array(self.z.ravel())
        return self.quad


def plot_pcolor(lons, lats):

    class OldUpdateQuad(object):

        def __init__(self, ax, map_object, lons, lats):
            self.ax = ax
            self.m  = map_object
            self.lons = lons
            self.lats = lats
            vmin = 0
            vmax = 1
            self.ydim, self.xdim = lons.shape
            self.z = np.zeros((self.ydim-1, self.xdim-1))
            levels = MaxNLocator(nbins=15).tick_values(vmin,vmax)
            cmap = plt.cm.viridis
            norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
            x, y = self.m(lons, lats)
            self.quad = self.ax.pcolormesh(x, y, self.z, alpha=0.9, norm=norm, cmap=cmap, vmin=vmin, vmax=vmax)

        def init(self):
            print('update init')
            self.quad.set_array(np.asarray([]))
            return self.quad

        def __call__(self, i):
            for i in range(self.ydim-1):
                for j in range(self.xdim-1):
                    self.z[i, j] = random.random()
            self.quad.set_array(self.z.ravel())
            return self.quad


    fig, ax = plt.subplots()

    m = Basemap(width=2000000, height=2000000, resolution='l', projection='laea',
                lat_ts=10.0, lat_0=64.0, lon_0=10.0, ax=ax)

    m.fillcontinents()

    ud = UpdateQuad(ax, m, lons, lats)

    anim = animation.FuncAnimation(fig, ud, init_func=ud.init, frames=20,  blit=False)

    fig.tight_layout()

    plt.show()

    return ud.quad


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from mpl_toolkits.basemap import Basemap
    import numpy as np
    import random
    from matplotlib.colors import BoundaryNorm
    from matplotlib.ticker import MaxNLocator

    lons = np.linspace(-5.,25., num = 25)[:50]
    lats = np.linspace(56., 71., num = 25)[:50]
    lons, lats =  np.meshgrid(lons, lats)

    quad = plot_pcolor(lons, lats)
