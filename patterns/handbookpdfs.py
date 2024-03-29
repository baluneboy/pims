# For new handbook PDF type, do the following here:
# 1. Add it's name as string to __all__ near top
# 2. Add it's regex pattern info section below
# 3. Use Rx helper to verify good matching
# 4. Add new class in handbook.py

__all__ = [
    '_HANDBOOKPDF_PATTERN',
    '_OSSBTMFROADMAPPDF_PATTERN',
    '_RADGSEROADMAPNUP1X2PDF_PATTERN',    
    '_SPGXROADMAPPDF_PATTERN',
    '_SPGXPLOTPDF_PATTERN',
    '_INTSTATPDF_PATTERN',
    '_PLOTTYPES',
    '_ABBREVS',
    '_PSD3ROADMAPPDF_PATTERN',
    '_GVT3PDF_PATTERN',
    '_CHIMPDF_PATTERN',
    '_CVFSROADMAPPDF_PATTERN',
    '_RVTXPDF_PATTERN',
    '_SUFFIX_CALLOUTS',
    ]

#/tmp/pth/1qualify_notes.pdf
#---------------------------
#.*/(?P<page>\d{1})(?P<subtitle>qualify|quantify)_(?P<notes>.*)\.pdf\Z
#.*/(?P<page>\d{2})(?P<subtitle>qualify|quantify)_(?P<start>[0-9_\.]+)_(?P<sensor>[a-z0-9]+)_(?P<plot_type>spg.|gvt.|rvt.|imm|irms|pcs.)_(?P<notes>.*)\.pdf
_OLD_HANDBOOKPDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<page>\d{2})"                           # a digit OR A to Z single char, then
    "(?P<subtitle>qualify|quantify)_"           # enum for subtitle underscore, then
    "(?P<start>[0-9_\.]+)_"                     # start time underscore, then
    "(?P<sensor>[a-z0-9]+)_"                    # sensor underscore, then
    "(?P<plot_type>spg.|gvt.|rvt.|imm|irms|pcs.)_"  # plot abbreviation underscore, then
    "(?P<notes>.*)"                             # notes, then
    "\.pdf\Z"                                   # extension to finish
    )

#---------------------------
#.*/(?P<start>[0-9_\.]+)_(?P<sensor>[a-z0-9]+)_(?P<plot_type>spg.|gvt.|rvt.|imm|irms|pcs.)_(?P<notes>.*)\.pdf
_HANDBOOKPDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<start>[0-9_\.]+)_"                     # start time underscore, then
    "(?P<sensor>[a-z0-9]+?)"                    # sensor, then << non-greedy trailing question mark FTW
    "(?P<sensorsuffix>ten|one|006|)_"           # suffix (or empty) underscore, then
    "(?P<plot_type>iav.|psd.|spg.|gvt.|rvt.|imm.|irms|pcs.)_"  # plot abbreviation underscore, then
    "(?P<notes>.*)"                             # notes, then
    "\.pdf\Z"                                   # extension to finish
    )

# ---------------------------
# _SUFFIX_CALLOUTS = (
#    ".*/"                                       # path at the start, then
#    "(?P<page>\d{1}|[A-Z])"                     # a digit OR A to Z single char, then
#    "(?P<subtitle>qualify|quantify)"            # enum for subtitle, then
#    "_"                                         # underscore, then
#    "(?P<notes>.*)"                             # notes, then
#    "_xoff_(?P<xoffset>[-+]?\d*\.\d+|\d+)"      # xoffset in cm, then
#    "_yoff_(?P<yoffset>[-+]?\d*\.\d+|\d+)"      # yoffset in cm, then
#    "_scale_(?P<scale>[-+]?\d*\.\d+|\d+)"       # scale, then
#    "_ori_(?P<orient>portrait|landscape)"       # orientation portrait or landscape, then    
#    "\.pdf\Z"                                   # extension to finish
#    )

#/tmp/pth/3qualify_2013_09_01_121f05006_irmsy_entire_month.pdf
#-------------------------------------------------------------
#.*(?P<page>\d{1})(?P<subtitle>qualify|quantify)_(?P<timestr>[\d_\.]*)_(?P<sensor>.*)_(?P<plot_type>imm|irms)(?P<axis>.)_(?P<notes>.*)\.pdf
_INTSTATPDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<page>\d{1}|[A-Z])"                     # a digit OR A to Z single char, then
    "(?P<subtitle>qualify|quantify)"            # enum for subtitle, then
    "_"                                         # underscore, then
    "(?P<timestr>[\d_\.]*)"                     # timestr, then    
    "_"                                         # underscore, then
    "(?P<sensor>.*)"                            # sensor, then
    "_(?P<plot_type>imm|irms)"                  # underscore iabbrev, then
    "(?P<axis>.)"                               # axis, then
    "_(?P<notes>.*)"                            # underscore notes, then
    "\.pdf\Z"                                   # extension to finish
    )

