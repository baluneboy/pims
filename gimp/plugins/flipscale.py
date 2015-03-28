#!/usr/bin/env python

import os, re, glob
from gimpfu import *
from gimpenums import *

def flip_and_scale(image, drawable,  scale_w,  scale_h) :
    pdb.gimp_image_flip( image, ORIENTATION_HORIZONTAL )
    pdb.gimp_image_scale_full(image, scale_w, scale_h, INTERPOLATION_LANCZOS)
    return

# This is the plugin registration function
register(
    "python_fu_flipscale",    
    "Flip and scale image",   
    "A simple Python Script that flips-and-scales the image.",
    "Michel Ardan",
    "Michel Ardan Company",
    "May 2011",
    "<Image>/MyScripts/Flip And Scale Image",
    "*",
    [
         (PF_INT, 'scale_w', 'New width for the image', 100),
         (PF_INT, 'scale_h', 'New height for the image', 100)
    ],  
    [],
    flip_and_scale,
)

main()