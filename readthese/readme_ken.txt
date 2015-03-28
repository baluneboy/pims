SELECT count(*) FROM pims.121f03 where time>unix_timestamp('2013-10-23 18:45:01') and time<unix_timestamp('2013-10-25 00:05:34');

3. add cronjob on jimmy for backfill_ossbtmf_roadmap.py with better default args

4. verify MANUALLY that copy PDF to ~/yodahb/ path, then auto_insert_handbook SQL yields web page end item, then
verify handbook.py does things in right order (copy file first, then auto_insert_handbook)

5. log entry after build (or just after success on insert?)

6. make all log.process calls (info or error or warn) as sentences ending in period or bang or ?

7. see TODOs in handbook.py

8. make sure snippets are common [and/or abbreviations?] in komodo @home and @work

9. cropcat_middle: pdfjam 2013_10_11_08_00_00.000_121f03_spgs_roadmaps500.pdf --trim '3.05cm 0cm 5.5cm 0cm' --clip true --landscape --outfile middle.pdf

# FIXME the following err_msg prefix propagation is ugly
root     : INFO    : Logging started at 2013-10-20 09:43:05.068513.
PROCESS  : INFO    : Parsed source_dir string: regime:Vibratory, category:Vehicle, and title:Big Bang
PROCESS  : INFO    : Attempting process_build in /home/pims/Documents/test/hb_vib_vehicle_Big_Bang/build
PROCESS  : INFO    : Ran HandbookPdftkCommand (unoconv and offset/scale) for 2 odt files
PROCESS  : INFO    : We now have 3 unjoined files, including ancillary file
PROCESS  : INFO    : Attempting to finalize_entry
PROCESS  : INFO    : Renamed hb_pdf with time stamp
PROCESS  : INFO    : Ran pdfjoin command to get /home/pims/Documents/test/hb_vib_vehicle_Big_Bang/hb_vib_vehicle_Big_Bang.pdf
PROCESS  : INFO    : Did the unbuild okay
PROCESS  : ERROR   : Database problem hb_vib_vehicle_Big_Bang.pdf already exists in one of the records
PROCESS  : ERROR   : db_insert error db_insert err_msg is Database problem hb_vib_vehicle_Big_Bang.pdf already exists in one of the records
process_build err_msg is finalize_entry err_msg is db_insert err_msg is Database problem hb_vib_vehicle_Big_Bang.pdf already exists in one of the records

========================================================
obspy header info
========================================================

network = system (sams, mams, etc.)
station = sensor (121f05, 0bbd, etc.)
location = SensorCoordinateSystem's comment field
channel = X,Y,Z for SSA (or A,B,C for sensor)

Agency.Deployment.Station.Location (Channel)

CHANNEL CHAR 1
F (unknown description)		fs >= 1000 and fs < 5000
C (unknown description)		fs >= 250 and fs < 1000
E (Extremely Short Period)	fs >= 80 and fs < 250
S (Short Period)			fs >= 10 and fs < 80

CHANNEL CHAR 2
N (Accelerometer)

CHANNEL CHAR 3
A B C (SSA's X, Y, Z)
1 2 3 (sensor's X, Y, Z)

NASA.ISS.SAMS.05.CNA for SAMS, SE-05,  500 sps, X-axis
NASA.ISS.SAME.03.CNB for SAMS, ES-06,  500 sps, Y-axis
NASA.ISS.MAMS.HI.FNC for MAMS, HiRAP, 1000 sps, Z-axis

See sandbox/flatbook_demo.py for starter kit on upgrade to "pads" & "roadmaps" tally_grid workers.  The big deal will
be if (1) PADs gets populated first, (2) then roadmaps after that, (3) then some form of link between the 2 grids so
that processing cells in PADs may have resample hooked to it, but also the ability to highlight PAD cells that have some
hours, but where no roadmaps exist, then there's good way to process those cells (in PADs) to create the missing roadmaps FTW!


#######################################################
In gui/stripchart.py we may be able to gain efficiency
see bernie post at: http://stackoverflow.com/questions/9627686/plotting-dates-on-the-x-axis-with-pythons-matplotlib

# *** You can do this more simply using plot() instead of plot_date().
#
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# First, convert your strings to instances of Python datetime.date:
dates = ['01/02/1991','01/03/1991','01/04/1991']
x = [dt.datetime.strptime(d,'%m/%d/%Y').date() for d in dates]
y = range(len(x))

# Then plot:
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator())
plt.plot(x,y)
plt.gcf().autofmt_xdate()


# DELETE THIS CHUNK OF CODER FROM packetfeeder.py (ORIGINAL slice and slide right chunk)
            # if possible, then slice and slide right for data object attached to plot; otherwise, do nothing        
            npts = self.rt_trace['x'].stats.npts 
            if npts == 0 or (npts % self.analysis_samples):
                log.debug( "%04d %s NON-DIVISIBLE" % (get_line(), str(self.rt_trace['x'])) )
            else:
                log.debug( "%04d %s IS DIVISIBLE" % (get_line(), str(self.rt_trace['x'])) )
                endtime = self.starttime + self.analysis_interval
                slice_range = {'starttime':UTCDateTime(self.starttime), 'endtime':UTCDateTime(endtime)}
                traces = {}
                traces['x'] = self.rt_trace['x'].slice(**slice_range)
                slice_len = traces['x'].stats.npts
                cumulative_info_tuple = (str(self.starttime), str(endtime), '%d' % len(traces['x']))
                #if self.analysis_samples - 1 <= slice_len <= self.analysis_samples + 1:
                if (slice_len / self.analysis_samples) > 0.90:
                    # now get y and z
                    for ax in ['y', 'z']:
                        traces[ax] = self.rt_trace[ax].slice(**slice_range)
                    t = traces['x'].absolute_times()
                    #traces['y'].filter('lowpass', freq=2.0, zerophase=True)
                    #traces['z'].filter('highpass', freq=2.0, zerophase=True)
            
                    # get info and data to pass to step callback routine
                    current_info_tuple = (str(slice_range['starttime']), str(slice_range['endtime']), '%d' % len(t))
                    flash_msg = None
                        
                    # slide to right by analysis_interval
                    self.starttime = endtime
                else:
                    msg = '%04d how did we get DIVISIBLE, but bad slice_len here?' % get_line()
                    log.error(msg)
                    raise Exception(msg)
            
                if self.step_callback:
                    step_data = (current_info_tuple, cumulative_info_tuple, t, traces, flash_msg)            
                    self.step_callback(step_data) 