#/tmp/pth/4quantify_2013_09_28_16_radgse_roadmapnup1x2.pdf
#---------------------------------------------------------------
#.*/(?P<page>\d{1})(?P<subtitle>qualify|quantify)_(?P<timestr>.*)_(?P<sensor>radgse)_roadmapnup1x2(?P<notes>.*)\.pdf\Z
_RADGSEROADMAPNUP1X2PDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<page>\d{1}|[A-Z])"                     # a digit OR A to Z single char, then
    "(?P<subtitle>qualify|quantify)"            # enum for subtitle, then
    "_"                                         # underscore, then
    "(?P<timestr>.*)"                           # timestr, then    
    "_"                                         # underscore, then
    "(?P<sensor>radgse)"                        # sensor, then
    "_roadmapnup1x2"                            # underscore roadmapnup1x2, then
    "(?P<notes>.*)"                             # notes, then
    "\.pdf\Z"                                   # extension to finish
    )

#/tmp/pth/2quantify_2013_10_01_08_ossbtmf_roadmap+some_notes.pdf
#---------------------------------------------------------------
#.*/(?P<page>\d{1})(?P<subtitle>qualify|quantify)_(?P<timestr>.*)_(?P<sensor>ossbtmf)_roadmap(?P<notes>.*)\.pdf\Z
_OSSBTMFROADMAPPDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<page>\d{1}|[A-Z])"                     # a digit OR A to Z single char, then
    "(?P<subtitle>qualify|quantify)"            # enum for subtitle, then
    "_"                                         # underscore, then
    "(?P<timestr>.*)"                           # timestr, then    
    "_"                                         # underscore, then
    "(?P<sensor>ossbtmf)"                       # sensor, then
    "_roadmap"                                  # underscore roadmap, then
    "(?P<notes>.*)"                             # notes, then
    "\.pdf\Z"                                   # extension to finish
    )

#/tmp/1qualify_2013_10_01_16_00_00.000_121f02ten_spgs_roadmaps500.pdf
#--------------------------------------------------------------------
#.*/(?P<page>\d{1})(?P<subtitle>qualify|quantify)_(?P<timestr>.*)_(?P<sensor>.*)_(?P<plot_type>\w*)(?P<axis>.)_roadmaps(?P<sample_rate>[0-9]*[p\.]?[0-9]+)(?P<notes>.*)\.pdf\Z
_SPGXROADMAPPDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<page>\d{1}|[A-Z])"                     # a digit OR A to Z single char, then
    "(?P<subtitle>qualify|quantify)"            # enum for subtitle, then
    "_"                                         # underscore, then
    "(?P<timestr>.*)"                           # timestr, then    
    "_"                                         # underscore, then
    "(?P<sensor>.*)"                            # sensor, then
    "_(?P<plot_type>spg)"                       # underscore spg, then
    "(?P<axis>.)"                               # axis, then
    "_roadmaps"                                 # underscore roadmaps, then
    "(?P<sample_rate>[0-9]*[p\.]?[0-9]+)"       # zero or more digits, zero or one pee or dot, one or more digit, then
    "(?P<notes>.*)"                             # notes, then
    "\.pdf\Z"                                   # extension to finish
    )

#/tmp/4qualify_2015_05_14_13_30_00_121f05_spgs_airlock_hatch_activities
#--------------------------------------------------------------------
#
_SPGXPLOTPDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<page>\d{1}|[A-Z])"                     # a digit OR A to Z single char, then
    "(?P<subtitle>qualify|quantify)"            # enum for subtitle, then
    "_"                                         # underscore, then
    "(?P<timestr>.*)"                           # timestr, then    
    "_"                                         # underscore, then
    "(?P<sensor>.*)"                            # sensor, then
    "_(?P<plot_type>spg)"                       # underscore spg, then
    "(?P<axis>.)"                               # axis, then
    "_"                                         # underscore, then
    "(?P<notes>.*)"                             # notes, then
    "\.pdf\Z"                                   # extension to finish
    )

