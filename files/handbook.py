#!/usr/bin/env python

# For new handbook PDF type, do the following:
# 1. In pims.patterns.handbookpdfs, add new UNIQUE regex pattern and...
#    be sure pattern varname ends with "PDF_PATTERN", but does NOT start with "_HANDBOOK".
# 2. In the current module (this file), use existing class (if possible), or add new class for new pattern.
# 3. In the current module (this file), add example/new filename to "files" and run to see if it checks out here.

# TODO see /home/pims/dev/programs/python/pims/README.txt

"""
Building handbook files.
"""

import os
import re
import wx
import sys
import inspect
import datetime
import warnings
from pims.files.base import RecognizedFile, UnrecognizedPimsFile
from pims.strings.utils import underscore_as_datetime, title_case_special, sensor_tuple
from pims.files.utils import guess_file
from pims.files.utils import listdir_filename_pattern
from pims.files.pdfs.pdfjam import PdfjamCommand, PdfjoinCommand
from pims.files.log import HandbookLog
from pims.files.pod.templates import _HANDBOOK_TEMPLATE_ODT, _HANDBOOK_TEMPLATE_ANCILLARY_ODT, _HANDBOOK_TEMPLATE_NUP1x2_ODT
from pims.files.pdfs.pdftk import PdftkCommand, convert_odt2pdf
from pims.pad.padheader import PadHeaderDict
from appy.pod.renderer import Renderer
from pims.paths import _YODA_HANDBOOK_DIR
from pims.database.pimsquery import db_insert_handbook, HandbookQueryFilename
from pims.utils.iterabletools import quantify
import pims.patterns.handbookpdfs as hbpat  # patterns
from pims.gui.multichoice_dialog import MultiChoiceFilterFileDialog

class HandbookPdf(RecognizedFile):
    """
    A class derived from RecognizedFile, which provides
    additional features for dealing with handbook files.
    """
    def __init__(self, name, pattern=hbpat._HANDBOOKPDF_PATTERN, show_warnings=False):
        super(HandbookPdf, self).__init__(name, pattern, show_warnings=show_warnings)
        self.plot_type = self._get_plot_type()
        self.page = self._get_page()
        self.subtitle = self._get_subtitle()
        self.notes = self._get_notes()

    def __str__(self): return '%s isa %s\n' % (self.name, self.__class__.__name__)   

    def __repr__(self): return self.__str__()
   
    def _get_page(self): return int( self._match.group('page') )

    def _get_subtitle(self): return title_case_special( self._match.group('subtitle') )

    def _get_notes(self): return self._match.group('notes') or 'empty'

    def _get_plot_type(self): return hbpat._PLOTTYPES['']
    
class OssBtmfRoadmapPdf(HandbookPdf):
    """
    OSSBTMF Roadmap PDF handbook file like this example:
    /tmp/2quantify_2013_10_01_08_ossbtmf_roadmap+some_notes.pdf
    """
    def __init__(self, name, pattern=hbpat._OSSBTMFROADMAPPDF_PATTERN, show_warnings=False):
        super(OssBtmfRoadmapPdf, self).__init__(name, pattern, show_warnings=show_warnings) # pattern is specialized for this class
        self.timestr = self._get_timestr()
        self.datetime = self._get_datetime()
        self.sensor = self._get_sensor()
        self.pad_header = PadHeaderDict(self.sensor, self.datetime)
        
        # Get header type info
        self.system = self.pad_header['System']
        self.sample_rate = self.pad_header['SampleRate']
        self.cutoff = self.pad_header['CutoffFreq']
        self.location = self.pad_header['Location']

        # Get command object for pdfjam -> slightly shrunk PDF up/left via offset/scale
        self.pdfjam_cmd = self._get_pdfjam_cmd()
        self.pdfjam_cmdstr = str(self.pdfjam_cmd)
    
    def get_odt_renderer(self):
        pth, fname = os.path.split(self.name)
        bname, ext = os.path.splitext(fname)
        self.odt_name = os.path.join(pth, 'build', bname + '.odt')
        # Explicitly assign page_dict that contains expected names for appy/pod template substitution
        page_dict = self.__dict__
        return Renderer( _HANDBOOK_TEMPLATE_ODT, page_dict, self.odt_name )
    
    def _get_pdfjam_cmd(self):
        xoffset, yoffset = -4.25, 1.0
        scale = 0.86
        orient = 'landscape'
        return HandbookPdfjamCommand(self.name, xoffset=xoffset, yoffset=yoffset, scale=scale, orient=orient)
    
    def _get_timestr(self): return self._match.group('timestr')

    def _get_datetime(self): return underscore_as_datetime(self.timestr)

    def _get_sensor(self):
        tmp = self._match.group('sensor')
        sensor, suffix = sensor_tuple(tmp)
        # FIXME a better regex pattern would probably help here:
        if suffix and ( suffix.endswith('006') or suffix.endswith('one') ):
            return sensor + '006'
        else:
            return sensor

    def _get_plot_type(self): return hbpat._PLOTTYPES['gvt']

