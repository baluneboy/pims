#!/usr/bin/env python

from pims.files.pdfs.pdfjam import PdfjamCommand
from pims.files.pdfs.pdftk import convert_odt2pdf, PdftkCommand
from appy.pod.renderer import Renderer

# this routine assumes you renamed ODT like so (notice _fg.odt at end)
# '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Cygnus_Capture_Install/testing/4quantify_2013_09_28_16_radgse_roadmapnup1x2_fg.odt'

# this routine assumes you modified template (temporarily) to show scale, xoffset, and yoffset values on the page
modified_odt_template = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Cygnus_Capture_Install/testing/handbook_template_nup1x2_mod.odt'

fullsize_pdf = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Cygnus_Capture_Install/testing/4quantify_2013_09_28_16_radgse_roadmapnup1x2.pdf'

#pdftk unoconv_odtfile.pdf background unoconv_odtfile_offset_-4.25cm_1cm_scale_0.88.pdf output updir/hb_regime_category_title.pdf

#scales =    [x/100.0 for x in range(74,78,1)]
#xoffsets =  [x/100.0 for x in range(-325,-275,25)]
#yoffsets =  [x/100.0 for x in range(20,80,10)]

#scales =    [x/100.0 for x in range(86, 89, 1)]
#xoffsets =  [x/100.0 for x in range(-435,-415, 10)]
#yoffsets =  [1.25, 1.00, 0.75]

scales =    [74/100.0]
xoffsets =  [-340/100.0]
yoffsets =  [0.0]

for scale in scales:
    for xoffset in xoffsets:
        for yoffset in yoffsets:
            
            pdfjam_cmd = PdfjamCommand(fullsize_pdf, xoffset=xoffset, yoffset=yoffset, scale=scale, log=None)
            pdfjam_cmd.run()
            
            offset_pdfname = pdfjam_cmd.outfile
            odt_name = offset_pdfname.replace('.pdf', '_fg.odt')
            
            # Explicitly assign page_dict that contains expected names for appy/pod template substitution
            page_dict = {'scale': scale, 'xoffset': xoffset, 'yoffset': yoffset}
            odt_renderer = Renderer( modified_odt_template, page_dict, odt_name )
            odt_renderer.run()
            
            convert_odt2pdf(odt_name)
            
            pdftk_cmd = PdftkCommand(odt_name.replace('.odt', '.pdf'), offset_pdfname, offset_pdfname.replace('.pdf', '_pdftk.pdf'))
            pdftk_cmd.run()
