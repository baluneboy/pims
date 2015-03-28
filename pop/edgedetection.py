#!/usr/bin/env python

import numpy as np
import scipy.ndimage as ndimage
import platform
if platform.platform().startswith('Linux'):
    from PIL import Image
    _BASEDIR = '/home/pims'
else:
    import Image
    _BASEDIR = '/Users/ken'
from pims.pop.examples.simple_example import data
from pims.utils.iterabletools import runlength_blocks

def full_print_array(*args, **kwargs):
  from pprint import pprint
  opt = np.get_printoptions()
  np.set_printoptions(threshold='nan')
  pprint(*args, **kwargs)
  np.set_printoptions(**opt)

# a class for working with image edges
class Edges(object):
    
    def __init__(self, img_arr):
        self.img_arr = img_arr
        
        # mask is True where columns are all ones       
        self.mask = np.all(img_arr, axis=0) # column-wise check all ones
        
        # get run blocks of [start, stop, value]        
        self.blocks = runlength_blocks(self.mask)
        
        # filter out where columns were not all ones (and get rid of 3rd element value in each block)        
        self.idx_bounds = [ i[:-1] for i in self.blocks if i[2] ]
        
    def left_edge(self):
        left_edge = [ i for i in self.idx_bounds if i[0] == 0 ]
        return left_edge[0] if left_edge else None        
        
    def right_edge(self):
        right_edge = [ i for i in self.idx_bounds if i[-1] == (self.img_arr.shape[1] - 1 ) ]
        return right_edge[0] if right_edge else None        

# a simple edge detection function
def simple_edge_detect(d):
    """a simple edge detection function"""
    
    for label, arr in d.iteritems():
        lefts, rights = int(label[-2]), int(label[-1])
        print arr
        print label, 'should have', lefts, 'lefts &', rights, 'rights; "all-ones" columns at:'
        #idx = np.where( np.all(arr, axis=0) )[0] # column-wise check all ones
        
        # mask is True where columns are all ones
        mask = np.all(arr, axis=0) # column-wise check all ones
        
        # get run blocks of [start, stop, value]
        blocks = runlength_blocks(mask)
        
        # filter out where columns were not all ones (and get rid of 3rd element value in each block)
        idx_bounds = [ i[:-1] for i in blocks if i[2] ]
        
        left_edge = [ i for i in idx_bounds if i[0] == 0 ]
        right_edge = [ i for i in idx_bounds if i[-1] == (arr.shape[1] -1 ) ]
        #print blocks
        #print idx_bounds
        print 'left edge huggers:',
        for lh in left_edge:
            print lh,
        print
        print 'Right edge huggers:',
        for rh in right_edge:
            print rh,
        print
        print '-' * 33

def demo(d):

    # Fill holes to make sure we get nice clusters
    filled = ndimage.morphology.binary_fill_holes(d)
     
    # Now separate each group of contiguous ones into a distinct value
    # This will be an array of values from 1 - num_objects, with zeros
    # outside of any contiguous object
    objects, num_objects = ndimage.label(filled)
    
    # Show contiguous objects' labels: 1, 2, ..., n
    print 'These are the labeled objects:'
    print objects
    
    # Now return a list of slices around each object
    #  (This is effectively the tuple that you wanted)
    object_slices =  ndimage.find_objects(objects)
    
    # Just to illustrate using the object_slices
    print '\nobject slices:'
    #print object_slices
    for obj_slice in object_slices:
        print '-' * 80
        print d[obj_slice],
        print '<- ROW RANGE =',
        print obj_slice[0].start, ':',
        print obj_slice[0].stop, ',',
        print 'COL RANGE =',
        print obj_slice[1].start, ':',
        print obj_slice[1].stop        
     
    # Find the object with the largest area
    areas = [np.product([x.stop - x.start for x in slc]) for slc in object_slices]
    largest = object_slices[np.argmax(areas)]
    
    print '\nobject with largest area:'
    print d[largest]
  
#demo( data['both22'] )
#print '#-' * 22 

#simple_edge_detect(data)

labels = ['right01', 'both22', 'left20', 'none11']
for label in labels:
    print '\n', label, 'has'
    edges = Edges( data[label] )
    if edges.left_edge(): print 'LEFT :', edges.left_edge()
    if edges.right_edge(): print 'RIGHT:', edges.right_edge()
