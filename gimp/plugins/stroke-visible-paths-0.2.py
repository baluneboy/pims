#!/usr/bin/env python
# -*- coding: utf-8 -*-

# GIMP plugin to stroke all visible paths on separate layers
# (c) Ofnuts 2013
#
#   History:
#
#   v0.0: 2012-06-22: Initial version
#   v0.1: 2013-08-04: Add gradient support
#   v0.2: 2013-08-05: Check that there are some paths to stroke
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.


import math, sys, os
from gimpfu import *

def strokePath(image,path,fill,suffix):
	layer=gimp.Layer(image, path.name+' '+suffix, image.width, image.height,RGBA_IMAGE, 100., NORMAL_MODE)
	image.add_layer(layer,0)
	pdb.gimp_drawable_fill(layer,fill)	
	pdb.gimp_edit_stroke_vectors(layer,path)

def strokeVisiblePaths(image,fill,useGradient,suffix):
	pdb.gimp_image_undo_group_start(image)
	pdb.gimp_context_push()
	try:
		colors=None
		strokedPaths=[p for p in image.vectors if p.visible]
		if len(strokedPaths) < 2:
			raise Exception("There should be at least two visible paths")
		if useGradient:
			colors=gimp.gradient_get_uniform_samples(gimp.context_get_gradient(),len(strokedPaths))
		for i,path in enumerate(reversed(strokedPaths)):
			if colors:
				pdb.gimp_context_set_foreground(colors[i])
				pdb.gimp_context_set_opacity(100*colors[i][3])
			strokePath(image,path,fill,suffix)

        except Exception as e:
		print e.args[0]
		pdb.gimp_message(e.args[0])

	pdb.gimp_context_pop()
	pdb.gimp_image_undo_group_end(image)
	pdb.gimp_displays_flush()
	return;
	
### Registration
whoiam='\n'+os.path.abspath(sys.argv[0])

register(
	'stroke-visible-paths',
	'Stroke visible paths on new layers...'+whoiam,
	'Stroke visible paths',
	'Ofnuts',
	'Ofnuts',
	'2013',
	'Stroke visible paths',
	'*',
	[
		(PF_IMAGE, 'image', 'Input image', None),
		(PF_OPTION,'fill','Background fill', 1, ['Foreground color','Background color','White','Transparent','Pattern']),
		(PF_OPTION,'useGradient','Color',0,['Foreground color','From gradient']),
		(PF_STRING,'suffix', 'Name suffix', ''),
	],
	[],
	strokeVisiblePaths,
	menu='<Image>/Image',
)

main()
