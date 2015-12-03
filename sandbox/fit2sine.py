import numpy as np
from scipy.optimize import leastsq
import pylab as plt

N = 1000 # number of data points
t = np.linspace(0, 4*np.pi, N)
data = 3.0*np.sin(t+0.001) + 0.5 + np.random.randn(N) # create artificial data with noise

#handpick_pts = np.array( [
#    [ 736207.172781911795,2.783498478185 ],
#    [ 736207.166319617536,2.671673469657 ],
#    [ 736207.156303061405,2.551246537396 ],
#    [ 736207.149194537662,2.597123463972 ],
#    [ 736207.142086013919,2.694611932945 ],
#    [ 736207.137283479795,2.781990669714 ],
#    [ 736207.133172282251,2.862166531266 ],
#    [ 736207.125607163412,2.929731181644 ],
#    [ 736207.117795335827,2.912319701536 ],
#    [ 736207.112233344116,2.833656592089 ],
#    [ 736207.107330469531,2.754761131829 ],
#    [ 736207.103219271987,2.676098022381 ],
#    [ 736207.092060307390,2.574743631363 ],
#    [ 736207.083250598516,2.606511425563 ],
#    [ 736207.077083802200,2.715429577105 ],
#    [ 736207.071210662951,2.828885984961 ],
#    [ 736207.065631180652,2.906036342304 ],
#    [ 736207.057996099582,2.936291384399 ],
#    [ 736207.050321434624,2.869517715514 ],
#    [ 736207.041920452029,2.743356167431 ]
#    ] )
#
#N = 20
#t = handpick_pts[:, 0]
#data = handpick_pts[:, 1]

guess_mean = np.mean(data)
guess_std = 3*np.std(data)/(2**0.5)
guess_phase = 0

# we'll use this to plot our first estimate. This might already be good enough for you
data_first_guess = guess_std*np.sin(t+guess_phase) + guess_mean

# Define the function to optimize, in this case, we want to minimize the difference
# between the actual data and our "guessed" parameters
optimize_func = lambda x: x[0]*np.sin(t+x[1]) + x[2] - data
est_std, est_phase, est_mean = leastsq(optimize_func, [guess_std, guess_phase, guess_mean])[0]

# recreate the fitted curve using the optimized parameters
data_fit = est_std*np.sin(t+est_phase) + est_mean

plt.plot(data, '.')
plt.plot(data_fit, label='after fitting')
plt.plot(data_first_guess, label='first guess')
plt.legend()
plt.show()