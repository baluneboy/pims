#!/usr/bin/env python

import math
from gimpfu import *

def lazy_scale_image(timg, tdrawable, max_width, max_height):
    print "max width: %s\nmax height: %s" % (max_width, max_height)
    width = tdrawable.width
    height = tdrawable.height

    if max_width <= 0:
        # Assume width is okay as it is
        max_width = width
    if max_height <= 0:
        # Assume height is okay
        max_height= height

    if width <= max_width and height <= max_height:
        print "Nothing to do, returning"
        return

    image_aspect    = float(width) / float(height)
    boundary_aspect = float(max_width) / float(max_height)
    if image_aspect > boundary_aspect:
        # Width is the limiting factor:
        new_width = max_width
        new_height= int(round(  new_width/image_aspect ))
    else:
        # Height is the limiting factor:
        new_height = max_height
        new_width = int(round(  image_aspect*new_height  ))

    print "Resizing %s:%s to %s:%s" % (width, height, new_width, new_height)

    # At present, documenatation does not specify the interpolation--
    # another tutorial claimed it was cubic:
    pdb.gimp_image_scale(timg, new_width, new_height)

register(
        "lazy_scale_image",
        "Scale the specified image so that it is no larger than the given dimensions",
        "Scale the specified image so that it is no larger than the given dimensions",
        "Dan Swell",
        "Dan Swell",
        "2012",
        "<Image>/_Xtns/_Lazy Resize",
        "RGB*, GRAY*",
        [
                (PF_INT, "max_width", "Maximum new width", 1280),
                (PF_INT, "max_height", "Maximum new height", 900),
        ],
        [],
        lazy_scale_image)

main()
