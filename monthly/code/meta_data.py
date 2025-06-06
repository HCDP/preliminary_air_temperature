import os
import sys
import pytz
import rasterio
import numpy as np
from affine import Affine
from pyproj import Transformer
from datetime import datetime,timedelta
from calendar import monthrange
from dateutil import parser


master_dir = os.environ.get("PROJECT_ROOT")
ref_dir = master_dir + "dependencies/geoTiffs_250m/dem/"
hst = pytz.timezone('HST')
county_dict = {"bi":"Hawaii County","ka":"Kauai County","mn":"Maui County (Maui, Lanai, Molokai, Kahoolawe)","oa":"Honolulu County (Oahu)"}
version = "preliminary"
fill_value = "-9999"
coord = "Decimal Degrees"
ref_sys = "+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0"

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

def get_missing(extent,subproduct):
    with open(master_dir+f"meta_work_{subproduct}_{extent}.txt","r") as f:
        missing_dates = f.read()
    ndays = len(missing_dates.split(", "))
    return (ndays,missing_dates)

def get_isl_dims(iCode):
    tiffname = ref_dir + f"{iCode}_dem_250m.tif"
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

def write_metadata(date,subproduct,county):
    today = datetime.today().astimezone(hst)
    county_list = county_dict[county]
    monyear = date.strftime('%b. %Y')
    data_statement = f"This {monyear} monthly temperature {subproduct} map of {county_list} is a high spatial resolution gridded prediction of {subproduct} temperature in degrees Celsius. This was produced using a temporal average of the daily gridded temperature maps produced by the HCDP. All maps are subject to change as new data becomes available or unknown errors are corrected in reoccurring versions. Errors in temperature estimates do vary over space meaning any gridded temperature value, even on higher quality maps, could still produce incorrect estimates."
    kw_list = ', '.join([county_list,'Hawaii',subproduct+' temperature prediction','monthly temperature','temperature','climate'])
    isl_dims = get_isl_dims(county)
    nmissed,missing_day_list = get_missing(county,subproduct)
    ndays = int(monthrange(date.year,date.month)[1]) -  int(nmissed)
    credit_statement = "All data are produced by the University of Hawai‘i at Manoa with the Water Resources Research Center (WRRC) and the Dept. of Geography and the Environment Ecohydrology Lab. This work is supported by the ChangeHI program, funded by NSF EPSCoR Research Infrastructure Improvement Award OIA-2149133. The technical support and advanced computing resources from University of Hawaii Information Technology Services – Cyberinfrastructure, funded in part by the National Science Foundation CC* awards # 2201428 and # 2232862 are gratefully acknowledged."
    contact_list = "Keri Kodama (kodamak8@hawaii.edu), Matthew Lucas (mplucas@hawaii.edu), Ryan Longman (rlongman@hawaii.edu), Thomas Giambelluca (thomas@hawaii.edu)"
    field_value_list = {'attribute':'value','dataStatement':data_statement,
                        'keywords':kw_list,'county':county,
                        'productionDate':today.strftime('%Y-%m-%d'),
                        'dataYearMon':monyear,
                        'dataVersionType':version,
                        'numDaysUsed':str(ndays),
                        'missingDays':missing_day_list,
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
    meta_file = master_dir + f"temperature_metadata_{subproduct}_{county}.txt"
    with open(meta_file,"w") as fmeta:
        for (key,val) in zip(col1,col2):
            line = [key,val]
            fmt_line = "{:20}{:60}\n".format(*line)
            fmeta.write(fmt_line)

if __name__=="__main__":
    extent = sys.argv[1]
    subproduct = sys.argv[2]
    if len(sys.argv) > 3:
        input_date = sys.argv[3]
        month_date = parser.parse(input_date)
    else:
        #Ensure runs for only the most recent completed month in near-real-time
        hst = pytz.timezone('HST')
        today = datetime.today().astimezone(hst)
        #Get start of current month
        month_st = datetime(today.year,today.month,1)
        #Fall back into previous month
        prev = month_st - timedelta(days=1)
        #Set date to start of previous full month
        month_date = datetime(prev.year,prev.month,1)
    write_metadata(month_date,subproduct,extent)