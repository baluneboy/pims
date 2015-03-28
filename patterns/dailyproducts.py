#!/usr/bin/env python

# FIXME the file separator character (slash) is for Linux and Mac (not Windows)

__all__ = [
    '_PADHEADERFILES_PATTERN',
    '_BATCHROADMAPS_PATTERN',
    ]

_YODAPATH  = "/misc/yoda"
_PLOTSPATH = "/misc/yoda/www/plots"

###############################################################################################################################
#/misc/yoda/pub/pad/year2013/month11/day01/sams2_accel_121f05/2013_11_01_23_52_29.944-2013_11_02_00_02_29.959.121f05.header
_PADPATH_PATTERN = "(?P<ymdpath>%s/pub/pad/year(?P<year>\d{4})/month(?P<month>\d{2})/day(?P<day>\d{2}))" % _YODAPATH
_PADHEADERFILES_PATTERN = _PADPATH_PATTERN + (
    "/(?P<subdir>.*_accel_(?P<sensor>.*))/"                             # subdir
    "(?P<start>(?P=year)_(?P=month)_(?P=day)_\d{2}_\d{2}_\d{2}\.\d{3})" # underscore-delimited start part of fname, then
    "(?P<pm>[\+\-])"                                                    # plus/minus
    "(?P<stop>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})"              # underscore-delimited stop part of fname, then
    "\.(?P=sensor)"                                                     # dot sensor
    "\.header\Z"                                                        # extension to finish
    )

'(?P<ymdpath>/misc/yoda/www/plots/batch/year(?P<year>\d{4})/month(?P<month>\d{2})/day(?P<day>\d{2}))/(?P<start>(?P=year)_(?P=month)_(?P=day)_\d{2}(_\d{2}_\d{2}\.\d{3}|))_(?P<sensor>.*)_((?P<abbrev>.*)_roadmaps(?P<rate>.*)\.pdf|roadmap\.pdf)'
###############################################################################################################################
#/misc/yoda/www/plots/batch/year2013/month09/day29/2013_09_29_00_00_00.000_121f03_spgs_roadmaps500.pdf
_BATCHPATH_PATTERN = "(?P<ymdpath>%s/www/plots/batch/year(?P<year>\d{4})/month(?P<month>\d{2})/day(?P<day>\d{2}))" % _YODAPATH
_BATCHROADMAPS_PATTERN = _BATCHPATH_PATTERN + (
    "/(?P<start>(?P=year)_(?P=month)_(?P=day)_\d{2}(_\d{2}_\d{2}\.\d{3}|))" # underscore-delimited dtm part of fname, then
    "_(?P<sensor>.*)_((?P<abbrev>.*)_roadmaps(?P<rate>.*)|roadmap)"         # placeholders for sensor, plot type, rate, then
    "\.pdf\Z"                                                               # pdf extension to finish
    )
##_BATCHPATH_PATTERN = "(?P<ymdpath>%s/www/plots/batch/year(?P<year>\d{4})/month(?P<month>\d{2})/day(?P<day>\d{2}))" % _YODAPATH
##_BATCHROADMAPS_PATTERN = _BATCHPATH_PATTERN + (
##    "/(?P<start>(?P=year)_(?P=month)_(?P=day)_\d{2}_\d{2}_\d{2}\.\d{3})" # underscore-delimited dtm part of fname, then
##    "_(?P<sensor>.*)_(?P<abbrev>.*)_roadmaps(?P<rate>.*)"                # placeholders for sensor, plot type, rate, then
##    "\.pdf\Z"                                                            # pdf extension to finish
##    )

###############################################################################################################################
#/misc/yoda/tmp/ike/offline/batch/results/year2013/month11/day26/hirap/pcsa/2013_11_26_16_00_hirap_spgs+roadmaps.mat
_BATCHPCSAPATH_PATTERN = "(?P<ymdpath>%s/tmp/ike/offline/batch/results/year(?P<year>\d{4})/month(?P<month>\d{2})/day(?P<day>\d{2}))/.*/pcsa" % _YODAPATH
_BATCHPCSAMAT_PATTERN = _BATCHPCSAPATH_PATTERN + (
    "/\d{4}_(\d{2}_){4}.*_.*\+roadmaps"                                  # underscore-delimited dtm part of fname, then
    "\.mat\Z"                                                            # pdf extension to finish
    )
#(?P<ymdpath>/misc/yoda/tmp/ike/offline/batch/results/year(?P<year>\d{4})/month(?P<month>\d{2})/day(?P<day>\d{2}))/.*/pcsa/\d{4}_(\d{2}_){4}.*_.*\+roadmaps\.mat

###############################################################################################################################
#/misc/yoda/www/plots/sams/params/121f05_intrms.csv
_JAXACSV_DIRPATTERN = "(?P<params_path>%s/sams/params)" % _PLOTSPATH
_JAXACSV_FILEPATTERN = (
    "(?P<sensor>.*)_(?P<plot_type>.*)"  # sensor underscore plot_type
    "\.csv\Z"                            # csv extension to finish
    )
#print _JAXACSV_FILEPATTERN; raise SystemExit

#~~~~~~~~~~~~~~~~~~~~   #~~~~~~~~~~~~~~~~~~~~   #~~~~~~~~~~~~~~~~~~~~   #~~~~~~~~~~~~~~~~~~~~   #~~~~~~~~~~~~~~~~~~~~

def match_pattern_demo(fname, pat):
    """Check for match."""
    import re
    return re.match(pat, fname)

if __name__ == "__main__":
    #m = match_pattern_demo('/misc/yoda/www/plots/batch/year2013/month09/day29/2013_09_29_00_00_00.000_121f03_spgs_roadmaps500.pdf', _BATCHROADMAPS_PATTERN)
    #print m.group('sensor'), m.group('dtm')

    #/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f05006/2013_01_02_05_16_08.758+2013_01_02_05_29_47.061.121f05006.header
    #(?P<ymdpath>.*)(?P<start>\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})(?P<pm>[\+\-])(?P<stop>d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2}\.\d{3})\.(?P<sensor>.*f0[358].*)\.header

    #---------------------------------------------------
    m = match_pattern_demo('/misc/yoda/pub/pad/year2013/month01/day02/sams2_accel_121f05006/2013_01_02_00_08_27.913-2013_01_02_01_25_23.117.121f05006.header', _PADHEADERFILES_PATTERN)
    if m:
        print m.group('sensor'), m.group('start')
    else:
        print 'no match'
        
    #---------------------------------------------------
    m = match_pattern_demo('/misc/yoda/www/plots/batch/year2013/month10/day01/2013_10_01_08_00_00.000_121f03_spgs_roadmaps500.pdf', _BATCHROADMAPS_PATTERN)
    if m:
        print m.group('sensor'), m.group('start')
    else:
        print 'no match'