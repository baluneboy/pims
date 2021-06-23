from numba import njit
import numpy as np
import time


x = np.arange(1000000).reshape(1000, 1000)


@njit
def go_fast(a):  # Function is compiled to machine code when called the first time
    trace = 0.0
    for i in range(a.shape[0]):    # Numba likes loops
        trace += np.tanh(a[i, i])  # Numba likes NumPy functions
    return a + trace               # Numba likes NumPy broadcasting


# DO NOT REPORT THIS... COMPILATION TIME IS INCLUDED IN THE EXECUTION TIME!
start = time.time()
go_fast(x)  # very first call to this fast function yields compilation (slower than all subsequent calls)
end = time.time()
print("Elapsed (with compilation) = %e" % (end - start))

# NOW THE FUNCTION IS COMPILED, RE-TIME IT EXECUTING FROM CACHE
start = time.time()
go_fast(x)
end = time.time()
print("Elapsed (after compilation) = %e" % (end - start))