class RadgseRoadmapNup1x2Pdf(OssBtmfRoadmapPdf):
    """
    Radgse gvt3 (1x2 nup) Roadmap PDF handbook file like this example name:
    /tmp/4quantify_2013_09_28_16_radgse_roadmapnup1x2.pdf
    """
    def __init__(self, name, pattern=hbpat._RADGSEROADMAPNUP1X2PDF_PATTERN, show_warnings=False):
        super(RadgseRoadmapNup1x2Pdf, self).__init__(name, pattern, show_warnings=show_warnings)
        self.location = 'ISS'
    
    # FIXME looks like ODT template should be part of init (maybe?)
    def get_odt_renderer(self):
        pth, fname = os.path.split(self.name)
        bname, ext = os.path.splitext(fname)
        self.odt_name = os.path.join(pth, 'build', bname + '.odt')
        # Explicitly assign page_dict that contains expected names for appy/pod template substitution
        page_dict = self.__dict__
        return Renderer( _HANDBOOK_TEMPLATE_NUP1x2_ODT, page_dict, self.odt_name )
        
    # FIXME find sweet spot params here
    def _get_pdfjam_cmd(self):
        xoffset, yoffset = -3.4, 0.0
        scale = 0.74
        orient = 'landscape'
        return HandbookPdfjamCommand(self.name, xoffset=xoffset, yoffset=yoffset, scale=scale, orient=orient)
   
    def _get_plot_type(self): return hbpat._PLOTTYPES['gvt']

class SpgxRoadmapPdf(OssBtmfRoadmapPdf):
    """
    Spectrogram Roadmap PDF handbook file like this example:
    /tmp/1qualify_2013_10_01_16_00_00.000_121f02ten_spgs_roadmaps500_maybe_notes.pdf
    """
    def __init__(self, name, pattern=hbpat._SPGXROADMAPPDF_PATTERN, show_warnings=False):
        super(SpgxRoadmapPdf, self).__init__(name, pattern, show_warnings=show_warnings)
        self.axis = self._get_axis()
    
    # FIXME if sensor suffix is "one", then scale a bit smaller to maybe 0.83?
    def _get_pdfjam_cmd(self):
        xoffset, yoffset = -4.25, 1.0
        #scale = 0.86
        scale = 0.78
        orient = 'landscape'
        return HandbookPdfjamCommand(self.name, xoffset=xoffset, yoffset=yoffset, scale=scale, orient=orient)
   
    def _get_plot_type(self): return hbpat._PLOTTYPES['spg']
    
    def _get_axis(self): return self._match.group('axis')

class RvtxPdf(SpgxRoadmapPdf):
    
    def __init__(self, name, pattern=hbpat._RVTXPDF_PATTERN, show_warnings=False):
        super(RvtxPdf, self).__init__(name, pattern, show_warnings=show_warnings)
    
    def _get_pdfjam_cmd(self):
        xoffset, yoffset = -4.25, 1.0
        scale = 0.8
        orient = 'landscape'
        return HandbookPdfjamCommand(self.name, xoffset=xoffset, yoffset=yoffset, scale=scale, orient=orient)    
    
    def _get_plot_type(self): return hbpat._PLOTTYPES['rvt']

class PcsaRoadmapPdf(SpgxRoadmapPdf):
    def _get_plot_type(self): return hbpat._PLOTTYPES['pcs']

