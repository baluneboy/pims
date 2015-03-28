#! /usr/bin/env python2

# This is free and unencumbered software released into the public domain.

# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.

# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

# For more information, please refer to <http://unlicense.org/>

from gimpfu import *

def set_font(img, layer, font, size, change_size):
	pdb.gimp_image_undo_group_start(img)
	all_layers = img.layers
	for l in all_layers:
		if pdb.gimp_item_is_text_layer(l):
			pdb.gimp_text_layer_set_font(l, font)
			if change_size:
				pdb.gimp_text_layer_set_font_size(l, size, 0)
	pdb.gimp_image_undo_group_end(img)
	
register(
	"python_fu_setfont",
	"Global Font Settings",
	"Sets all layers to use the specified font and size",
	"Kota Weaver",
	"Kota Weaver",
	"2012",
	"<Image>/Image/Global Font Settings",
	"*",
	[
		(PF_FONT, "font", "Font", None),
		(PF_SLIDER, "size", "Font Size", 20, [1, 300, 1]),
		(PF_TOGGLE, "change_size", "Change font size?", True)
	],
	[],
	set_font
)

main()
