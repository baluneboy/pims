#!/usr/bin/env python

import os
from pims.files.pdfs.pdfjam import CpdfAddTextCommand
from pims.files.utils import listdir_filename_pattern


# return list of PDF files matching filename pattern criteria (not having STAMPED in filename)
def get_pdf_files(dirpath, fname_pat):
    """return list of PDF files for this drop number (i.e. drop dir)"""
    tmp_list = listdir_filename_pattern(dirpath, fname_pat)
    # filter tmp_list to ignore previous run's _cpdf_ filenames
    return [ x for x in tmp_list if "STAMPED" not in x ]


if __name__ == "__main__":

    # get list of analysis template plot PDFs
    sensor = '121f02'
    sensor_suffix = '010'
    fname_pat = '.*' + sensor + sensor_suffix + '_gvtm_pops_.*_EML_analysis.pdf'
    dirpath = '/home/pims/dev/matlab/programs/special/EML/hb_vib_crew_Vehicle_and_Crew_Activity/plots'
    pdf_files = sorted(get_pdf_files(dirpath, fname_pat))
    
    c = 0
    for f in pdf_files:
        c += 1
        print 'page %02d %s' % (c, f)
        #cpdf -prerotate -add-text "${F}" ${F} -color "0.5 0.3 0.4" -font-size 6 -font "Courier" -pos-left "450 5" -o ${F/.pdf/_cpdf_add-text.pdf}
        color = "0.5 0.3 0.4"
        font = "Courier"
        font_size = 6
        pos_left = "450 5"
        cat = CpdfAddTextCommand(f, color, font, font_size, pos_left)
        cat.run()
        