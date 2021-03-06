#!/usr/bin/env python

import math
from gimpfu import *

# Since author had these hard-coded twice below, use constants here instead:
_BX = 99
_BY = 9
_AZ = 135
_EL = 45
_DEPTH = 3

def python_clothify(timg, tdrawable, bx=_BX, by=_BY, azimuth=_AZ, elevation=_EL, depth=_DEPTH):
    width = tdrawable.width
    height = tdrawable.height

    img = gimp.Image(width, height, RGB)
    img.disable_undo()

    layer_one = gimp.Layer(img, "tmpXdots", width, height, RGB_IMAGE, 100, NORMAL_MODE)
    img.add_layer(layer_one, 0)
    pdb.gimp_edit_fill(layer_one, BACKGROUND_FILL)

    pdb.plug_in_noisify(img, layer_one, 0, 0.7, 0.7, 0.7, 0.7)

    layer_two = layer_one.copy()
    layer_two.mode = MULTIPLY_MODE
    layer_two.name = "tmpYdots"
    img.add_layer(layer_two, 0)

    pdb.plug_in_gauss_rle(img, layer_one, bx, 1, 0)
    pdb.plug_in_gauss_rle(img, layer_two, by, 0, 1)

    img.flatten()

    bump_layer = img.active_layer

    pdb.plug_in_c_astretch(img, bump_layer)
    pdb.plug_in_noisify(img, bump_layer, 0, 0.2, 0.2, 0.2, 0.2)
    pdb.plug_in_bump_map(img, tdrawable, bump_layer, azimuth,
                         elevation, depth, 0, 0, 0, 0, True, False, 0)
    
    gimp.delete(img)

register(
        "python_fu_clothify",
        "Make the specified layer look like it is printed on cloth",
        "Make the specified layer look like it is printed on cloth",
        "James Henstridge",
        "James Henstridge",
        "1997-1999",
        "<Image>/Filters/Artistic/_KenClothify...",
        "RGB*, GRAY*",
        [
                (PF_INT, "x_blur", "X blur", _BX),
                (PF_INT, "y_blur", "Y blur", _BY),
                (PF_INT, "azimuth", "Azimuth", _AZ),
                (PF_INT, "elevation", "Elevation", _EL),
                (PF_INT, "depth", "Depth", _DEPTH)
        ],
        [],
        python_clothify)

main()
