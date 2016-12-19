#!/usr/bin/env python

# TODO handle when output from pdfjam run contains "pdfjam ERROR: Output file not written"

import os
import subprocess

from pims.utils.commands import timeLogRun, time_run

class PdfjamProperty(object):
    """
    This class implements property values for pdfjam commands.

    Argument is converted to float.

    PdfjamProperty can also be constructed from:

      - numeric strings similar to those accepted by the
        float constructor (for example, '-2.3')

      - float, Fraction, and Decimal instances

      - integers
      
    """
    def __init__(self, value=0):
        """Constructs a PdfjamProperty.

        Takes a string like '3/2' or '1.5', Fraction instance, an
        integer, or a float.

        Examples
        --------
        >>> PdfjamProperty( 1.3579 )
        PdfjamProperty(1.36)
        >>> PdfjamProperty( 9 )
        PdfjamProperty(9.00)
        >>> from fractions import Fraction
        >>> PdfjamProperty( Fraction(1,2) )
        PdfjamProperty(0.50)
        >>> PdfjamProperty( '-4.2' ).value
        -4.2
        
        """
        super(PdfjamProperty, self).__init__()
        try:
            self.value = float(value)
        except TypeError:
            raise TypeError("input value should be a float, int, "
                            "string or a Fraction instance")
    
    def __repr__(self):
        """repr(self)"""
        return ('PdfjamProperty(%.2f)' % (self.value))

    def __str__(self):
        """str(self)"""
        return '%.2f' % self.value

class PdfjamScale(PdfjamProperty):
    """
    This class implements property values for pdfjam scale argument.

    Takes a string like '85/100' or '0.88', Fraction instance, or
    a float (but not an int).
    
    Argument is converted to float and must satisfy 0 < value <= 1.
    
    PdfjamScale can also be constructed just like PdjjamProperty.

    Examples
    --------
    >>> PdfjamScale( 1.5 )
    Traceback (most recent call last):
    ...
    ValueError: input value must have 0 < value <=1
    >>> PdfjamScale( 9 )
    Traceback (most recent call last):
    ...
    ValueError: input value must have 0 < value <=1
    >>> from fractions import Fraction
    >>> PdfjamScale( Fraction(1,2) )
    PdfjamScale(0.50)

    """
    def __init__(self, value=0):
        """
        Constructs a PdfjamScale property.
        """
        super(PdfjamScale, self).__init__(value=value)
        
        # scale must have value between 0 and 1
        if self.value <= 0 or self.value > 1:
            raise ValueError('input value must have 0 < value <=1')
        
    def __repr__(self):
        """repr(self)"""
        return 'PdfjamScale(%.2f)' % self.value

class PdfjamOffsetScale(object):
    """
    This class implements offset/scale part of arguments for pdfjam command.

    Takes args for xoffset, yoffset, and scale; where offset values are PdjjamProperty
    and scale is a PdfjamScale.

    Examples
    --------
    >>> print PdfjamOffsetScale( xoffset=-3.75 )
    --offset '-3.75cm 0.00cm' --scale 1.00

    """    
    def __init__(self, xoffset=0.0, yoffset=0.0, scale=1.0):
        self.xoffset = PdfjamProperty( xoffset )
        self.yoffset = PdfjamProperty( yoffset )
        self.scale = PdfjamScale( scale )

    def __str__(self):
        # pdfjam --offset '-2.75cm 0.75cm' --scale 0.88 inputFile.pdf --landscape etc.
        return "--offset '{0:0.2f}cm {1:0.2f}cm' --scale {2:0.2f}".format(self.xoffset.value, self.yoffset.value, self.scale.value)

class PdfjamCommand(object):
    """This class implements pdfjam commands.

    INPUTS:
    infile - required string to input PDF file
    xoffset - optional float for X-offset in cm
    yoffset - optional float for Y-offset in cm
    scale - optional float for 0 < scale <= 1
    orient - optional string, either empty or '--landscape'
    
    OUTPUT:
    The PDF output file with name similar to input, but with suffix added from:
    pdfjam --offset '-2.75cm 0.75cm' --scale 0.88 infile.pdf --landscape --outfile infile_offset_-2p75_0p75_scale_0p88.pdf

    """
    def __init__(self, infile, xoffset=0, yoffset=0, scale=1, orient='landscape', log=None):
        """
        A pdfjam command with appropriate arguments.
        """
        if os.path.exists(infile) and infile.lower().endswith('.pdf'):
            self.infile = infile
        else:
            raise ValueError('input file must exist and have pdf/PDF extension')
        self._offset_scale = PdfjamOffsetScale(xoffset=xoffset, yoffset=yoffset, scale=scale)
        self.xoffset = self._offset_scale.xoffset.value
        self.yoffset = self._offset_scale.yoffset.value
        self.scale = self._offset_scale.scale.value
        self.orient = '--' + (orient or '')
        self.log = log
        self.outfile = self.get_outfile()
        self.command = self.get_command()
        
    def __str__(self):
        return self.command
    
    def get_outfile(self):
        prefix, ext = os.path.splitext(self.infile)
        suffix = "_offset_{0:0.2f}cm_{1:0.2f}cm_scale_{2:0.2f}.pdf".format(self.xoffset, self.yoffset, self.scale)
        return prefix + suffix
    
    def get_command(self):
        return "pdfjam %s %s %s --outfile %s" % (self._offset_scale, self.infile, self.orient, self.outfile)
    
    def run(self, timeoutSec=10, log=None):
        retCode, elapsedSec = timeLogRun('echo -n "Start pdfjam cmd at "; date; %s; echo -n "End   pdfjam cmd at "; date' % self.command, timeoutSec, log=log)


