#!/usr/bin/env python

import os
import re
import gtk
import time
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

#------------------------------------------------------------------------------------------
# Map abbrev key to tuple of descriptive text, Qualify or Quantify, and offsets/scale list
#------------------------------------------------------------------------------------------
PLOT_ABBREV_MAP = {
    'spgs': ('Spectrogram',                         'Qualify',  [-4.85, 1.25, 0.76], 'landscape'),
    'pcss': ('PSD/Time Histogram',                  'Qualify',  [-4.85, 1.25, 0.76], 'landscape'),
    'gvt3': ('XYZ Accel. vs. Time',                 'Quantify', [-4.85, 1.25, 0.76], 'landscape'),
    'iav3': ('Int. Avg. Accel. vs. Time',           'Quantify', [-4.85, 1.25, 0.76], 'landscape'),
    'rvt3': ('XYZ RMS Accel. vs. Time',             'Quantify', [-4.85, 1.25, 0.76], 'landscape'),
    'rvts': ('RMS Accel. vs. Time',                 'Quantify', [-4.85, 1.25, 0.76], 'landscape'),
    'psd3': ('XYZ Power Spectral Density',          'Quantify', [-4.85, 1.25, 0.76], 'landscape'),
    'gvtm': ('Accel. Vector Mag. vs. Time',         'Quantify', [-4.85, 1.25, 0.76], 'landscape'),
    'immm': ('Accel. Vector Mag. Min/Max vs. Time', 'Quantify', [-4.85, 1.25, 0.76], 'landscape'),
}

# name of PDF files spreadsheet to use
_PDF_FILES_XLSX = '0pdf_files.xlsx'

# regimes from shortened string
REGIMES = {
    'vib':  'Vibratory',
    'qs':   'Quasi-Steady',
}

# page dict values that serve as placeholders
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

# return odt_filename derived from pdf full filename
def get_odt_filename_from_pdf_filename(fullfilename):
    """return odt_filename derived from pdf full filename"""
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

# return Rendered object for odt files based on pdf full filename
def get_odt_renderer(fullfilename, page_dict=DEFAULT_ODT_PAGE_DICT):
    """return Rendered object for odt files based on pdf full filename"""
    pth, fname = os.path.split(fullfilename)
    bname, ext = os.path.splitext(fname)
    prefix = '%02d%s' % (page_dict['page'], page_dict['subtitle'])
    odt_name = os.path.join(pth, 'build', prefix + '_' + bname + '.odt')
    # Explicitly assign page_dict that contains expected names for appy/pod template substitution
    return Renderer( _HANDBOOK_TEMPLATE_ODT, page_dict, odt_name )

# handle subprocess commands with a timeout
class MyCommand(object):
    """handle subprocess commands with a timeout"""
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

# return (return_code, elapsed_sec) from given command string    
def run_timeout_cmd(command, timeout_sec=5):
    """
    return (return_code, elapsed_sec) from given command string;
    also has timeout feature with default value of 5 seconds
    """
    cmd_obj = MyCommand(command)
    tzero = time.time()
    return_code = cmd_obj.run(timeout=timeout_sec)
    elapsed_sec = time.time() - tzero
    return return_code, elapsed_sec

# handle pdfjam command
class MyPdfjamCommand(PdfjamCommand):
    """handle pdfjam command"""
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

# create and run pdfjam command using dataframe Series object fields
def pdfjam_func(x):
    """create and run pdfjam command using dataframe Series object fields"""
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

# create and run odt renderer command using dataframe Series object fields
def odtrender_func(x):
    """create and run odt renderer command using dataframe Series object fields"""
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
        'plot_type':    x['plot_type'],
        'page':         x['page'],
    }    
    #print x
    fname = os.path.sep.join( [ x['path'], x['filename']] )
    odt_renderer = get_odt_renderer(fname, page_dict=odt_page_dict)
    odt_renderer.run()    
    
