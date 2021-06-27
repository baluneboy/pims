import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

SCALES = {
    'micro': (1.0e06, r'$\mu$'),
    'milli': (1.0e03, r'm'),
    '': (1.0, r'')
}


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


def get_fmt(axis):
    """return string for format of dateaxis that we query from axis object"""
    axis.axes.figure.canvas.draw()
    formatter = axis.get_major_formatter()
    locator_unit_scale = float(formatter._locator._get_unit())
    fmt = next((fmt for scale, fmt in sorted(formatter.scaled.items())
                if scale >= locator_unit_scale),
               formatter.defaultfmt)
    return fmt.replace('%', '')


class Plot3x1(object):

    def __init__(self, arr, labels):
        """initialize plot using 4-column (txyz) array, arr, and labels for x-axis, y-axis and title"""
        self.arr = arr
        self.labels = labels
        self.dpi = 120
        self.fig = None
        self.axs = None
        self.upper_text = {'left': [], 'center': [], 'right': []}

    @staticmethod
    def _init_subplots():
        """return figure and axes objects after creating 3-panel subplots"""
        fig, axs = plt.subplots(3, sharex='all', sharey='all')
        fig.subplots_adjust(hspace=0.06)  # bring subplots closer to each other (fraction of avg ax height is hspace)
        fig.set_size_inches(8.5, 11)
        return fig, axs

    def plot(self):
        """plot each of x-, y-, and z-axis data"""
        self.fig, self.axs = self._init_subplots()
        for i in range(3):
            self.axs[i].plot(self.arr[:, 0], self.arr[:, i + 1], color='black', marker=None, linestyle='solid')

    def set_labels(self):
        """set labels for xlabel, ylabel and title"""
        if self.axs is not None:
            for i in range(3):
                if self.labels['y'][i] is not None:
                    self.axs[i].set_ylabel('{:s} ({:s})'.format(*self.labels['y'][i]))
                if self.labels['x'][i] is not None:
                    self.axs[i].set_xlabel('{:s} ({:s})'.format(*self.labels['x'][i]))
                if self.labels['title'][i] is not None:
                    self.axs[i].set_title(self.labels['title'][i])

    def set_upper_text(self, horiz_align, text_list):
        """create upper ancillary text objects"""
        xycoords = ('axes fraction', 'axes fraction')
        xpos = {'left': -0.08, 'center': 0.5, 'right': 1.05}
        xval = xpos[horiz_align]
        yval, ydelta = 1.35, 0.05
        handles = []
        for txt in text_list:
            handles.append(self.axs[0].annotate(txt, xy=(xval, yval), xycoords=xycoords, ha=horiz_align, fontsize=8))
            yval -= ydelta
        self.upper_text[horiz_align] = handles

    def save_fig(self, pdf_file):
        """save figure to pdf file"""
        self.fig.savefig(pdf_file, dpi=self.dpi)


class SamsPlot3x1(Plot3x1):

    def __init__(self, arr, labels, scale='micro', invert=True, demean=True):
        """initialize plot using 4-column (txyz) array, arr, and labels for x-axis, y-axis and title plus pre-process"""
        super().__init__(arr, labels)
        self.scale = scale
        self.invert = invert
        self.demean = demean
        self.means = np.array([None, None, None])
        arr = self._preprocess(arr)

    def _preprocess(self, arr):
        """return pre-processed array, possibly inverted and/or demeaned and/or scaled"""
        if self.invert:
            arr[:, 1:4] = -arr[:, 1:4]
        if self.demean:
            self.means = arr[:, 1:4].mean(axis=0)
            arr[:, 1:4] = arr[:, 1:4] - self.means
        scale_factor = SCALES[self.scale][0]
        if scale_factor != 1:
            arr[:, 1:4] = scale_factor * arr[:, 1:4]
        return arr


