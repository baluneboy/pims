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

# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f03 -d 2016-01-01 -e 2016-01-31 -t sleep,0,4 wake,8,16
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f03 -d 2016-02-01 -e 2016-02-29 -t sleep,0,4 wake,8,16
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f03 -d 2016-03-01 -e 2016-03-31 -t sleep,0,4 wake,8,16
#
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f03 -d 2018-01-18 -e 2018-01-31 -t sleep,0,4 wake,8,16
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f03 -d 2018-02-01 -e 2018-02-28 -t sleep,0,4 wake,8,16
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f03 -d 2018-03-01 -e 2018-03-31 -t sleep,0,4 wake,8,16
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f03 -d 2018-04-01 -e 2018-04-17 -t sleep,0,4 wake,8,16
#
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f05 -d 2018-01-18 -e 2018-01-31 -t sleep,0,4 wake,8,16
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f05 -d 2018-02-01 -e 2018-02-28 -t sleep,0,4 wake,8,16
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f05 -d 2018-03-01 -e 2018-03-31 -t sleep,0,4 wake,8,16
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f05 -d 2018-04-01 -e 2018-04-17 -t sleep,0,4 wake,8,16
#
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f08 -d 2018-01-18 -e 2018-01-31 -t sleep,0,4 wake,8,16
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f08 -d 2018-02-01 -e 2018-02-28 -t sleep,0,4 wake,8,16
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f08 -d 2018-03-01 -e 2018-03-31 -t sleep,0,4 wake,8,16
# /home/pims/dev/programs/python/pims/otorunhist/main.py -s 121f08 -d 2018-04-01 -e 2018-04-17 -t sleep,0,4 wake,8,16
#
# '/misc/yoda/www/plots/batch/results/onethird/year2016/month01/2016-01-01_2016-01-31_121f03_sleep_all_wake_otorunhist.pkl'
# '/misc/yoda/www/plots/batch/results/onethird/year2016/month02/2016-02-01_2016-02-29_121f03_sleep_all_wake_otorunhist.pkl'
# '/misc/yoda/www/plots/batch/results/onethird/year2016/month03/2016-03-01_2016-03-31_121f03_sleep_all_wake_otorunhist.pkl'
# '
# '/misc/yoda/www/plots/batch/results/onethird/year2018/month01/2018-01-18_2018-01-31_121f03_sleep_all_wake_otorunhist.pkl'
# '/misc/yoda/www/plots/batch/results/onethird/year2018/month02/2018-02-01_2018-02-28_121f03_sleep_all_wake_otorunhist.pkl'
# '/misc/yoda/www/plots/batch/results/onethird/year2018/month03/2018-03-01_2018-03-31_121f03_sleep_all_wake_otorunhist.pkl'
# '/misc/yoda/www/plots/batch/results/onethird/year2018/month04/2018-04-01_2018-04-17_121f03_sleep_all_wake_otorunhist.pkl'
# '
# '/misc/yoda/www/plots/batch/results/onethird/year2018/month01/2018-01-18_2018-01-31_121f05_sleep_all_wake_otorunhist.pkl'
# '/misc/yoda/www/plots/batch/results/onethird/year2018/month02/2018-02-01_2018-02-28_121f05_sleep_all_wake_otorunhist.pkl'
# '/misc/yoda/www/plots/batch/results/onethird/year2018/month03/2018-03-01_2018-03-31_121f05_sleep_all_wake_otorunhist.pkl'
# '/misc/yoda/www/plots/batch/results/onethird/year2018/month04/2018-04-01_2018-04-17_121f05_sleep_all_wake_otorunhist.pkl'
# '
# '/misc/yoda/www/plots/batch/results/onethird/year2018/month01/2018-01-18_2018-01-31_121f08_sleep_all_wake_otorunhist.pkl'
# '/misc/yoda/www/plots/batch/results/onethird/year2018/month02/2018-02-01_2018-02-28_121f08_sleep_all_wake_otorunhist.pkl'
# '/misc/yoda/www/plots/batch/results/onethird/year2018/month03/2018-03-01_2018-03-31_121f08_sleep_all_wake_otorunhist.pkl'
# '/misc/yoda/www/plots/batch/results/onethird/year2018/month04/2018-04-01_2018-04-17_121f08_sleep_all_wake_otorunhist.pkl'


