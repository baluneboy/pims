import os
import re
import glob
import time
import errno
import shutil
import hashlib
import pandas as pd
from pims.files.base import File, UnrecognizedPimsFile
from pims.patterns.handbookpdfs import is_unique_handbook_pdf_match
from pims.patterns.dailyproducts import _BATCHROADMAPS_PATTERN, _PADHEADERFILES_PATTERN
from pims.utils.pimsdateutil import timestr_to_datetime, ymd_pathstr_to_date
from pims.strings.utils import remove_non_ascii


def get_immediate_subdirs(a):
    return [name for name in os.listdir(a) if os.path.isdir(os.path.join(a, name))]


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


def extract_between_lines_as_list(text_file, line1, line2):
    with open(text_file, 'rb') as f:
        textfile_temp = f.read()
        if line1 and line2:
            s = textfile_temp.split(line1 + '\n')[1].split('\n' + line2)[0]
        elif not line1 and line2:
            s = textfile_temp.split('\n' + line2)[0]
        elif line1 and not line2:
            s = textfile_temp.split(line1 + '\n')[1]
        else:
            s = textfile_temp
        return s.split('\n')

    
def most_recent_file_with_suffix(pth, suffix):
    """get most recent file along pth that ends with suffix"""
    files = [ os.path.join(pth, f) for f in os.listdir(pth) if f.endswith(suffix) ]
    files.sort(key=lambda x: os.path.getmtime(x))
    return os.path.join(pth, files[-1])


def get_pathpattern_files(pth, pat):
    """get list of files in directory, pth, matching regular expression, pat"""
    # pth = '/Users/ken/Pictures/foscam'
    # pat = r'\d{4}-\d{2}-\d{2}_\d{2}_\d{2}_(open|close)\.jpg' # LIKE 2017-11-09_06_07_close.jpg
    files = [f for f in os.listdir(pth) if re.match(pat, f)]
    return files


