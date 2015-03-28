#!/usr/bin/env python

import sys
import datetime

_PREAMBLE = """<html><head>
  
  <script type="text/javascript" src="https://www.google.com/jsapi"></script>
  
  <script type="text/javascript">
      google.load('visualization', '1', {packages:['table']});
      google.setOnLoadCallback(drawTable);
      function drawTable() {
        var data = new google.visualization.DataTable();
        data.addColumn('date',    'GMT Date/Time');
        data.addColumn('string',  'PlotFile');
        data.addColumn('string',  'Accepted');
        data.addColumn('string',  'Note');
        data.addRows(["""

_EPILOGUE = " " * 17 + """]);

        // Create formatter for datetime
        var formatter = new google.visualization.DateFormat({pattern: "yyyy-MM-dd/HH:mm:ss"});

        // Reformat
        formatter.format(data, 0)

        var table = new google.visualization.Table(document.getElementById('table_div'));
        table.draw(data, {showRowNumber: false});
      }
</script>
  </head>
  <body>
  <small><em property="italic"">This table was updated at</em>  %s</small><br>
    <div id='table_div' style="width: 444px"></div>
  </body>
</html>""" % datetime.datetime.now().strftime('GMT %Y-%m-%d/%H:%M:%S')

def main(html_file):

    # get table entries
    table_rows = """
    \t\t\t[new Date(2014, 2, 1, 12, 15, 55), '121f05_intrms',  'yes', 'hello'],
    \t\t\t[new Date(2014, 2, 1, 12, 15, 55), '121f03_intavg',  'yes', 'hello'],
    """
    
    # write to html_file
    with open(html_file, "w") as text_file:
        text_file.write(_PREAMBLE)
        text_file.write(table_rows)
        text_file.write(_EPILOGUE)
    
if __name__ == "__main__":
    main(sys.argv[1])
    
    
    
# SET SQL_SAFE_UPDATES=0;
# UPDATE jaxapost.plotfile SET status="pending", time="2014-02-01 09:30:00" WHERE file = "121f05_intrms.csv";
# SET SQL_SAFE_UPDATES=1;