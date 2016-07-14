"""
This is a bit of an experiment with a technique of applying filters to lists of
files.

The base functions are iter_files which is a simple wrapper around os.walk and
then filter_file_list which is used to create filter functions.

white_list and black_list are then examples of filters created using the filter_file_list 
function as a decorator

As a demonstration of creating filters on the fly, has_mode is then created in 
the __main__ section
"""

import os
import fnmatch
import time

__author__ = 'Eysteinn Kristinsson <eysispeisi@gmail.com>'

def iter_files(folder, **extraWalkArgs):
    '''
    A simple wrapper around os.walk that returns file paths.
    **extraWalkArgs are passed to os.walk if you want to change the defaults 
    there.
    '''
    for root, dirs, files in os.walk(folder, **extraWalkArgs):
        for f in files:
            yield os.path.join(root, f)

def filter_file_list(func):
    '''
    This is the filter creator function, you can also use it as a decorator.

    usage: filter_file_list(function, *args **keywordArgs)
    args and keywordArgs are automatically passed to the function during 
    iteration.

    The function passed to it must take a valid file path as a first argument
    example:
        @filter_file_list
        def min_size(file, minsize):
            return os.path.getsize(file) >= minsize:
        # Now you have created a filter that can take a list of files and a
        # minsize argument and apply the minsize condition to the files list
        # Print files in '.' that are 1MB or larger
        for file in min_size(os.listdir('.'), 1024*1024):
            print file
    '''
    def wrapper(files, *a, **kw):
        for f in files:
            if func(f, *a, **kw):
                yield f
    return wrapper
    
@filter_file_list
def white_list(f, patterns):
    for pat in patterns:       
        if fnmatch.fnmatch(f, pat):
            #print 'whitelist %s based on %s' % (f, pat)
            return True
        #else:
        #    print 'DO NOT whitelist %s based on %s' % (f, pat)
    return False

@filter_file_list
def black_list(f, patterns):
    for pat in patterns:
        if fnmatch.fnmatch(f, pat):
            #print 'blacklist %s based on %s' % (f, pat)
            return False
        #else:
        #    print 'DO NOT blacklist %s based on %s' % (f, pat)        
    return True

@filter_file_list
def min_size(f, minsize):
    return os.path.getsize(f) >= minsize

# class for list of pdf files that are at least min_size bytes in size   
class BigPdfFiles(object):
    """A class for list of pdf files that are at least min_size bytes in size.
    
    """
    
    def __init__(self, parent_dir='/tmp', min_size=3*1024*1024):
        self.parent_dir = parent_dir
        self.min_size = min_size
        self._verify_inputs()
        self._pdf_files = self._get_pdf_files()
        self.files = self._get_big_files()
    
    def __str__(self):
        s = self.__class__.__name__
        s += ': %s' % self.parent_dir
        s += ' has %d files' % len(self.files)
        s += ' matching %s' % self._nice_criteria()
        return s
    
    def _nice_criteria(self):
        s = "white_list ('*.pdf',)"
        s += ' | size >= %d bytes' % self.min_size
        return s    
    
    def _verify_inputs(self):
        if not os.path.exists(self.parent_dir):
            raise OSError('parent directory "%s" does not exist' % self.parent_dir)
        if not isinstance(self.min_size, int):
            raise TypeError('minimum size argument is not of type int')
        
    def _get_pdf_files(self):
        files = list( iter_files(self.parent_dir) )
        pdf_files = list( white_list(files, ('*.pdf',)) )
        return pdf_files
        
    def _get_big_files(self):
        big_files = list( min_size(self._pdf_files, self.min_size) )
        return big_files
    
def demo_big_pdf_files():
    #big_pdf_files = BigPdfFiles(parent_dir='/tmpx')
    #big_pdf_files = BigPdfFiles(min_size=None)
    big_pdf_files = BigPdfFiles(min_size=25000)
    print big_pdf_files
    #for f in big_pdf_files.files:
    #    print f

if __name__ == '__main__':

    demo_big_pdf_files()
    raise SystemExit
    
    folder = '/tmp/test' # folder to process

    # get an iterator of all files under <folder>
    files = list( iter_files(folder) )
    
    print 'before whitelist'
    for fn in files:
        print fn
        
    # apply a whitelist to the files iterator
    wfiles = list( white_list(files, ('*.py', '*.txt', '*.jnk')) )
    
    print '\nafter whitelist'
    for w in wfiles: print w

    # apply a blacklist to the whitelisted-files iterator
    bfiles = list( black_list(wfiles, ('*.jnk', '*.crp', '*black*')) )
    
    print '\nafter blacklist'
    for b in bfiles: print b

    # Filters can also constructed on the fly
    # the has_mode function constructed here checks the file mode, it filters
    # out all files that don't have the mode you pass into it.
    import stat # for permission constants
    import datetime
    has_mode = filter_file_list(lambda file, mode: os.stat(file).st_mode & mode == mode)
    print '\nfiles others have read and write access to'
    mode = stat.S_IROTH|stat.S_IWOTH
    for hmf in has_mode(iter_files(folder), mode):
        print hmf
    print
    
    # just to state the obvious, you don't have to use IterFilesInFolder to get
    # a list of files to feed a filter, just something that is iterable but 
    # contains actual valid file paths
    my_dir = '/tmp/test/sub1'
    files = os.listdir(my_dir)
    print 'python files in %s' % my_dir
    for wf in white_list(files, ('*.py',)):
        print wf
    print
    
    # Print files in /tmp that are 3 MB or larger
    my_dir = '/tmp'
    files = list( iter_files(my_dir) )
    pdf_files = list( white_list(files, ('*.pdf',)) )
    for bf in min_size(pdf_files, 3*1024*1024):
        print bf