class Psd3RoadmapPdf(SpgxRoadmapPdf):
    """
    PSD XYZ PDF handbook file like this example:
    /tmp/4qualify_2013_10_08_13_35_00_es03_psd3_compare_msg_wv3fans.pdf
    """
    def __init__(self, name, pattern=hbpat._PSD3ROADMAPPDF_PATTERN, show_warnings=False):
        super(Psd3RoadmapPdf, self).__init__(name, pattern, show_warnings=show_warnings)

    def _get_plot_type(self): return hbpat._PLOTTYPES['psd']

    def _get_pdfjam_cmd(self):
        xoffset, yoffset = -4.25, 1.0
        scale = 0.82
        orient = 'landscape'
        return HandbookPdfjamCommand(self.name, xoffset=xoffset, yoffset=yoffset, scale=scale, orient=orient)

class Gvt3Pdf(SpgxRoadmapPdf):
    """
    GVT XYZ PDF handbook file like this example:
    /tmp/4qualify_2013_10_08_13_35_00_es03_gvt3_my_notes_here.pdf
    """
    def __init__(self, name, pattern=hbpat._GVT3PDF_PATTERN, show_warnings=False):
        super(Gvt3Pdf, self).__init__(name, pattern, show_warnings=show_warnings)

    def _get_plot_type(self): return hbpat._PLOTTYPES['gvt']

class ChimPdf(SpgxRoadmapPdf):
    """
    CHI MAG PDF handbook file like this example:
    /tmp/9quantify_2014_09_25_08_30_00_121f08006_chim_compare_rodent_research_install.pdf
    """
    def __init__(self, name, pattern=hbpat._CHIMPDF_PATTERN, show_warnings=False):
        super(ChimPdf, self).__init__(name, pattern, show_warnings=show_warnings)

    def _get_plot_type(self): return hbpat._PLOTTYPES['chi']

class CvfsRoadmapPdf(SpgxRoadmapPdf):
    """
    Cumulative RMS vs. frequency (sum) PDF handbook file like this example:
    /tmp/5quantify_2013_10_08_13_35_00_es03_cvfs_msg_wv3fans_compare.pdf
    """
    def __init__(self, name, pattern=hbpat._CVFSROADMAPPDF_PATTERN, show_warnings=False):
        super(CvfsRoadmapPdf, self).__init__(name, pattern, show_warnings=show_warnings)

    def _get_plot_type(self): return hbpat._PLOTTYPES['cvf']

    def _get_pdfjam_cmd(self):
        xoffset, yoffset = -4.25, 1.0
        scale = 0.82
        orient = 'landscape'
        return HandbookPdfjamCommand(self.name, xoffset=xoffset, yoffset=yoffset, scale=scale, orient=orient)

class IntStatPdf(SpgxRoadmapPdf):
    """
    Interval stat PDF handbook file like this example:
    /tmp/2qualify_2013_09_01_121f05006_irmsx_entire_month.pdf
    """
    def __init__(self, name, pattern=hbpat._INTSTATPDF_PATTERN, show_warnings=False):
        super(IntStatPdf, self).__init__(name, pattern, show_warnings=show_warnings)
        self.axis = self._get_axis()
        
    def _get_pdfjam_cmd(self):
        xoffset, yoffset = -4.25, 1.0
        scale = 0.86
        orient = 'landscape'
        return HandbookPdfjamCommand(self.name, xoffset=xoffset, yoffset=yoffset, scale=scale, orient=orient)
   
    def _get_plot_type(self): return hbpat._PLOTTYPES['ist']

# FIXME do some log.info
class HandbookPdfjamCommand(PdfjamCommand):
    """A custom pdfjam command handler."""
    def __init__(self, *args, **kwargs):
        kwargs['log'] = HandbookLog()
        self.subdir = 'build'
        super(HandbookPdfjamCommand, self).__init__(*args, **kwargs)
        
    def get_outfile(self):
        tmp = super(HandbookPdfjamCommand, self).get_outfile()
        pth, fn = os.path.split(tmp)
        return os.path.join(pth, self.subdir, fn)

class OutputFileExistsError(Exception):
    pass
class OdtFileError(Exception):
    pass
