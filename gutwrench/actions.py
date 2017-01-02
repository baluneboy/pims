#!/usr/bin/env python

ACTIONS = {
    # ACTION          MATLABFUN       POSTPROCESS
    'reboost':      ('gvt3',         'reboost_postplot'),
    'maneuver':     ('gvt3',         'maneuver_postplot'),
    'docking':      ('spgs',         'docking_postplot'),
}
