"""
Modified 01.2026
Patch notes:
--updated MASTER_DIR to accept environment variable for seamless transition from testing to production env
--updated major directory concats to use os.path.join to prevent '/' errors

DESCRIPTION:
Prior to temperature daily data aggregation, run this to pull requisite files, if exist
Pull
-yyyymmdd_hads_parsed.csv
-yyyymmdd_madis_parsed.csv
-daily_Tmin_yyyy_mm.csv (if exist)
-daily_Tmax_yyyy_mm.csv (if exist)
"""
import os
import sys
import subprocess
import pytz
import pandas as pd
import os
from datetime import datetime, timedelta

PARENT_DIR = r'https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/workflow_data/preliminary/'
REMOTE_BASEURL =r'https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/production/temperature/'
LOCAL_PARENT = os.environ.get("PROJECT_ROOT")
LOCAL_DATA_AQS = os.path.join(LOCAL_PARENT,'working_data/')
LOCAL_TEMP = os.path.join(LOCAL_PARENT,'data_outputs/tables/station_data/daily/raw/statewide/')
SRC_LIST = ['hads','madis']

if __name__=='__main__':
    if len(sys.argv) > 1:
        input_date = sys.argv[1]
        dt = pd.to_datetime(input_date)
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

    #Pull the daily data acquisitions (don't pull hi_mesonet even though it's there. handled directly from database)
    for src in SRC_LIST:
        src_url = PARENT_DIR+r'data_aqs/data_outputs/'+src+r'/parse/'
        dest_url = LOCAL_DATA_AQS
        filename = src_url + r'_'.join((prev_day_day,src,'parsed')) + r'.csv'
        local_name = dest_url + r'_'.join((prev_day_day,src,'parsed')) + r'.csv'
        cmd = ["wget",filename,"-O",local_name]
        subprocess.call(cmd)

    # Cumulative Month Data
    # Tmin partial_filled
    src_url = REMOTE_BASEURL + r'min/day/statewide/partial/station_data/'+year_str+r'/'+mon_str+r'/'
    filename = src_url + r'_'.join(('temperature','min','day_statewide_partial_station_data',prev_day_mon)) + r'.csv'
    local_name =  f"{LOCAL_PARENT}data_outputs/tables/station_data/daily/raw_qc/statewide/daily_Tmin_{prev_day_mon}_qc.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    # Tmax partial_filled
    src_url = REMOTE_BASEURL + r'max/day/statewide/partial/station_data/'+year_str+r'/'+mon_str+r'/'
    filename = src_url + r'_'.join(('temperature','max','day_statewide_partial_station_data',prev_day_mon)) + r'.csv'
    local_name =  f"{LOCAL_PARENT}data_outputs/tables/station_data/daily/raw_qc/statewide/daily_Tmax_{prev_day_mon}_qc.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    
    #Tmin daily stations pull
    src_url = REMOTE_BASEURL + r'min/day/statewide/raw/station_data/'+year_str+r'/'+mon_str+r'/'
    filename = src_url + r'_'.join(('temperature','min','day_statewide_raw_station_data',prev_day_mon)) + r'.csv'
    local_name = LOCAL_TEMP + r'_'.join(('daily','Tmin',prev_day_mon)) + r'.csv'
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)

    #Tmax daily stations pull
    src_url = REMOTE_BASEURL + r'max/day/statewide/raw/station_data/'+year_str+r'/'+mon_str+r'/'
    filename = src_url + r'_'.join(('temperature','max','day_statewide_raw_station_data',prev_day_mon)) + r'.csv'
    local_name = LOCAL_TEMP + r'_'.join(('daily','Tmax',prev_day_mon)) + r'.csv'
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)

    # Intermediate Working Data
    #Madis Tmin, Tmax
    src_name = "madis"
    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/temperature/working_data/processed_data/{src_name}/{year_str}/{mon_str}/"
    filename = f"{src_url}Tmin_{src_name}_{year_str}_{mon_str}_processed.csv"
    local_name =  f"{LOCAL_PARENT}working_data/processed_data/madis/Tmin_madis_{year_str}_{mon_str}_processed.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/temperature/working_data/processed_data/{src_name}/{year_str}/{mon_str}/"
    filename = f"{src_url}Tmax_{src_name}_{year_str}_{mon_str}_processed.csv"
    local_name =  f"{LOCAL_PARENT}working_data/processed_data/{src_name}/Tmax_{src_name}_{year_str}_{mon_str}_processed.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    #Hads Tmin, Tmax
    src_name = "hads"
    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/temperature/working_data/processed_data/{src_name}/{year_str}/{mon_str}/"
    filename = f"{src_url}Tmin_{src_name}_{year_str}_{mon_str}_processed.csv"
    local_name =  f"{LOCAL_PARENT}working_data/processed_data/{src_name}/Tmin_{src_name}_{year_str}_{mon_str}_processed.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/temperature/working_data/processed_data/{src_name}/{year_str}/{mon_str}/"
    filename = f"{src_url}Tmax_{src_name}_{year_str}_{mon_str}_processed.csv"
    local_name =  f"{LOCAL_PARENT}working_data/processed_data/{src_name}/Tmax_{src_name}_{year_str}_{mon_str}_processed.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    #Hi_mesonet
    src_name = "hi_mesonet"
    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/temperature/working_data/processed_data/{src_name}/{year_str}/{mon_str}/"
    filename = f"{src_url}Tmin_{src_name}_{year_str}_{mon_str}_processed.csv"
    local_name =  f"{LOCAL_PARENT}working_data/processed_data/{src_name}/Tmin_{src_name}_{year_str}_{mon_str}_processed.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/temperature/working_data/processed_data/{src_name}/{year_str}/{mon_str}/"
    filename = f"{src_url}Tmax_{src_name}_{year_str}_{mon_str}_processed.csv"
    local_name =  f"{LOCAL_PARENT}working_data/processed_data/{src_name}/Tmax_{src_name}_{year_str}_{mon_str}_processed.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    #Aggregated station data by county (partial_filled only)
    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/production/temperature/max/day/mn/partial/station_data/{year_str}/{mon_str}/"
    filename = f"{src_url}temperature_max_day_mn_partial_station_data_{year_str}_{mon_str}.csv"
    local_name =  f"{LOCAL_PARENT}data_outputs/tables/station_data/daily/raw_qc/county/daily_Tmax_MN_{year_str}_{mon_str}_qc.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/production/temperature/min/day/mn/partial/station_data/{year_str}/{mon_str}/"
    filename = f"{src_url}temperature_min_day_mn_partial_station_data_{year_str}_{mon_str}.csv"
    local_name =  f"{LOCAL_PARENT}data_outputs/tables/station_data/daily/raw_qc/county/daily_Tmin_MN_{year_str}_{mon_str}_qc.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/production/temperature/max/day/bi/partial/station_data/{year_str}/{mon_str}/"
    filename = f"{src_url}temperature_max_day_bi_partial_station_data_{year_str}_{mon_str}.csv"
    local_name =  f"{LOCAL_PARENT}data_outputs/tables/station_data/daily/raw_qc/county/daily_Tmax_BI_{year_str}_{mon_str}_qc.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/production/temperature/min/day/bi/partial/station_data/{year_str}/{mon_str}/"
    filename = f"{src_url}temperature_min_day_bi_partial_station_data_{year_str}_{mon_str}.csv"
    local_name =  f"{LOCAL_PARENT}data_outputs/tables/station_data/daily/raw_qc/county/daily_Tmin_BI_{year_str}_{mon_str}_qc.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/production/temperature/max/day/ka/partial/station_data/{year_str}/{mon_str}/"
    filename = f"{src_url}temperature_max_day_ka_partial_station_data_{year_str}_{mon_str}.csv"
    local_name =  f"{LOCAL_PARENT}data_outputs/tables/station_data/daily/raw_qc/county/daily_Tmax_KA_{year_str}_{mon_str}_qc.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/production/temperature/min/day/ka/partial/station_data/{year_str}/{mon_str}/"
    filename = f"{src_url}temperature_min_day_ka_partial_station_data_{year_str}_{mon_str}.csv"
    local_name =  f"{LOCAL_PARENT}data_outputs/tables/station_data/daily/raw_qc/county/daily_Tmin_KA_{year_str}_{mon_str}_qc.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/production/temperature/max/day/oa/partial/station_data/{year_str}/{mon_str}/"
    filename = f"{src_url}temperature_max_day_oa_partial_station_data_{year_str}_{mon_str}.csv"
    local_name =  f"{LOCAL_PARENT}data_outputs/tables/station_data/daily/raw_qc/county/daily_Tmax_OA_{year_str}_{mon_str}_qc.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)

    src_url = f"https://ikeauth.its.hawaii.edu/files/v2/download/public/system/ikewai-annotated-data/HCDP/production/temperature/min/day/oa/partial/station_data/{year_str}/{mon_str}/"
    filename = f"{src_url}temperature_min_day_oa_partial_station_data_{year_str}_{mon_str}.csv"
    local_name =  f"{LOCAL_PARENT}data_outputs/tables/station_data/daily/raw_qc/county/daily_Tmin_OA_{year_str}_{mon_str}_qc.csv"
    cmd = ["wget",filename,"-O",local_name]
    subprocess.call(cmd)
    if os.path.getsize(local_name) == 0:
        os.remove(local_name)
