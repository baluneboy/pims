#!/usr/bin/env python

"""A nautilus utility for converting ATL readme.txt to MATLAB script."""

__author__ = "Ken Hrovat"
__date__   = "$12 January, 2016 08:38:00 AM$"

import os
import re
import sys
import gtk
import datetime

from pims.patterns.dirnames import _HANDBOOKDIR_PATTERN
from pims.files.utils import tail
from pims.pop.asflown_event_base import AsFlownEvent, ProgressDockingMatlabCode


# show alert dialog and return code
def alert(msg, title='ALERT'):
    """show alert dialog and return code"""
    label = gtk.Label(msg)
    dialog = gtk.Dialog(title,
                        None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        buttons=(gtk.STOCK_OK, 1, "Cancel", 2))
    dialog.vbox.pack_start(label)
    label.show()
    response = dialog.run()
    dialog.destroy()
    return response # 1 for "OK", 2 for "Cancel", otherwise -4 (for X)


# take action from nautilus script based on last line of readme.txt
def main(curdir):
    """take action from nautilus script based on last line of readme.txt"""
    
    # Strip off uri prefix
    if curdir.startswith('file:///'):
        curdir = curdir[7:]

    # Verify curdir matches pattern (this works even in build subdir! a good thing?)
    match = re.search( re.compile(_HANDBOOKDIR_PATTERN), curdir )

    ########################################################################################
    # this is where we do branching based on last line of readme.txt
    if match:
    
        # readme.txt must be at main parent source dir for typical handbook
        bname = os.path.basename(curdir)
        if bname.startswith('hb_vib_') or bname.startswith('hb_qs_'):
            
            #------------------------------------------------------
            # We are in main parent source dir like the following:
            # /misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Progress_62P_Docking_2015-12-23
            #------------------------------------------------------
            
            readme_file = os.path.join(curdir, 'readme.txt')
            
            if os.path.exists(readme_file):
                # readme.txt file exists, get just last line for branching
                with open(readme_file, 'r') as f:
                    last_line = tail(f, 1)[0]
                    
                if last_line.startswith('# AS-FLOWN EVENTS ARE LISTED ABOVE'):
                    mc = ProgressDockingMatlabCode(readme_file)
                    mc.digest_events()
                    mc.append_code()
                    print mc # TODO append matlab code to readme.txt
                    msg = 'Appended MATLAB code to readme file for standard processing of Progress Docking (%d events).' % len(mc.asflown_events)
                    
                elif last_line.startswith('# STANDARD PROCESSING FOR PROGRESS DOCKING ENDS HERE'):
                    msg = 'NOW DO SENSOR-TO-SENSOR COMPARISON OF DOCKING EVENT TIME AND MAG'
                    
                elif last_line.startswith('# FOUR-HOUR WINDOW STATS ON VECMAG ENDS HERE'):
                    msg = 'DONE WITH PROGRESS DOCKING ANALYSIS'
                    
                else:
                    msg = 'UNRECOGNIZED last line of readme.txt ' + last_line

            else:
                # no readme.txt file, so abort
                msg = 'ABORT: %s does NOT exist' % readme_file
                
        else:
            
            #------------------------------------------------------
            # We are in unknown hb subdir
            #------------------------------------------------------
                        
            msg = 'ABORT: ignore because in some hb subdir'
    
    else:
        
        msg = 'ABORT: ignore non-hb dir'

    response = alert( '%s' % msg ) # 1 for "OK", 2 for "Cancel", otherwise -4 (for eXited out)

#convert_odt2pdf('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Soyuz_42S_Thruster_Test_2015-09-08/build/01Qualify_2015_09_08_00_00_00.000_121f03_pcss_roadmaps500.odt')
#raise SystemExit

#main('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_SARJ_Sinusoidal_Correlation/build/unjoined')
#main('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_MSG_Troubleshooting_and_Repair')
#main('/misc/yoda/www/plots/user/handbook/source_docs/hb_qs_vehicle_25-Nov-2015_Progress_61P_Reboost')
#main('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_2015_Cygnus-4_Capture_and_Install/build')
main('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Progress_62P_Docking_2015-12-23')

raise SystemExit

#odt_renderer = get_odt_renderer('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Soyuz_42S_Thruster_Test_2015-09-08/build/01qualify_2015_09_08_00_00_00.000_121f03_pcss_roadmaps500_offsets_-4.25cm_1.00cm_scale_0.86_landscape.pdf')
#odt_renderer.run()
#raise SystemExit

if __name__ == "__main__":
    # Get nautilus current uri and take action in main func
    curdir = os.environ.get('NAUTILUS_SCRIPT_CURRENT_URI', os.curdir)
    main(curdir)
