#!/usr/bin/env python

import sys
from pims.database.pimsquery import CoordQueryAsDataFrame
import datetime

_PREAMBLE = """<html>
  <head>
    <!--Load the AJAX API-->
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">

      // Load the Visualization API and the timeline package.
      google.load('visualization', '1.0', {'packages':['timeline']});

      // Set a callback to run when the Google Visualization API is loaded.
      google.setOnLoadCallback(drawChart);

      // Callback that creates and populates a data table,
      // instantiates the timeline chart, passes in the data
      // and draws it.
      function drawChart() {
        var container = document.getElementById('sams_sensor_timeline');
        var chart = new google.visualization.Timeline(container);
        var dataTable = new google.visualization.DataTable();
        dataTable.addColumn({ type: 'string', id: 'Sensor' });
        dataTable.addColumn({ type: 'string', id: 'Name' });
        dataTable.addColumn({ type: 'date', id: 'Start' });
        dataTable.addColumn({ type: 'date', id: 'End' });
        dataTable.addRows(["""

_EPILOGUE = """        ]);

        var options = {
          timeline: { colorByRowLabel: false },
          backgroundColor: '#FFF',
          //colors: ['#003380', '#0066FF', '#003380', '#007A00', '#FF5C33', '#991F00'],
        };

        chart.draw(dataTable, options);
      }
</script>
  </head>

  <body>
  <big><span style="font-weight: bold;">Updated %s</span></big><br>
    <!--Div that will hold the timeline chart-->
    <div id="sams_sensor_timeline" style="height: 900px;"></div>
  </body>
</html>""" % datetime.datetime.now().strftime('GMT %Y-%m-%d/%H:%M:%S')

def main(html_file):

    csv_file = html_file.replace('.html', '.csv')
    
    # grab sensor location info
    c = CoordQueryAsDataFrame(host='kyle') # or localhost for testing on jimmy
    c.filter_dataframe_sensors('^121f0|^es0|hirap')
    c.filter_pre2001()

    # write CSV to csv_file
    c.dataframe.to_csv(csv_file, index=False)

    # make HTML sensor_rows succinct (no rpy or xyz)
    c.consolidate_rpy_xyz()
    sensor_rows = c.get_rows()
    
    # write HTML to html_file
    with open(html_file, "w") as text_file:
        text_file.write(_PREAMBLE)
        text_file.write(sensor_rows)
        text_file.write(_EPILOGUE)
    
    #print _PREAMBLE
    #print sensor_rows
    #print _EPILOGUE
    
if __name__ == "__main__":
    main(sys.argv[1])
    