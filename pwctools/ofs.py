
MIN_PULSE_DUR = 50   # microseconds
MAX_PULSE_DUR = 100  # microseconds


class OssFuncSimNEW(object):

    def __init__(self, config_file=None):
        self._x_range = None
        self._y_range = None
        self._z_range = None
        self._y_capture_disabled = None
        self._z_capture_disabled = None
        self.update()

    def __str__(self):
        s = 'something about LabJack U3 version GOES HERE?'
        s += '\n x-axis range is %s' % self.x_range
        s += '\n y-axis range is %s' % self.y_range
        s += '\n z-axis range is %s' % self.z_range
        s += '\n y-axis capture disabled is %s' % str(self.y_capture_disabled)
        s += '\n z-axis capture disabled is %s' % str(self.z_capture_disabled)
        return s

    def update(self):
        # self.x_range = self.get_range('x')
        # self.y_capture_disabled = self.get_capture_disabled('y')

    @property
    def x_range(self):
        """x-axis range property"""
        return self._x_range

    @x_range.setter
    def x_range(self, value):
        self._x_range = value

    @property
    def y_range(self):
        """y-axis range property"""
        return self._y_range

    @y_range.setter
    def y_range(self, value):
        self._y_range = value

    @property
    def z_range(self):
        """z-axis range property"""
        return self._z_range

    @z_range.setter
    def z_range(self, value):
        self._z_range = value

    @property
    def z_capture_disabled(self):
        """z-axis capture disabled property"""
        return self._z_capture_disabled

    @z_capture_disabled.setter
    def z_capture_disabled(self, value):
        self._z_capture_disabled = value

    @property
    def y_capture_disabled(self):
        """y-axis capture disabled property"""
        return self._y_capture_disabled

    @y_capture_disabled.setter
    def y_capture_disabled(self, value):
        self._y_capture_disabled = value

    def get_digital_pin(self, p):
        pass


def main():
    ofs = OssFuncSimNEW()
    print(ofs)


if __name__ == '__main__':
    main()
