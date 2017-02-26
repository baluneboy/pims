#!/usr/bin/env python

# FIXME better way to track limits over time and apply here (span all EEs!)?
# define y-limits based on measure
YLIMS = {       
        'head0_tempX':      [  23,  30 ],
        'head0_tempY':      [  23,  30 ],
        'head0_tempZ':      [  23,  30 ],
        'head1_tempX':      [  23,  30 ],
        'head1_tempY':      [  23,  30 ],
        'head1_tempZ':      [  23,  30 ],
        'tempbase':         [  21,  28 ],
        'head0_plus5V':     [   4,   6 ],
        'head0_plus15V':    [  13,  16 ],
        'head0_minus15V':   [ -16, -13 ],
        'head1_plus5V':     [  -6,  -4 ],
        'head1_plus15V':    [  13,  16 ],
        'head1_minus15V':   [ -16, -13 ],
        'pc104_plus5V':     [   4,   6 ],
        'ref_plus5V':       [   4,   6 ],
        'ref_zeroV':        [  -1,   1 ],
}

# define measures to consider for truly tracking trending
GROUP_MEASURES = {

    'TEMPS':
        [
        'head0_tempX',
        'head0_tempY',
        'head0_tempZ',
        'head1_tempX',
        'head1_tempY',
        'head1_tempZ',
        'tempbase'
        ],

    'VOLTS':
        [
        'head0_plus5V',
        'head0_plus15V',
        'head0_minus15V',
        'head1_plus5V',
        'head1_plus15V',
        'head1_minus15V',
        'pc104_plus5V',
        'ref_plus5V',
        'ref_zeroV'        # this one never seems to change (probably not actual measurement)
        ]
}