def get_lines_between(beginstr, endstr, filename, include_newlines=True):
    """get file lines between two delimiter strings"""
    if include_newlines:
        beginstr += '\n'
        endstr = '\n' + endstr
    with open(filename, 'r') as f:
        temp = f.read()
        s = temp.split(beginstr)[1].split(endstr)[0]
    return s

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
    >>> sensor = '121f03'
    >>> fullfile_pattern = r'(?P<ymdpath>/misc/yoda/pub/pad/year\d{4}/month\d{2}/day\d{2}/)(?P<subdir>.*_%s)/(?P<start>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})(?P<pm>[\+\-])(?P<stop>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})\.%s\Z' % (sensor, sensor)
    >>> dirpath = '/misc/yoda/pub/pad/year2015/month03/day17'
    >>> for f in list(filter_filenames(dirpath, re.compile(fullfile_pattern).match))[0:5]: print f
    /misc/yoda/pub/pad/year2015/month03/day17/sams2_accel_121f03/2015_03_17_00_06_05.702+2015_03_17_00_16_05.708.121f03
    /misc/yoda/pub/pad/year2015/month03/day17/sams2_accel_121f03/2015_03_17_00_16_05.710+2015_03_17_00_26_05.719.121f03
    /misc/yoda/pub/pad/year2015/month03/day17/sams2_accel_121f03/2015_03_17_00_26_05.721+2015_03_17_00_36_05.728.121f03
    /misc/yoda/pub/pad/year2015/month03/day17/sams2_accel_121f03/2015_03_17_00_36_05.730+2015_03_17_00_46_05.737.121f03
    /misc/yoda/pub/pad/year2015/month03/day17/sams2_accel_121f03/2015_03_17_00_46_05.739+2015_03_17_00_56_05.747.121f03
    >>> # EXAMPLE 2 ---------------------------------------------------------
    >>> from pims.patterns.probepats import _ROADMAP_PDF_FILENAME_PATTERN
    >>> dirpath = os.path.join('/misc/yoda/www/plots/batch', 'year2015/month03/day17')
    >>> pat = '.*' + _ROADMAP_PDF_FILENAME_PATTERN
    >>> for f in list(filter_filenames(dirpath, re.compile(pat).match))[0:5]: print f
    /misc/yoda/www/plots/batch/year2015/month03/day17/2015_03_17_00_00_00.000_121f03one_spgs_roadmaps142.pdf
    /misc/yoda/www/plots/batch/year2015/month03/day17/2015_03_17_00_00_00.000_121f03one_spgx_roadmaps142.pdf
    /misc/yoda/www/plots/batch/year2015/month03/day17/2015_03_17_00_00_00.000_121f03one_spgy_roadmaps142.pdf
    /misc/yoda/www/plots/batch/year2015/month03/day17/2015_03_17_00_00_00.000_121f03one_spgz_roadmaps142.pdf
    /misc/yoda/www/plots/batch/year2015/month03/day17/2015_03_17_08_00_00.000_121f03one_spgs_roadmaps142.pdf
    >>> # EXAMPLE 3 ---------------------------------------------------------
    >>> from pims.patterns.probepats import _OSSBTMF_ROADMAP_PDF_FILENAME_PATTERN
    >>> dirpath = os.path.join('/misc/yoda/www/plots/batch', 'year2016/month07/day01')
    >>> pat = '.*' + _OSSBTMF_ROADMAP_PDF_FILENAME_PATTERN
    >>> for f in list(filter_filenames(dirpath, re.compile(pat).match))[0:3]: print f
    /misc/yoda/www/plots/batch/year2016/month07/day01/2016_07_01_00_ossbtmf_roadmap.pdf
    /misc/yoda/www/plots/batch/year2016/month07/day01/2016_07_01_08_ossbtmf_roadmap.pdf
    /misc/yoda/www/plots/batch/year2016/month07/day01/2016_07_01_16_ossbtmf_roadmap.pdf
    """
    for root, dirnames, filenames in os.walk(dirpath):
        for filename in filenames:
            abspath = os.path.join(root, filename)
            if predicate(abspath):
                yield abspath

def filter_dirnames(dirpath, predicate):
    """
    >>> subdirPattern = 'sams2_accel_121f0[28].*'
    >>> dirpath = r'/misc/yoda/pub/pad/year2016/month01/day01'
    >>> predicate = re.compile(os.path.join(dirpath, subdirPattern)).match
    >>> for dirname in filter_dirnames(dirpath, predicate): print dirname
    /misc/yoda/pub/pad/year2016/month01/day01/sams2_accel_121f08
    /misc/yoda/pub/pad/year2016/month01/day01/sams2_accel_121f02
    /misc/yoda/pub/pad/year2016/month01/day01/sams2_accel_121f08006
    /misc/yoda/pub/pad/year2016/month01/day01/sams2_accel_121f02006
    """
    for root, dirnames, filenames in os.walk(dirpath):
        for dirname in dirnames:
            abspath = os.path.join(root, dirname)
            #print abspath
            if predicate(abspath):
                yield abspath

def glob_padheaders(ymdpat, subdirpat, filepat='*.header', padbase=r'/misc/yoda/pub/pad'):
    """
    >>> ymdpat = r'year2017/month04/day01'
    >>> subdirpat = r'sams2_accel_121f0[23]'
    >>> for hdrfile in glob_padheaders(ymdpat, subdirpat)[0:3]: print hdrfile
    /misc/yoda/pub/pad/year2017/month04/day01/sams2_accel_121f03/2017_04_01_00_05_02.943+2017_04_01_00_15_02.945.121f03.header
    /misc/yoda/pub/pad/year2017/month04/day01/sams2_accel_121f03/2017_04_01_00_15_02.947+2017_04_01_00_25_02.949.121f03.header
    /misc/yoda/pub/pad/year2017/month04/day01/sams2_accel_121f03/2017_04_01_00_25_02.951+2017_04_01_00_35_02.955.121f03.header
    """
    glob_pattern = os.path.join(padbase, ymdpat, subdirpat, filepat)
    return glob.glob(glob_pattern)

def glob_paddirs(ymdpat, subdirpat, padbase=r'/misc/yoda/pub/pad'):
    """
    >>> ymdpat = r'year201[24]/month03/day2[2-4]'
    >>> subdirpat = r'sams2_accel_121f0[23]'
    >>> for dirname in glob_paddirs(ymdpat, subdirpat): print dirname
    /misc/yoda/pub/pad/year2012/month03/day22/sams2_accel_121f02
    /misc/yoda/pub/pad/year2012/month03/day22/sams2_accel_121f03
    /misc/yoda/pub/pad/year2012/month03/day23/sams2_accel_121f02
    /misc/yoda/pub/pad/year2012/month03/day23/sams2_accel_121f03
    /misc/yoda/pub/pad/year2012/month03/day24/sams2_accel_121f02
    /misc/yoda/pub/pad/year2012/month03/day24/sams2_accel_121f03
    /misc/yoda/pub/pad/year2014/month03/day22/sams2_accel_121f02
    /misc/yoda/pub/pad/year2014/month03/day22/sams2_accel_121f03
    /misc/yoda/pub/pad/year2014/month03/day23/sams2_accel_121f02
    /misc/yoda/pub/pad/year2014/month03/day23/sams2_accel_121f03
    /misc/yoda/pub/pad/year2014/month03/day24/sams2_accel_121f02
    /misc/yoda/pub/pad/year2014/month03/day24/sams2_accel_121f03
    """
    glob_pattern = os.path.join(padbase, ymdpat, subdirpat)
    return glob.glob(glob_pattern)

def grep_r(pattern, topdir):
    r = re.compile(pattern)
    for parent, dnames, fnames in os.walk(topdir):
        for fname in fnames:
            filename = os.path.join(parent, fname)
            if os.path.isfile(filename):
                with open(filename) as f:
                    for line in f:
                        if r.search(line):
                            yield line

# transfer file uploaded (by JAXA) FROM fromdir TO todir
def ike_jaxa_file_transfer(fromdir, todir):
    """transfer file uploaded (by JAXA) FROM fromdir TO todir"""
    pass

def demofiltfiles():
    dirpath = '/misc/yoda/pub/pad/year2015/month03/day17'
    sensor_subdir = 'sams2_accel_121f03'
    fullfile_pattern = '(?P<ymdpath>/misc/yoda/pub/pad/year\d{4}/month\d{2}/day\d{2}/)(?P<subdir>.*_(?P<sensor>.*))/(?P<start>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})(?P<pm>[\+\-])(?P<stop>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})\.(?P=sensor)\.header\Z'
    big_list = [ x for x in filter_filenames(dirpath, re.compile(fullfile_pattern).match) if x.endswith('121f03.header')]
    for f in big_list: #filter_filenames(dirpath, re.compile(fullfile_pattern).match):
        print f

#demofiltfiles()
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


def get_md5(my_file, blocksize=65536):
    hasher = hashlib.md5()
    with open(my_file, 'rb') as afile:
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
    md5str = hasher.hexdigest()
    return md5str


def find_needles_in_haystack(dailyhistmats, roadmaps):
    """return subset list of files from roadmaps that match dates in list of files in dailyhistmats"""
    
    # a set of "needles" are read from dailyhistmats file
    with open(dailyhistmats, 'r') as dh_file: dh_list = dh_file.read().splitlines()
    needles = set([ymd_pathstr_to_date(f) for f in dh_list])
    
    # a list for "haystack" is read from roadmaps file
    with open(roadmaps, 'r') as rp_file: rp_list = rp_file.read().splitlines()
    haystack = [ymd_pathstr_to_date(f) for f in rp_list]
    
    # find indices of needles in haystack
    idx = [i for i, e in enumerate(haystack) if e in needles]
    
    # return subset list of files from roadmaps
    return [rp_list[i] for i in idx]


def demo_needles_haystack():
    dailyhistpad_fname = '/home/pims/Documents/CIR_PaRIS_Based_on_es05_spgs_below_20Hz_QUIETER.txt'
    roadmap_fname = '/home/pims/Documents/CIR_PaRIS_Based_on_es05_spgs_below_20hz_map_large_outPDF.txt'
    matched_list = find_needles_in_haystack(dailyhistpad_fname, roadmap_fname)
    print 'pdfunite ' + ' '.join(matched_list)


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    