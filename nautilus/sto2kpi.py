#!/usr/bin/env python

"""From nautilus-selected filename, verify '.sto' extension and convert the STO file to XLSX for AMP KPI."""

import os
import sys
import subprocess
from pims.pad.amp_kpi import convert_sto2xlsx


def show_filename(fname, title):
    """show filename and title in in zenity dialog"""

    # FIXME zenity removes underscores
    cmd = 'zenity --entry --text "' + fname + '" --title "' + title + '"'
    #process = subprocess.Popen(cmd, shell=True)
    subprocess.Popen(cmd, shell=True)


def show_message(msg, title):
    """show message and title in in zenity dialog"""

    # FIXME zenity removes underscores
    cmd = 'zenity --entry --text "' + msg + '" --title "' + title + '"'
    subprocess.Popen(cmd, shell=True)


def input_filename_ok(filename):
    """return boolean: True if input filename is as expected for sto2xlsx conversion"""
    # proper extension
    if not filename.endswith('sto'):
        show_message('bad extension, not lowercase ext=sto file', 'FAIL')
        return False

    return True


def main():
    """return status code after processing nautilus-selected filename to convert STO file to XLSX for AMP KPI"""

    # get nautilus selected files
    sel_files = os.environ['NAUTILUS_SCRIPT_SELECTED_FILE_PATHS'].splitlines()

    # expecting exactly one file
    if len(sel_files) != 1:
        show_message('expected exactly one file', 'ABORT')
        return -1
    stofile = sel_files[0]

    # sanity check filename
    if not input_filename_ok(stofile):
        return -2

    # get output filename
    dir_name = os.path.dirname(os.path.dirname(stofile))
    base_name = os.path.basename(stofile).replace('.sto', '.xlsx')
    xlsxfile = os.path.join(dir_name, base_name)

    # show_filename(xlsxfile, 'XLSXFILE')

    # convert to Excel file
    convert_sto2xlsx(stofile, xlsxfile)

    show_message('See parent directory for XLSX file.', 'DONE')

    return 0


if __name__ == '__main__':
    sys.exit(main())
