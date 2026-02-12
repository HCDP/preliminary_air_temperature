"""
Runs prior to mapping workflow
"""
import os
import sys
import subprocess
import pytz
from datetime import datetime, timedelta
from pandas import to_datetime

REMOTE_BASEURL =r'https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/production/temperature/'
DEPEND_DIR = r'https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/temperature/'
LOCAL_PARENT = os.environ.get("PROJECT_ROOT")

if __name__=="__main__":
    if len(sys.argv) > 1:
        input_date = sys.argv[1]
        dt = to_datetime(input_date)
        this_year = dt.year
        this_mon = dt.month
        month_st = datetime(this_year,this_mon,1)
        hst = pytz.timezone('HST')
        today = datetime.today().astimezone(hst)
        today_year = today.year
        today_mon = today.month
        today_st = datetime(today_year,today_mon,1)
        if month_st == today_st:
            print('Month incomplete. Exiting.')
            quit()
        else:
            year_str = month_st.strftime('%Y')
            mon_str = month_st.strftime('%m')
    else:
        hst = pytz.timezone('HST')
        today = datetime.today().astimezone(hst)
        this_year = today.year
        this_mon = today.month
        this_st = datetime(this_year,this_mon,1)
        prev = this_st - timedelta(days=1)
        prev_year = prev.year
        prev_mon = prev.month
        month_st = datetime(prev_year,prev_mon,1)
        year_str = month_st.strftime('%Y')
        mon_str = month_st.strftime('%m')

    #Tmin daily stations pull
    src_url = REMOTE_BASEURL + r'min/day/statewide/partial/station_data/'+year_str+r'/'+mon_str+r'/'
    filename = src_url + r'_'.join(('temperature','min','day_statewide_partial_station_data',year_str,mon_str)) + r'.csv'
    local_name = LOCAL_PARENT + r'_'.join(('daily','Tmin',year_str,mon_str,'qc')) + r'.csv'
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)

    #Tmax daily stations pull
    src_url = REMOTE_BASEURL + r'max/day/statewide/partial/station_data/'+year_str+r'/'+mon_str+r'/'
    filename = src_url + r'_'.join(('temperature','max','day_statewide_partial_station_data',year_str,mon_str)) + r'.csv'
    local_name = LOCAL_PARENT + r'_'.join(('daily','Tmax',year_str,mon_str,'qc')) + r'.csv'
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)

    #Tmin monthly stations pull
    src_url = REMOTE_BASEURL + r'min/month/statewide/partial/station_data/'+year_str+r'/'
    filename = src_url + r'_'.join(('temperature','min','month_statewide_partial_station_data',year_str))+r'.csv'
    local_name = LOCAL_PARENT + r'_'.join(('monthly','Tmin',year_str,'qc'))+r'.csv'
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)

    #Tmax monthly stations pull
    src_url = REMOTE_BASEURL + r'max/month/statewide/partial/station_data/'+year_str+r'/'
    filename = src_url + r'_'.join(('temperature','max','month_statewide_partial_station_data',year_str))+r'.csv'
    local_name = LOCAL_PARENT + r'_'.join(('monthly','Tmax',year_str,'qc'))+r'.csv'
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
