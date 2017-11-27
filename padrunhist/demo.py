#!/usr/bin/env python

import os.path
import numpy as np
import matplotlib.pyplot as plt

from ugaudio.load import padread
from ugaudio.pad import PadFile

from pims.files.filter_pipeline import FileFilterPipeline


    
if __name__ == "__main__":
    
    ## get sample rate from header file
    #header_file = '/misc/yoda/pub/pad/year2017/month04/day01/sams2_accel_121f04/2017_04_01_20_55_05.415+2017_04_01_21_05_05.426.121f04.header'
    #data_file = header_file.replace('.header', '')
    #show_samplerate(data_file)
    
    ## generate artficial chirp, then create sound file (AIFF format) and plot it (PNG format)
    #demo_chirp()
    
    # plot SAMS TSH (es06) data file (just one axis)
    data_file = '/tmp/2017_05_22_23_39_02.803+2017_05_22_23_49_02.861.es06'
    #show_samplerate(data_file)
    demo_accel_file(data_file, axis='x') # just x-axis here