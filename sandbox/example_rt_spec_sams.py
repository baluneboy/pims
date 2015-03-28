#!/usr/bin/env python

import sys

params = [
    ('screen_snap', '(0,1)', 1),
    ('snap_interval', '(Sec)', 30,),
    ('head_start', '(Min)', 60,),
    ('database', '(Text)', 'pims',),
    ('jpg_path', '(Text)', '/misc/yoda/www/plots/sams/laible/',),
    ('jpg_quality', '(%)', 90,),
    ('axis_select', '(Textx,y,z,c)', 'c',),
    ('timespan', '(Minutes)', '=1680*((NFFT-NO)/SAMPLINGRATE)/60', '=1680*((B23-B24)/B22)/60'),
    ('delta_f', '(Hz)', '=SAMPLINGRATE/NFFT', '=B22/B23'),
    ('fscale', '(Hz-min,max,tick)', [0.000,200.000,20.000],),
    ('temporalresolution', '(Seconds)', '=(NFFT-NO)/SAMPLINGRATE', '=(B23-B24)/B22'),
    ('windowing', '(text)', 'Hanning',),
    ('spectralvariance', '(%)', 100,),
    ('colorbarlimits', '(g^2/Hz-min/max)', [-1.30E+1,-5.00E+0],),
    ('COORD_SYSTEM', '(Text)', '121F08',),
    ('CONVERT_COORD', '(1x9)', [1.000000,0.000000,0.000000,0.000000,1.000000,0.000000,0.000000,0.000000,1.000000],),
    ('TABLE_LOCATION', '(Text)', 'timmeh',),
    ('TABLE_NAME', '(Text)', '121f08',),
    ('MCOR_HOST', '(text)', 'chef',),
    ('MCOR_TABLE', '(text)', 'mcor_121f03',),
    ('TIMEINTERVAL', '(Sec)', 0,),
    ('SAMPLINGRATE', '(Hz)', 500,),
    ('NFFT', '(samp)', 2048,),
    ('NO', '(samp)', 0,),
    ('P', '(%)', '=100*NO/NFFT', '=100*B24/B23'),
    ('K', '(Integer)', '=7200/temporalresolution', '=7200/B11'),
]

for tup in params:
    for p in tup:
        print p,
    print

def main(infile):
    # Read data file into dataframe
    #infile = '/misc/yoda/www/plots/user/handbook/source_docs/hb_vib_Columbus_EMCS_Candidates/EMCSdata3.csv'
    dateparse = lambda x: pd.datetime.strptime(x, '%Y:%j:%H:%M:%S')
    df = pd.read_csv(infile, parse_dates=['GMT'], date_parser=dateparse)
    t = pd.to_datetime(df['GMT'].values)
    
    for c in df.columns:
        if not c.startswith('GMT'):
            plot_var(t, df, c)

if __name__ == "__main__":
    #main( sys.argv[1] )
    pass