# return DataFrame read from_dir/0pdf_files.xlsx
def process_pdf_filenames_from_spreadsheet(from_dir, xlsx_basename=_PDF_FILES_XLSX):
    """return DataFrame read from_dir/0pdf_files.xlsx"""
    file_name = os.path.join(from_dir, xlsx_basename)
    excel_file = pd.ExcelFile(file_name)
    df = excel_file.parse('Sheet1')
    df['page'] = range(1, len(df) + 1) # for numbering plots/pages
    df.apply(pdfjam_func, axis=1)      # produces build subdir with scale/offset PDFs
    df.apply(odtrender_func, axis=1)   # produces word-processing ODT files with fields filled
    return df

# get regime, category, and title from regex pattern match of pdf filename
def get_regime_category_title_from_sourcedir_rx_match(m):
    """get regime, category, and title from regex pattern match of pdf filename"""
    regime = REGIMES[ m.group('regime') ].title()
    category = m.group('category').title()
    title = m.group('title').replace('_', ' ')
    return regime, category, title

# get fields of pattern match from pdf filename (startstr, sensor, suffix, plot abbrev)
def get_start_sensor_abbrev_notes_from_pdf_filename(pdf_filename):
    """get fields of pattern match from pdf filename (startstr, sensor, suffix, plot abbrev)"""
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

# map plot abbreviation (like spgs) to plot type text, subtitle (Qualify or Quantify), offsets and scale
def map_abbrev_info(abbrev):
    """map plot abbreviation (like spgs) to plot type text, subtitle (Qualify or Quantify), offsets and scale"""
    
    if PLOT_ABBREV_MAP.has_key(abbrev):
        plot_type, subtitle, offsets_scale, orientation = PLOT_ABBREV_MAP[abbrev]
    else:
        plot_type, subtitle, offsets_scale, orientation = abbrev, 'NoMatch', [-4.85, 1.25, 0.76], 'landscape'
    return plot_type, subtitle, offsets_scale, orientation
        
# write PDF files into Sheet1 of to_dir/0pdf_files.xlsx
def write_pdf_filenames_to_spreadsheet(pdf_files, to_dir, match):
    """write PDF files into to_dir/0pdf_files.xlsx"""
    
    # initialize dict to gather header info based on key of (sensor, dtm)
    header_dict = {}
    
    # to_dir should be source_dir...
    # LIKE /misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Soyuz_42S_Thruster_Test_2015-09-08
    # from source_dir, parse regime (vibratory|quasi-steady), category (crew|vehicle|equipment), and title
    regime, category, title = get_regime_category_title_from_sourcedir_rx_match(match)
    
    file_name = os.path.join(to_dir, _PDF_FILES_XLSX)
    #writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    writer = pd.ExcelWriter(file_name)
    rows_list = []
    for pdf_file in pdf_files:
        
        pdf_bname = os.path.basename(pdf_file)
        start, sensor, sensor_suffix, abbrev, notes = get_start_sensor_abbrev_notes_from_pdf_filename(pdf_file)
        system, sample_rate, cutoff, location, header_dict =  get_header_info(sensor, sensor_suffix, start, header_dict)
    
        #-------------------------------------------
        # map from abbrev to plot type and subtitle
        #-------------------------------------------
        plot_type, subtitle, offsets_scale, orientation = map_abbrev_info(abbrev)
        xoffset = offsets_scale[0]
        yoffset = offsets_scale[1]
        scale = offsets_scale[2]
        
        dictrow = {
            'path': os.path.dirname(pdf_file),
            'filename': pdf_bname,
            'subtitle': subtitle,
            'xoffset_cm': xoffset, # cm
            'yoffset_cm': yoffset, # cm
            'scale': scale,
            'orient': orientation,
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
            'plot_type': plot_type,
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
                        'plot_type',
                        'notes'])
    
    df.to_excel(writer, sheet_name='Sheet1', index=False)

# show alert dialog
def alert(msg, title='ALERT'):
    """show alert dialog"""
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

def OLDdo_build(pth):
    """Create interim hb entry build products."""
    hbe = HandbookEntry( source_dir=pth )
    if not hbe.will_clobber():
        err_msg = hbe.process_pages()
        return err_msg or 'pre-processed %d hb pdf files' % len(hbe.pdf_files), hbe
    else:
        return 'ABORT PAGE PROCESSING: hb pdf filename conflict on yoda', hbe

