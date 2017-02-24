#!/usr/bin/env python

import os
from collections import OrderedDict
from pims.files.pdfs.pdfjam import PdfjamCommand
from pims.files.pdfs.pdftk import convert_odt2pdf, PdftkCommand
from pims.files.pdfs.pdfjam import CpdfScalePageCommand, CpdfStampCommand
from pims.files.utils import listdir_filename_pattern
from appy.pod.renderer import Renderer

# FIXME see about totally avoiding ODT template and using cpdf for header and footer placeholder text, etc.

# FIXME see about why some pages (all portrait, 3-panel subplots get scaled differently)


# create PDF output file rendered from ODT template that has conditional text (appy.pod) placeholders
def render_pdf_background_from_odt_template(input_odt_template_file, header_dict, page_num, total_num, appendix_letter, fig_num, caption, pdf_out_dir):
    """create PDF output file rendered from ODT template that has conditional text (appy.pod) placeholders"""

    # add specifics for this page to dict
    page_dict = header_dict
    page_dict['PN'] = page_num
    page_dict['TN'] = total_num
    page_dict['AL'] = appendix_letter
    page_dict['FN'] = fig_num
    page_dict['Caption'] = caption
    
    # now page_dict contains all expected names for appy/pod template substitution   
    
    # create output filename
    pagestr = '_page%03d' % page_num
    tmp_name = 'appendix' + appendix_letter.upper() + pagestr + '.odt'
    tmp_odt_file = os.path.join(pdf_out_dir, tmp_name)

    # render odt
    odt_renderer = Renderer( input_odt_template_file, page_dict, tmp_odt_file )
    odt_renderer.run()
    
    # convert to pdf
    convert_odt2pdf(tmp_odt_file)    

    # return PDF fullfilename
    return tmp_odt_file.replace('.odt', '.pdf')


# return list of PDF files for this drop number (i.e. drop dir)
def get_analysis_template_plot_pdfs(drop_num):
    """return list of PDF files for this drop number (i.e. drop dir)"""
    dirpath = '/misc/yoda/www/plots/user/urban/sams_zgf_2016/publication/drop%d' % drop_num
    fname_pat = 'drop.*\.pdf'
    tmp_list = listdir_filename_pattern(dirpath, fname_pat)
    # filter tmp_list to ignore previous run's _cpdf_ filenames
    return [ x for x in tmp_list if "_cpdf_" not in x ]


# return filename of scaled plot PDF file
def scale_plot_pdf_file(plot_pdf_file, xscale=0.8, yscale=0.8):
    """return filename of scaled plot PDF file"""
    cmd = CpdfScalePageCommand(plot_pdf_file, xscale=xscale, yscale=yscale)
    cmd.run()
    return cmd.outfile


# return filename of newly created background (header, page number, title, etc.)
def create_background_onto_file(page_num, total_num, appendix_letter, fig_num, caption, pdf_out_dir, title, subtitle, mon_year):
    """return filename of newly created background (header, page number, title, etc.)"""
    # trusted template ODT file
    odt_template_file = '/home/pims/Documents/appendix_plots_and_figures_template.odt'
    
    # these dict items apply to all pages (header lines) in appendices
    header_dict = {'title': title, 'subtitle': subtitle, 'mon_year': mon_year} # applies to all pages
    return render_pdf_background_from_odt_template(odt_template_file, header_dict, page_num, total_num, appendix_letter, fig_num, caption, pdf_out_dir)    


def do_drop(drop_num):
    appendix_letter = DROP_MAP[drop_num]
    print 'Working on Drop %d for Appendix %s' % (drop_num, appendix_letter)
    
    # get pdf files for this drop
    drop_files = get_analysis_template_plot_pdfs(drop_num)


def three_appendices_at_once():
    FIRST_ATP_APP_PAGE_NUM        = 27 # 1st page num from Word document's 1st "Analysis Template..." appendix
    INTERIM_PAGES_ADDED           =  2 # one each for Drop 3's and Drop 4's first (non-fig) page
    NUM_PAGES_AFTER_LAST_ATP_PAGE =  3 # how many pages in Word doc come after last "Analysis Template..." appendix page
    DROP_MAP = {
    #DROP_NUM   APPENDIX
        2:      'C',
        3:      'D',
        4:      'E',
    }

    # these dict items apply to all pages (header lines) in appendices
    title = 'Analysis of SAMS Measurements on M-Vehicle in Zero Gravity Research Facility for Characterization Drops from January 20 to February 3, 2016'
    subtitle = 'SAMS-DOC-013'
    mon_year = 'September, 2016'
    
    # get list of analysis template plot PDFs
    pdf_files = []
    for drop_num in [2, 3, 4]:
        drop_files = get_analysis_template_plot_pdfs(drop_num)
        pdf_files.extend(drop_files)

    #print pdf_files[0:3]
    #print pdf_files[-2:]
    #raise SystemExit

    # get list of captions; FIXME as this naively assumes one-to-one match with pdf_files gotten above
    captions_file = '/misc/yoda/www/plots/user/urban/sams_zgf_2016/publication/captions_for_analysis_template_plots.txt'
    with open(captions_file) as f:
        caption_lines = f.readlines()
    captions = [x.strip('\n') for x in caption_lines]

    if len(pdf_files) != len(captions):
        raise Exception('Abort: the number of PDFs found does not match the number of captions.')

    total_num = FIRST_ATP_APP_PAGE_NUM + len(captions) + INTERIM_PAGES_ADDED + NUM_PAGES_AFTER_LAST_ATP_PAGE
    top_offset = 99 # used by CpdfStampCommand to offset scaled plot from top of page during stamping
        
    # for each plot PDF file, scale it and stamp on background PDF with header, page number, page total, etc.
    count = 0
    page_num = FIRST_ATP_APP_PAGE_NUM
    old_drop = None
    for tup in zip(pdf_files, captions):
        pdf_file = tup[0]
        caption = tup[1]
        count += 1
        
        drop_num = int(os.path.basename(pdf_file)[4])
        appendix_letter = DROP_MAP[drop_num]

        # FIXME what is better, pythonic way to get page_num reset for each new appendix
        if old_drop and drop_num != old_drop:
            page_num += 1 # advance to allow for first Appendix (non-fig) page
            count = 1     # reset count within appendix
        
        # scale plot PDF (portrait) file and return scaled filename
        scaled_plot_pdf_file = scale_plot_pdf_file(pdf_file)
        
        # specifics for this page
        fig_num = count
        page_num += 1
               
        # FIXME use temp files and do clean-up of those
        
        # FIXME see about quieting down the logging output crap
        
        pdf_out_dir = '/tmp'
        onto_file = create_background_onto_file(page_num, total_num, appendix_letter, fig_num, caption, pdf_out_dir, title, subtitle, mon_year)

        cmd = CpdfStampCommand(scaled_plot_pdf_file, top_offset, onto_file)
        cmd.run()

        print 'p.%02d Fig.%s-%02d %s\n%s' % (page_num, appendix_letter, count, os.path.basename(pdf_file), cmd.outfile)
        
        old_drop = drop_num

    print 'NOW DO pdfjoin appendix*_cpdf_stamp-on_99.pdf IN /tmp DIR'


