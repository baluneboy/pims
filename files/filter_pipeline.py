#!/usr/bin/env python

import os
import re

class FileFilterPipeline(object):

    def __init__(self, *functions, **kwargs):
        self.functions = functions
        self.data = kwargs.get('data') # makes this callable

    def __call__(self, data):
        return FileFilterPipeline(*self.functions, data=data)

    def __iter__(self):
        data = self.data
        for func in self.functions:
            data = func(data)
        return data
    
    def __str__(self):
        s = self.__class__.__name__
        for f in self.functions:
            s += '\n' + str(f)
        s += '\n-----------------------'
        return s

##############################
# SOME FUNDAMENTAL OPERATORS #
##############################

#---------------------------------------------------
# Operator #1 is a file-exists function (old, func way...)
def old_file_exists(file_list):
    for f in file_list:
        if os.path.exists(f):
            yield f

# ...better alternative (for consistency) is a callable class
class FileExists(object):
        
    def __call__(self, file_list):
        for f in file_list:
            if os.path.exists(f):
                yield f
                
    def __str__(self):
        return 'is an existing file'

#---------------------------------------------------
# Operator #2 is a big-file callable class
class BigFile(object):
    
    def __init__(self, min_bytes=1024*1024):
        self.min_bytes = min_bytes
        
    def __call__(self, file_list):
        for f in file_list:
            if os.path.getsize(f) >= self.min_bytes:
                yield f

    def __str__(self):
        return 'is a file with at least %d bytes' % self.min_bytes

#---------------------------------------------------    
# Operator #3 is an extension-checking function
def has_ext(file_list, ext='pdf'):
    for f in file_list:
        if f.endswith(ext):
            yield f

#---------------------------------------------------
# Operator #4 is a file-missing function
def file_missing(file_list):
    for f in file_list:
        if not os.path.exists(f):
            yield f
    
def demo():
    #---------------------------------------------------            
    # Operator #7 is a text file using partial in order to supply keyword arg
    from functools import partial
    is_txt = partial(has_ext, ext='txt')
    
    # Initialize processing pipeline (no file list as input yet)
    ffp = FileFilterPipeline(FileExists(), BigFile(min_bytes=33))
    print ffp
    
    # Apply processing pipeline input #1 (now ffp is callable)
    inp1 = ['/tmp/one.txt', '/tmp/two.not', '/tmp/three.121f03.header', '/tmp/four.txt', '/tmp/five.not']
    for f in ffp(inp1):
        print f
    
if __name__ == "__main__":
    demo()