class UnoconvError(Exception):
    pass

# FIXME do some log.info
class HandbookPdftkCommand(PdftkCommand):
    """A better way to get pdftk outfile for handbook ODTs."""
    def __init__(self, odtfile):
        
        if self._verify_fname_ext(odtfile, 'odt'):
            self.odtfile = odtfile
            infile = odtfile.replace('.odt','.pdf')
            if os.path.exists(infile):
                raise OutputFileExistsError('%s already exits' % infile)
        else:
            raise OdtFileError('odtfile must exist and have odt extension')
        
        ret_code = convert_odt2pdf(odtfile)
        if ret_code: # zero is good return by linux cmd line convention
            raise UnoconvError('did not get zero (success) return from unoconv on %s' % odtfile)
    
        bgfile = self._get_bgfile()
        outfile = infile.replace('.pdf', '_pdftk.pdf')
        super(HandbookPdftkCommand, self).__init__(infile, bgfile, outfile)

    def _get_bgfile(self):
        pth = os.path.dirname(self.odtfile)
        bname = os.path.basename(self.odtfile)
        fpattern = bname.replace('.odt', '_offset_.*_scale_.*\.pdf$')
        files = listdir_filename_pattern(pth, fpattern)
        if len(files) == 1:
            return files[0]
        else:
            return None

# convert camel-case name to underscore pattern name
def camelname_to_patname(cname):
    pname = '_' + cname.upper() + '_PATTERN'
    return pname

_HB_CLASS_MEMBERS = [ s for s,c in inspect.getmembers(sys.modules[__name__], inspect.isclass) ]

# we want hb classes that end with "Pdf", but not start with "Handbook"
def get_map_regexp_class():
    map_regexp_class = {}
    dhb = [c for c in _HB_CLASS_MEMBERS if c.endswith('Pdf') and not c.startswith('Handbook')]
    for hb_class_name in dhb:
        regexp_name = camelname_to_patname(hb_class_name)
        #the_class = getattr(hb, hb_class_name)
        the_class = globals()[hb_class_name] # FIXME if there is better, more pythonic way
        the_pattern = getattr(hbpat, regexp_name)
        map_regexp_class[re.compile(the_pattern)] = the_class
    return map_regexp_class

# map filename via unique pattern match to its class
def map_fname_pat_to_class(s):
    """map filename via unique pattern match to its class"""
    
    # get dict that maps regexp to class
    map_regexp_class = get_map_regexp_class()
    
    # match each regex on the string
    matches = ( (c, regex.match(s)) for regex, c in map_regexp_class.iteritems() )
    
    # filter out empty (non) matches, and extract groups
    match_list = [ (c, match.groups()) for c, match in matches if match is not None ]
    
    # verify unique pattern match
    if len(match_list) != 1:
        warnings.warn( 'DO NOT have unique handbook pattern match for %s' % s )    
        klass = None
        args = None
    else:
        # since only one, pull class, mgroups off list
        klass, args = match_list[0]
    return klass, args

def show_matches(fullnames):
    """Map via dictionary with fname regexp pattern as key and class name as value"""
    for f in fullnames:
        klass, args = map_fname_pat_to_class(f)
        print f, klass, args

def is_unique_hb_pdf(fname):
    klass, args = map_fname_pat_to_class(fname)
    if klass:
        return True
    else:
        return False

class HandbookFileDialog(MultiChoiceFilterFileDialog):

    def __init__(self, files):
        # we will use this predicate for preselect method
        self.predicate = is_unique_hb_pdf
        title = 'Handbook File Dialog'
        prompt1 = 'Are all desired files checked?'
        prompt2 = 'IF NOT, THEN HIT CANCEL and fix to verify patterns match...'
        prompt3 = 'OTHERWISE, just leave the desired ones checked and hit OK'
        prompt = '\n'.join( (prompt1, prompt2, prompt3) )
        super(MultiChoiceFilterFileDialog, self).__init__(title, prompt, files)
    
    def all_match(self):
        """Return True if all unique matches for handbook patterns; else return False."""
        idx = [ i for i, f in enumerate(self.choices) if self.predicate(f) ]
        self.dialog.SetSelections(idx)

