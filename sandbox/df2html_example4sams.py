#!/usr/bin/env python 

import numpy as np
import pandas as pd

#FF0000 is RED
#000000 is BLACK
#FFFFFF is WHITE

HEADER = '''
<html>
    <head>
        <style>
            .okay tbody tr { background-color: #FFFFFF; color: #000000 }
            .host tbody tr { background-color: #000000; color: #FFFFFF }
            .red  tbody tr { background-color: #FFFFFF; color: #FF0000 }
        </style>
    </head>
    <body>
'''

FOOTER = '''
    </body>
</html>
'''

df = pd.DataFrame({
        'GMT': ['2015:174:12:00:15', '2015:174:12:00:15', '2015:174:12:00', '2015:174:11:55:00'],
        'Device': ['121f03rt', '121f04rt', 'butters', 'es03rt'],
        'Type': ['SE', 'SE', 'HOST', 'MSG'] })

with open('/misc/manbearpig/tmp/test.html', 'w') as f:
    f.write(HEADER)
    f.write(df1.to_html(classes='okay', index=False))
    f.write(df2.to_html(classes='host', index=False, header=False))
    f.write(df3.to_html(classes='red', index=False, header=False))
    f.write(FOOTER)
