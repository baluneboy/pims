#!/usr/bin/env python

# gimp -i -b '(python-fu-batchmyscript RUN-NONINTERACTIVE "*.gif" "/tmp/pics" 512 512)' -b '(gimp-quit 0)'

import os, re, glob
from gimpfu import *
from gimpenums import *

def _rename(inputfile, prefix='flipscaled_'):
    dirpath = os.path.dirname(inputfile)
    bname = os.path.basename(inputfile)
    return os.path.join( dirpath, prefix + bname)    
    
# the batch script
def pybatch(globpattern,  source,  scale_w,  scale_h) :
    pdb.gimp_message("Globbing: " + source + os.sep + globpattern)
    glob_result = pdb.file_glob(source + os.sep + globpattern,  1)
    filecount = glob_result[0]
    for f in glob_result[1]:
        imagefile = f
        #dirpath = os.path.dirname(imagefile)
        #bname = os.path.basename(imagefile)
        #outfile = os.path.join( dirpath, 'flipscaled_' + bname)
        outfile = _rename(imagefile)
        pdb.gimp_message("Opening: " + imagefile)
        try:
           image = pdb.gimp_file_load(imagefile,  imagefile)
           #pdb.gimp_display_new(image)
           drawable = pdb.gimp_image_get_active_layer(image)
           pdb.python_fu_flipscale(image,  drawable,  scale_w,  scale_h)
           pdb.gimp_file_save(image,  drawable,  outfile,  outfile)
           pdb.gimp_image_delete(image)

        except:
           pdb.gimp_message("Opening Error: " + imagefile)
    return
    
# This is the plugin registration function
register(
    "python_fu_batchmyscript",    
    "A procedure to batch another script",   
    "A simple Python Script that can batch another script.",
    "Michel Ardan",
    "Michel Ardan Company",
    "May 2011",
   "<Toolbox>/MyScripts/Batch My Python flipscale script...",
    "",
    [
        (PF_STRING,  "glob_pattern",     "Glob Pattern",     "*.*"),
        (PF_DIRNAME, "source_directory", "Source Directory", ""),
        (PF_INT,     "scale_w",          "Scale Width",      "120"),
        (PF_INT,     "scale_h",          "Scale Height",     "120"),
    ],  
    [],
    pybatch,
)

main()