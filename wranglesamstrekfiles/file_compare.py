#!/usr/bin/env python

import os
from itertools import combinations
from md5 import md5

files = [
    '/media/trek21/Database/SAMS_GSE_Format3.mdb',
    '/media/trek21/Trek/telemetry_database/SAMS_6A_TLM.mdb',
    '/media/trek21/Database/SAMS_GSE_13A-calibrated.mdb',
    '/media/trek21/Database/SAMS-GSE-CU-DB.mdb',
    '/media/trek21/Trek/command_database/SAMS_Commands.mdb',
    '/media/trek21/Trek/telemetry_database/sams-accel-db.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/database/SAMS_GSE_ULF4.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/command_database/SAMS_Commands.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/database/SAMS_GSE_PEHB_PORTS.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/database/SAMS_GSE_PEHB_PORTS-OLD.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/database/SAMS_GSE_13A.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/database/SAMS_GSE_13A-calibrated.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/command_database/SAMS-1E-CMDS.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/database/SAMS-GSE-13A1.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/database/SAMS_GSE_12A1.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/command_database/SAMS-12A1-CMDS.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/database/SAMS_ULF1_I7.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/database/SAMS_6A_TLM.mdb',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/database/sams-accel-db.mdb',
    '/media/trek21/Database/sams-accel-db.mdb'
    '/media/trek21/Trek/configuration_files/telemetry_processing/sams_cu_2015_04_29_IN44.tpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/command_processing/SAMS-CMD-TREK21_IN44.cpc',
    '/media/trek21/Trek/configuration_files/telemetry_processing/sams_cu_2014_12_10.tpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/command_processing/SAMS-CMD-TREK21_IN42.cpc',
    '/media/trek21/Trek/configuration_files/telemetry_processing/obsolete/sams_cu_2014_03_21.tpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/command_processing/obsolete/SAMS-CMD-TREK21.cpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/command_processing/obsolete/SAMS-CMD-TREK21_IN41.cpc',
    '/media/trek21/Trek/configuration_files/telemetry_processing/obsolete/do_not_use.tpc',
    '/media/trek21/Trek/configuration_files/telemetry_processing/obsolete/sams_cu.tpc',
    '/media/trek21/Trek/configuration_files/command_processing/SAMS-CMD-TREK21.cpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/telemetry_processing/TReK100_all.tpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/telemetry_processing/sams_cu_2014_03_21.tpc',
    '/media/trek21/Trek/configuration_files/telemetry_processing/obsolete/samsplayback.tpc',
    '/media/trek21/Trek/configuration_files/telemetry_processing/obsolete/sams_tp.tpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/telemetry_processing/TReK100_all_onTReK21.tpc',
    '/media/trek21/Trek/configuration_files/command_processing/SAMS_POICToRICSim_Commanding.cpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/command_processing/obsolete/SAMS-CMD-TREK100.cpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/telemetry_processing/DataFromTReK20.tpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/command_processing/SAMS_SCS_JohnmTest.cpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/telemetry_processing/TReK100_APID898_412.tpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/telemetry_processing/TReK100.tpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/telemetry_processing/TReK109.tpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/telemetry_processing/GSE_Pkts_12A1.tpc',
    '/media/trek21/Ground Software/SAMS ISS Ground Software/TReK/configuration_files/command_processing/obsolete/SAMS-CMD-TREK109.cpc'
]

for f in files:
    bname = os.path.basename(f)
    dname = os.path.dirname(f)
    print '%55s  "%s"' % (bname, f)
    
raise SystemExit

for f in files:
    md5sum = md5(f).hexdigest()
    print md5sum, f
    
raise SystemExit

count = 0
for c in combinations(files, 2):
    count += 1
    print count, c
