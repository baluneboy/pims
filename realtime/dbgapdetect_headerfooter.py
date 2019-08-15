#!/usr/bin/env python

import socket
import datetime

#-----------------------------------------------------------------------------------------------------        
HEADER = '''<!doctype html>
<html lang="en">
<head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
	  <title>SAMS Pkt %</title>
      <style>
            .dataframe {
                  width: 1350px;
                  table-layout: fixed;
                  border-collapse: collapse;
            }
            .dataframe th {
                  text-decoration: underline;
            }
            .dataframe th,
            .dataframe td {
                  padding: 5px;
                  text-align: left;
            }
            .dataframe td:nth-child(1),
            .dataframe th:nth-child(1) {
                  min-width: 150px;
            }
            .dataframe td:nth-child(2),
            .dataframe th:nth-child(2) {
                  min-width: 48px;
            }
            .dataframe td:nth-child(3),
            .dataframe th:nth-child(3) {
                 min-width: 48px;
            }
            .dataframe td:nth-child(4),
            .dataframe th:nth-child(4) {
                 min-width: 48px;
            }            
            .dataframe td:nth-child(5),
            .dataframe th:nth-child(5) {
                 min-width: 48px;
            }            
            .dataframe td:nth-child(6),
            .dataframe th:nth-child(6) {
                 min-width: 48px;
            }
            .dataframe td:nth-child(7),
            .dataframe th:nth-child(7) {
                 min-width: 48px;
            }
            .dataframe td:nth-child(8),
            .dataframe th:nth-child(8) {
                 min-width: 48px;
            }
            .dataframe td:nth-child(9),
            .dataframe th:nth-child(9) {
                 min-width: 48px;
            }            
            .dataframe td:nth-child(10),
            .dataframe th:nth-child(10) {
                 min-width: 48px;
            }
            .dataframe td:nth-child(11),
            .dataframe th:nth-child(11) {
                 min-width: 48px;
            }
            .dataframe td:nth-child(12),
            .dataframe th:nth-child(12) {
                 min-width: 48px;
            }
            .dataframe td:nth-child(13),
            .dataframe th:nth-child(13) {
                 min-width: 48px;
            }            
            .dataframe td:nth-child(14),
            .dataframe th:nth-child(14) {
                 min-width: 48px;
            }            
            .dataframe td:nth-child(15),
            .dataframe th:nth-child(15) {
                 min-width: 48px;
            }
            .dataframe td:nth-child(16),
            .dataframe th:nth-child(16) {
                 min-width: 48px;
            }
            .dataframe td:nth-child(17),
            .dataframe th:nth-child(17) {
                 min-width: 48px;
            }
            .dataframe td:nth-child(18),
            .dataframe th:nth-child(18) {
                 min-width: 48px;
            }            
            .dataframe td:nth-child(19),
            .dataframe th:nth-child(19) {
                 min-width: 48px;
            }            
            .dataframe td:nth-child(20),
            .dataframe th:nth-child(20) {
                 min-width: 48px;
            }            
            .dataframe thead {
                  background-color: #333333;
                  color: #fdfdfd;
            }
            .dataframe thead tr {
                  display: block;
                  position: relative;
            }
            .dataframe tbody {
                  display: block;
                  overflow: auto;
                  width: 100%;
                  height: 750px;
                  background-color: #dddddd;
            }
            .dataframe tbody tr:nth-child(even) {
                  background-color: #cac5c5;
            }
      </style>
</head>
<body>
<!-- THE HEADER ENDS HERE -->
'''

#-----------------------------------------------------------------------------------------------------        
FOOTER = '''<!-- THE FOOTER STARTS HERE -->
					</div>
				</div>					
				<div class="clear"></div>
				<h2 id="ft_feedback" >Feedback / Comments</h2>
				<p>
					Send any feedback or comments on this page to: <a class="glow" href="mailto:pimsops@grc.nasa.gov">pimsops@grc.nasa.gov</a>
				</p>
			</div>
		</div>
		<div class="clear"></div>
		<div id="footer">'''
FOOTER += '<div class="text-align-left">Last modified by %s at <b>GMT %s</b></div>' %  (socket.gethostname(), str(datetime.datetime.now())[0:-7])
FOOTER += '''</div>
	</body>
</html>
'''

#-----------------------------------------------------------------------------------------------------        
OLDHEADER = '''<!DOCTYPE html>
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
OLDFOOTER = '<updatetag>updated at GMT %s</updatetag><br>' % str(datetime.datetime.now())[0:-7]
OLDFOOTER += '<hosttag>host: %s</hosttag><br><br>' % socket.gethostname()
OLDFOOTER += '''
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