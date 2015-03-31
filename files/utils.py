import os
import re
import time
import errno
from pims.files.base import File, UnrecognizedPimsFile
from pims.patterns.handbookpdfs import is_unique_handbook_pdf_match
from pims.patterns.dailyproducts import _BATCHROADMAPS_PATTERN, _PADHEADERFILES_PATTERN
from pims.utils.pimsdateutil import timestr_to_datetime
from pims.strings.utils import remove_non_ascii

def file_age_days(fname):
    utime_file = os.path.getmtime(fname)
    utime_now = time.time()
    return int( (utime_now - utime_file) // 86400 )

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# get most recent file along pth that ends with suffix
def most_recent_file_with_suffix(pth, suffix):
    """get most recent file along pth that ends with suffix"""
    files = [ os.path.join(pth, f) for f in os.listdir(pth) if f.endswith(suffix) ]
    files.sort(key=lambda x: os.path.getmtime(x))
    return os.path.join(pth, files[-1])

# prepend to text file
def prepend_tofile(s, txtfile):
    """prepend to text file"""
    bool_success = False
    try:
        with open(txtfile, 'r') as original: old_text = original.read()
        with open(txtfile, 'w') as modified: modified.write(s + '\n' + old_text)
        bool_success = True
    except:
        print 'FAILED to prepend to %s' % txtfile
    return bool_success

# similar to unix tail
def tail(f, n, offset=0):
    """Reads a n lines from f with an offset of offset lines."""
    avg_line_length = 74
    to_read = n + offset
    while 1:
        try:
            f.seek(-(avg_line_length * to_read), 2)
        except IOError:
            # oops, apparently file smaller than what we want to step back, so go to beginning instead
            f.seek(0)
        pos = f.tell()
        lines = f.read().splitlines()
        if len(lines) >= to_read or pos == 0:
            return lines[-to_read:offset and -offset or None]
        avg_line_length *= 1.3

def overwrite_file_with_non_ascii_chars_removed(f):
    with open (f, "r") as myfile:
        data = myfile.read()
    s = remove_non_ascii(data)
    with open (f, "w") as newfile:
        newfile.write(s)

def parse_roadmap_filename(f):
    """Parse roadmap filename."""
    m = re.match(_BATCHROADMAPS_PATTERN, f)
    if m:
        dtm = timestr_to_datetime(m.group('dtm'))
        sensor = m.group('sensor')
        abbrev = m.group('abbrev')
        return dtm, sensor, abbrev, os.path.basename(f)
    else:
        return 'UNKNOWN', 'UNKNOWN', 'UNKNOWN', "%s" % os.path.basename(f)

def guess_file(name, klass, show_warnings=False):
    """
    Verify unique pattern, then instantiate class.
    """
    p = File(name)
    try:
        p = klass(name, show_warnings=show_warnings)
        #print i, name
        return p
    except UnrecognizedPimsFile:
        p.recognized = False
    #if show_warnings and not p.recognized:
    if not p.recognized:
        print 'Unrecognized file "%s"' % name
    return p

def extract_sensor_from_headers_list(headers):
    """extract sensor part of string from list of header files

    Returns list with items: sensor part if matches regex pattern; otherwise, empty string.

    >>> a = '/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f0A/2013_01_02_00_08_27.913-2013_01_02_01_25_23.117.121f0A.header'
    >>> b = '/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f0B/2013_01_02_00_08_27.913-2013_01_02_01_25_23.117.121f0B.header'
    >>> c = 'seesaw'
    >>> d = 'stringcheese'
    >>> extract_sensor_from_headers_list([a, b, c, d]) # headers = [a, b, c, d]
    ['121f0A', '121f0B', '', '']
    >>> extract_sensor_from_headers_list([c, a, d])    # headers = [c, a, d]
    ['', '121f0A', '']

    """    
    def get_sensor_part(hdr_file):
        result = ''
        if hdr_file:
            m = re.match(_PADHEADERFILES_PATTERN, hdr_file)
            if m: result = m.group('sensor')
        return result
    sensors = [ get_sensor_part(x) for x in headers ]    
    return sensors

def listdir_filename_pattern(dirpath, fname_pattern):
    """Listdir files that match fname_pattern."""
    if not os.path.exists(dirpath):
        return None
    files = [os.path.join(dirpath, f) for f in os.listdir(dirpath) if re.match(fname_pattern, f)]
    files.sort()
    return files

def filter_filenames(dirpath, predicate):
    """
    #>>> filePattern = '\d{14}.\d{14}/\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}.\d{3}.\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}.\d{3}.*'
    #>>> dirpath = '/misc/jaxa'
    #>>> predicate = re.compile(r'/misc/jaxa/' + filePattern).match
    #>>> for filename in filter_filenames(dirpath, predicate): print filename
    """
    for root, dirnames, filenames in os.walk(dirpath):
        for filename in filenames:
            abspath = os.path.join(root, filename)
            if predicate(abspath):
                yield abspath

# transfer file uploaded (by JAXA) FROM fromdir TO todir
def ike_jaxa_file_transfer(fromdir, todir):
    """transfer file uploaded (by JAXA) FROM fromdir TO todir"""
    pass

def demo():
    dirpath = '/misc/yoda/pub/pad/year2015/month03/day17'
    sensor_subdir = 'sams2_accel_121f03'
    fullfile_pattern = '(?P<ymdpath>/misc/yoda/pub/pad/year\d{4}/month\d{2}/day\d{2}/)(?P<subdir>.*_(?P<sensor>.*))/(?P<start>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})(?P<pm>[\+\-])(?P<stop>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})\.(?P=sensor)\.header\Z'
    big_list = [ x for x in filter_filenames(dirpath, re.compile(fullfile_pattern).match) if x.endswith('121f03.header')]
    for f in big_list: #filter_filenames(dirpath, re.compile(fullfile_pattern).match):
        print f

#demo()
#raise SystemExit

# remove files in folder that are older than numdays
def remove_old_files(folder, numdays):
    """remove files in folder that are older than numdays"""
    now = time.time()
    cutoff = now - (numdays * 86400)
    files = os.listdir(folder)
    for f in files:
        fullfile = os.path.join(folder, f)
        if os.path.isfile( fullfile ):
            t = os.stat( fullfile )
            c = t.st_ctime
            # delete f if older than numdays
            if c < cutoff:
                print 'removing %s' % fullfile
                #os.remove( fullfile )
            else:
                print 'keeping %s' % fullfile

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    