#############################
# SEE realtime/rtsetup.py too
#############################
"""
This is an object-orient real-time plotting library for PIMS.

See matplotlib's __init__.py file where we modeled this __init__.py file from

The base matplotlib namespace includes:

    :data:`~matplotlib.rtParams`
        a global dictionary of default configuration settings.  It is
        initialized by code which may be overridded by a matplotlibrc
        file.

    :func:`~matplotlib.rc`
        a function for setting groups of rtParams values

"""

__version__  = '0.0.0rc'

import os
import sys
import warnings
from collections import OrderedDict
from pims.realtime.rtsetup import default_params

class Verbose(object):
    """
    A class to handle reporting.  Set the fileo attribute to any file
    instance to handle the output.  Default is sys.stdout
    """
    levels = ('silent', 'helpful', 'debug', 'debug-annoying')
    vald = dict( [(level, i) for i,level in enumerate(levels)])

    # parse the verbosity from the command line; flags look like
    # --verbose-silent or --verbose-helpful
    _commandLineVerbose = None

    for arg in sys.argv[1:]:
        if not arg.startswith('--verbose-'): continue
        _commandLineVerbose = arg[10:]

    def __init__(self):
        self.set_level('silent')
        self.fileo = sys.stdout

    def set_level(self, level):
        'set the verbosity to one of the Verbose.levels strings'

        if self._commandLineVerbose is not None:
            level = self._commandLineVerbose
        if level not in self.levels:
            raise ValueError('Illegal verbose string "%s".  Legal values are %s'%(level, self.levels))
        self.level = level

    def set_fileo(self, fname):
        std = {
            'sys.stdout': sys.stdout,
            'sys.stderr': sys.stderr,
        }
        if fname in std:
            self.fileo = std[fname]
        else:
            try:
                fileo = file(fname, 'w')
            except IOError:
                raise ValueError('Verbose object could not open log file "%s" for writing.\nCheck your matplotlibrc verbose.fileo setting'%fname)
            else:
                self.fileo = fileo

    def report(self, s, level='helpful'):
        """
        print message s to self.fileo if self.level>=level.  Return
        value indicates whether a message was issued

        """
        if self.ge(level):
            print >>self.fileo, s
            return True
        return False

    def wrap(self, fmt, func, level='helpful', always=True):
        """
        return a callable function that wraps func and reports it
        output through the verbose handler if current verbosity level
        is higher than level

        if always is True, the report will occur on every function
        call; otherwise only on the first time the function is called
        """
        assert callable(func)
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)

            if (always or not wrapper._spoke):
                spoke = self.report(fmt%ret, level)
                if not wrapper._spoke: wrapper._spoke = spoke
            return ret
        wrapper._spoke = False
        wrapper.__doc__ = func.__doc__
        return wrapper

    def ge(self, level):
        'return true if self.level is >= level'
        return self.vald[self.level]>=self.vald[level]

verbose=Verbose()

def _get_home():
    """Find user's home directory if possible.
    Otherwise raise error.

    :see:  http://mail.python.org/pipermail/python-list/2005-February/263921.html
    """
    path=''
    try:
        path=os.path.expanduser("~")
    except:
        pass
    if not os.path.isdir(path):
        for evar in ('HOME', 'USERPROFILE', 'TMP'):
            try:
                path = os.environ[evar]
                if os.path.isdir(path):
                    break
            except: pass
    if path:
        return path
    else:
        raise RuntimeError('please define environment variable $HOME')

get_home = verbose.wrap('$HOME=%s', _get_home, always=False)

def _get_configdir():
    """
    Return the string representing the configuration dir.

    default is $HOME/.pimsrealtime
    you can override this with the
    PRTCONFIGDIR environment variable
    """

    configdir = os.environ.get('PIMSRTCONFIGDIR')
    if configdir is not None:
        if not os.path.exists(configdir):
            os.makedirs(configdir)
        if not _is_writable_dir(configdir):
            raise RuntimeError('Could not write to PIMSRTCONFIGDIR="%s"'%configdir)
        return configdir

    h = get_home()
    p = os.path.join(get_home(), '.pimsrealtime')

    if os.path.exists(p):
        if not _is_writable_dir(p):
            raise RuntimeError("'%s' is not a writable dir; you must set %s/.pimsrealtime to be a writable dir.  You can also set environment variable PIMSRTCONFIGDIR to any writable directory where you want matplotlib data stored "% (h, h))
    else:
        if not _is_writable_dir(h):
            raise RuntimeError("Failed to create %s/.pimsrealtime; consider setting PIMSRTCONFIGDIR to a writable directory for matplotlib configuration data"%h)

        os.mkdir(p)

    return p
get_configdir = verbose.wrap('CONFIGDIR=%s', _get_configdir, always=False)

def _get_snap_path():
    """get the path to snap images to"""

    if 'PIMSRTSNAPPATH' in os.environ:
        path = os.environ['PIMSRTSNAPPATH']
        if not os.path.isdir(path):
            raise RuntimeError('Path in environment PIMSRTSNAPPATH not a directory')
        return path

    path = '/tmp'
    if os.path.isdir(path):
        return path

    raise RuntimeError('Could not find the pims real-time snap path')

def get_example_data(fname):
    """
    get_example_data is deprecated -- use matplotlib.cbook.get_sample_data instead
    """
    raise NotImplementedError('get_example_data is deprecated -- use matplotlib.cbook.get_sample_data instead')

class RtParams(OrderedDict):

    """
    A dictionary object INCLUDING VALIDATION.

    validating functions are defined and associated with rt parameters in
    :mod:`pims.realtime.rtsetup`
    """

    validate = dict([ (key, converter) for key, (default, converter) in \
                     default_params.iteritems() ])
    msg_depr = "%s is deprecated and replaced with %s; please use the latter."
    msg_depr_ignore = "%s is deprecated and ignored. Use %s"

    def __str__(self):
        """show the dict [TWSS]"""
        keys = self.keys()
        maxlen = max(len(x) for x in keys)  # find max length
        fmt = '{0:<%ds} : {1:s}\n' % maxlen        
        s = ''
        for k in keys:
            s += fmt.format( k, str(self[k]) )
        return s

    def __setitem__(self, key, val):
        try:
            cval = self.validate[key](val)
            dict.__setitem__(self, key, cval)
        except KeyError:
            raise KeyError('%s is not a valid rc parameter.  See rtParams.keys() for a list of valid parameters.' % (key,))
            
    def keys(self):
        """
        Return sorted list of keys.
        """
        k = dict.keys(self)
        k.sort()
        return k

    def values(self):
        """
        Return values in order of sorted keys.
        """
        return [self[k] for k in self.keys()]

def get_rt_params():
    'Return the default params updated from the values in the rc file'
    rt = default_params
    for key in rt:
        if not rt[key][1](rt[key][0]) == rt[key][0]:
            print "%s: %s != %s"%(key, rt[key][1](rt[key][0]), rt[key][0])
        #if rt[key][1](rt[key][0]) == rt[key][0]:
            print "%s: %s = %s"%(key, rt[key][1](rt[key][0]), rt[key][0])        
    return RtParams([ (key, default) for key, (default, converter) in default_params.iteritems() ])

# this is global instance we want out of here
rt_params = get_rt_params()

if __name__ == '__main__':
    #for key, v in rt_params.iteritems():
    #    print key, v
    print rt_params