#/tmp/1qualify_2013_10_01_16_00_00.000_121f02ten_spgs_roadmaps500.pdf
#--------------------------------------------------------------------
#.*/(?P<page>\d{1})(?P<subtitle>qualify|quantify)_(?P<timestr>.*)_(?P<sensor>.*)_(?P<plot_type>\w*)(?P<axis>.)_roadmaps(?P<sample_rate>[0-9]*[p\.]?[0-9]+)(?P<notes>.*)\.pdf\Z
_PCSAROADMAPPDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<page>\d{1}|[A-Z])"                     # a digit OR A to Z single char, then
    "(?P<subtitle>qualify|quantify)"            # enum for subtitle, then
    "_"                                         # underscore, then
    "(?P<timestr>.*)"                           # timestr, then    
    "_"                                         # underscore, then
    "(?P<sensor>.*)"                            # sensor, then
    "_(?P<plot_type>pcs)"                       # underscore pcs, then
    "(?P<axis>.)"                               # axis, then
    "_roadmaps"                                 # underscore roadmaps, then
    "(?P<sample_rate>[0-9]*[p\.]?[0-9]+)"       # zero or more digits, zero or one pee or dot, one or more digit, then
    "(?P<notes>.*)"                             # notes, then
    "\.pdf\Z"                                   # extension to finish
    )

#/tmp/1qualify_2013_10_01_16_00_00.000_121f02_rvts_glacier3_note.pdf
#--------------------------------------------------------------------
#.*/(?P<page>\d{1})(?P<subtitle>qualify|quantify)_(?P<timestr>.*)_(?P<sensor>.*)_(?P<plot_type>rvt)(?P<axis>.)_(?P<notes>.*)\.pdf\Z
_RVTXPDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<page>\d{1}|[A-Z])"                     # a digit OR A to Z single char, then
    "(?P<subtitle>qualify|quantify)"            # enum for subtitle, then
    "_"                                         # underscore, then
    "(?P<timestr>.*)"                           # timestr, then    
    "_"                                         # underscore, then
    "(?P<sensor>.*)"                            # sensor, then
    "_(?P<plot_type>rvt)"                       # underscore rvt, then
    "(?P<axis>.)"                               # axis, then
    "_"                                         # underscore, then
    "(?P<notes>.*)"                             # notes, then
    "\.pdf\Z"                                   # extension to finish
    )

#/tmp/4qualify_2013_10_08_13_35_00_es03_psd3_compare_msg_wv3fans.pdf
#-------------------------------------------------------------------
#.*/(?P<page>\d{1})(?P<subtitle>qualify|quantify)_(?P<timestr>.*)_(?P<sensor>.*)_(?P<plot_type>\w*)(?P<axis>.)_(?P<notes>.*)\.pdf\Z
_PSD3ROADMAPPDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<page>\d{1}|[A-Z])"                     # a digit OR A to Z single char, then
    "(?P<subtitle>qualify|quantify)"            # enum for subtitle, then
    "_"                                         # underscore, then
    "(?P<timestr>.*)"                           # timestr, then    
    "_"                                         # underscore, then
    "(?P<sensor>.*)"                            # sensor, then
    "_(?P<plot_type>psd)"                       # underscore spg, then
    "(?P<axis>.)"                               # axis, then
    "_(?P<notes>.*)"                            # notes, then
    "\.pdf\Z"                                   # extension to finish
    )

#/tmp/1qualify_2011_05_19_18_18_00_121f03006_gvt3_12hour_pm1mg_001800_12hc.pdf
#-----------------------------------------------------------------------------
_GVT3PDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<page>\d{1}|[A-Z])"                     # a digit OR A to Z single char, then
    "(?P<subtitle>qualify|quantify)"            # enum for subtitle, then
    "_"                                         # underscore, then
    "(?P<timestr>.*)"                           # timestr, then    
    "_"                                         # underscore, then
    "(?P<sensor>.*)"                            # sensor, then
    "_(?P<plot_type>gvt)"                       # underscore gvt, then
    "(?P<axis>.)"                               # axis, then
    "_(?P<notes>.*)"                            # notes, then
    "\.pdf\Z"                                   # extension to finish
    )

#/tmp/1qualify_2011_05_19_18_18_00_121f03006_chim_rodent_research_install.pdf
#-----------------------------------------------------------------------------
#.*/(?P<page>\d{1})(?P<subtitle>qualify|quantify)_(?P<timestr>.*)_(?P<sensor>.*)_(?P<plot_type>chi)(?P<axis>.)_(?P<notes>.*)\.pdf\Z
_CHIMPDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<page>\d{1}|[A-Z])"                     # a digit OR A to Z single char, then
    "(?P<subtitle>qualify|quantify)"            # enum for subtitle, then
    "_"                                         # underscore, then
    "(?P<timestr>.*)"                           # timestr, then    
    "_"                                         # underscore, then
    "(?P<sensor>.*)"                            # sensor, then
    "_(?P<plot_type>chi)"                       # underscore chi, then
    "(?P<axis>.)"                               # axis, then
    "_(?P<notes>.*)"                            # notes, then
    "\.pdf\Z"                                   # extension to finish
    )

