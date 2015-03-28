#!/usr/bin/env python

import os

# customize as needed
def is_hz_file(filename):
    return 'hz_' in filename

def createHTML(input_dir, output_html, predicate=None):
    files = os.listdir(input_dir)
    files.sort(reverse=True)
    with open(output_html, "w") as f:
        f.write("<html><body><ul>\n")
        for filename in files:
            fullpath = os.path.join(input_dir, filename).replace('/misc/yoda/www/plots', 'http://pims.grc.nasa.gov/plots')
            if predicate:
                if predicate(filename):
                    f.write('<li><a href="%s">%s</a></li>\n' % (fullpath, filename))
            else:
                f.write('<li><a href="%s">%s</a></li>\n' % (fullpath, filename))
        f.write("</ul></body></html>\n")

if __name__ == "__main__":
    createHTML('/misc/yoda/www/plots/screenshots', '/misc/yoda/www/plots/user/pims/screenshots.html', predicate=None)