class HandbookEntry(object):
    """
    A handbook entry container that processes recognized pdf files in a recognized
    source_dir to create editable ODTs as interim products, then can build from those
    the end item, which gets inserted into db on yoda.
    """
    def __init__( self, source_dir, log=HandbookLog() ):
        # Get info from source_dir
        self.source_dir = source_dir
        self.log = log
        pth, dname = os.path.split(source_dir)
        self._hb_pdf_basename = dname + '.pdf'
        self.hb_pdf = os.path.join(source_dir, self._hb_pdf_basename)
        self.regime, self.category, self.title = self._parse_source_dir_string()
        self._pdf_classes = self._get_class_members()
        self.db_entry_exists = self._db_filename_exists()

    def _db_filename_exists(self):
        db_chk = HandbookQueryFilename(self._hb_pdf_basename)
        return db_chk.file_exists

    def __str__(self):
        return "\n".join( [self.title, self.category, self.regime] )

    def will_clobber(self):
        """Return True if we are gonna clobber existing file on yoda."""
        # check if clobber existing hb pdf at destination on yoda
        if os.path.exists( os.path.join(_YODA_HANDBOOK_DIR, self._hb_pdf_basename) ):
            return True
        else:
            return False

    def _get_class_members(self):
        _class_members = []
        clsmembers = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        for cls_name, cls in clsmembers:
            if cls_name.endswith('Pdf') and not cls_name.startswith('Handbook'):
                _class_members.append(cls)
        return _class_members

    def _parse_source_dir_string(self):
        """ Parse source directory string into regime, category, and title. """
        parentDir, s = os.path.split(self.source_dir)
        tup = s.split('_')
        regime = hbpat._ABBREVS[tup[1]]
        category = title_case_special(tup[2])
        title = ' '.join(tup[3:])
        self.log.process.info( 'Parsed source_dir string: regime:{0}, category:{1}, and title:{2}'.format(regime, category, title) )
        return regime, category, title

    def graceful_mkdir_build(self):
        """Rename if pre-existing build subdir and make a fresh build subdir."""
        builddir = os.path.join(self.source_dir, 'build')
        if os.path.isdir(builddir):
            time_stamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            newdir = builddir + '_' + time_stamp
            os.rename(builddir, newdir)
        os.mkdir(builddir)

    def _get_files(self, pth, fname_pattern):
        """Get files that match filename pattern at path."""
        return listdir_filename_pattern(pth, fname_pattern) 

    def _get_files_dialog(self, pth, fname_pattern):
        """Get files that match filename pattern at path with dialog."""
        # if ALL files have unique match (for mapping to class), then use as-is
        files = listdir_filename_pattern(pth, fname_pattern)
        dialog = HandbookFileDialog(files)
        user_selections = dialog.show_dialog()    
        if user_selections is None:
            msg = 'user pressed cancel on file dialog'
        elif len(user_selections) == 0:
            msg = 'user chose no files from file dialog'
        else:
            return user_selections
        
        self.log.process.error(msg)
        raise ValueError(msg)

    def _get_handbook_files(self):
        """Get files that match pattern for handbook PDFs."""
        fname_pattern = hbpat._HANDBOOKPDF_PATTERN[3:] # get rid of ".*/"
        return self._get_files_dialog(self.source_dir, fname_pattern)

    def process_pages(self):
        """Process the files found in source_dir."""
        err_msg = None
        
        # FIXME prompt user to write PDF even when db has this hb entry
        # make sure the ultimate hb pdf filename is not already in db
        if self.db_entry_exists:
            err_msg = 'Database entry with filename %s already exists' % self._hb_pdf_basename
            self.log.process.error(err_msg)
            return err_msg
       
        try:
            self.pdf_files = self._get_handbook_files()        
            self.log.process.info( 'Attempting to process %d pages from files in %s' % ( len(self.pdf_files), self.source_dir ) )
            self.graceful_mkdir_build()
            for f in self.pdf_files:
                
                klass, args = map_fname_pat_to_class(f)
                #print klass, f, args
                #print type(klass)
                #continue
                
                bname = os.path.basename(f)
                try:
                    
                    # FIXME we do not need to guess
                    hbf = guess_file(f, klass, show_warnings=False)
    
                    # Add 3 high-level hb entry properties to hb file object
                    hbf.regime = self.regime
                    hbf.category = self.category
                    hbf.title = self.title
                    
                    # Run pdfjam command if this hbf has one                
                    if hasattr(hbf, 'pdfjam_cmd'):
                        self.log.process.info(hbf.pdfjam_cmdstr)
                        hbf.pdfjam_cmd.run(log=self.log.process)
    
                    # Get ODT renderer and run it to write to-be-editted (imageless) background odt file
                    if hasattr(hbf, 'get_odt_renderer'):
                        odt_renderer = hbf.get_odt_renderer()
                        self.log.process.info('Run odt_renderer for hb file %s' % os.path.basename(hbf.name) )
                        odt_renderer.run()
                    
                    log_msg = 'Done with %s' % bname
                
                except UnrecognizedPimsFile:
                    log_msg = 'SKIPPED unrecognized file %s' % bname
                except Exception as e:
                    err_msg = "could not process all pages, pdfjam/odt_render issue with %s, Exception %s" % (bname, e.message)
                    return err_msg
                
                self.log.process.info(log_msg)
            
            # now render the ancillary odt file`
            try:
                self.ancillary_odt_renderer = self.get_ancillary_odt_renderer()
                self.ancillary_odt_renderer.run()
            except Exception as e:
                err_msg = "could not render ancillary odt file, Exception %s" % e.message
                return err_msg
        
        except Exception as e:
            err_msg = "Exception %s" % e.message
        finally:
            if err_msg: err_msg = 'process_pages err_msg is %s' % err_msg

        return err_msg

    def get_ancillary_odt_name(self):
        """Create ancillary odt filename."""
        fname = 'ancillary_notes.odt'
        return os.path.join(self.source_dir, 'build', fname)

    def get_ancillary_odt_renderer(self):
        """After processing pages, create ancillary odt as last page."""
        ancillary_odt_name = self.get_ancillary_odt_name()
        # Explicitly assign page_dict that contains expected names for appy/pod template substitution
        ancillary_dict = {'title': self.title}
        return Renderer( _HANDBOOK_TEMPLATE_ANCILLARY_ODT, ancillary_dict, ancillary_odt_name )        

    def _get_odt_files(self):
        """Get files that match pattern for ODTs."""
        fname_pattern = hbpat._HANDBOOKPDF_PATTERN[3:].replace('.pdf', '.odt') # FIXME with low priority (SEE _get_handbook_files)
        return self._get_files(self.build_dir, fname_pattern)

    def process_build(self):
        """Process files (pages) in the build subdir."""
        err_msg = None
        try:
            self.build_dir = os.path.join(self.source_dir, 'build')
            if os.path.isdir(self.build_dir):
                self.log.process.info( 'Attempting process_build in %s' % self.build_dir)
                self.odt_files = self._get_odt_files()
                for odtfile in self.odt_files:
                    pdftk_cmd = HandbookPdftkCommand(odtfile)
                    pdftk_cmd.run()
                self.log.process.info('Ran HandbookPdftkCommand (unoconv and offset/scale) for %d odt files' % len(self.odt_files))
            else:
                raise IOError('The build sudir %s is not a directory' % self.build_dir)
            
            # get list of files to join (except for ancillary at this point)
            fname_pattern = hbpat._HANDBOOKPDF_PATTERN[3:].replace('.pdf', '_pdftk.pdf')
            self.unjoined_files = self._get_files(self.build_dir, fname_pattern)
            
            # convert ancillary ODT to PDF, prepend page num, and include with other pages to be joined
            ancillary_pdf = self.convert_ancillary( len(self.unjoined_files)+1 )
            self.unjoined_files.append(ancillary_pdf)
            self.log.process.info('We now have %d unjoined files, including ancillary file' % len(self.unjoined_files))
            
            # finalize
            err_msg = self.finalize_entry()
            
        except IOError as e:
            err_msg = "IOError: {0}".format(e.message)
        except Exception as e:
            err_msg = "Exception %s" % e.message
        finally:
            if err_msg: err_msg = 'process_build err_msg is %s' % err_msg

        return err_msg
    
    def finalize_entry(self):
        """Rename a pre-existing hb pdf, then create final hb pdf for db and web."""
        err_msg = None
        try:
            self.log.process.info('Attempting to finalize_entry')
            if os.path.exists(self.hb_pdf):
                time_stamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
                os.rename(self.hb_pdf, self.hb_pdf + '.' + time_stamp)
                self.log.process.info('Renamed hb_pdf with time stamp')
            pdfjoin_cmd = PdfjoinCommand(self.unjoined_files, self.hb_pdf)
            pdfjoin_cmd.run()
            self.log.process.info('Ran pdfjoin command to get %s' % self.hb_pdf)
            if os.path.exists(self.hb_pdf):
                unused_flag, unbuild_err_msg = self.unbuild(execute=True)
                if unbuild_err_msg:
                    self.log.process.error('SKIP db_insert because unbuild error msg: %s' % err_msg)
                    return 'finalize_entry err_msg is %s' % unbuild_err_msg
                else:
                    self.log.process.info('Did the unbuild okay')
                    
                # Now do db insert for this entry
                db_err_msg = self.db_insert()
                if db_err_msg:
                    self.log.process.error(db_err_msg)
                    return 'finalize_entry err_msg is %s' % db_err_msg
                
            else:
                err_msg = 'Did NOT unbuild or do db insert because hb_pdf did not exist'
        
        except Exception as e:
            err_msg = "Exception %s" % e.message
        finally:
            if err_msg: err_msg = 'finalize_entry err_msg is %s' % err_msg
    
        return err_msg

    # TODO needs work for details and PROBABLY a new stored procedure on yoda?
    def db_insert(self):
        """Insert db record via Eric's routine on yoda."""
        err_msg = None
        fname = os.path.basename(self.hb_pdf)
        #err_msg =  db_insert_handbook(fname, self.title, 'vibratory', None)
        err_msg = db_insert_handbook(fname, self.title, self.regime, self.category)
        if err_msg:
            self.log.process.error(err_msg)
            err_msg = 'db_insert err_msg is %s' % err_msg
        return err_msg

    # FIXME pull out unused error flag output and fix reference to it in finalize_entry
    # FIXME do some log.info here for files getting tossed (or not matching ODT), etc.
    def unbuild(self, execute=True):
        """
        Check if we are ready to unbuild, which allows for modified ODTs.
        *if execute is True, then actually do the rebuild
        """
        files_to_toss = []
        
        # Remove *_pdftk.pdf files
        build_dir = os.path.join(self.source_dir, 'build')
        pdftk_files = self._get_files(build_dir, '.*_pdftk.pdf')
        if not pdftk_files:
            msg = 'NO pdftk_pdf files found during unbuild'
            return False, msg
        files_to_toss += pdftk_files

        # Remove *.pdf files that have matching .odt file
        pdf_files_matching_odt = []
        odt_files = self._get_files(build_dir, '.*.odt')
        for odt_file in odt_files:
            pdf_file = odt_file.replace('.odt', '.pdf')
            if os.path.exists(pdf_file):
                pdf_files_matching_odt.append(pdf_file)
            else:
                msg = 'Seems unpaired odt/pdf files'
                return False, msg
        files_to_toss += pdf_files_matching_odt

        # Get '\dancillary_.*\.odt'
        dancillary_odt = self._get_files(build_dir, '\dancillary_.*.odt')
        if len(dancillary_odt) == 1:
            dancillary_odt = dancillary_odt[0]
        else:
            msg = 'NO unbuild because len(dancillary_odt) not exactly one'
            return False, msg
        
        # Rename \dancillary_.*\.odt WITHOUT leading page num digit
        pth, bname = os.path.split(dancillary_odt)
        renamed_odt = os.path.join(pth, bname[1:])
        try:
            os.rename( dancillary_odt, renamed_odt )
            os.rename( renamed_odt, dancillary_odt )
        except:
            msg = 'Could not rename dancillary odt file to no-leading-digit odt file'
            return False, msg

        # Get out here if okay to unbuild, but not wanting to execute
        if not execute:
            msg = 'Okay to unbuild, but execute boolean input is False, so skip out'
            return True, msg
        
        # Actually do the unbuild
        [os.remove(f) for f in files_to_toss]
        os.rename( dancillary_odt, renamed_odt )
        return False, None
    
    def convert_ancillary(self, page_num):
        """Use unoconv for ancillary odt with prepend of page number."""
        self.ancillary_odt_name = self.get_ancillary_odt_name()
        new_name = self.ancillary_odt_name.replace('ancillary_', '%dancillary_' % page_num)
        os.rename(self.ancillary_odt_name, new_name)
        ret_code = convert_odt2pdf(new_name)
        return new_name.replace('.odt','.pdf')

