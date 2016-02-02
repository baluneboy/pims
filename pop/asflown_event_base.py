#!/usr/bin/env python

"""Convert AsFlownEvents to MATLAB code."""

import abc
from dateutil import parser

from pims.files.utils import extract_between_lines_as_list

class AsFlownEventBase(object):

    __metaclass__ = abc.ABCMeta
    
    def __init__(self, readme_line):
        tmp = readme_line.rstrip('\n').split(' ')
        self.time = parser.parse(tmp[0] + ' ' + tmp[1])
        self.text = ' '.join( tmp[2:] )

    def __str__(self):
        s = ''
        s += 'AS-FLOWN EVENT TIME = %s, TEXT = %s' % (self.time, self.text)
        return s

    @abc.abstractmethod    
    def get_matlab_code(self):
        """return matlab code for this event"""
        pass


class AsFlownEvent(AsFlownEventBase):
    
    def get_matlab_code(self):
        """return matlab code for this event"""
        return '% ' + str(self)


class ProgressDockingAsFlownEvent(AsFlownEvent):
    
    def get_matlab_code(self):
        """return matlab code for this Progress Docking event"""
        s = ''
        if self.text.startswith('Plot gvt'):
            if self.text.endswith('Start'):
                s += "strStartGvtPlotSpan = datenum('%s'); %% Plot gvt START" % self.time
            elif self.text.endswith('CRease'):
                s += "strCeaseGvtPlotSpan = datenum('%s'); %% Plot gvt CEASE" % self.time
            else:
                s += '%% UNRECOGNIZED AS FLOWN EVENT TEXT = "%s"' % self.text
                return s
            
        return s + ' % PROG DOCK EVT ' + str(self)


class MatlabCode(object):

    __metaclass__ = abc.ABCMeta
    
    def __init__(self, readme_file):
        self.readme_file = readme_file

    def __str__(self):
        s = ''
        for evt in self.asflown_events:
            s += '% %s, %s\n' % (evt.time, evt.text)
        return s

    @abc.abstractmethod    
    def parse_readme_file(self, begin_str, end_str):
        """return parsed rendition of readme.txt file for as-flown events related to some specific activity"""
        pass

    @abc.abstractmethod
    def digest_events(self):
        """take action based on parsed asflown_events"""
        pass

    @abc.abstractmethod    
    def append_code(self):
        """append matlab code to readme_file related to specific activity"""
        pass    


class ProgressDockingMatlabCode(MatlabCode):
    
    def __init__(self, *args, **kwargs):
        super(ProgressDockingMatlabCode, self).__init__(*args, **kwargs)
        self.asflown_events = self.parse_readme_file()
        
    def __str__(self):
        s = self.get_header()
        s += self.get_sensor_subdirs()
        s += '\n\n'
        for evt in self.asflown_events:
            #s += 'AS-FLOWN PROGRESS DOCKING EVENT TIME = %s, TEXT = %s\n' % (evt.time, evt.text)
            s += '%s\n' % evt.get_matlab_code()
        s += '\n# STANDARD PROCESSING FOR PROGRESS DOCKING ENDS HERE'
        return s

    def parse_readme_file(self):
        """return parsed rendition of readme.txt file for as-flown events related to Progress Docking"""
        asflown_events = []
        begin_str = None
        end_str = '# AS-FLOWN EVENTS ARE LISTED ABOVE'
        lines = extract_between_lines_as_list(self.readme_file, begin_str, end_str)
        for line in lines:
            # if not blank and not comment, then append event
            if line.strip() and not line.startswith('#'):
                evt = ProgressDockingAsFlownEvent(line)
                asflown_events.append(evt)
        return asflown_events

    def digest_events(self):
        print 'Not implemented digestion yet.'

    def append_code(self):
        """append matlab code to readme_file related to progress docking activity"""
        print 'Not implemented appending yet.'
    
    def get_header(self):
        s = '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n'
        s += '% STANDARD PROCESSING FOR PROGRESS DOCKING %\n'
        s += '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n\n'
        s += '% Produce gvt3 plots\n'
        return s
    
    def get_sensor_subdirs(self, subdirs=['sams2_accel_121f03006', 'sams2_accel_121f05006', 'sams2_accel_121f08006', 'sams2_accel_121f02006', 'sams2_accel_121f04006', 'mams_accel_hirap006' ]):
        s = "casSources = {'"
        s += "', '".join(subdirs)
        s += "'};"
        return s
    
    def get_4hour_start_stop():
        pass    

    
