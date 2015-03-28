
__all__ = [
    '_HANDBOOKDIR_PATTERN',
    ]

#\A(?P<parentdir>.*)/hb_(?P<regime>vib|qs)_(?P<category>\w+?)_(?P<title>.*)$
_HANDBOOKDIR_PATTERN = (
    "\A(?P<parentdir>.*)/hb_"                   # parentdir slash hb underscore to start string
    "(?P<regime>vib|qs)_"                       # enum for regime underscore, then
    "(?P<category>\w+?)_"                       # non-greedy alphanum for category underscore, then
    "(?P<title>.*)\Z"                           # any title to finish string
    )

#(?P<sensor_dir>(?P<pad_dir>.*)/year\d{4}/month\d{2}/day\d{2}/(?P<sensor_subdir>(?P<system>.*)_(accel|rad)_.*))/(?P<Y1>\d{4})_(?P<M1>\d{2})_(?P<D1>\d{2})_(?P<h1>\d{2})_(?P<m1>\d{2})_(?P<s1>\d{2})\.(?P<ms1>\d{3})(?P<pm>[\+-])(?P<Y2>\d{4})_(?P<M2>\d{2})_(?P<D2>\d{2})_(?P<h2>\d{2})_(?P<m2>\d{2})_(?P<s2>\d{2})\.(?P<ms2>\d{3})\.(?P<sensor>.*)\.header\Z
_HEADER_PATTERN = (
    "(?P<sensor_dir>(?P<pad_dir>.*)/year\d{4}/month\d{2}/day\d{2}/(?P<sensor_subdir>(?P<system>.*)_(accel|rad)_.*))/" # partitioned to sensor subdir slash
    "(?P<start_str>(?P<Y1>\d{4})_(?P<M1>\d{2})_(?P<D1>\d{2})_(?P<h1>\d{2})_(?P<m1>\d{2})_(?P<s1>\d{2})\.(?P<ms1>\d{3}))" # start time underscore delimited
    "(?P<pm>[\+-])" # plus or minus                       
    "(?P<stop_str>(?P<Y2>\d{4})_(?P<M2>\d{2})_(?P<D2>\d{2})_(?P<h2>\d{2})_(?P<m2>\d{2})_(?P<s2>\d{2})\.(?P<ms2>\d{3}))" # end   time underscore delimited
    "\.(?P<sensor>.*)\.header\Z" # string ends with sensor.header
    )

if __name__ == '__main__':
    import re
    input_value = '/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f03/2013_01_02_00_01_02.210+2013_01_02_00_11_02.214.121f03.header'
    m = re.compile(_HEADER_PATTERN).match(input_value)
    if m is None:
        raise ValueError('Invalid literal for _HANDBOOKDIR_PATTERN: %r' % input_value)
    else:
        print '"%s" matches _HEADER_PATTERN' % input_value
        print m.group('Y1')
        print m.group('ms1')
        print m.group('start_str')
