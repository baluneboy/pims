The user specifies the following parameters:
--------------------------------------------
sensor
axis (like x, y, z, or s)
gmt_span
frange (like [0.01 fc], [0.2 0.3], or [0.01 10] Hz)
metric (like 2-minute interval RMS)
summary_stat (like median, 95th percentile, min, max, mean)
unique label via TBD label convention (includes: sensor, axis, gmt_span, frange, metric_abbrev, summary_stat_abbrev)


PIMS routine does the following (either in bg or if user prepares, then in advance of real-time deployment):
============================================================================================================
compute metric for sensor/axis during gmt_span
produce summary_stat
insert summary_stat with unique label into MySQL db


Finally:
~~~~~~~~
once we have the benchmark, overlay this on existing near real-time plot (ftw)!
the real-time plot will only show stat overlay and unique label
