#!/usr/bin/env python

import os
import pygtk; pygtk.require('2.0')
import gtk
import time
import re
import threading
import subprocess
import pandas as pd
from appy.pod.renderer import Renderer

from pims.files.utils import mkdir_p
from pims.patterns.dirnames import _HANDBOOKDIR_PATTERN
from pims.patterns.handbookpdfs import _HANDBOOKPDF_PATTERN
from pims.files.pod.templates import _HANDBOOK_TEMPLATE_ODT, _HANDBOOK_TEMPLATE_ANCILLARY_ODT, _HANDBOOK_TEMPLATE_NUP1x2_ODT
from pims.files.utils import listdir_filename_pattern
from pims.files.pdfs.pdfjam import PdfjamCommand
from pims.utils.pimsdateutil import handbook_pdf_startstr_to_datetime
from pims.pad.padheader import PadHeaderDict
#from pims.files.pdfs.pdftk import convert_odt2pdf

REGIMES = {
    'vib':  'Vibratory',
    'qs':   'Quasi-Steady',
}

DEFAULT_ODT_PAGE_DICT = {
    'title':        'Handbook Title',
    'subtitle':     'Qualify | Quantify',        
    'regime':       'Vibratory | Quasi-Steady',
    'category':     'Crew | Vehicle | Equipment',
    'system':       'SAMS | MAMS',
    'sensor':       'SENSOR',
    'sample_rate':  'SAMPLE_RATE',
    'cutoff':       'CUTOFF',
    'location':     'LOCATION',
    'plot_type':    'PLOT_TYPE'
}

def get_odt_filename_from_pdf_filename(fullfilename):
    pth, fname = os.path.split(fullfilename)
    bname, ext = os.path.splitext(fname)
    page_prefix = bname.split('_')[0]
    odt_name = bname.split('_offsets_')[0] + '.odt'
    odt_filename = os.path.join(pth,  odt_name)
    print odt_filename
    if os.path.exists( odt_filename ):
        return odt_filename
    else:
        return None

def get_odt_renderer(fullfilename, page_dict=DEFAULT_ODT_PAGE_DICT):
    pth, fname = os.path.split(fullfilename)
    bname, ext = os.path.splitext(fname)
    prefix = '%02d%s' % (page_dict['page'], page_dict['subtitle'])
    odt_name = os.path.join(pth, 'build', prefix + '_' + bname + '.odt')
    # Explicitly assign page_dict that contains expected names for appy/pod template substitution
    return Renderer( _HANDBOOK_TEMPLATE_ODT, page_dict, odt_name )

