#!/usr/bin/env python

"""
 PIL.ImageDraw.floodfill(image, xy, value, border=None, thresh=0)

    Warning

    This method is experimental.

    Fills a bounded region with a given color.
    Parameters:	

        image - Target image.
        xy - Seed position (a 2-item coordinate tuple).
        value - Fill color.
        border - Optional border value. If given, the region consists of pixels with a color different from the border color. If not given, the region consists of pixels having the same color as the seed pixel.
        thresh - Optional threshold value which specifies a maximum tolerable difference of a pixel value from the background in order for it to be replaced. Useful for filling regions of non- homogeneous, but similar, colors.
"""

import sys
from PIL import Image, ImageDraw

im = Image.open("/home/pims/Downloads/unnamed.png")

xy = (100, 100)
value = (11, 11, 11)
ImageDraw.floodfill(im, xy, value, border=None, thresh=300)

# write to stdout
im.save(sys.stdout, "PNG")