# cpdf -scale-page "0.8 0.8" -o out2.pdf 2016_01_21_10_00_51_es14_gvt3_8m59s_samseses14topshelfmdropv_drop2_gvt3_bigpic.pdf
class CpdfScalePageCommand(object):
    """This class implements cpdf scale-page command.

    INPUTS:
    infile - required string to input PDF file
    xscale - optional float for 0 < scale <= 1 (for x)
    yscale - optional float for 0 < scale <= 1 (for y)
    
    OUTPUT:
    The PDF output file with name similar to input, but with suffix added from like:
    cpdf -scale-page "0.8 0.8" -o OUT.pdf INFILE.pdf

    """
    def __init__(self, infile, xscale=0.8, yscale=0.8):
        """
        A cpdf scale-page command with appropriate arguments.
        """
        if os.path.exists(infile) and infile.lower().endswith('.pdf'):
            self.infile = infile
        else:
            raise ValueError('input file must exist and have pdf/PDF extension')
        self.xscale = xscale
        self.yscale = yscale
        self.outfile = self.get_outfile()
        self.command = self.get_command()
        
    def __str__(self):
        return self.command
    
    def get_outfile(self):
        prefix, ext = os.path.splitext(self.infile)
        suffix = "_cpdf_scale-page_{0:0.2f}_{1:0.2f}.pdf".format(self.xscale, self.yscale)
        return prefix + suffix
    
    def get_command(self):
        return 'cpdf -scale-page "%.2f %.2f" -o %s %s' % (self.xscale, self.yscale, self.outfile, self.infile)
    
    def run(self):
        p = subprocess.Popen([self.command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


# cpdf -stamp-on out2.pdf -top 99 ~/temp/appendixC_page14.pdf -o new2.pdf
class CpdfStampCommand(object):
    """This class implements cpdf stamp-on command.

    INPUTS:
    logo_file - required string to input PDF file
    top_offset - offset from top # FIXME what units; try 99
    onto_file - required string for other/background input PDF file
    
    OUTPUT:
    The PDF output file with name similar to onto_file, but with suffix added from like:
    cpdf -stamp-on LOGO_FILE.pdf -top 99 ONTO_FILE.pdf -o OUT.pdf

    """
    def __init__(self, logo_file, top_offset, onto_file):
        """
        A cpdf stamp-on command with appropriate arguments.
        """
        if os.path.exists(logo_file) and logo_file.lower().endswith('.pdf'):
            self.logo_file = logo_file
        else:
            raise ValueError('logo input file must exist and have pdf/PDF extension')
        if os.path.exists(onto_file) and onto_file.lower().endswith('.pdf'):
            self.onto_file = onto_file
        else:
            raise ValueError('onto input file must exist and have pdf/PDF extension')        
        self.top_offset = top_offset
        self.outfile = self.get_outfile()
        self.command = self.get_command()
        
    def __str__(self):
        return self.command
    
    def get_outfile(self):
        prefix, ext = os.path.splitext(self.onto_file)
        suffix = "_cpdf_stamp-on_{0:d}.pdf".format(self.top_offset)
        return prefix + suffix
    
    def get_command(self):
        return 'cpdf -stamp-on %s -top %d %s -o %s' % (self.logo_file, self.top_offset, self.onto_file, self.outfile)
    
    def run(self):
        p = subprocess.Popen([self.command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


#cpdf -prerotate -add-text "${F}" ${F} -color "0.5 0.3 0.4" -font-size 6 -font "Courier" -pos-left "450 5" -o ${F/.pdf/_STAMPED.pdf}
class CpdfAddTextCommand(object):
    """This class implements cpdf add-text command.

    INPUTS:
    pdf_file - required string to input PDF file
    color - offset from top # FIXME what units; try 99
    font - string for font (like "Courier")
    font_size - integer (like 6)
    pos_left - string for position (like "450 5")
    
    OUTPUT:
    The PDF output file with name similar to pdf_file, but with suffix added _cpdf_add-text.

    """
    def __init__(self, pdf_file, color, font, font_size, pos_left):
        """
        A cpdf add-text command with appropriate arguments.
        """
        if os.path.exists(pdf_file) and pdf_file.lower().endswith('.pdf'):
            self.pdf_file = pdf_file
        else:
            raise ValueError('pdf input file must exist and have pdf/PDF extension')
        self.color = color
        self.font = font
        self.font_size = font_size
        self.pos_left = pos_left
        self.outfile = self.get_outfile()
        self.command = self.get_command()
        
    def __str__(self):
        return self.command
    
    def get_outfile(self):
        prefix, ext = os.path.splitext(self.pdf_file)
        suffix = "_cpdf_add-text.pdf"
        return prefix + suffix
    
    def get_command(self):
        #       cpdf -prerotate -add-text "${F}" ${F} -color "0.5 0.3 0.4" -font-size 6 -font "Courier" -pos-left "450 5" -o ${F/.pdf/_STAMPED.pdf}
        return 'cpdf -prerotate -add-text "%s" %s -color "%s" -font-size %d -font "%s" -pos-left "%s" -o %s' % (os.path.basename(self.pdf_file), self.pdf_file, self.color, self.font_size, self.font, self.pos_left, self.outfile)
    
    def run(self):
        p = subprocess.Popen([self.command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
        
class PdfjoinCommand(object):
    """This class implements pdfjoin command.

    INPUTS:
    infiles - required list of strings for input PDF files
    outfile - required string for output PDF file
    
    OUTPUT:
    The PDF output file from:
    pdfjoin infile1 infile2 infile3 ... --outfile outfile

    """
    def __init__(self, infiles, outfile):
        """
        A pdfjoin command with infiles and outfile arguments.
        """
        self.infiles = self._verify_infiles(infiles)
        self.outfile = self._verify_outfile(outfile)
        self.command = self.get_command()
        
    def __str__(self):
        return self.command

    def get_command(self):
        """get command to be run"""
        s = ['pdfjoin']
        [s.append(f) for f in self.infiles]
        s.append('--outfile')
        s.append(self.outfile)
        return ' '.join(s)
    
    def run(self, timeoutSec=10, log=None):
        """run the command"""
        retCode, elapsedSec = timeLogRun('echo -n "Start pdfjoin cmd at "; date; %s; echo -n "End   pdfjoin cmd at "; date' % self.command, timeoutSec, log=log)
    
    def _verify_outfile(self, outfile):
        """outfile must not pre-exist"""
        if os.path.exists(outfile):
            raise ValueError('outfile already exists')
        return outfile
    
    def _verify_infiles(self, infiles):
        """infiles must pre-exist"""
        for f in infiles:
            if not os.path.exists(f) and f.lower().endswith('.pdf'):
                raise ValueError('input file must exist and have pdf/PDF extension')
        return infiles

def demo(f, scale=0.5, log=False):
    from pims.files.log import demo_log, NoLog
    from pims.files.handbook import SpgPdfjamCommand, Gvt3PdfjamCommand

    if log:
        logDemo = demo_log('/tmp/trashdemo.log')
    else:
        logDemo = NoLog()

    pdfjam_cmd = SpgPdfjamCommand(f, log=logDemo)
    pdfjam_cmd.run(log=logDemo)

def demojoin():
    infiles = [
        '/home/pims/Documents/test/hb_vib_vehicle_Big_Bang/build/1qualify_2013_10_10_00_00_00.000_121f03one_spgs_roadmaps142_amazing_pdftk.pdf',
        '/home/pims/Documents/test/hb_vib_vehicle_Big_Bang/build/2quantify_2013_10_01_00_ossbtmf_roadmap_pdftk.pdf'
    ]
    outfile = '/home/pims/Documents/test/hb_vib_vehicle_Big_Bang/hb_FILE.pdf'
    pdfjoin_cmd = PdfjoinCommand(infiles, outfile)
    pdfjoin_cmd.run()

def manual_pdfjam_and_join():
    import os
    from pims.files.utils import listdir_filename_pattern
    dirpath = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_CMG_Desat'
    xysfs = [
        (-4.25, 1.00, 0.86, os.path.join(dirpath, '1quantify_2011_05_19_18_18_00_121f03006_gvt3_12hour_pm1mg_001800_12hc.pdf')),
        (-4.25, 1.00, 0.86, os.path.join(dirpath, '2quantify_2011_05_19_18_18_00_121f03006_gvt3_12hour_pm1mg_001800_hist.pdf')),
        (-4.25, 1.00, 0.86, os.path.join(dirpath, '3quantify_2011_05_19_00_08_00_121f03006_gvt3_12hour_pm1mg_001800_z1mg.pdf')),
        ]
    for xoffset, yoffset, scale, f in xysfs:
        p = PdfjamCommand(f, xoffset=xoffset, yoffset=yoffset, scale=scale)
        p.run()
    
    fname_pattern = '.qua.*_offset_.*cm_.*cm_scale_.*\.pdf'
    infiles = listdir_filename_pattern(dirpath, fname_pattern)
    outfile = os.path.join(dirpath, 'hb.pdf')
    pdfjoin_cmd = PdfjoinCommand(infiles, outfile)
    pdfjoin_cmd.run()

#manual_pdfjam_and_join(); raise SystemExit

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
    print 'Now for a demo...'
    #demo('/tmp/1qualify_2013_10_01_00_ossbtmf_roadmap.pdf', log=True)
    demojoin()
