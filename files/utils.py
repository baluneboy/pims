import os
import re
import time
import errno
import shutil
import pandas as pd
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

# get file lines between two delimiter strings
def get_lines_between(beginstr, endstr, filename, include_newlines=True):
    """get file lines between two delimiter strings"""
    if include_newlines:
        beginstr += '\n'
        endstr = '\n' + endstr
    with open(filename, 'r') as f:
        temp = f.read()
        s = temp.split(beginstr)[1].split(endstr)[0]
    return s

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

def reshape_csv_file(csv_file, shape_tuple):
    # reshape the data
    df = pd.read_csv(csv_file)
    data = df.values
    a = data.reshape(shape_tuple)
    df_new = pd.DataFrame(a)
    
    # write new shaped data to new csv file
    new_file = csv_file + '.RESHAPED.csv'
    df_new.to_csv(new_file, index=False, header=False)
    print 'wrote ' + new_file

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

def tuplify_headers(headers):
    """convert list of header files to list of (year..., path) tuples

    Returns list of tuples like [('year2015/month03...', '/misc/yoda/pub/'), etc.]

    >>> a = '/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f0A/2013_01_02_00_08_27.913-2013_01_02_01_25_23.117.121f0A.header'
    >>> b = '/data/pad/year2013/month01/day02/sams2_accel_121f0C/2013_01_02_00_08_27.913-2013_01_02_01_25_23.117.121f0C.header'
    >>> c = 'stringcheese'
    >>> tuplify_headers([a, b, c])
    [('year2013/month01/day02/sams2_accel_121f0A/2013_01_02_00_08_27.913-2013_01_02_01_25_23.117.121f0A.header', '/misc/yoda/pub/pad/'), ('year2013/month01/day02/sams2_accel_121f0C/2013_01_02_00_08_27.913-2013_01_02_01_25_23.117.121f0C.header', '/data/pad/'), (None, None)]

    """
    def get_path_part(hdr_file):
        pat = _PADHEADERFILES_PATTERN.replace('/misc/yoda/pub/pad', '.*/pad')
        result = ''
        if hdr_file:
            m = re.match(pat, hdr_file)
            if m: result = m.group('ymdpath')
        return result.split('year')[0]
    tups = []
    for h in headers:
        path_part = get_path_part(h)
        if path_part:
            tups.append( (h.replace(path_part, ''), path_part) )
        else:
            tups.append( (None, None) )
    return tups

def extract_sensor_from_headers_list(headers):
    """extract sensor part of string from list of header files

    Returns list with items: sensor part if matches regex pattern; otherwise, empty string.

    >>> a = '/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f0A/2013_01_02_00_08_27.913-2013_01_02_01_25_23.117.121f0A.header'
    >>> b = '/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f0B/2013_01_02_00_08_27.913-2013_01_02_01_25_23.117.121f0B.header'
    >>> c = '/data/pad/year2013/month01/day02/sams2_accel_121f0C/2013_01_02_00_08_27.913-2013_01_02_01_25_23.117.121f0C.header'
    >>> d = 'stringcheese'
    >>> extract_sensor_from_headers_list([a, b, b, c, d]) # headers = [a, b, b, c, d]
    ['121f0A', '121f0B', '121f0B', '121f0C', '']
    >>> extract_sensor_from_headers_list([c, a, d])    # headers = [c, a, d]
    ['121f0C', '121f0A', '']

    """    
    def get_sensor_part(hdr_file):
        pat = _PADHEADERFILES_PATTERN.replace('/misc/yoda/pub/pad', '.*/pad')
        result = ''
        if hdr_file:
            m = re.match(pat, hdr_file)
            if m: result = m.group('sensor')
        return result
    sensors = [ get_sensor_part(x) for x in headers ]    
    return sensors

def mkdir_original_for_trim(header_file):
    """mkdir for this sensor/day from fullpath header_file

    Returns string for newly created "original" subdir.

    >>> header_file = '/misc/yoda/test/pad/year2015/month03/day20/sams2_accel_121f02/2015_03_20_00_01_27.307+2015_03_20_00_11_27.321.121f02.header'
    >>> mkdir_original_for_trim(header_file)
    '/misc/yoda/test/pad/year2015/month03/day20/sams2_accel_121f02/original'
    >>> hdr_file = '/misc/yoda/test/pad/year2015/month03/day22/sams2_accel_121f08/2015_03_22_23_55_23.946+2015_03_23_00_05_23.960.121f08.header'
    >>> mkdir_original_for_trim(hdr_file)
    '/misc/yoda/test/pad/year2015/month03/day22/sams2_accel_121f08/original'

    """
    new_path = os.path.join(os.path.dirname(header_file), 'original')
    mkdir_p(new_path)
    return new_path

def move_pad_pair(header_file, dest_dir):
    """move header_file and its data file to destination directory

    Returns string for header_file on its new path.

    #>>> dest_dir = '/misc/yoda/test/pad/year2015/month03/day20/sams2_accel_121f02/original'
    #>>> header_file = '/misc/yoda/test/pad/year2015/month03/day20/sams2_accel_121f02/2015_03_20_00_01_27.307+2015_03_20_00_11_27.321.121f02.header'
    #>>> move_pad_pair(header_file, dest_dir)
    #'/misc/yoda/test/pad/year2015/month03/day20/sams2_accel_121f02/original/2015_03_20_00_01_27.307+2015_03_20_00_11_27.321.121f02.header'

    """    
    if not os.path.isdir(dest_dir):
        raise Exception('destination directory "%s" does not exist' % dest_dir)
    shutil.move(header_file, dest_dir)                    # move header file
    shutil.move(header_file.rstrip('.header'), dest_dir)  # move data file
    return os.path.join(dest_dir, os.path.basename(header_file))

def listdir_filename_pattern(dirpath, fname_pattern):
    """Get list of files that match fname_pattern."""
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

def filter_dirnames(dirpath, predicate):
    """
    >>> subdirPattern = 'sams2_accel_121f0[28].*'
    >>> dirpath = r'/misc/yoda/pub/pad/year2015/month01/day01'
    >>> predicate = re.compile(os.path.join(dirpath, subdirPattern)).match
    >>> for dirname in filter_dirnames(dirpath, predicate): print dirname
    /misc/yoda/pub/pad/year2015/month01/day01/sams2_accel_121f02
    /misc/yoda/pub/pad/year2015/month01/day01/sams2_accel_121f02006
    /misc/yoda/pub/pad/year2015/month01/day01/sams2_accel_121f08
    /misc/yoda/pub/pad/year2015/month01/day01/sams2_accel_121f08006
    """
    for root, dirnames, filenames in os.walk(dirpath):
        for dirname in dirnames:
            abspath = os.path.join(root, dirname)
            #print abspath
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
    