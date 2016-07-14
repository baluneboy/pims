#!/usr/bin/env python

# class to do filtering on list of files
class FileFilter(object):
    """Return list of files that have been filtered.
    
    >>> ff = FileFilter(['/tmp/one', '/tmp/two'])
    
    """
    
    def __init__(self, *args, **kwargs):
        self.files = None
    
    def __str__(self):
        s = self.__class__.__name__

if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)