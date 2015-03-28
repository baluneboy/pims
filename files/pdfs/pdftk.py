#!/usr/bin/env python

import os
from pims.utils.commands import timeLogRun

def convert_odt2pdf(odtfile):
    command = 'unoconv %s' % odtfile
    return_code, elapsedSec = timeLogRun('echo -n "Start conv cmd at "; date; %s; echo -n "End   conv cmd at "; date' % command, 15, log=None)
    return return_code

class PdftkCommand(object):
    """This class implements pdftk commands.

    INPUTS:
    infile - required string to input PDF file
    bgfile - required string for background PDF file
    
    OUTPUT:
    The PDF output file with name similar to input, but with suffix added from:
    pdftk unoconv_odtfile.pdf background unoconv_odtfile_offset_-4.25cm_1cm_scale_0.88.pdf output updir/hb_regime_category_title.pdf

    """
    def __init__(self, infile, bgfile, outfile):
        """
        A pdftk command with appropriate arguments.
        """
        if self._verify_fname_ext(infile, 'pdf') and self._verify_fname_ext(bgfile, 'pdf'):
            self.infile = infile
            self.bgfile = bgfile
            if os.path.exists(outfile):
                raise RuntimeError('outfile %s already exits' % outfile)
            self.outfile = outfile
        else:
            raise ValueError('infile and bgfile must exist and have pdf/PDF extension')
        self.command = self.get_command()
        
    def __str__(self):
        return self.command
    
    def _verify_fname_ext(self, fname, ext):
        if os.path.exists(fname) and fname.lower().endswith('.' + ext):
            return True
        else:
            return False
    
    def get_command(self):
        return "pdftk %s background %s output %s" % (self.infile, self.bgfile, self.outfile)
    
    def run(self, timeoutSec=10, log=None):
        return_code, elapsedSec = timeLogRun('echo -n "Start pdftk cmd at "; date; %s; echo -n "End   pdftk cmd at "; date' % self.command, timeoutSec, log=log)

def demo():
    pth = '/home/pims/Documents/test/hb_vib_vehicle_Big_Bang/build_2013_10_14_15_58_07'
    infile = os.path.join(pth, '1qualify_2013_10_10_00_00_00.000_121f03one_spgs_roadmaps142_amazing.pdf')
    bgfile = os.path.join(pth, '1qualify_2013_10_10_00_00_00.000_121f03one_spgs_roadmaps142_amazing_offset_-3.00cm_1.00cm_scale_0.72.pdf')
    outfile = os.path.join(pth, 'trash2.pdf')

    pdftk_cmd = PdftkCommand(infile, bgfile, outfile)
    pdftk_cmd.run()

def demo2():
    odtfile = '/home/pims/Documents/test/hb_vib_vehicle_Big_Bang/build_2013_10_14_15_58_07/2quantify_2013_10_01_00_ossbtmf_roadmap.odt'
    retcode = convert_odt2pdf(odtfile)
    print retcode

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    print 'Now for a demo...'
    demo2()
