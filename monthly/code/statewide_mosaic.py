import os
import sys
import pytz
import subprocess
import rasterio
import numpy as np
from datetime import datetime,timedelta
from affine import Affine
from pyproj import Transformer
from dateutil import parser

master_dir = os.environ.get("PROJECT_ROOT")
output_dir = master_dir
ref_dir = master_dir
varname = "temperature"
version = "preliminary"
fill_value = "-9999"
coord = "Decimal Degrees"
ref_sys = "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

hst = pytz.timezone('HST')

def get_coordinates(GeoTiff_name):

    # Read raster
    with rasterio.open(GeoTiff_name) as r:
        T0 = r.transform  # upper-left pixel corner affine transform
        A = r.read()  # pixel values

    # All rows and columns
    cols, rows = np.meshgrid(np.arange(A.shape[2]), np.arange(A.shape[1]))

    # Get affine transform for pixel centres
    T1 = T0 * Affine.translation(0.5, 0.5)
    # Function to convert pixel row/column index (from 0) to easting/northing
    # at centre
    def rc2en(r, c): return T1 * (c, r)

    # All eastings and northings (there is probably a faster way to do this)
    eastings, northings = np.vectorize(
        rc2en, otypes=[
            float, float])(
        rows, cols)

    transformer = Transformer.from_proj(
        'EPSG:4326',
        '+proj=longlat +datum=WGS84 +no_defs +type=crs',
        always_xy=True)

    LON, LAT = transformer.transform(eastings, northings)
    return LON, LAT

def get_isl_dims(iCode,subproduct):
    tiffname = ref_dir + f"{varname}_{subproduct}_{iCode}.tif"
    lons,lats = get_coordinates(tiffname)
    lons = np.unique(lons.reshape(-1))
    lats = np.unique(lats.reshape(-1))
    xdiff = lons[1:]-lons[:-1]
    ydiff = lats[1:]-lats[:-1]
    xresolution = np.round(np.min(xdiff),6)
    yresolution = np.round(np.min(ydiff),6)
    xmin = np.min(lons)
    xmax = np.max(lons)
    ymin = np.min(lats)
    ymax = np.max(lats)
    isl_dims = {'XResolution':xresolution,'YResolution':yresolution,'Xmin':xmin,'Xmax':xmax,'Ymin':ymin,'Ymax':ymax}

    return isl_dims

def read_county_meta(subproduct):
    county_list = ['bi','ka','mn','oa']
    ndays = []
    missing_days = []
    for county in county_list:
        meta_file = master_dir + f"{varname}_metadata_{subproduct}_{county}.txt"
        with open(meta_file,"r") as f:
            lines = f.readlines()
        meta_dict = dict([(line[:20].strip(),line[20:].split('\n')[0].strip()) for line in lines])
        ndays.append(meta_dict['numDaysUsed'])
        missing_days.append(meta_dict['missingDays'])
    return (ndays,missing_days)

def state_metadata(date,subproduct):
    
    today = datetime.today().astimezone(hst)
    monyear = date.strftime('%b. %Y')
    data_statement = f"This {monyear} monthly temperature {subproduct} mosaic of the State of Hawaii is a high spatial resolution gridded prediction of {subproduct} temperature in degrees Celsius. This was produced using a temporal average of the daily gridded temperature maps produced by the HCDP. This process was done for four individually produced maps of Kauai, Honolulu (Oahu), Maui (Maui, Lanai, Molokai, & Kahoolawe) and Hawaii counties. All maps are subject to change as new data becomes available or unknown errors are corrected in reoccurring versions. Errors in temperature estimates do vary over space meaning any gridded temperature value, even on higher quality maps, could still produce incorrect estimates"
    kw_list = ', '.join(['Hawaii','Hawaiian Islands',subproduct+' temperature prediction','monthly temperature','temperature','climate'])
    county_list = "bi, ka, mn, oa"
    isl_dims = get_isl_dims("statewide",subproduct)
    ndays_list, missing_day_list = read_county_meta(subproduct)
    ndays_str = ", ".join(ndays_list)
    missing_day_all = "; ".join(missing_day_list)
    credit_statement = "All data are produced by the University of Hawai‘i at Manoa with the Water Resources Research Center (WRRC) and the Dept. of Geography and the Environment Ecohydrology Lab. This work is supported by the ChangeHI program, funded by NSF EPSCoR Research Infrastructure Improvement Award OIA-2149133. The technical support and advanced computing resources from University of Hawaii Information Technology Services – Cyberinfrastructure, funded in part by the National Science Foundation CC* awards # 2201428 and # 2232862 are gratefully acknowledged."
    contact_list = "Keri Kodama (kodamak8@hawaii.edu), Matthew Lucas (mplucas@hawaii.edu), Ryan Longman (rlongman@hawaii.edu), Thomas Giambelluca (thomas@hawaii.edu)"
    field_value_list = {'attribute':'value','dataStatement':data_statement,
                        'keywords':kw_list,'county':county_list,
                        'productionDate':today.strftime('%Y-%m-%d'),
                        'dataYearMon':monyear,
                        'dataVersionType':version,
                        'numDaysUsed':ndays_str,
                        'missingDays':missing_day_all,
                        'GeoCoordUnits':coord,
                        'GeoCoordRefSystem':ref_sys,
                        'XResolution':str(isl_dims['XResolution']),
                        'YResolution':str(isl_dims['YResolution']),
                        'ExtentXmin':str(isl_dims['Xmin']),
                        'ExtentXmax':str(isl_dims['Xmax']),
                        'ExtentYmin':str(isl_dims['Ymin']),
                        'ExtentYmax':str(isl_dims['Ymax']),
                        'credits':credit_statement,'contacts':contact_list}
    col1 = list(field_value_list.keys())
    col2 = [field_value_list[key] for key in col1]
    meta_file = master_dir + f"temperature_metadata_{subproduct}_statewide.txt"
    with open(meta_file,"w") as fmeta:
        for (key,val) in zip(col1,col2):
            line = [key,val]
            fmt_line = "{:20}{:60}\n".format(*line)
            fmeta.write(fmt_line)

def statewide_mosaic(subproduct):
    icode_list = ['bi','ka','mn','oa']
    file_names = [output_dir+"_".join((varname,subproduct,icode))+ ".tif" for icode in icode_list]
    output_name = output_dir + "_".join((varname,subproduct,"statewide")) + ".tif"
    cmd = "gdal_merge.py -o "+output_name+" -of gtiff -co COMPRESS=LZW -init -9999 -a_nodata -9999"
    return subprocess.run(cmd.split()+file_names).returncode

#should run date agnostic. Will automatically mosaic the existing county files in the container
if __name__=="__main__":
    subproduct = sys.argv[1]
    if len(sys.argv) > 2:
        input_date = sys.argv[2]
        month_date = parser.parse(input_date)
    else:
        #Ensure runs for only the most recent completed month in near-real-time
        today = datetime.today().astimezone(hst)
        #Get start of current month
        month_st = datetime(today.year,today.month,1)
        #Fall back into previous month
        prev = month_st - timedelta(days=1)
        #Set date to start of previous full month
        month_date = datetime(prev.year,prev.month,1)
    
    statewide_mosaic(subproduct)
    state_metadata(month_date,subproduct)