# use this function to test a folder of interest
def check_dir(folder):

    files = listdir_filename_pattern(folder, hbpat._HANDBOOKPDF_PATTERN[3:])

    #files = [
    #    '/tmp/1qualify_2013_12_19_08_00_00.000_121f03_spgs_roadmaps500_cmg_spin_downup.pdf',
    #    '/tmp/5quantify_2013_10_08_13_35_00_es03_cvfs_msg_wv3fans_compare.pdf',
    #    '/tmp/1qualify_2013_10_01_00_00_00.000_121f05_pcss_roadmaps500.pdf',
    #    '/tmp/x3quantify_2013_09_22_121f03_irmss_cygnus_fan_capture_31p7to41p7hz.pdf',
    #    '/tmp/1quantify_2013_12_11_16_20_00_ossbtmf_gvt3_progress53p_reboost.pdf',
    #    '/tmp/1qualify_2011_05_19_18_18_00_121f03006_gvt3_12hour_pm1mg_001800_12hc.pdf',
    #    '/tmp/2quantify_2011_05_19_18_18_00_121f03006_gvt3_12hour_pm1mg_001800_hist.pdf',
    #    '/tmp/x3quantify_2011_05_19_00_08_00_121f03006_gvt3_12hour_pm1mg_001800_z1mg.pdf',
    #    '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_CMG_Desat/1quantify_2011_05_19_18_18_00_121f03006_gvt3_12hour_pm1mg_001800_12hc.pdf',
    #    '/tmp/x3quantify_2014_03_03_14_30_00_121f08_rvts_glacier3_duty_cycle.pdf',
    #    ]
    #show_matches(files)
       
    dialog = HandbookFileDialog(files)
    user_selections = dialog.show_dialog()    
    if user_selections is None:
        print 'you pressed cancel'        
    elif len(user_selections) == 0:
        print 'you chose nothing'
    else:
        print user_selections
    
    print "=== above are user selections, below are class assignments ==="
    show_matches(user_selections)
    
