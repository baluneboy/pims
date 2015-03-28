#!/usr/bin/env python

import os
from urllib2 import urlopen, URLError, HTTPError

def download_file(url):
    # open the url
    try:
        f = urlopen(url)
        print "downloading " + url

        # open our local file for writing
        with open(os.path.basename(url), "wb") as local_file:
            local_file.write(f.read())

    # handle these errors
    except HTTPError, e:
        print "HTTP Error:", e.code, url
    except URLError, e:
        print "URL Error:", e.reason, url

def main():
    # loop over range
    for index in range(150, 151):
        url = ("http://www.archive.org/download/"
               "Cory_Doctorow_Podcast_%d/"
               "Cory_Doctorow_Podcast_%d_64kb_mp3.zip" %
               (index, index))
        download_file(url)

if __name__ == '__main__':
    main()
    