class SamsGvtPlot3x1(SamsPlot3x1):

    def __init__(self, arr, header, scale='micro', invert=True, demean=True):
        """initialize plot using 4-column (txyz) array, arr, and labels for x-axis, y-axis and title plus pre-process"""
        self.header = header
        labels = self._get_labels(scale)
        super().__init__(arr, labels, scale=scale, invert=invert, demean=demean)

    def on_press(self, event):
        """callback handler for keypress event"""
        sys.stdout.flush()
        if event.key == 't':
            print('pressed t for Time Toggle', event.key)
            fmt_str = get_fmt(plt.gca().xaxis)
            self.axs[2].set_xlabel('{:s} ({:s})'.format('Time', fmt_str))
            self.fig.canvas.draw()

    def on_xlim_change(self, event_ax):
        """callback handler for x-axis limits changed event"""
        print("updated xlims: ", event_ax.get_xlim())
        fmt_str = get_fmt(plt.gca().xaxis)
        self.axs[2].set_xlabel('{:s} ({:s})'.format('Time', fmt_str))
        self.fig.canvas.draw()

    def on_ylim_change(self, event_ax):
        """callback handler for y-axis limits changed event"""
        print("updated ylims: ", event_ax.get_ylim())

    def plot(self):
        """plot each of x-, y-, and z-axis data"""
        self.fig, self.axs = self._init_subplots()
        dtm = self._get_datetime_array()
        for i in range(3):
            self.axs[i].plot_date(dtm, self.arr[:, i + 1], color='black', marker=None, linestyle='solid')
            # cid = self.fig.canvas.mpl_connect('key_press_event', self.on_press)
            self.axs[i].callbacks.connect('xlim_changed', self.on_xlim_change)
            self.axs[i].callbacks.connect('ylim_changed', self.on_ylim_change)

    def _get_datetime_array(self):
        """return array of absolute datetimes using tzero (GMT) and relative offset (sec) from arr's first column"""
        # delta in milliseconds (which is the L in freq string)
        delta = 1000.0 / self.header['fs']
        freq = '%.3fL' % delta
        dtm = pd.date_range(self.header['tzero'], freq=freq, periods=self.arr.shape[0]).to_pydatetime()
        return dtm

    def _get_labels(self, scale):
        """return dict for x- and y-labels strings and title text"""
        q = 'Acceleration'
        u = SCALES[scale][1] + 'g'
        top_title = self.header['tzero'].strftime('Start GMT %Y-%m-%d, %j/%H:%M:%S.%f')[:-3]
        #                   Top Subplot              Mid Subplot            Bottom Subplot
        labels = {'x': [None, None, ('Time', 'sec')],
                  'y': [('X-Axis %s' % q, u), ('Y-Axis %s' % q, u), ('Z-Axis %s' % q, u)],
                  'title': [top_title, None, None]}
        return labels

    def _get_upper_text_lists(self):
        """return dict for upper left, center, and right ancillary text at top of figure"""
        hdr = self.header
        strUL1 = '{:s}, {:s} at {:s}, {:s}'.format(hdr['system'], hdr['sensor'], hdr['location'],
                                                   str(hdr['xyz_coords']))
        strUL2 = '{:.3f} sa/sec ({:.3f} Hz)'.format(hdr['fs'], hdr['fc'])
        text_upper_left = [strUL1, strUL2]
        strUR1 = '{:s}, {:s}'.format(hdr['coord_sys'], str(hdr['rpy_orient']))
        text_upper_right = [strUR1, ]
        strUC3 = 'Sensor {:s} at {:s}'.format(hdr['sensor'], hdr['location'])
        text_upper_center = [None, None, None, strUC3]
        return text_upper_left, text_upper_center, text_upper_right

    def set_ancillary_text(self):
        """return handles after setting ancillary upper text objects"""
        txtUL, txtUC, txtUR = self._get_upper_text_lists()
        self.set_upper_text('left', txtUL)
        self.set_upper_text('center', txtUC)
        self.set_upper_text('right', txtUR)
        self.upper_text['center'][3].set_fontsize(11)


def get_example_sams_data():
    """return 2 numpy arrays for example x, y data"""
    import ugaudio.load as load
    from pims.pad.read_header import get_sams_simple_header

    pad_file = 'G:/data/pad/year2020/month04/day05/sams2_accel_121f03/2020_04_05_00_05_15.785+2020_04_05_00_15_15.803.121f03'
    hdr_file = pad_file + '.header'

    hdr = get_sams_simple_header(hdr_file)
    for k, v in hdr.items():
        print(k, v)

    arr = load.pad_read(pad_file)
    return arr, hdr


def get_example_sams_labels(hdr):
    """return dict for x- and y-labels strings given simple sams pad header info"""
    top_title = hdr['tzero'].strftime('Start GMT %Y-%m-%d, %j/%H:%M:%S.%f')[:-3]
    #                       Top Subplot              Mid Subplot            Bottom Subplot
    example_labels = {'x': [None, None, ('Time', 'sec')],
                      'y': [('X-Axis Quantity', 'units'), ('Y-Axis Quantity', 'units'), ('Z-Axis Quantity', 'units')],
                      'title': [top_title, None, None]}
    return example_labels


def main():
    # load example data and labels
    a, hdr = get_example_sams_data()

    # create plot object
    gvt3 = SamsGvtPlot3x1(a, hdr, scale='milli', invert=True, demean=True)

    # plot data
    gvt3.plot()

    # set xlabels, ylabels and title
    gvt3.set_labels()

    # set ancillary (upper) text
    gvt3.set_ancillary_text()

    # save svg
    gvt3.save_fig('c:/temp/sample.svg')
    gvt3.save_fig('c:/temp/sample.pdf')

    return gvt3


if __name__ == '__main__':
    p3 = main()
    # print(p3.means)
    # print(p3.tzero)
    # move_figure(p3.fig, 10, 1)
    # plt.show()