def OLDfinalize(pth):
    """Finalize handbook page."""
    hbe = HandbookEntry(source_dir=pth)
    if not hbe.will_clobber():
        err_msg = hbe.process_build()
        return err_msg or 'did pdftk post-processing', hbe
    else:
        return 'ABORT BUILD: hb pdf filename conflict on yoda', hbe

def OLDshow_log(log_file):
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

# print list of hb pdf files on yoda
def show_yodahb_list(pdf_filename):
    """print list of hb pdf files on yoda"""
    pat = '.*/hb_(?P<regime>.*?)_(?P<category>.*?)_(?P<title>.*)\.pdf$'
    match = re.search( re.compile(pat), pdf_filename )
    if match:
        regime = match.group('regime')
        category = match.group('category')
        title = match.group('title')
    else:
        regime = 'REGIME'
        category = 'CATEGORY'
        title = 'TITLE'
    return regime, category, title
    
#regime, category, title = show_yodahb_list('/home/pims/yodahb/hb_vib_vehicle_upa_rev_2011_12_22.pdf')
#print regime
#print category
#print title
#raise SystemExit

# take handbooking action from nautilus script based on curdir
def main(curdir):
    """take handbooking action from nautilus script based on curdir"""
    
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
            
            hb_pdf = os.path.join(curdir, bname + '.pdf')
            if os.path.exists(hb_pdf):
                # hb page PDF exists here already, so abort
                msg = '%s.pdf exists already, so abort' % bname
            elif os.path.exists(os.path.join(curdir, _PDF_FILES_XLSX)):
                # got spreadsheet, so process it
                df = process_pdf_filenames_from_spreadsheet(curdir)
                msg = 'created build subdir using %s' % _PDF_FILES_XLSX
            else:
                # initially, no spreadsheet, so create it
                pdf_files = listdir_filename_pattern(curdir, '.*\.pdf$')
                write_pdf_filenames_to_spreadsheet(pdf_files, curdir, match)
                msg = 'redo ORDERING if needed, now is time to modify %s' % _PDF_FILES_XLSX
                
        elif match.string.endswith('build'):
            
            #------------------------------------------------------
            # We are in build subdir
            #------------------------------------------------------
            
            unjoined_path = os.path.join(curdir, 'unjoined')
            if os.path.exists(unjoined_path):
                msg = 'unjoined subdir exists already, so abort'
            else:
                msg = ''
                mkdir_p(unjoined_path)
                pdf_files = listdir_filename_pattern(curdir, '.*_offsets_.*_scale_.*\.pdf$')
                # iterate over scale/offset PDFs to get odt filename, convert that to pdf, & produce final pdf
                for pdf_file in pdf_files:
                    odt_filename = get_odt_filename_from_pdf_filename(pdf_file)
                    if not odt_filename:
                        msg += 'unable to  odt file to match %s\n' % pdf_file
                    else:
                        ##############################################
                        ### convert odt to pdf ###
                        cmd = 'unoconv %s' % odt_filename
                        mc = MyCommand(cmd)
                        mc.run(9) # 9-sec timeout
                        ##############################################
                        ### overlay two PDF's to get one final PDF ###
                        fg_pdf = pdf_file
                        bg_pdf = odt_filename.replace('.odt', '.pdf')
                        out_name = os.path.basename(bg_pdf).replace('.pdf', '_final.pdf')
                        out_pdf = os.path.join(unjoined_path, out_name)
                        cmd = 'pdftk %s background %s output %s' % (fg_pdf, bg_pdf, out_pdf)
                        mc = MyCommand(cmd)
                        mc.run(9) # 9-sec timeout
                if len(msg) == 0:
                    msg = 'done with build and we used all %d PDF files' % len(pdf_files)
                else:
                    msg += 'done with build BUT WE DID NOT USE ALL %d PDF FILES' % len(pdf_files)
                    
        elif match.string.endswith('build/unjoined'):
            
            #------------------------------------------------------
            # We are in build/unjoined subdir
            #------------------------------------------------------
            
            # now join the unjoined PDFs
            # hb_path = curdir.rstrip('build/unjoined') # << WHY DOES THIS NOT ALWAYS WORK
            hb_path = os.path.sep.join( curdir.split(os.path.sep)[:-2] )
            junk, hb_name = os.path.split(hb_path)
            hb_pdf = os.path.join(hb_path, hb_name + '.pdf')
            if os.path.exists(hb_pdf):
                msg = '%s.pdf already exists in parent source dir, so abort' % hb_name
            else:
                print curdir
                print hb_path
                print hb_name
                print hb_pdf
                cmd = '/usr/bin/pdfjam --landscape *.pdf -o %s' % hb_pdf
                mc = MyCommand(cmd)
                retcode = mc.run(15) # 15-sec timeout
                print retcode
                msg = 'check parent source dir for hb_pdf'
        else:
            
            #------------------------------------------------------
            # We are in unknown hb subdir
            #------------------------------------------------------
                        
            msg = 'ABORT: ignore unknown hb subdir'
    
    else:
        
        msg = 'ABORT: ignore non-hb dir'

    response = alert( '%s' % msg ) # 1 for "OK", 2 for "Show Log", otherwise -4 (for eXited out)

