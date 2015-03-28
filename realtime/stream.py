#!/usr/bin/env python
"""Classes for PIMS real-time plotting support."""

class RealtimeStream(object):
    """A stream from pims db table."""
    
    def __init__(self, sensor):
        """Initialize real-time stream object."""
        self.cutoff_hz = 200

    def is_unique(self):
        """Boolean true if we have uniqueness."""
        return True

class RealtimePlotParameters(object):
    """fake it for now"""
    
    def __init__(self, plot_type='frvt3', frange_hz='0.2-0.3', plot_minutes='10', update_minutes='0.5'):
        self.plot_type = plot_type
        self.frange_hz = self._get_frange(frange_hz)
        self.plot_minutes = float(plot_minutes)
        self.update_minutes = float(update_minutes)

    def _get_frange(self, frange_hz):
        """Convert lower/upper limits from string to floats."""
        return [float(i) for i in frange_hz.split('-')]
