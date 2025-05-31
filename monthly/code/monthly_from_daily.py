import os
import sys
import pytz
import rasterio
import urllib.request
import urllib.error
import numpy as np
from pandas import date_range
from rasterio.io import MemoryFile
from dateutil import parser
from datetime import datetime,timedelta
from calendar import monthrange
from util import handle_retry

master_dir = os.environ.get("PROJECT_ROOT")
dep_dir = master_dir + "dependencies/"
hcdp_api_token = os.environ.get("HCDP_API_TOKEN")
varname = "temperature"
skip_max = 5
NO_DATA_VAL = os.environ.get("NO_DATA_VAL")

def output_tiff(data_arr,extent,subproduct):
    ref_tiff = os.path.join(dep_dir,"geoTiffs_250m","dem","_".join((extent,"dem_250m"))+".tif")
    output_file = os.path.join(master_dir,"_".join((varname,subproduct,extent))) + ".tif"
    #Get tiff profile from reference
    with rasterio.open(ref_tiff) as ref:
        ref_profile = ref.profile
        ref_profile.update(compress='lzw')
        ref_profile.update(nodata=NO_DATA_VAL)
        data = ref.read(1)
        mask = ref.read_masks(1)
        #mask = np.isnan(data)
        data_arr[mask==0] = NO_DATA_VAL
        with rasterio.open(output_file,'w',**ref_profile) as dst:
            dst.write(data_arr,1)

def get_data(date_s,extent,subproduct,data_arr):
    found = False
    #set raster url
    raster_url = f"https://api.hcdp.ikewai.org/raster?date={date_s}&extent={extent}&datatype={varname}&aggregation={subproduct}&period=day"
    #prepare request
    req = urllib.request.Request(raster_url)
    #add auth header to request
    req.add_header("Authorization", f"Bearer {hcdp_api_token}")
    try:
        #open remote file
        with urllib.request.urlopen(req, timeout = 5) as f:
            #wrap file handle in rasterio memory file
            with MemoryFile(f) as mem_f:
                #open the memory file as a rasterio object
                with mem_f.open() as raster:
                    #initialize data array of daily files
                    if data_arr is None:
                        data_arr = [raster.read(1)]
                    else:
                        data_arr.append(raster.read(1))
        found = True
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise e
        print(f"API request failed on {date_s}")

    return (found,data_arr)


def get_monthly_from_daily(date,extent,subproduct):
    mon_st = datetime(date.year,date.month,1)
    ndays = monthrange(date.year,date.month)[1]
    mon_en = datetime(date.year,date.month,ndays)
    days_in_mon = date_range(mon_st,mon_en)
    #initialize data_arr to collect monthly values
    daily_arr = None
    missing_days = []
    for day in days_in_mon:
        date_s = day.strftime("%Y-%m-%d")
        found,daily_arr = handle_retry(get_data,(date_s,extent,subproduct,daily_arr))
        if not found:
            missing_days.append(date_s)
    
    #Check if any days missed
    daily_arr = np.stack(daily_arr,axis=0)
    ncollect = daily_arr.shape[0]
    if ncollect > (ndays - skip_max):
        monthly_avg = np.mean(daily_arr,axis=0)
    else:
        print("Missing too many days. Exiting.")
        quit()
    
    with open(master_dir+f"meta_work_{subproduct}_{extent}.txt","w") as f:
        f.write(", ".join(missing_days))

    output_tiff(monthly_avg,extent,subproduct)
        


if __name__=="__main__":
    extent = sys.argv[1]
    subproduct = sys.argv[2] #minimum or maximum or mean
    if len(sys.argv) > 3:
        input_date = sys.argv[3]
        month_date = parser.parse(input_date)
    else:
        hst = pytz.timezone('HST')
        today = datetime.today().astimezone(hst)
        prev = today - timedelta(days=1)
        month_date = datetime(prev.year,prev.month,1)
    
    get_monthly_from_daily(month_date,extent,subproduct)
