#!/usr/bin/env python
#
# -------------------------------------------------------------------------------------
#
# Copyright (c) 2014, Kenneth Hrovat
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, 
# are permitted provided that the following conditions are met:
#
#    - Redistributions of source code must retain the above copyright notice, this 
#    list of conditions and the following disclaimer.
#    - Redistributions in binary form must reproduce the above copyright notice, 
#    this list of conditions and the following disclaimer in the documentation and/or 
#    other materials provided with the distribution.
#    - Neither the name of the author nor the names of its contributors may be used 
#    to endorse or promote products derived from this software without specific prior 
#    written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY 
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES 
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT 
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR 
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN 
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH 
# DAMAGE.

import os
from gimpfu import *

def save_all_gradmaps_to_files(image, layer, out_folder):
    ''' Save the current layer into a PNG files, one for each gradient map.
    
    Parameters:
    image : image The current image.
    layer : layer The layer of the image that is selected.
    out_folder : string The folder in which to save the images.
    '''
    
    # Indicates that the process has started.
    gimp.progress_init("Saving to '" + out_folder + "'...")
    
    # Get list of gradient maps
    n, gradmaps = pdb.gimp_gradients_get_list('.*') # use print to show this list

    for gradmap in gradmaps:

        # copy layer
        layer_gradmap = layer.copy()
        layer_gradmap.name = "tmp4gradmap"
        image.add_layer(layer_gradmap, 0) 

        # apply gradmap
        try:
            
            # set gradient map and output PNG filename
            stub = os.path.join( out_folder, layer.name + gradmap.replace(' ', '_').lower() )
            pdb.gimp_context_set_gradient(gradmap)
            
            # apply gradient map
            img = pdb.plug_in_gradmap(image, layer_gradmap, run_mode=RUN_NONINTERACTIVE)
            
            # Save as PNG
            gimp.pdb.file_png_save(image, layer_gradmap, stub + ".png", "raw_filename", 0, 9, 0, 0, 0, 0, 0)
            
        except Exception as err:
            
            gimp.message("Unhandled error: " + str(err))

                    
        # remove layer
        image.remove_layer(layer_gradmap)
    
register(
    "python_fu_test_save_all_gradmaps_to_files",
    "Save all gradient map samples to PNG files",
    "Save the current layer into PNG files, one for each gradient map.",
    "KH",
    "Open source (BSD 3-clause license)",
    "2014",
    "<Image>/Filters/Test/Save PNG gradmap files",
    "*",
    [
        (PF_DIRNAME, "out_folder", "Output directory", ""),
    ],
    [],
    save_all_gradmaps_to_files)

main()
