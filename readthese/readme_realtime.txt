The user specifies the following parameters:
--------------------------------------------
sensor
plot_type (like gvt3, fgvt3, rvt3, frvt3); "f" prefix for "filtered"
frange_hz ( the default is [0.01 fc) )
plot_minutes (like 10 or 120; MIN is 2)
update_minutes ("how often" has practical fastest rate, say 0.5, and upper limit of half plot_minutes)


PIMS routine does the following (either in bg or if user prepares, then in advance of real-time deployment):
============================================================================================================
use sensor to find host/table with "recent" data and must be unique; e.g. no manbearpig dupe
prime buffer with data from db
update plot every update_interval


Ken, start with:
~~~~~~~~~~~~~~~~
sensor = 121f05
plot_type = frvt3
frange_hz = [0.2 0.3]
plot_minutes = 10
update_minutes = 0.5
