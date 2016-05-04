#!/usr/bin/env python

import sys
import unittest

from http_directory import resolve_link, ListingParser, download_directory

download_directory('http://pims.grc.nasa.gov/ftp/pad/year2005/month01/day01/mams_accel_ossbtmf', '/tmp/pad')
raise SystemExit

class TestLinkResolution(unittest.TestCase):
    def test_absolute_link(self):
        self.assertEqual(
                resolve_link('http://website.org/p/test.txt',
                             'http://some/other/url'),
                'http://website.org/p/test.txt')
        self.assertEqual(
                resolve_link('http://website.org',
                             'http://some/other/url'),
                'http://website.org/')

    def test_absolute_path(self):
        self.assertEqual(
                resolve_link('/p/test.txt', 'http://some/url'),
                'http://some/p/test.txt')
        self.assertEqual(
                resolve_link('/p/test.txt', 'http://some/url/'),
                'http://some/p/test.txt')
        self.assertEqual(
                resolve_link('/p/test.txt', 'http://site'),
                'http://site/p/test.txt')
        self.assertEqual(
                resolve_link('/p/test.txt', 'http://site/'),
                'http://site/p/test.txt')

    def test_relative_path(self):
        self.assertEqual(
                resolve_link('some/file', 'http://site/folder'),
                'http://site/folder/some/file')
        self.assertEqual(
                resolve_link('some/file', 'http://site/folder/'),
                'http://site/folder/some/file')
        self.assertEqual(
                resolve_link('some/dir/', 'http://site/folder'),
                'http://site/folder/some/dir/')


class TestParser(unittest.TestCase):
    def test_parse(self):
        parser = ListingParser('http://a.remram.fr/test')
        parser.feed("""
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html><head><title>
Index of /test</title></head><body><h1>Index of /test</h1><table><tr><th>
<img src="/icons/blank.gif" alt="[ICO]"></th><th><a href="?C=N;O=D">Name</a>
</th><th><a href="?C=M;O=A">Last modified</a></th><th><a href="?C=S;O=A">Size
</a></th><th><a href="?C=D;O=A">Description</a></th></tr><tr><th colspan="5">
<hr></th></tr><tr><td valign="top"><img src="/icons/back.gif" alt="[DIR]"></td>
<td><a href="/">Parent Directory</a></td><td>&nbsp;</td><td align="right">  - 
</td><td>&nbsp;</td></tr><tr><td valign="top">
<img src="/icons/unknown.gif" alt="[   ]"></td><td><a href="a">a</a></td>
<td align="right">11-Sep-2013 15:46  </td><td align="right">  3 </td><td>&nbsp;
</td></tr><tr><td valign="top"><img src="/icons/unknown.gif" alt="[   ]"></td>
<td><a href="/bb">bb</a></td><td align="right">11-Sep-2013 15:46  </td>
<td align="right">  3 </td><td>&nbsp;</td></tr><tr><td valign="top">
<img src="/icons/folder.gif" alt="[DIR]"></td><td><a href="/cc/">cc/</a></td>
<td align="right">11-Sep-2013 15:46  </td><td align="right">  - </td><td>&nbsp;
</td></tr><tr><td valign="top"><img src="/icons/folder.gif" alt="[DIR]"></td>
<td><a href="http://a.remram.fr/dd">dd/</a></td><td align="right">
11-Sep-2013 15:46  </td><td align="right">  - </td><td>&nbsp;</td></tr><tr>
<th colspan="5"><hr></th></tr></table></body></html>
        """)
        links = set(l for l in parser.links if '?' not in l)
        self.assertEqual(links, set([
                'http://a.remram.fr/',
                'http://a.remram.fr/test/a',
                'http://a.remram.fr/bb',
                'http://a.remram.fr/cc/',
                'http://a.remram.fr/dd',
        ]))


class TestDownload(unittest.TestCase):
    def test_download(self):
        url = 'http://a.remram.fr/test/'

        import os
        import shutil
        import tempfile
        testdir = tempfile.mkdtemp()
        try:
            download_directory(url, testdir)
            files = {}
            def addfiles(dirpath):
                td = os.path.join(testdir, dirpath)
                for name in os.listdir(td):
                    filename = os.path.join(testdir, dirpath, name)
                    dn = os.path.join(dirpath, name)
                    if os.path.isdir(filename):
                        addfiles(os.path.join(dirpath, name))
                    else:
                        with open(filename, 'rb') as f:
                            files[dn.replace(os.sep, '/')] = f.read()
            addfiles('')
            self.assertEqual(len(files), 4)
            del files['f.html']
            self.assertEqual(files, {
                    'a': 'aa\n',
                    'bb': 'bb\n',
                    'cc/d': 'dd\n',
                })
        finally:
            shutil.rmtree(testdir)


if __name__ == '__main__':
    unittest.main()