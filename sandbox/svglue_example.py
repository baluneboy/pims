#!/usr/bin/env python
# -*- coding: utf-8 -*-

import svglue

# load the template from a file
#tpl = svglue.load(file='/home/pims/Downloads/sample-tpl.svg')
tpl = svglue.load(file='/Users/ken/Downloads/sample-tpl.svg')

# replace some text
tpl.set_text('sample-text', u'This was replaced.')

# replace the pink box with 'hello.png'. if you do not specify the mimetype,
# the image will get linked instead of embedded
#tpl.set_image('pink-box', file='/home/pims/Downloads/hello.png', mimetype='image/png')
tpl.set_image('pink-box', file='/Users/ken/Downloads/hello.png', mimetype='image/png')

# svgs are merged into the svg document (i.e. always embedded)
#tpl.set_svg('yellow-box', file='/home/pims/Downloads/Ghostscript_Tiger.svg')
#tpl.set_svg('yellow-box', file='/Users/ken/temp/gutone/2016_08_09_00_00_00.000_121f02_spgs_roadmaps500.svg')
tpl.set_svg('yellow-box', file='/Users/ken/Downloads/Ghostscript_Tiger.svg')

# to render the template, cast it to a string. this also allows passing it
# as a parameter to set_svg() of another template
src = str(tpl)

# write out the result as an SVG image
outfile = '/tmp/output.svg'
with open(outfile, 'w') as svgout:
    svgout.write(src)
    print 'wrote %s' % outfile