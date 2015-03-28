#!/usr/bin/env python

###############################################################################
# SEE /usr/lib/pymodules/python2.7/matplotlib/rcsetup.py (not rc there, rt here)
# which is where this code was modeled (using rtParams instead of rcParams)
###############################################################################

"""
This rtsetup module contains the default values and the validation code for
customization using rt settings.

Each rt setting is assigned a default value and a function used to validate any
attempted changes to that setting. The default values and validation functions
are defined in this rtsetup module, and are used to construct the rtParams global
object which stores the settings and is referenced throughout.

SEE /usr/lib/pymodules/python2.7/matplotlib/rtsetup.py FOR HOW WE MODELED HERE
"""

import os
import warnings
from matplotlib.fontconfig_pattern import parse_fontconfig_pattern
from matplotlib.colors import is_color_like

class ValidateInStrings(object):
    def __init__(self, key, valid, ignorecase=False):
        'valid is a list of legal strings'
        self.key = key
        self.ignorecase = ignorecase
        def func(s):
            if ignorecase: return s.lower()
            else: return s
        self.valid = dict([(func(k),k) for k in valid])

    def __call__(self, s):
        if self.ignorecase: s = s.lower()
        if s in self.valid: return self.valid[s]
        raise ValueError('Unrecognized %s string "%s": valid strings are %s'
                         % (self.key, s, self.valid.values()))

def validate_path_exists(s):
    'If s is a path, return s, else False'
    if os.path.exists(s): return s
    else:
        raise RuntimeError('"%s" should be a path but it does not exist'%s)

def validate_bool(b):
    'Convert b to a boolean or raise'
    if type(b) is str:
        b = b.lower()
    if b in ('t', 'y', 'yes', 'on', 'true', '1', 1, True): return True
    elif b in ('f', 'n', 'no', 'off', 'false', '0', 0, False): return False
    else:
        raise ValueError('Could not convert "%s" to boolean' % b)

def validate_bool_maybe_none(b):
    'Convert b to a boolean or raise'
    if type(b) is str:
        b = b.lower()
    if b=='none': return None
    if b in ('t', 'y', 'yes', 'on', 'true', '1', 1, True): return True
    elif b in ('f', 'n', 'no', 'off', 'false', '0', 0, False): return False
    else:
        raise ValueError('Could not convert "%s" to boolean' % b)

def validate_float(s):
    'convert s to float or raise'
    try: return float(s)
    except ValueError:
        raise ValueError('Could not convert "%s" to float' % s)

def validate_int(s):
    'convert s to int or raise'
    try: return int(s)
    except ValueError:
        raise ValueError('Could not convert "%s" to int' % s)

def validate_fonttype(s):
    'confirm that this is a Postscript of PDF font type that we know how to convert to'
    fonttypes = { 'type3':    3,
                  'truetype': 42 }
    try:
        fonttype = validate_int(s)
    except ValueError:
        if s.lower() in fonttypes.keys():
            return fonttypes[s.lower()]
        raise ValueError('Supported Postscript/PDF font types are %s' % fonttypes.keys())
    else:
        if fonttype not in fonttypes.values():
            raise ValueError('Supported Postscript/PDF font types are %s' % fonttypes.values())
        return fonttype

class ValidateNseqFloat(object):
    def __init__(self, n):
        self.n = n
    def __call__(self, s):
        'return a seq of n floats or raise'
        if type(s) is str:
            ss = s.split(',')
            if len(ss) != self.n:
                raise ValueError('You must supply exactly %d comma separated values'%self.n)
            try:
                return [float(val) for val in ss]
            except ValueError:
                raise ValueError('Could not convert all entries to floats')
        else:
            assert type(s) in (list,tuple)
            if len(s) != self.n:
                raise ValueError('You must supply exactly %d values'%self.n)
            return [float(val) for val in s]

class ValidateNseqInt(object):
    def __init__(self, n):
        self.n = n
    def __call__(self, s):
        'return a seq of n ints or raise'
        if type(s) is str:
            ss = s.split(',')
            if len(ss) != self.n:
                raise ValueError('You must supply exactly %d comma separated values'%self.n)
            try:
                return [int(val) for val in ss]
            except ValueError:
                raise ValueError('Could not convert all entries to ints')
        else:
            assert type(s) in (list,tuple)
            if len(s) != self.n:
                raise ValueError('You must supply exactly %d values'%self.n)
            return [int(val) for val in s]

