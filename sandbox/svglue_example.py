#!/usr/bin/env python
# -*- coding: utf-8 -*-

import svglue


# load the template from a file
tpl = svglue.load(file='/home/pims/Downloads/sample-tpl.svg')

# replace some text
tpl.set_text('sample-text', u'This was replaced.')

# replace the pink box with 'hello.png'. if you do not specify the mimetype,
# the image will get linked instead of embedded
tpl.set_image('pink-box', file='/home/pims/Downloads/hello.png', mimetype='image/png')

# svgs are merged into the svg document (i.e. always embedded)
tpl.set_svg('yellow-box', file='/home/pims/Downloads/Ghostscript_Tiger.svg')

# to render the template, cast it to a string. this also allows passing it
# as a parameter to set_svg() of another template
src = str(tpl)

# write out the result as an SVG image
with open('output.svg', 'w') as svgout:
    svgout.write(src)
