import numpy as np
from dataclasses import dataclass


@dataclass
class MinMax:
    """a class to keep track of min/max values in column-wise fashion"""
    mins: np.ndarray
    maxs: np.ndarray

    def update(self, other_array):
        """update mins and maxs based on comparison with input, other_array"""
        other_mins = np.min(other_array, axis=0)
        other_maxs = np.max(other_array, axis=0)
        self.update_mins(other_mins)
        self.update_maxs(other_maxs)

    def update_mins(self, other_mins):
        """update min values based on these new, other min values"""
        self.mins = self._get_updated_values(other_mins, np.min)

    def update_maxs(self, other_maxs):
        """update max values based on these new, other max values"""
        self.maxs = self._get_updated_values(other_maxs, np.max)

    def _get_updated_values(self, other_values, func) -> np.ndarray:
        """return new values for min (or max) values by comparing to input, other values"""
        if func == np.min:
            values = self.mins
        elif func == np.max:
            values = self.maxs
        else:
            raise ValueError('function for comparison must be np.min or np.max')
        return func(np.vstack((values, other_values)), axis=0)

    def save(self, npz_file):
        """save mins & maxs to npz file"""
        with open(npz_file, 'wb') as f:
            np.savez(f, mins=self.mins, maxs=self.maxs)


def demo_minmax():
    """demo of MinMax dataclass"""
    # get starting values for mins and maxs
    resume = False
    start_mins = np.array([np.inf, np.inf, np.inf, np.inf])
    start_maxs = np.array([-np.inf, -np.inf, -np.inf, -np.inf])
    if resume:
        # load data to resume based on previous (day(s)?) values FIXME dummy data
        start_mins = np.array([1, 2, 3, 4])
        start_maxs = np.array([11, 22, 33, 44])

    mm = MinMax(mins=start_mins, maxs=start_maxs)
    print(f'{mm = }')

    mm.update(np.array([[1, 2, 3, 4], [111, 222, 333, 444]]))
    print(f'{mm = }')

    mm.update(np.array([[0.051, 23, 0.03, 444], [1, 222, 300, 4]]))
    print(f'{mm = }')

    mm.update(np.array([[0.1, 222, 0.03, 444], [111.8, 222, 300, 4444]]))
    print(f'{mm = }')

    mm.save('/tmp/trash.npz')


if __name__ == '__main__':
    demo_minmax()