#/tmp/5quantify_2013_10_08_13_35_00_es03_cvfs_msg_wv3fans_compare.pdf
#-------------------------------------------------------------------
#.*/(?P<page>\d{1})(?P<subtitle>qualify|quantify)_(?P<timestr>.*)_(?P<sensor>.*)_(?P<plot_type>\w*)(?P<axis>.)_(?P<notes>.*)\.pdf\Z
_CVFSROADMAPPDF_PATTERN = (
    ".*/"                                       # path at the start, then
    "(?P<page>\d{1}|[A-Z])"                     # a digit OR A to Z single char, then
    "(?P<subtitle>qualify|quantify)"            # enum for subtitle, then
    "_"                                         # underscore, then
    "(?P<timestr>.*)"                           # timestr, then    
    "_"                                         # underscore, then
    "(?P<sensor>.*)"                            # sensor, then
    "_(?P<plot_type>cvf)"                       # underscore spg, then
    "(?P<axis>.)"                               # axis, then
    "_(?P<notes>.*)"                            # notes, then
    "\.pdf\Z"                                   # extension to finish
    )

#121f03one, hirap, ossbtmf
#-------------------------
#\A(?P<head>121f0|hira|oss|0bb)(?P<tail>btmf|raw|\w{1})(?P<suffix>one|ten|006)?\Z
_SENSOR_PATTERN = (
    "\A(?P<head>121f0|es0|hira|oss|0bb|rad)"    # known head at the start of string, then
    "(?P<tail>btmf|raw|gse|\w{1})"              # btmf, raw, or single alphanumeric
    "(?P<suffix>one|ten|006)?\Z"                # zero or one enum for suffix to finish string
    )

# TODO .*(tig\s+\d{2}(:\d{2})+)+.*(dur\s+\d{2}(:\d{2})+)*.* GETS REPLACED WITH
#-------------------------------------------------------------------
_TIGDUR_PATTERN = (
    ".*"                                        # any prefix string
    "(?P<tig>TIG\s+\d{2}(:\d{2})+){1}"          # TIG hh:mm[:ss]
    ".*"                                        # any interim string
    "(?P<dur>DUR\s+\d{2}(:\d{2})+){1}"          # DUR hh:mm:ss   
    ".*"                                        # any suffix string
)

_PLOTTYPES = {
    'gvt':   'Acceleration vs. Time',
    'psd':   'Power Spectral Density',
    'spg':   'Spectrogram',
    'pcs':   'PCSA',
    'cvf':   'Cumulative RMS vs. Frequency',
    'ist':   'Interval Stat',
    'imm':   'Interval Min/Max',
    'rvt':   'RMS vs. Time',    
    'chi':   'Cumulative Histogram',    
    '':      'empty',
}

_ABBREVS = {
'vib':  'Vibratory',
'qs':   'Quasi-Steady',
}

    #yyyy_mm_dd_HH_MM_ss.sss_SENSOR_PLOTTYPE_roadmapsRATE.pdf
    #(DTOBJ, SYSTEM=SMAMS, SENSOR, PLOTTYPE={pcss|spgX}, fs=RATE, fc='unknown', LOCATION='fromdb')
    #------------------------------------------------------------
    #2013_10_01_00_00_00.000_121f02_pcss_roadmaps500.pdf
    #2013_10_01_08_00_00.000_121f05ten_spgx_roadmaps500.pdf
    #2013_10_01_08_00_00.000_121f03one_spgs_roadmaps142.pdf
    #2013_10_01_08_00_00.000_hirap_spgs_roadmaps1000.pdf


    #yyyy_mm_dd_HH_ossbtmf_roadmap.pdf
    #(DTOBJ, SYSTEM=MAMS, SENSOR=OSSBTMF, PLOTTYPE=gvt3, fs=0.0625, fc=0.01, LOCATION=LAB1O2, ER1, Lockers 3,4)
    #------------------------------------------------------------
    #2013_10_01_08_ossbtmf_roadmap.pdf

