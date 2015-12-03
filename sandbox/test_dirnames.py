#!/usr/bin/env python

import os
import datetime

def test_name(d):
    #hb_path = d.rstrip('/build/unjoined')
    hb_path = os.path.sep.join( d.split(os.path.sep)[:-2] )
    junk, hb_name = os.path.split(hb_path)
    hb_pdf = os.path.join(hb_path, hb_name + '.pdf')
    print d
    print hb_path
    print hb_name
    print hb_pdf
    print '-----------------'

if __name__ == '__main__':
    dirs = [
        '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_SARJ_Corr/build/unjoined',
        '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_SARJ_Correl/build/unjoined',
        '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_SARJ_Correla/build/unjoined',
        '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_SARJ_Correlat/build/unjoined',
        '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_SARJ_Correlation/build/unjoined',        
    ]
    for d in dirs:
        test_name(d)