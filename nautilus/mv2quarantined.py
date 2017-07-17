#!/usr/bin/env python

"""Move nautilus-selected filenames to quarantined subdirectory."""

import os
import sys
import shutil
import subprocess

from pims.files.utils import mkdir_p
from pims.nautilus.sto2kpi import show_message


def show_count_filenames(fnames, title='Count of Filenames'):
    """show count of filenames and title in in zenity dialog"""

    # FIXME zenity removes underscores
    cstr = len(fnames)
    cmd = 'zenity --entry --text "' + cstr + '" --title "' + title + '"'
    subprocess.Popen(cmd, shell=True)


def inputs_ok(filenames):
    """return boolean: True if input filenames are as expected for mv to quarantined subdirectory"""

    if len(filenames) < 2:
        return False

    # TODO what checks makes sense (match regular expression for proper PAD path
    return True


def main():
    """return status code after processing nautilus-selected filenames to move PAD files to quarantined subdirectory"""

    # get nautilus selected files
    sel_files = os.environ['NAUTILUS_SCRIPT_SELECTED_FILE_PATHS'].splitlines()

    # show_message('GOT %d FILESa' % len(sel_files), 'DONE')

    # sanity check filenames
    if not inputs_ok(sel_files):
        return -2

    if len(sel_files) < 1:
        return -3

    # show_message('GOT %d FILESb' % len(sel_files), 'DONE')

    # mkdir for quarantined subdirectory
    dir_name = os.path.dirname(sel_files[0])
    subdir_name = os.path.join(dir_name, 'quarantined')
    #show_message(subdir_name, 'SUBDIR')
    mkdir_p(subdir_name)

    # move files to quarantined subdir
    for f in sel_files:
        shutil.move(f, subdir_name)

    show_message('Moved %d files to %s' % (len(sel_files), subdir_name), 'DONE')

    return 0


if __name__ == '__main__':
    sys.exit(main())
