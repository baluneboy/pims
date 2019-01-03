pickle_file = '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-01_2016-01-07_121f03_sleep_all_wake_otorunhist.pkl'

with open(pickle_file, 'rb') as handle:
    my_dict = pkl.load(handle)  # keys: ['files', 'fidx', 'freqs', 'stop', 'taghours', 'start', 'sensor', 'fat_array']

"""
Variable            Type        Data/Info
-----------------------------------------
pickle_file         str         /misc/yoda/www/plots/batc<...>p_all_wake_otorunhist.pkl
my_dict             dict        n=8

                                  TxFxA   Time-by-Freq-by-Ax       
fat_array           ndarray     972x46x4: 178848 elems, type `float64`, 1430784 bytes (1 Mb)
fidx                dict        n=3 << sleep, wake and all
taghours            dict        n=3 << sleep, wake and all
files               list        n=972
freqs               ndarray     46x1: 46 elems, type `float64`, 368 bytes
sensor              str         121f03
start               date        2016-01-01
stop                date        2016-01-07

"""


