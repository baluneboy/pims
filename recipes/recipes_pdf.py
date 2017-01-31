#!/usr/bin/env python

import sys
from pyPdf import PdfFileWriter, PdfFileReader

def extract_every_nth_page(n, infile, outfile):
    inputf = PdfFileReader(file(infile, "rb"))
    n_pages = inputf.getNumPages()
    output = PdfFileWriter()
    for p in range(0, n_pages, n):    
        output.addPage(inputf.getPage(p))
        print 'added page %d' % p
    output_stream = file(outfile, "wb")
    output.write(output_stream)
    print 'wrote %s' % outfile        

if __name__ == '__main__':
    #infile =  '/media/F50_PIVOT/pims/crew_exercise/cevis_protein_crystal_growth/samsf04_per_minute_int_rms.pdf'
    #outfile = '/media/F50_PIVOT/pims/crew_exercise/cevis_protein_crystal_growth/samsf04_per_minute_int_rms_total.pdf'
    #infile = '/media/F50_PIVOT/pims/handbook/cevis_exercise/email_to_Protein_Crystal_Growers/connor_cevis_stat_compare_from1minuteRMS_121f04.pdf'
    #outfile = '/media/F50_PIVOT/pims/handbook/cevis_exercise/email_to_Protein_Crystal_Growers/trash.pdf'
    infile = '/media/F50_PIVOT/pims/handbook/cevis_exercise/email_to_Protein_Crystal_Growers/samsf04_per_minute_int_rms_total_set1.pdf'
    outfile = '/media/F50_PIVOT/pims/handbook/cevis_exercise/email_to_Protein_Crystal_Growers/overlay.pdf'
    
    extract_every_nth_page(444, infile, outfile)
    sys.exit(0)