# defaults
defaults = {
'sensor_subdirs':               [
                                'sams2_accel_121f03006',
                                'sams2_accel_121f05006',
                                'sams2_accel_121f08006',
                                'sams2_accel_121f02006',
                                'sams2_accel_121f04006',
                                'mams_accel_hirap006' ],          
'plot_type':                    'gvt',
'fun_handle_plot':              '@vibratory_disposal_gvt',
'fun_handle_post':              '@poppostplot',
'plot_glim':                    '[-6 6]',
'freedrift_cushion_minutes':    '4', 
}
parameters = defaults.copy()


def params_okay():
    """check for reasonableness of input parameters"""
    return True


def main(argv):
    """return big string of matlab code for progress docking standard processing"""
    
    # parse command line
    for p in argv[1:]:
        pair = p.split('=')
        if (2 != len(pair)):
            print 'bad parameter: %s' % p
            break
        else:
            parameters[pair[0]] = pair[1]
    else:
        if params_okay():
            print 'yay'
            return 0

    print_usage()  


##if __name__ == '__main__':
##
##    print get_sensor_subdirs(parameters['sensor_subdirs'])
##    raise SystemExit
##
##    sys.exit(main(sys.argv))

    
"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% STANDARD PROCESSING FOR PROGRESS DOCKING %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Produce gvt3 plots
casSources = {'sams2_accel_121f03006', 'sams2_accel_121f05006', 'sams2_accel_121f08006', 'sams2_accel_121f02006', 'sams2_accel_121f04006', 'mams_accel_hirap006'};

strStartGvtPlotSpan = '23-Dec-2015,08:00:00.000';
strStopGvtPlotSpan =  '23-Dec-2015,12:00:00.000';

strPlotType = 'gvt';
fhPlot = @vibratory_disposal_gvt;
fhPostPlot = @poppostplot;

strOutDir = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_vehicle_Progress_62P_Docking_2015-12-23';
strSuffix = 'progress62p_docking';

% Add specific plot parameters
sPlotParams.casxNew = {...
'23-Dec-2015 08:00:00',...	# Start of 4-hour window
'23-Dec-2015 08:19:00',...	# Handover US to RS
'23-Dec-2015 10:27:00',...	# Start free drift for docking
'23-Dec-2015 10:49:00',...	# Start mnvr to post-docking attitude
'23-Dec-2015 11:11:00',...	# Stop mnvr to post-docking attitude
'23-Dec-2015 11:37:00',...	# Handover RS to US Mom Mgmt
'23-Dec-2015 12:00:00',...	# Stop of 4-hour window
};
sPlotParams.strStartFreeDrift = '23-Dec-2015 10:27:00';
sPlotParams.strStopFreeDrift =  '23-Dec-2015 10:49:00';
sPlotParams.FreeDriftWindowCushionMinutes = 4;
sPlotParams.strFileSummaryText = fullfile(strOutDir, 'progress_docking_summary.txt');
sPlotParams.TTickLabelMode = 'dateaxis';
sPlotParams.GLim = [-7 7];

popmain(casSources, strStartGvtPlotSpan, strStopGvtPlotSpan, strPlotType, fhPlot, sPlotParams, fhPostPlot, strOutDir, strSuffix);

# STANDARD PROCESSING FOR PROGRESS DOCKING ENDS HERE
"""