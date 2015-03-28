#!/usr/bin/env python

from gimpfu import *

def add_border(image, drawable, radius):
    # Group the operations of this script
    pdb.gimp_image_undo_group_start(image)
    width      = image.width
    height     = image.height
    width_new  = width  + 2*radius
    height_new = height + 2*radius

    # Increase the canvas size
    pdb.gimp_image_resize(image, width_new, height_new, radius, radius)
    # Add a new layer, fill it with FG color
    layer = pdb.gimp_layer_new(image, width_new, height_new,
                0, "border layer", 100, NORMAL_MODE)
    pdb.gimp_drawable_fill(layer, FOREGROUND_FILL)

    # Add new layer, move it to bottom:
    pdb.gimp_image_add_layer(image, layer, -1)
    pdb.gimp_image_lower_layer_to_bottom(image, layer)

    pdb.gimp_image_undo_group_end(image)

register(
        "add_border",
        "Add a border around an image, colored in the current FG color.",
        "Add a border around an image, colored in the current FG color.",
        "Dan Swell",
        "Dan Swell",
        "2012",
        "<Image>/_Xtns/_Add border",
        "RGB*, GRAY*",
        [
                (PF_INT, "radius", "Border radius", 20),
        ],
        [],
        add_border)

main()