def validate_color(s):
    'return a valid color arg'
    try:
        if s.lower() == 'none':
            return 'None'
    except AttributeError:
        pass
    if is_color_like(s):
        return s
    stmp = '#' + s
    if is_color_like(stmp):
        return stmp
    # If it is still valid, it must be a tuple.
    colorarg = s
    msg = ''
    if s.find(',')>=0:
        # get rid of grouping symbols
        stmp = ''.join([ c for c in s if c.isdigit() or c=='.' or c==','])
        vals = stmp.split(',')
        if len(vals)!=3:
            msg = '\nColor tuples must be length 3'
        else:
            try:
                colorarg = [float(val) for val in vals]
            except ValueError:
                msg = '\nCould not convert all entries to floats'

    if not msg and is_color_like(colorarg):
        return colorarg

    raise ValueError('%s does not look like a color arg%s'%(s, msg))

def validate_colorlist(s):
    'return a list of colorspecs'
    if type(s) is str:
        return [validate_color(c.strip()) for c in s.split(',')]
    else:
        assert type(s) in [list, tuple]
        return [validate_color(c) for c in s]

def validate_stringlist(s):
    'return a list'
    if type(s) is str:
        return [ v.strip() for v in s.split(',') ]
    else:
        assert type(s) in [list,tuple]
        return [ str(v) for v in s ]

validate_orientation = ValidateInStrings('orientation',[
    'landscape', 'portrait',
    ])

def validate_aspect(s):
    if s in ('auto', 'equal'):
        return s
    try:
        return float(s)
    except ValueError:
        raise ValueError('not a valid aspect specification')

def validate_fontsize(s):
    if type(s) is str:
        s = s.lower()
    if s in ['xx-small', 'x-small', 'small', 'medium', 'large', 'x-large',
             'xx-large', 'smaller', 'larger']:
        return s
    try:
        return float(s)
    except ValueError:
        raise ValueError('not a valid font size')

def validate_font_properties(s):
    parse_fontconfig_pattern(s)
    return s

validate_fontset = ValidateInStrings('fontset', ['cm', 'stix', 'stixsans', 'custom'])

validate_mathtext_default = ValidateInStrings(
    'default', "rm cal it tt sf bf default bb frak circled scr regular".split())

