import numpy as np
import scipy.io

def round_up_ten(x):
    return int(np.ceil(x/10.0)) * 10

def get_sample_data():
    # read noisy data
    mat = scipy.io.loadmat('/home/pims/dev/programs/python/pims/sandbox/data/noisy.mat')
    noisy = mat['y'][0]
    
    # assign bins
    #bins = np.array([0.0, 25.0, 31.0, 34.0, 38.0, 41.0, 44.0, round_up_ten(np.max(noisy))])
    #bins = np.array([25.0, 30.0, 35.0, 40.0, 45.0, 200.0])
    bins = np.array([30.0, 40.0, 50.0, 200.0])
    
    # now digitize
    digitized = np.digitize(noisy, bins, right=True)
    return noisy, bins, digitized

def digitize_demo():
    # read and digitize noisy demo data
    noisy, bins, digitized = get_sample_data()
    #bin_means = [noisy[digitized == i].mean() for i in range(1, len(bins))]
    #for n in range(noisy.size):
    #    #     ---- bin below ----        --noisy--       --- bin above ---
    #    print bins[digitized[n]-1], "<=", noisy[n], "<", bins[digitized[n]]
    return noisy, bins, digitized, [bins[digitized[n]] for n in range(noisy.size)]
        
def crude_demo2():
    # get digitized bin means
    data = np.random.random(100)
    bins = np.linspace(0, 1, 10)
    digitized = np.digitize(data, bins)
    bin_means = [data[digitized == i].mean() for i in range(1, len(bins))]
    print bin_means
    
def crude_demo3():
    # An alternative to this is to use np.histogram():
    bin_means = (np.histogram(data, bins, weights=data)[0] / np.histogram(data, bins)[0])
    
    x = np.array([0.2, 6.4, 3.0, 1.6])
    print "noisy data", x
    bins = np.array([0.0, 1.0, 2.5, 4.0, 10.0])
    digitized = np.digitize(x, bins)
    print digitized
    
    for n in range(x.size):
        print(bins[digitized[n]-1], "<=", x[n], "<", bins[digitized[n]])
    # 0.0 <= 0.2 < 1.0
    # 4.0 <= 6.4 < 10.0
    # 2.5 <= 3.0 < 4.0
    # 1.0 <= 1.6 < 2.5
    
    x = np.array([1.2, 10.0, 12.4, 15.5, 20.])
    bins = np.array([0, 5, 10, 15, 20])
    print np.digitize(x,bins,right=True)
    # array([1, 2, 3, 4, 4])
    print np.digitize(x,bins,right=False)
    # array([1, 3, 3, 4, 5])
    
if __name__ == "__main__":
    #import doctest
    #doctest.testmod(verbose=True)
    noisy, bins, inds, digitized = digitize_demo()
    print noisy
    print digitized
    