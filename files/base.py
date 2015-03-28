#!/usr/bin/env python

import os
import re

class PimsFileDoesNotExist(Exception): pass
class UnrecognizedPimsFile(Exception): pass

class File(object):
    """
    A generic representation of a PIMS file.
    """
    def __init__(self, name):
        self.name = name
        self.exists = self._get_exists()
        if not self.exists:
            raise PimsFileDoesNotExist('caught IOError for file "%s", is path okay?' % self.name)
        self.size = self._get_size()

    def __str__(self):
        return '%s object "%s" for PIMS' % (self.__class__.__name__, self.name)

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self or "None")

    def __len__(self): return self.size

    def _get_size(self):
        return os.path.getsize(self.name)
    
    def _get_dict(self):
        #D = [ (x, self.as_dict()[x]) for x in self.as_dict()] # convert to tuple
        #alpha = sorted(D, key = lambda x: x[0]) # alpha sort on keys
        #s += '\n'.join(elem[0]+':'+str(elem[1]) for elem in alpha)   
        return dict((name, getattr(self, name)) for name in dir(self) if not name.startswith('_'))
    
    def _get_exists(self):
        try:
            with open(self.name):
                pass
            return True
        except IOError:
            return False

class RecognizedFile(File):
    """
    A generic representation of a PIMS recognized file.
    """
    def __init__(self, name, pattern='.*', show_warnings=False):
        super(RecognizedFile, self).__init__(name)
        self._pattern = pattern
        self._show_warnings = show_warnings
        self._match = self._get_match()
        if not self._is_recognized():
            self.recognized = False
            raise UnrecognizedPimsFile('"%s"' % self.name)
        else:
            self.recognized = True

    def __str__(self):
        return '%s object for recognized PIMS file "%s"' % (self.__class__.__name__, self.name)

    def _is_recognized(self):
        if self._match:
            return True
        return False
    
    def _get_match(self):
        return re.search( re.compile(self._pattern), self.name)

class StupidRecognizedFile(RecognizedFile):
    """
    A PIMS file that is recognized because the filename contains 'stupid'.
    """
    def __init__(self, name, pattern='.*stupid.*', show_warnings=False):
        super(StupidRecognizedFile, self).__init__(name, pattern, show_warnings=show_warnings)
    
    def _is_recognized(self):
        if "stupid" in self.name:
            return True
        return False


# Decorator for convenience
def add_squiggles(fn):
    def new(*args):
        print "~" * len(args[0])
        return fn(*args)
    return new

# You could also nest decorators in declaration order:
#    add_banner(add_squiggles(print_fname('$'*33)))
# when "add_banner" is above "add_squiggles"
@add_squiggles
def print_fname(f): print f

if __name__ == '__main__':

    from pims.files.utils import guess_file

    files = [
        '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_CMG_Desat/1quantify_2011_05_19_18_18_00_121f03006_gvt3_12hour_pm1mg_001800_12hc.pdf',
        ]
    filetype_classes = [ RecognizedFile ]

    #files = [
    #    '/tmp/trash_stupid.txt',
    #    '/tmp/trash.txt'
    #    ]
    #filetype_classes = [ StupidRecognizedFile ]

    for f in files:
        print_fname(f)
        try:
            srf = guess_file(f, filetype_classes, show_warnings=False)
            print srf._get_dict()
        except UnrecognizedPimsFile:
            print 'SKIPPED unrecognized file'