validate_verbose = ValidateInStrings('verbose',[
    'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    ])

validate_cairo_format = ValidateInStrings('cairo_format',
                            ['png', 'ps', 'pdf', 'svg'],
                            ignorecase=True)

validate_ps_papersize = ValidateInStrings('ps_papersize',[
    'auto', 'letter', 'legal', 'ledger',
    'a0', 'a1', 'a2','a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10',
    'b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'b10',
    ], ignorecase=True)

def validate_ps_distiller(s):
    if type(s) is str:
        s = s.lower()

    if s in ('none',None):
        return None
    elif s in ('false', False):
        return False
    elif s in ('ghostscript', 'xpdf'):
        return s
    else:
        raise ValueError('matplotlibrc ps.usedistiller must either be none, ghostscript or xpdf')

validate_joinstyle = ValidateInStrings('joinstyle',['miter', 'round', 'bevel'], ignorecase=True)

validate_capstyle = ValidateInStrings('capstyle',['butt', 'round', 'projecting'], ignorecase=True)

validate_negative_linestyle = ValidateInStrings('negative_linestyle',['solid', 'dashed'], ignorecase=True)

def validate_negative_linestyle_legacy(s):
    try:
        res = validate_negative_linestyle(s)
        return res
    except ValueError:
        dashes = ValidateNseqFloat(2)(s)
        warnings.warn("Deprecated negative_linestyle specification; use 'solid' or 'dashed'")
        return (0, dashes)  # (offset, (solid, blank))

def validate_tkpythoninspect(s):
    # Introduced 2010/07/05
    warnings.warn("tk.pythoninspect is obsolete, and has no effect")
    return validate_bool(s)

validate_legend_loc = ValidateInStrings('legend_loc',[
  'best',
  'upper right',
  'upper left',
  'lower left',
  'lower right',
  'right',
  'center left',
  'center right',
  'lower center',
  'upper center',
  'center',
], ignorecase=True)

def deprecate_svg_embed_char_paths(value):
    warnings.warn("svg.embed_char_paths is deprecated.  Use svg.fonttype instead.")

validate_svg_fonttype = ValidateInStrings('fonttype', ['none', 'path', 'svgfont'])

class ValidateInterval(object):
    """
    Value must be in interval
    """
    def __init__(self, vmin, vmax, closedmin=True, closedmax=True):
        self.vmin = vmin
        self.vmax = vmax
        self.cmin = closedmin
        self.cmax = closedmax

    def __call__(self, s):
        try: s = float(s)
        except: raise RuntimeError('Value must be a float; found "%s"'%s)

        if self.cmin and s<self.vmin:
            raise RuntimeError('Value must be >= %f; found "%f"'%(self.vmin, s))
        elif not self.cmin and s<=self.vmin:
            raise RuntimeError('Value must be > %f; found "%f"'%(self.vmin, s))

        if self.cmax and s>self.vmax:
            raise RuntimeError('Value must be <= %f; found "%f"'%(self.vmax, s))
        elif not self.cmax and s>=self.vmax:
            raise RuntimeError('Value must be < %f; found "%f"'%(self.vmax, s))
        return s

class ValidateTimeInterval(object):
    """
    Value must be in interval and positive integer
    """
    def __init__(self, vmin, vmax, closedmin=True, closedmax=True):
        self.vmin = validate_int(vmin)
        self.vmax = validate_int(vmax)
        self.cmin = closedmin
        self.cmax = closedmax

    def __call__(self, s):
        try:
            s = int(s)
            assert(s>=0)
        except:
            raise RuntimeError('Value must be a positive int; found "%s"'%s)

        if self.cmin and s<self.vmin:
            raise RuntimeError('Value must be >= %d; found "%d"'%(self.vmin, s))
        elif not self.cmin and s<=self.vmin:
            raise RuntimeError('Value must be > %d; found "%d"'%(self.vmin, s))

        if self.cmax and s>self.vmax:
            raise RuntimeError('Value must be <= %d; found "%d"'%(self.vmax, s))
        elif not self.cmax and s>=self.vmax:
            raise RuntimeError('Value must be < %d; found "%d"'%(self.vmax, s))
        return s

#################################################################################################
# FIXME get at least key values below from XLS spreadsheet immune to Excel auto-format weirdness

# FIXME these were probably set for debug and testing, but you change to what makes sense in general:
OLAP =    9  #   9 seconds overlap of analysis_intervals
ANIN =   10  #  10 seconds for analysis_interval
PLTS =  600  # 600 seconds for plot_span
EXTR =    2  #   2 count for extra_intervals
#MAXT = int( EXTR * ANIN + PLTS ) # seconds max for real-time trace

# a map from key -> value, converter
default_params = {

    # path(s)
    # FIXME snap_path not always 121f05
    'paths.snap_path'          : ['/misc/yoda/www/plots/sams/121f05', validate_path_exists],
    'paths.params_path'        : ['/misc/yoda/www/plots/sams/params', validate_path_exists],

    # verbosity setting
    'verbose.level'     : ['INFO', validate_verbose], # debug, info, warning, error, or critical
    'verbose.fileo'     : ['pims_realtime', str], # basename w/o ext; see if 'sys.stdout' can be used too?

    # line props
    'lines.linewidth'       : [1.0, validate_float],     # line width in points
    'lines.linestyle'       : ['-', str],                # solid line
    'lines.color'           : ['b', validate_color],     # blue
    'lines.marker'          : ['None', str],             # black
    'lines.markeredgewidth' : [0.5, validate_float],
    'lines.markersize'      : [6, validate_float],       # markersize, in points
    'lines.antialiased'     : [True, validate_bool],     # antialised (no jaggies)
    'lines.dash_joinstyle'  : ['round', validate_joinstyle],
    'lines.solid_joinstyle' : ['round', validate_joinstyle],
    'lines.dash_capstyle'   : ['butt', validate_capstyle],
    'lines.solid_capstyle'  : ['projecting', validate_capstyle],

    # figure props
    # figure size in inches: width by height
    'figure.figsize'    : [ [8.0,6.0], ValidateNseqFloat(2)],
    'figure.dpi'        : [100, validate_float],   # DPI
    'figure.facecolor'  : [ '0.75', validate_color], # facecolor; scalar gray
    'figure.edgecolor'  : [ 'w', validate_color],  # edgecolor; white

    # figure subplot props
    'figure.subplot.left'   : [0.125, ValidateInterval(0, 1, closedmin=True, closedmax=True)],
    'figure.subplot.right'  : [0.9, ValidateInterval(0, 1, closedmin=True, closedmax=True)],
    'figure.subplot.bottom' : [0.1, ValidateInterval(0, 1, closedmin=True, closedmax=True)],
    'figure.subplot.top'    : [0.9, ValidateInterval(0, 1, closedmin=True, closedmax=True)],
    'figure.subplot.wspace' : [0.2, ValidateInterval(0, 1, closedmin=True, closedmax=False)],
    'figure.subplot.hspace' : [0.2, ValidateInterval(0, 1, closedmin=True, closedmax=False)],

    # time props (units are seconds)
    'time.analysis_overlap'     : [OLAP, validate_float],    
    'time.analysis_interval'    : [ANIN, ValidateTimeInterval(  1,   61, closedmin=True, closedmax=False)],
    'time.plot_span'            : [PLTS, ValidateTimeInterval(  4, 7201, closedmin=True, closedmax=False)],
    'time.extra_intervals'      : [EXTR, validate_int],
    #'time.maxsec_trace'         : [MAXT, validate_int],
    
    # data/buffer props
    'data.maxlen'               : [ 600, validate_int], # max pts; limit otherwise ever-growing data deque
    'data.scale_factor'         : [ 1e6, validate_int],
        
    # legacy packetWriter.py parameters
    'pw.ancillaryHost'          : ['kyle',            str], # the name of the computer with the auxiliary databases (or 'None')
    'pw.host'                   : ['localhost',       str], # the name of the computer with the database
    'pw.database'               : ['pims',            str], # the name of the database to process
    'pw.tables'                 : ['121f05',          str], # the database table that should be processed (NOT "ALL" & NOT separated by commas)
    'pw.destination'            : ['.',               str], # the directory to write files into in scp format (host:/path/to/data) or local .
    'pw.delete'                 : ['0',               str], # 0=delete processed data, 1=leave in database OR use databaseName to move to that db
    'pw.resume'                 : [0,        validate_int], # try to pick up where a previous run left off, or do whole database
    'pw.inspect'                : [2 ,       validate_int], # JUST INSPECT FOR UNEXPECTED CHANGES, DO NOT WRITE PAD FILES
    'pw.showWarnings'           : [0,        validate_int], # show or supress warning message
    'pw.ascii'                  : [0,        validate_int], # write data in ASCII or binary
    'pw.startTime'              : [-1.0,   validate_float], # first data time to process (0 means anything back to 1970, negative for "good" start)
    'pw.endTime'                : [0.0,    validate_float], # last data time to process (0 means no limit)
    'pw.quitWhenDone'           : [0,        validate_int], # end this program when all data is processed
    'pw.bigEndian'              : [0,        validate_int], # write binary data as big endian (Sun, Mac) or little endian (Intel)
    'pw.cutoffDelay'            : [0.0,    validate_float], # maximum amount of time to keep data in the database before processing (sec)
    'pw.maxFileTime'            : [600.0,  validate_float], # maximum time span for a PAD file (0 means no limit)
    'pw.additionalHeader'       : ['\"\"',            str], # additional XML to put in header.
                                                            #   in order to prevent confusion in the shell and command parser,
                                                            #   represent XML with: ' ' replaced by '#', tab by '~', CR by '~~'       
}
#default_params['paths.snap_path'] = [
#    default_params['/misc/yoda/www/plots/sams/'] + default_params['pw.tables'], validate_path_exists
#    ]

def check_defaults():
    rt = default_params
    for key in rt:
        if not rt[key][1](rt[key][0]) == rt[key][0]:
            print "INVALID %s: %s != %s"%(key, rt[key][1](rt[key][0]), rt[key][0])
        else:
            print "OKAY %s: %s" % (key, rt[key][0])

if __name__ == '__main__':
    check_defaults()
    