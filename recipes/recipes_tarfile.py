#!/usr/bin/env python

import os
import re
import tarfile
     
def walk_non_gz_files(dirpath):
    """walk dirpath and show files that do not endwith gz"""
    print 'filtered filenames (do not end with gz)\n', '='*40
    for root, dirnames, filenames in os.walk(dirpath):
        for filename in filenames:
            abspath = os.path.join(root, filename)
            if not abspath.endswith('gz'):
                print abspath

def extract(theTarFile, extractTarPath):

    # open the tar file
    tfile = tarfile.open(theTarFile)
    
    # process it
    if tarfile.is_tarfile(theTarFile):
        
        # list all contents
        #print "tar file contents:"
        #print tfile.list(verbose=True)
        
        # extract all contents
        print '>extracting %s' % theTarFile
        tfile.extractall(extractTarPath)
        print '>done'
        
    else:
        print theTarFile + " is not a tarfile."
    
    tfile.close()    

if __name__ == "__main__":
     
    # tar file path to extract
    extractTarPath = '/tmp/junk'
    
    # tar file to extract
    theTarFile = os.path.join(extractTarPath, 'samslogs014.tgz')
    
    # extract
    extract(theTarFile, extractTarPath)

    walk_non_gz_files(extractTarPath)