#check_dir('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_Bogus_Entry'); raise SystemExit

if __name__ == '__main__':

    #hbe = HandbookEntry(source_dir='/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Cygnus_Capture_Install')
    #hbe = HandbookEntry(source_dir='/home/pims/Documents/test/hb_vib_vehicle_Big_Bang')
    #hbe = HandbookEntry(source_dir='/home/pims/Documents/test/hb_vib_vehicle_Cygnus_Capture_Install')
    #hbe = HandbookEntry(source_dir='/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_Cygnus_Fan')
    #hbe = HandbookEntry(source_dir='/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_CMG_Desat')
    #hbe = HandbookEntry(source_dir='/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_Columbus_GLACIER-3')
    #hbe = HandbookEntry(source_dir='/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_Bogus_Entry')
    hbe = HandbookEntry(source_dir='/misc/yoda/www/plots/user/handbook/source_docs/hb_qs_vehicle_Attitude_Catalog')
    
    if True: # True for process_pages (the first stage), False for process_build (the last stage)
        
        if not hbe.will_clobber():
            err_msg = hbe.process_pages()
            print err_msg or 'process_pages okay'
        else:
            print 'ABORT PAGE PROCESSING because hb pdf filename conflict on yoda'
    
    else:
        
        if not hbe.will_clobber():
            err_msg = hbe.process_build()
            print err_msg or 'process_build okay'
        else:
            print 'ABORT BUILD because hb pdf filename conflict on yoda'
    
    #ok_to_unbuild, msg = hbe.unbuild(execute=False)
    #print "ok_to_unbuild", ok_to_unbuild
    #print msg
    pass
