from collections import deque

NUMPTS_AVG = 5  # MAMS sample rate is 10 Hz (T = 100 ms) & want OFS sampling every 50 ms (20 Hz)
DEBUG = not __debug__  # command line option -O (capital O) turns debugging ON [I know, an enigmatic built-in keyword]


class TripleMeanDeque(deque):

    """a deque that can give sum and mean values BUT always initialized as empty"""

    def __init__(self, maxlen=NUMPTS_AVG):
        super().__init__(maxlen=maxlen)

    def append(self, new_triple):
        if not len(new_triple) == 3:
            raise ValueError('got unexpected length (need 3 for triple, not %d)' % len(new_triple))
        if not isinstance(new_triple, tuple):
            raise TypeError('need to append 3-element tuple, but got non-tuple instead')
        super().append(new_triple)

    def sum(self):
        xsum = ysum = zsum = 0.0
        for x, y, z in self:
            xsum += x
            ysum += y
            zsum += z
        return xsum, ysum, zsum

    def mean(self):
        n = len(self)
        xsum, ysum, zsum = self.sum()
        return xsum/n, ysum/n, zsum/n


def demo_buffer():
    a = TripleMeanDeque(maxlen=NUMPTS_AVG)
    if DEBUG:
        UPPER = 11
    else:
        UPPER = 3
    for i in range(UPPER):
        a.append((i, i + 1, i + 2))
        print(a)
        print(a.mean())


if __name__ == '__main__':
    demo_buffer()