class MyCommand(object):
    """Run a command in a thread."""
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None

    def run(self, timeout):
        def target():
            self.process = subprocess.Popen(self.cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            out, err = self.process.communicate()
            if err:
                Exception('here is stderr...\n' + err)
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            print 'Terminating process'
            self.process.terminate()
            thread.join()
        return self.process.returncode
    
def run_timeout_cmd(command, timeout_sec=5):
    """
    Function that returns (returnCode, elapsed_sec) from given command string.
    Also has timeout feature.
    """
    cmd_obj = MyCommand(command)
    tzero = time.time()
    return_code = cmd_obj.run(timeout=timeout_sec)
    elapsed_sec = time.time() - tzero
    return return_code, elapsed_sec

class MyPdfjamCommand(PdfjamCommand):

    def __init__(self, *args, **kwargs):
        self.page = kwargs.pop('page', 0)
        self.subtitle = kwargs.pop('subtitle', 'qualify')
        super(MyPdfjamCommand, self).__init__(*args, **kwargs)

    def get_outfile(self, subdir='build'):
        prefix, ext = os.path.splitext(self.infile)
        ori = self.orient.replace('-', '')
        suffix = "_offsets_{0:0.2f}cm_{1:0.2f}cm_scale_{2:0.2f}_{3:s}.pdf".format(self.xoffset, self.yoffset, self.scale, ori)
        if subdir:
            pth = os.path.sep.join( [os.path.dirname(prefix), subdir] )
            pagenum = '%02d' % self.page
            prefix = os.path.sep.join( [pth, pagenum + self.subtitle + '_' + os.path.basename(prefix)] )
            if not os.path.exists(pth):
                mkdir_p(pth)
        return prefix + suffix
    
    def run(self, timeout_sec=10):
        return_code, elapsed_sec = run_timeout_cmd('echo -n "Start pdfjam cmd at "; date; %s; echo -n "End   pdfjam cmd at "; date' % self.command, timeout_sec)

#x is Series like this:
#path             /misc/yoda/www/plots/user/handbook/source_docs...
#filename         2015_09_08_00_00_00.000_121f03_pcss_roadmaps50...
#subtitle                                                   Qualify
#xoffset_cm                                                   -4.25
#yoffset_cm                                                       1
#scale                                                         0.86
#orient                                                   landscape
#regime                                                   Vibratory
#category                                                   Vehicle
#title                           Soyuz_42S_Thruster_Test_2015-09-08
#start                                          2015-09-08 00:00:00
#sensor                                                      121f03
#sensor_suffix                                                  NaN
#system                                                        SAMS
#sample_rate                                                    500
#cutoff                                                         200
#location                                LAB1O1, ER2, Lower Z Panel
#abbrev                                                        pcss
#notes                                                  roadmaps500
#page                                                             1

def pdfjam_func(x):
    fname = os.path.sep.join( [ x['path'], x['filename']] )
    pdfjam_cmd = MyPdfjamCommand(
        fname,
        subtitle=x['subtitle'],
        xoffset=x['xoffset_cm'],
        yoffset=x['yoffset_cm'],
        scale=x['scale'],
        orient=x['orient'],
        page=x['page'])
    print pdfjam_cmd
    pdfjam_cmd.run()

def odtrender_func(x):
    odt_page_dict = {
        'title':        x['title'],
        'subtitle':     x['subtitle'],        
        'regime':       x['regime'],
        'category':     x['category'],
        'system':       x['system'],
        'sensor':       x['sensor'],
        'sample_rate':  x['sample_rate'],
        'cutoff':       x['cutoff'],
        'location':     x['location'],
        'plot_type':    x['abbrev'],
        'page':         x['page'],
    }    
    print x
    fname = os.path.sep.join( [ x['path'], x['filename']] )
    odt_renderer = get_odt_renderer(fname, page_dict=odt_page_dict)
    odt_renderer.run()    
    
# return DataFrame read from_dir/0pdf_files.xlsx
def process_pdf_filenames_from_spreadsheet(from_dir, xlsx_basename='0pdf_files.xlsx'):
    """return DataFrame read from_dir/0pdf_files.xlsx"""
    file_name = os.path.join(from_dir, xlsx_basename)
    excel_file = pd.ExcelFile(file_name)
    df = excel_file.parse('Sheet1')
    df['page'] = range(1, len(df) + 1) # for numbering plots/pages
    df.apply(pdfjam_func, axis=1)      # produces build subdir with scale/offset PDFs
    df.apply(odtrender_func, axis=1)   # produces word-processing ODT files with fields filled
    return df

# get regime, category, and title from regex pattern match
def get_regime_category_title_from_sourcedir_rx_match(m):
    """get regime, category, and title from regex pattern match"""
    regime = REGIMES[ m.group('regime') ].title()
    category = m.group('category').title()
    title = m.group('title')
    return regime, category, title

# get subtitle (qualify or quantify) from pdf basename
def get_subtitle_from_basename(pdfbname):
    """get subtitle (qualify or quantify) from pdf basename"""
    s = 'qualify'
    return s.title()

# get fields of pattern match from pdf filename
def get_start_sensor_abbrev_notes_from_pdf_filename(pdf_filename):
    # get fields of pattern match from pdf filename
    match = re.search( re.compile(_HANDBOOKPDF_PATTERN), pdf_filename )
    if match:
        startstr = match.group('start')
        sensor = match.group('sensor')
        sensor_suffix = match.group('sensorsuffix')
        abbrev = match.group('plot_type')
        notes = match.group('notes')
    else:
        startstr = '1970_01_01'
        sensor = 'sensor'
        sensor_suffix = 'sensorsuffix'
        abbrev = 'abb'
        notes = 'notes'
    start = handbook_pdf_startstr_to_datetime(startstr)
    return start, sensor, sensor_suffix, abbrev, notes

# return system, fs, fc, and location header info based on sensor and dtm inputs
def get_header_info(sensor, suffix, dtm, dict_header):
    """return system, fs, fc, and location header info based on sensor and dtm inputs"""
    if suffix == '006':
        sensor = sensor + suffix
    if not dict_header.has_key( (sensor, dtm) ):
        ph = PadHeaderDict( sensor, dtm )
        system, sample_rate, cutoff, location = ph['System'], ph['SampleRate'], ph['CutoffFreq'], ph['Location']
        dict_header[ (sensor, dtm) ] = ( system, sample_rate, cutoff, location )
    else:
        system, sample_rate, cutoff, location = dict_header[ (sensor, dtm) ]
    return system, sample_rate, cutoff, location, dict_header
    
# write PDF files into Sheet1 of to_dir/0pdf_files.xlsx
def write_pdf_filenames_to_spreadsheet(pdf_files, to_dir, match):
    """write PDF files into to_dir/0pdf_files.xlsx"""
    
    # initialize dict to gather header info based on key of (sensor, dtm)
    header_dict = {}
    
    # to_dir should be source_dir...
    # LIKE /misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Soyuz_42S_Thruster_Test_2015-09-08
    # from source_dir, parse regime (vibratory|quasi-steady), category (crew|vehicle|equipment), and title
    regime, category, title = get_regime_category_title_from_sourcedir_rx_match(match)
    
    file_name = os.path.join(to_dir, '0pdf_files.xlsx')
    #writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    writer = pd.ExcelWriter(file_name)
    rows_list = []
    for pdf_file in pdf_files:
        pdf_bname = os.path.basename(pdf_file)
        start, sensor, sensor_suffix, abbrev, notes = get_start_sensor_abbrev_notes_from_pdf_filename(pdf_file)
        system, sample_rate, cutoff, location, header_dict =  get_header_info(sensor, sensor_suffix, start, header_dict)
        dictrow = {
            'path': os.path.dirname(pdf_file),
            'filename': pdf_bname,
            'subtitle': get_subtitle_from_basename(pdf_bname),
            'xoffset_cm': -4.25, # cm
            'yoffset_cm':  1.00, # cm
            'scale': 0.86,
            'orient': 'landscape',
            'regime': regime,
            'category': category,
            'title': title,
            'start': str(start),
            'sensor': sensor,
            'sensor_suffix': sensor_suffix,
            'system': system,
            'sample_rate': sample_rate,
            'cutoff': cutoff,
            'location': location,
            'abbrev': abbrev,
            'notes': notes,
            }
        rows_list.append(dictrow)
    df = pd.DataFrame(data=rows_list, index=None,
                      columns=[
                        'path',
                        'filename',
                        'subtitle',
                        'xoffset_cm',
                        'yoffset_cm',
                        'scale',
                        'orient',
                        'regime',
                        'category',
                        'title',
                        'start',
                        'sensor',
                        'sensor_suffix',
                        'system',
                        'sample_rate',
                        'cutoff',
                        'location',
                        'abbrev',
                        'notes'])
    df.to_excel(writer, sheet_name='Sheet1', index=False)

def alert(msg, title='ALERT'):
    label = gtk.Label(msg)
    dialog = gtk.Dialog(title,
                        None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        buttons=(gtk.STOCK_OK, 1, "Show Log", 2))
    dialog.vbox.pack_start(label)
    label.show()
    response = dialog.run()
    dialog.destroy()
    return response # 1 for "OK", 2 for "Show Log", otherwise -4 (for X)

def OLDalert(msg):
    """Show a dialog with a simple message."""
    dialog = gtk.MessageDialog()
    dialog.set_markup(msg)
    dialog.run()

def do_build(pth):
    """Create interim hb entry build products."""
    hbe = HandbookEntry( source_dir=pth )
    if not hbe.will_clobber():
        err_msg = hbe.process_pages()
        return err_msg or 'pre-processed %d hb pdf files' % len(hbe.pdf_files), hbe
    else:
        return 'ABORT PAGE PROCESSING: hb pdf filename conflict on yoda', hbe

def finalize(pth):
    """Finalize handbook page."""
    hbe = HandbookEntry(source_dir=pth)
    if not hbe.will_clobber():
        err_msg = hbe.process_build()
        return err_msg or 'did pdftk post-processing', hbe
    else:
        return 'ABORT BUILD: hb pdf filename conflict on yoda', hbe

def show_log(log_file):
    os.system('subl %s' % log_file)

def OLDmain(curdir):

    # Strip off uri prefix
    if curdir.startswith('file:///'):
        curdir = curdir[7:]

    # Verify curdir matches pattern (this works even in build subdir, which is a good thing)
    match = re.search( re.compile(_HANDBOOKDIR_PATTERN), curdir )

    ########################################################################################
    # this is where we do branching based on if we are in "build" subdir or source_dir
    if match:
        #alert( match.string )
        if not match.string.endswith('build'):
            #------------------------------------------------------
            #alert( 'WE ARE IN SOURCE_DIR, SO DO INITIAL BUILD')
            msg, hbe = do_build(curdir)
        else:
            #------------------------------------------------------
            #alert( 'WE ARE IN BUILD DIRECTORY, SO FINALIZE')
            msg, hbe = finalize( os.path.dirname(curdir) )
    else:
        msg = 'ABORT: ignore non-hb dir'
        hbe = None

    response = alert( '%s' % msg ) # 1 for "OK", 2 for "Show Log", otherwise -4 (for eXited out)
    if match and response == 2 and hbe:
        hbe.log.process.info('  *** CLOSE SUBLIME TO FINALIZE GTK DIALOG ***')
        show_log(hbe.log.file)
    
def main(curdir):

    # Strip off uri prefix
    if curdir.startswith('file:///'):
        curdir = curdir[7:]

    # Verify curdir matches pattern (this works even in build subdir, which is a good thing)
    match = re.search( re.compile(_HANDBOOKDIR_PATTERN), curdir )

    ########################################################################################
    # this is where we do branching based on if we are in "build" subdir or source_dir
    if match:
    
        # FIXME this bname part is better if part of regexp match/parse
        #       but how to account for subdir levels at/below build level
        bname = os.path.basename(curdir)
        if bname.startswith('hb_vib_') or bname.startswith('hb_qs_'):
            #------------------------------------------------------
            # We are in main parent source dir
            #------------------------------------------------------
            pdf_files = listdir_filename_pattern(curdir, '.*\.pdf$')
            write_pdf_filenames_to_spreadsheet(pdf_files, curdir, match)
            msg = 'wrote %d PDF filenames into pdf_files.xlsx' % len(pdf_files)
            df = process_pdf_filenames_from_spreadsheet(curdir)
        elif match.string.endswith('build'):
            #------------------------------------------------------
            # We are in build subdir
            #------------------------------------------------------
            out_pth = os.path.join(curdir, 'final')
            mkdir_p(out_pth)
            pdf_files = listdir_filename_pattern(curdir, '.*_offsets_.*_scale_.*\.pdf$')
            for pdf_file in pdf_files:
                odt_filename = get_odt_filename_from_pdf_filename(pdf_file)
                if not odt_filename:
                    print 'no odt file to match %s' % pdf_file
                else:
                    # convert odt to pdf
                    cmd = 'unoconv %s' % odt_filename
                    mc = MyCommand(cmd)
                    mc.run(9)
                    # overlay two PDF's to get final
                    fg_pdf = pdf_file
                    bg_pdf = odt_filename.replace('.odt', '.pdf')
                    out_name = os.path.basename(bg_pdf).replace('.pdf', '_final.pdf')
                    out_pdf = os.path.join(out_pth, out_name)
                    cmd = 'pdftk %s background %s output %s' % (fg_pdf, bg_pdf, out_pdf)
                    mc = MyCommand(cmd)
                    mc.run(9)
            msg = 'done with build using %d PDF files' % len(pdf_files)
        else:
            msg = 'ABORT: ignore unknown hb subdir'
    else:
        msg = 'ABORT: ignore non-hb dir'

    response = alert( '%s' % msg ) # 1 for "OK", 2 for "Show Log", otherwise -4 (for eXited out)


#convert_odt2pdf('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Soyuz_42S_Thruster_Test_2015-09-08/build/01Qualify_2015_09_08_00_00_00.000_121f03_pcss_roadmaps500.odt')
#raise SystemExit

main('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Soyuz_42S_Thruster_Test_2015-09-08/build')
raise SystemExit

#odt_renderer = get_odt_renderer('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Soyuz_42S_Thruster_Test_2015-09-08/build/01qualify_2015_09_08_00_00_00.000_121f03_pcss_roadmaps500_offsets_-4.25cm_1.00cm_scale_0.86_landscape.pdf')
#odt_renderer.run()
#raise SystemExit

if __name__ == "__main__":
    # Get nautilus current uri
    curdir = os.environ.get('NAUTILUS_SCRIPT_CURRENT_URI', os.curdir)
    main(curdir)
