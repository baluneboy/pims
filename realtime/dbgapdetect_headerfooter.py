#!/usr/bin/env python

import socket
import datetime

#-----------------------------------------------------------------------------------------------------        
HEADER = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html>
	<head>  
		<meta http-equiv="content-type" content="text/html; charset=iso-8859-1" />
		<meta http-equiv="cache-control" content="no-cache" />
	
		<title>SAMS Pkt %</title>
		<link type="text/css" rel="stylesheet" media="all" href="css/reset.css" />
		<link type="text/css" rel="stylesheet" media="all" href="css/vader-jquery-ui.css" />
		<link type="text/css" rel="stylesheet" media="all" href="css/prettify.css" />
		<link type="text/css" rel="stylesheet" media="all" href="css/styles.css" />
		<link type="text/css" rel="stylesheet" media="all" href="css/fixed_table_rc.css" />

	  	<script src="js/jquery.min.js"></script>
	  	<script src="js/jquery-1.10.2.min.js" type="text/javascript"></script>
		<script src="js/global.js" type="text/javascript"></script>
		<script src="js/sortable_table.js" type="text/javascript"></script>
		<script src="js/fixed_table_rc.js" type="text/javascript"></script>
		<script src="js/prettify.js" type="text/javascript"></script>

		<style>
			#main-content { min-height: 600px; overflow: hidden; }			
			#example_d1 { width: 95%; }
			#example_d2 { width: 95%; }
			#example_d3 { width: 95%; }
			
			#example_d3 .dwrapper { width: 980px; }
			
			.dwrapper #fixed_hdr1 { width: 1500px; }
			#fixed_hdr1 th { font-weight: bold; }
			#fixed_hdr1 th, td { border-width: 1px; border-style: solid; padding: 2px 4px; }
			
			.dwrapper { padding: 2px; overflow: hidden; vertical-align: top; }
			.dwrapper div.tblWrapper { height: 300px; overflow: auto; margin-top: 10px;}
			.dwrapper div.ft_container { width: 100%; margin-top: 10px; height: 420px;}		
			
			body { line-height: 1.5em; }
			#main-content { min-width: 1000px; }
		</style>

		<script>
			$(function () {
				
				$('#main-content').width($('#page-content').width() - 251);
				
				$('#applyFixedTableRC').click(function () {
					
					if ($(this).hasClass('disabled')) return;
					
					$('#fixed_hdr1').unwrap();
					
					$('#fixed_hdr1').fxdHdrCol({
						fixedCols: 3,
						width:     '100%',
						height:    400,
						colModal: [
						   { width: 50, align: 'center' },
						   { width: 110, align: 'center' },
						   { width: 170, align: 'left' },
						   { width: 250, align: 'left' },
						   { width: 100, align: 'left' },
						   { width: 70, align: 'left' },
						   { width: 100, align: 'left' },
						   { width: 100, align: 'center' },
						   { width: 90, align: 'left' },
						   { width: 400, align: 'left' }
						]					
					});
					
					$(this).addClass('disabled');
				});
				
				$('.example').addClass('ui-widget-content');
				
				$('#fixed_hdr2').fxdHdrCol({
					fixedCols:  0,
					width:     "100%",
					height:    400,
					colModal: [
						   { width: 50, align: 'center' },
						   { width: 110, align: 'center' },
						   { width: 170, align: 'left' },
						   { width: 250, align: 'left' },
						   { width: 100, align: 'left' },
						   { width: 70, align: 'left' },
						   { width: 100, align: 'left' },
						   { width: 100, align: 'center' },
						   { width: 90, align: 'left' },
						   { width: 400, align: 'left' }
					],
					sort: true
				});
				
				$('#fixed_hdr3').fxdHdrCol({
					fixedCols:  0,
					width:     "100%",
					height:    510,
					colModal: [{width: 110, align: 'right'},
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}, 
					           {width: 40,  align: 'right'}
					          ]
				});				
				
				$('.menu-item').click (function () {
					$(this).parent().find('.sub_menu').slideToggle();
				});

				$('.showcode').click (function () {
			      	$(this).text(function (i, v) {
			      	    return (v == 'View code')?'Hide code':'View code'
			      	});
			        $(this).next().slideToggle();
			    });
			});
			
		</script>
	</head>
	<body onload="prettyPrint()">
		<div id="c_overlay"></div>
		<div id="c_helper"></div>
		<script>
			try { $('#c_overlay').css({height: $(document).height(), width: $(document).width()}); } catch (e) {	}
		</script>    
		<div class="clear"></div>
		<div id="page-content">
			<div id="main-content" class="ui-widget-content">			
				<h2 id="ft_demo">Scrollable SAMS Packet Percentages (click <a class="pop" href="details.html">here</a> for details).</h2>
				<div class="example" id="example_d3">
					<div class="dwrapper">
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