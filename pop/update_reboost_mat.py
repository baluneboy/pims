#!/usr/bin/evn python

import numpy as np
import scipy.io

mat_file = '/misc/yoda/www/plots/user/handbook/source_docs/reboost_tig_dur.mat'

my_arr = np.zeros((1,3), dtype=np.object)
my_arr[0, 0] = 'Progress_Reboost_69P_2018-06-23'
my_arr[0, 1] = '23-Jun-2018 08:15:00'
my_arr[0, 2] = '0h3m28s'

scipy.io.savemat('/tmp/trash.mat', mdict={'new_reboost': my_arr})