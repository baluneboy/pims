#!/usr/bin/env python

import socket
import datetime

#-----------------------------------------------------------------------------------------------------        
HEADER = '''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="600">
<title>PIMS db</title>
<style>
updatetag {
text-align: left;
color: black;
font-size: 0.83em;
font-family: Verdana,Geneva,sans-serif;
}
dbhosttag {
font-size: 0.55em;
text-align: right;
font-family: Verdana,Geneva,sans-serif;
color: gray;
}
hosttag {
font-size: 0.75em;
text-align: left;
font-family: Verdana,Geneva,sans-serif;
color: gray;
}
titletag {
font-size: 1.25em;
font-weight: bold;
font-family: Verdana,Geneva,sans-serif;
color: black;
text-align: left;
text-decoration: underline;
}
captiontag {
font-size: 1.1em;
font-weight: bold;
font-family: Verdana,Geneva,sans-serif;
color: black;
text-align: left;
}
toprow {
background-color: black;
font-size: 0.729em;
color: orange;
}
.df {
width: 100%;
font-family: Verdana,Geneva,sans-serif;
border-collapse: collapse;
}
.df td, .df th {
border: 1px solid #123456;
padding: 3px 7px 2px;
font-size: 0.99em;
}
.df th {
border: 1px solid #ffffff;
background-color: black;
font-size: 1.1em;
vertical-align: bottom;
padding-bottom: 5px;
padding-top: 5px;
color: #ffffff;
}
.df tbody tr:nth-child(even) {background: #CCC} tr:nth-child(odd) {background: #FFF}
</style>
</head>
<body>
<titletag>PIMS Database Tables <a href="./dbsams.html"> (click here for dbsams)</a></titletag><br>
        '''
        
#-----------------------------------------------------------------------------------------------------        
FOOTER = '<updatetag>updated at GMT %s</updatetag><br>' % str(datetime.datetime.now())[0:-7]
FOOTER += '<hosttag>host: %s</hosttag><br><br>' % socket.gethostname()
FOOTER += '''
    </body>
</html>
'''

#-----------------------------------------------------------------------------------------------------        
OTHER = """NOTE THIS GREEN COMMENT PART IS SNIPPET OF POSSIBLY IMPROVED TABLE HEADER ROW
<SNIP>
}
.df tbody tr:nth-child(even) {background: #CCC} tr:nth-child(odd) {background: #FFF}
</style>
</head>
<body>
<titletag>PIMS Database Tables <a href="./dbsams.html"> (click here for dbsams)</a></titletag><br>
<updatetag>updated at GMT 2014-09-06 10:11:03</updatetag><br>
<hosttag>host: jimmy</hosttag><br>
<br>
<table class="dataframe df" border="1">
<thead> <tr>
<th><toprow>LAB/RACK</toprow></th>
<th colspan="2"><toprow>COL/ER3</toprow></th>
<th colspan="2"><toprow>USL/ER2</toprow></th>
<th colspan="2"><toprow>USL/ER1</toprow></th>
<th colspan="2"><toprow>JEM/ER4</toprow></th>
<th colspan="2"><toprow>COL/ER3</toprow></th>
<th colspan="2"><toprow>USL/FIR</toprow></th>
</tr>
<tr>
<th>hour</th>
<th><dbhosttag>kenny</dbhosttag><br>121f02<br>
~data%</th>
<th><dbhosttag>kenny</dbhosttag><br>121f02<br>
#pkts</th>
<th><dbhosttag>tweek</dbhosttag><br>121f03<br>
~data%</th>
<th><dbhosttag>tweek</dbhosttag><br>121f03<br>
#pkts</th>
<th><dbhosttag>mr-hankey</dbhosttag><br>121f04<br>
~data%</th>
<th><dbhosttag>mr-hankey</dbhosttag><br>121f04<br>
#pkts</th>
<th><dbhosttag>chef</dbhosttag><br>121f05<br>
~data%</th>
<th><dbhosttag>chef</dbhosttag><br>121f05<br>
#pkts</th>
<th><dbhosttag>timmeh</dbhosttag><br>121f08<br>
~data%</th>
<th><dbhosttag>timmeh</dbhosttag><br>121f08<br>
#pkts</th>
<th><dbhosttag>manbearpig</dbhosttag><br>es06<br>
~data%</th>
<th><dbhosttag>manbearpig</dbhosttag><br>es06<br>
#pkts</th>
</tr>
</thead> <tbody>
<SNIP>
"""