def one_appendix(drop_num, appendix_letter, fig1_page_num, total_doc_pages, title, subtitle, mon_year):    
    # get list of analysis template plot PDFs
    pdf_files = get_analysis_template_plot_pdfs(drop_num)
    print 'Found %d PDF files for Drop %d in Appendix %s' % (len(pdf_files), drop_num, appendix_letter)

    # get list of captions; FIXME as this naively assumes one-to-one match with pdf_files gotten above
    captions_file = '/misc/yoda/www/plots/user/urban/sams_zgf_2016/publication/captions_for_analysis_template_plots_appendix_%s.txt' % appendix_letter.lower()
    with open(captions_file) as f:
        caption_lines = f.readlines()
    captions = [x.strip('\n') for x in caption_lines]

    if len(pdf_files) != len(captions):
        raise Exception('Abort: the number of PDFs found does not match the number of captions.')

    top_offset = 99 # used by CpdfStampCommand to offset scaled plot from top of page during stamping
        
    # for each plot PDF file, scale it and stamp on background PDF with header, page number, page total, etc.
    fig_num = 1
    page_num = fig1_page_num
    for tup in zip(pdf_files, captions):
        pdf_file = tup[0]
        caption = tup[1]
        
        # scale plot PDF (portrait) file and return scaled filename
        scaled_plot_pdf_file = scale_plot_pdf_file(pdf_file)
        
        # FIXME use temp files and do clean-up of those       
        # FIXME see about quieting down the logging output crap
        
        pdf_out_dir = '/tmp'
        onto_file = create_background_onto_file(page_num, total_doc_pages, appendix_letter, fig_num, caption, pdf_out_dir, title, subtitle, mon_year)

        cmd = CpdfStampCommand(scaled_plot_pdf_file, top_offset, onto_file)
        cmd.run()

        print 'p.%02d Fig.%s-%02d %s\n%s' % (page_num, appendix_letter, fig_num, os.path.basename(pdf_file), cmd.outfile)
        
        fig_num += 1
        page_num += 1
        
    print 'IN /tmp DIR, NOW DO FOLLOWING:'
    print 'pdfjoin appendixC_*_cpdf_stamp-on_99.pdf -o /tmp/appendixC.pdf'
    print 'pdfjoin appendixD_*_cpdf_stamp-on_99.pdf -o /tmp/appendixD.pdf'
    print 'pdfjoin appendixE_*_cpdf_stamp-on_99.pdf -o /tmp/appendixE.pdf'
    print 'THEN, THIS:'
    print '/usr/bin/gs -o gs-repaired-appendixC.pdf -dPDFSETTINGS=/prepress -sDEVICE=pdfwrite appendixC.pdf'
    print '/usr/bin/gs -o gs-repaired-appendixD.pdf -dPDFSETTINGS=/prepress -sDEVICE=pdfwrite appendixD.pdf'
    print '/usr/bin/gs -o gs-repaired-appendixE.pdf -dPDFSETTINGS=/prepress -sDEVICE=pdfwrite appendixE.pdf'

    
if __name__ == "__main__":
    
    #three_appendices_at_once()
    
    # FIXME -- modify these (maybe just mon_year and total_doc_pages)
    # these dict items apply to all pages (header lines) in all appendices
    title = 'Analysis of SAMS Measurements on M-Vehicle in Zero Gravity Research Facility for Characterization Drops from January 20 to February 3, 2016'
    subtitle = 'SAMS-DOC-013'
    mon_year = 'February, 2017'
    total_doc_pages = 119
    
    # FIXME -- modify these (in Word, try Ctrl+G and go to page nums shown and verify those are first fig pages)    
    # Check your Word doc to see how these value should be set:
    drop_info = {
    # DROP   APPENDIX    FIRST_FIG_PAGE_NUM
        2:  ('C',        28),
        3:  ('D',        57),
        4:  ('E',        86),
    }
    for drop_num, tup in drop_info.iteritems():
        appendix_letter, fig1_page_num = tup[0], tup[1]
        one_appendix(drop_num, appendix_letter, fig1_page_num, total_doc_pages, title, subtitle, mon_year)
        print drop_num, appendix_letter, fig1_page_num, "done"   