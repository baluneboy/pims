import datetime
import webbrowser
import pandas as pd


def open_url(dtm_str):
    webbrowser.open('https://pims.grc.nasa.gov/plots/user/sams/dbpimscache/hourly/' + dtm_str + '/dbpims.html', new=1)


if __name__ == '__main__':
    today_date = datetime.datetime.today()
    end_str = today_date.strftime('%Y-%m-%d')
    dr = pd.date_range(end=end_str, periods=14, freq='12H')
    for d in dr:
        dtm_str = d.strftime('%Y-%m-%dT%H')
        open_url(dtm_str)
