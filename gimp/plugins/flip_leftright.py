#!/usr/bin/env python

# command line:
# gimp -i -b '(python-flip-leftright RUN-NONINTERACTIVE "/tmp/test.jpg")' -b '(gimp-quit 0)'

from gimpfu import pdb, main, register, PF_STRING
from gimpenums import ORIENTATION_HORIZONTAL

def flip_leftright(file):
    image = pdb.gimp_file_load(file, file)
    drawable = pdb.gimp_image_get_active_layer(image)
    pdb.gimp_image_flip(image, ORIENTATION_HORIZONTAL)
    pdb.gimp_file_save(image, drawable, file, file)
    pdb.gimp_image_delete(image)

args = [(PF_STRING, 'file', 'GlobPattern', '*.*')]
register('python-flip-leftright', '', '', '', '', '', '', '', args, [], flip_leftright)

main()
