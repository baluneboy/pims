
import numpy as np
import matplotlib.pyplot as plt


def move_figure(f, x, y):
    """move figure's upper left corner to pixel (x, y)"""
    import matplotlib
    backend = matplotlib.get_backend()
    if backend == 'TkAgg':
        f.canvas.manager.window.wm_geometry("+%d+%d" % (x, y))
    elif backend == 'WXAgg':
        f.canvas.manager.window.SetPosition((x, y))
    else:
        # This works for QT and GTK
        # You can also use window.setGeometry
        f.canvas.manager.window.move(x, y)


class Plot3x1(object):

    def __init__(self, arr, labels):
        self.arr = arr
        self.labels = labels
        self.dpi = 100
        self.fig, self.axs = self._init_subplots()
        self._plot_data()
        self.set_labels()
        self.anns = {'left': [], 'center': [], 'right': []}

    @staticmethod
    def _init_subplots():
        fig, axs = plt.subplots(3, sharex='all')
        fig.subplots_adjust(hspace=0.06)  # bring subplots closer to each other (fraction of avg ax height is hspace)
        fig.set_size_inches(8.5, 11)
        return fig, axs

    def _plot_data(self):
        for i in range(3):
            self.axs[i].plot(self.arr[:, 0], self.arr[:, i+1], color='k')

    def set_labels(self):
        for i in range(3):
            if not self.labels['y'][i] is None:
                self.axs[i].set_ylabel('{:s} ({:s})'.format(*self.labels['y'][i]))
            if not self.labels['x'][i] is None:
                self.axs[i].set_xlabel('{:s} ({:s})'.format(*self.labels['x'][i]))
            if not self.labels['title'][i] is None:
                self.axs[i].set_title(self.labels['title'][i])

    def set_annotations(self, horiz_align, anns_list):
        xycoords = ('axes fraction', 'axes fraction')
        xpos = {'left': -0.08, 'center': 0.5, 'right': 1.05}
        xval = xpos[horiz_align]
        yval, ydelta = 1.35, 0.05
        handles = []
        for ann in anns_list:
            handles.append(self.axs[0].annotate(ann, xy=(xval, yval), xycoords=xycoords, ha=horiz_align))
            yval -= ydelta
        self.anns[horiz_align] = handles

    def save_fig(self, pdf_file, dpi=100):
        self.fig.savefig(pdf_file, dpi=dpi)


class SamsPlot3x1(Plot3x1):

    def __init__(self, arr, labels, invert=True, demean=True):
        self.invert = invert
        self.demean = demean
        self.means = np.array([None, None, None])
        arr = self._preprocess(arr)
        super().__init__(arr, labels)

    def _preprocess(self, arr):
        """return pre-processed array"""
        if self.invert:
            arr[:, 1:4] = -arr[:, 1:4]
        if self.demean:
            self.means = arr[:, 1:4].mean(axis=0)
            arr[:, 1:4] = arr[:, 1:4] - self.means
        return arr


def get_example_sams_data():
    """return 2 numpy arrays for example x, y data"""
    import ugaudio.load as load
    pad_file = 'G:/data/pad/year2020/month04/day05/sams2_accel_121f03/2020_04_05_00_05_15.785+2020_04_05_00_15_15.803.121f03'
    arr = load.pad_read(pad_file)
    return arr


def get_example_sams_labels():
    """return dict for x- and y-labels strings"""
    #                       Top Subplot              Mid Subplot            Bottom Subplot
    example_labels = {'x': [None,                    None,                ('Time', 'sec')],
                      'y': [('X-Axis Quantity', 'units'), ('Y-Axis Quantity', 'units'), ('Z-Axis Quantity', 'units')],
                      'title': ['Top Title',         None,                  None]}
    return example_labels


def main():
    # load example data and labels
    a = get_example_sams_data()
    my_labels = get_example_sams_labels()

    # plot example
    p3x1 = SamsPlot3x1(a, my_labels, invert=True, demean=True)

    # set annotations
    p3x1.set_annotations('left', ['Upper Left One', 'Upper Left Two', 'Upper Left Three', 'Upper Left Four', 'Five'])
    p3x1.set_annotations('right', ['one', 'two', 'three'])
    p3x1.set_annotations('center', ['one', 'two', 'three', 'four'])

    # save pdf
    # p3x1.save_fig('c:/temp/sample.pdf')

    return p3x1


if __name__ == '__main__':
    p3 = main()
    print(p3.means)
    move_figure(p3.fig, 10, 1)
    plt.show()