#convert_odt2pdf('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Soyuz_42S_Thruster_Test_2015-09-08/build/01Qualify_2015_09_08_00_00_00.000_121f03_pcss_roadmaps500.odt')
#raise SystemExit

#main('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_SARJ_Sinusoidal_Correlation/build/unjoined')
#main('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_MSG_Troubleshooting_and_Repair')
#main('/misc/yoda/www/plots/user/handbook/source_docs/hb_qs_vehicle_25-Nov-2015_Progress_61P_Reboost')
#main('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_2015_Cygnus-4_Capture_and_Install')
#main('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Soyuz_46S_Docking_19-Mar-2016')

#pdf_file = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_Manufacturing_Device_2016-06-09/2016_06_09_08_00_00_121f04_spgs_overlay_current_mfg_device.pdf'
#pdf_file = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_Manufacturing_Device_2016-06-09/2016_06_09_08_00_00_121f04_spgs_mfg_device.pdf'
#start, sensor, sensor_suffix, abbrev, notes = get_start_sensor_abbrev_notes_from_pdf_filename(pdf_file)
#print start
#print sensor
#print sensor_suffix
#print abbrev
#print notes
#system, sample_rate, cutoff, location, header_dict =  get_header_info(sensor, sensor_suffix, start, {})
#print system
#print sample_rate
#print cutoff
#print location
#print header_dict
#raise SystemExit

#main('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Progress_67P_Reboost_2017-08-09')
#raise SystemExit

#pdf_files = ['/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Progress_67P_Reboost_2017-08-09/2017_08_09_11_00_00_es05_gvtx_inverted_progress_67p_reboost.pdf',
#    '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Progress_67P_Reboost_2017-08-09/2017_08_09_11_00_00_es05_gvtx_inverted_progress_67p_reboost_zoom_with_iavx.pdf',
#    '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Progress_67P_Reboost_2017-08-09/2017_08_09_11_00_00_es05_spgs_progress_67p_reboost.pdf'];
#for pdf_file in pdf_files:
#    start, sensor, sensor_suffix, abbrev, notes = get_start_sensor_abbrev_notes_from_pdf_filename(pdf_file)
#    print start, sensor, sensor_suffix, abbrev, notes
#    system, sample_rate, cutoff, location, header_dict =  get_header_info(sensor, sensor_suffix, start, {})
#    print system, sample_rate, cutoff, location, header_dict
#raise SystemExit

#odt_renderer = get_odt_renderer('/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Soyuz_42S_Thruster_Test_2015-09-08/build/01qualify_2015_09_08_00_00_00.000_121f03_pcss_roadmaps500_offsets_-4.25cm_1.00cm_scale_0.86_landscape.pdf')
#odt_renderer.run()
#raise SystemExit

if __name__ == "__main__":
    # Get nautilus current uri and take action in main func
    curdir = os.environ.get('NAUTILUS_SCRIPT_CURRENT_URI', os.curdir)
    main(curdir)