def demo_hbfpat():
    import re

    input_value = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Cygnus_Capture_Install/4quantify_2013_09_28_16_radgse_roadmapnup1x2.pdf'
    m = re.match( re.compile(_RADGSEROADMAPNUP1X2PDF_PATTERN), input_value)

    input_value = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_Cygnus_Fan/3quantify_2013_09_22_121f03_irmss_cygnus_fan_capture_31p7to41p7hz.pdf'
    m = re.match( re.compile(_INTSTATPDF_PATTERN), input_value)
    
    input_value = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_Cygnus_Fan/1qualify_2013_10_01_00_00_00.000_121f05_pcss_roadmaps500.pdf'
    m = re.match( re.compile(_SPGXROADMAPPDF_PATTERN), input_value)
    
    if m is None:
        #raise ValueError('Invalid literal for PATTERN: %r' % input_value)
        pass
    else:
        print 'timestr: %s' % m.group('timestr')
        print 'plot_type: %s' % m.group('plot_type')

def is_unique_handbook_pdf_match(fname):
    """
    Return count of handbook pdf regex pattern matches.
    """
    import re
    from pims.utils.iterabletools import quantify
    
    # get rid of generic pattern first
    if '_HANDBOOKPDF_PATTERN' in __all__: __all__.remove('_HANDBOOKPDF_PATTERN')
    
    # use eval to get actual patterns from their __all__ names
    pats = [eval(x) for x in __all__ if x.endswith('PDF_PATTERN')]
    #pats.append(eval('_SUFFIX_CALLOUTS'))
    
    # define predicate to quantify num matches (hopefully unique patterns!)
    is_matched = lambda pat : bool(re.match(pat, fname))
    num_matches = quantify(pats, is_matched)
       
    #print num_matches, fname
    if num_matches == 1:
        return True
    else:
        #print num_matches, fname
        return False

if __name__ == "__main__":
       
    files = [
        #'/tmp/9quantify_2014_09_25_08_30_00_121f08006_chim_compare_rodent_research_install.pdf',
        #'/tmp/9quantify_2015_12_09_08_00_00_radgse_gvt3_cygnus-4_capture_install_zoom.pdf',
        #'/tmp/1qualify_2013_12_19_08_00_00.000_121f03_spgs_roadmaps500_cmg_spin_downup.pdf',
        #'/tmp/5quantify_2013_10_08_13_35_00_es03_cvfs_msg_wv3fans_compare.pdf',
        #'/tmp/1qualify_2013_10_01_00_00_00.000_121f05_pcss_roadmaps500.pdf',
        #'/tmp/3quantify_2013_09_22_121f03_irmss_cygnus_fan_capture_31p7to41p7hz.pdf',
        #'/tmp/1quantify_2013_12_11_16_20_00_ossbtmf_gvt3_progress53p_reboost.pdf',
        #'/tmp/1qualify_2011_05_19_18_18_00_121f03006_gvt3_12hour_pm1mg_001800_12hc.pdf',
        #'/tmp/2quantify_2011_05_19_18_18_00_121f03006_gvt3_12hour_pm1mg_001800_hist.pdf',
        #'/tmp/3quantify_2011_05_19_00_08_00_121f03006_gvt3_12hour_pm1mg_001800_z1mg.pdf',
        #'/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_CMG_Desat/1quantify_2011_05_19_18_18_00_121f03006_gvt3_12hour_pm1mg_001800_12hc.pdf',
        #'/tmp/3quantify_2014_03_03_14_30_00_121f08_rvts_glacier3_duty_cycle.pdf',
        #'/tmp/1quantify_2015_05_12_09_00_00_0bbd_gvt3_airlock_hatch_activities_xoff_-4.22_yoff_1.00_scale_0.77_ori_landscape.pdf',
        #'/tmp//misc/yoda/www/plots/user/handbook/source_docs/hb_vib_equipment_BioLab_Centrifuge_Rotor/1qualify_2015_08_03_13_00_00_121f08_spgs_roadmaps500_biolab_centrifuge_rotor_test.pdf',
        '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_2015_Cygnus-4_Capture_and_Install/1qualify_2015_12_08_18_00_00_ossbtmf_gvt3_twodays.pdf',
        '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_2015_Cygnus-4_Capture_and_Install/2quantify_2015_12_08_18_00_00_radgse_gvt3_cygnus-4_capture_install.pdf',
        '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_2015_Cygnus-4_Capture_and_Install/3quantify_2015_12_09_08_00_00_radgse_gvt3_cygnus-4_capture_install_zoom.pdf',
        ]

    for f in files:
        is_match = is_unique_handbook_pdf_match(f)
        print is_match, f