"""
Modified 01.2026
Patch notes:
--updated MASTER_DIR to accept environment variable for seamless transition from testing to production env
--updated major directory concats to use os.path.join to prevent '/' errors
--deleted redundancy with temp_agg_wget so that raw station data files are not pulled twice for no reason. Download and unpack dependency folder only.
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
LOCAL_DEPEND = os.path.join(LOCAL_PARENT,'daily/')

if __name__=="__main__":
    if len(sys.argv) > 1:
        input_date = sys.argv[1]
        dt = to_datetime(input_date)
        prev_day_day = dt.strftime('%Y%m%d')
        prev_day_mon = dt.strftime('%Y_%m')
        year_str = dt.strftime('%Y')
        mon_str = dt.strftime('%m')
    else:
        hst = pytz.timezone('HST')
        today = datetime.today().astimezone(hst)
        prev_day = today - timedelta(days=1)
        prev_day_day = prev_day.strftime('%Y%m%d')
        prev_day_mon = prev_day.strftime('%Y_%m')
        year_str = prev_day.strftime('%Y')
        mon_str = prev_day.strftime('%m')

    #Air temp daily dependencies
    src_url = DEPEND_DIR + "dependencies.tar.gz"
    dest_path = LOCAL_DEPEND + "dependencies.tar.gz"
    cmd = ["wget",src_url,"-O",dest_path]
    subprocess.call(cmd)
    cmd = ["tar","-xvf",dest_path,"-C",LOCAL_DEPEND]
    subprocess.call(cmd)
