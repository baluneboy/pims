#!/usr/bin/env python

import numpy as np
import platform
if platform.platform().startswith('Linux'):
    from PIL import Image
    _BASEDIR = '/home/pims'
else:
    import Image
    _BASEDIR = '/Users/ken'

def change_color_keep_transparency(rgb1, rgb2):
    #im = Image.open('/home/pims/Desktop/test.png')
    im = Image.open(_BASEDIR + '/dev/programs/python/pims/sandbox/data/original_image.png')

    im = im.convert('RGBA')
    data = np.array(im)
    
    r1, g1, b1 = rgb1[0], rgb1[1], rgb1[2]
    r2, g2, b2 = rgb2[0], rgb2[1], rgb2[2]
    
    # FIXME there might be an index trick that preserves alpha
    # data[..., :-1][mask] = (r2, g2, b2) # this does not work!?
    
    red, green, blue, alpha = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
    mask = (red == r1) & (green == g1) & (blue == b1) & (alpha >= 0)
    data[:,:,:3][mask] = [r2, g2, b2]
    #fullprint( data[ np.where(mask) ] )
    
    im2 = Image.fromarray(data)
    im2.save('/tmp/fig1_modified.png')
    im2.show()
        
def demo2():
  rgb1 = ( 22,  52, 100) # Original "dark-blue-is-blank" value
  rgb2 = (  0,   0,   0) # Replacement color is black
  
  rgb1 = (255, 255, 255) # WHITE
  rgb2 = (255,   0,   0) # RED
  
  change_color_keep_transparency(rgb1, rgb2)
  
demo2()