"""
Mesonet temperature data processor based on Mesonet API database.
Created: 12.2025

"""
import os
import sys
import pytz
import requests
import numpy as np
import pandas as pd
from io import StringIO
from datetime import datetime
from util import handle_retry
from os.path import exists

MASTER_DIR = os.environ.get("PROJECT_ROOT")
SOURCE_NAME = "hi_mesonet"
DAY_SECONDS = 86400

hcdp_api_token = os.environ.get("HCDP_API_TOKEN")
base_url = f"https://api.hcdp.ikewai.org/mesonet/db/"
master_meta_url = "https://raw.githubusercontent.com/ikewai/hawaii_wx_station_mgmt_container/refs/heads/main/Hawaii_Master_Station_Meta.csv"
conversion_url = "https://raw.githubusercontent.com/HCDP/loggernet_station_data/refs/heads/unit_handling/csv_data/stations/station_metadata.csv"
var_list = ["Tair_1_Avg","Tair_2_Avg"]
lower_limit = -9
upper_limit = 42
tolerance = 2

def make_request(dt):
    url = f"{base_url}measurements/"
    targ_date_utc = dt + pd.Timedelta(hours=10)
    st_dt = targ_date_utc.strftime('%Y-%m-%d %H:%M:%S')
    en_dt = (targ_date_utc + pd.Timedelta(hours=24) + pd.Timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M:%S')
    params = {
            "start_date":st_dt,
            "end_date":en_dt,
            "limit": 1000000,
            "var_ids":','.join(var_list),
            "join_metadata":"true"
    }
    req = requests.get(url,params,headers = {'Authorization': f'Bearer {hcdp_api_token}'}, timeout = 30)
    return req

def split_dataframe(df,meta_cols,dt_convert=True):
    df = df.set_index('SKN')
    data_cols = [col for col in list(df.columns) if col not in meta_cols]
    df_meta = df[meta_cols]
    df_data = df[data_cols]
    if dt_convert:
        date_cols = pd.to_datetime([col.split('X')[1] for col in data_cols])
    else:
        date_cols = pd.to_datetime(data_cols)
    df_data.columns = date_cols
    return df_data,df_meta

def update_csv(csv_name,new_data_df):
    """
    new_data_df should not be indexed. If feeding an indexed df, reset before feeding.
    This version accounts for some issues with pandas deprecating value replacement
    """
    master_df = pd.read_csv(master_meta_url,index_col="SKN")
    meta_cols = list(master_df.columns)
    new_data,new_meta = split_dataframe(new_data_df,meta_cols,dt_convert=False)
    if exists(csv_name):
        #Check not empty
        if os.stat(csv_name).st_size != 0:
            #Loading old data
            old_df = pd.read_csv(csv_name)
            old_data,old_meta = split_dataframe(old_df,meta_cols,dt_convert=True)
            old_cols = list(old_data.columns)
            old_inds = old_data.index.values
            #Connect old data to new data, override like other parse files
            upd_inds = np.union1d(old_data.index.values,new_data.index.values)
            joined_data = pd.DataFrame(index=upd_inds)
            #Ensure index name is correct to prep for write
            joined_data.index.name = "SKN"
            #Replace old data
            joined_data.loc[old_inds,old_data.columns] = old_data
            #Add new data
            joined_data.loc[new_data.index.values,new_data.columns] = new_data
            #Format the dates
            date_cols = list(joined_data.columns)
            fmt_cols = [dt.strftime("X%Y.%m.%d") for dt in date_cols]
            joined_data.columns = fmt_cols
            #Create new metadata table from master using combined SKNs
            joined_meta = master_df.loc[joined_data.index,:]
            #Stick meta and data back together
            combined_df = joined_meta.join(joined_data,how="left")
            combined_df.to_csv(csv_name)
        else:
            #File exists but is empty. Reset with existing data.
            #Format new_data dates
            date_cols = list(new_data.columns)
            fmt_cols = [dt.strftime("X%Y.%m.%d") for dt in date_cols]
            new_data.columns = fmt_cols
            #Rejoin the dataframe
            combined_df = new_meta.join(new_data,how="left")
            combined_df.to_csv(csv_name)
    else:
        #File does not previously exist. Start it new. Same procedure as empty
        #Format new_data dates
        date_cols = list(new_data.columns)
        fmt_cols = [dt.strftime("X%Y.%m.%d") for dt in date_cols]
        new_data.columns = fmt_cols
        #Rejoin the dataframe
        combined_df = new_meta.join(new_data,how="left")
        combined_df.to_csv(csv_name)

def process_raw_feed(ta_df,dt):
    #First subset to only 24 hours to remove overflow
    targ_date_utc = dt + pd.Timedelta(hours=10)
    next_day_utc = targ_date_utc + pd.Timedelta(hours=24)
    #-- Adjust reporting time
    ta_df.loc[:,"timestamp"] = ta_df["timestamp"] - pd.Timedelta(minutes=1)
    #-- Strip timezone info from datetime parameters
    ta_df["timestamp"] = pd.to_datetime(ta_df["timestamp"]).dt.tz_localize(None)
    ta_day = ta_df[(ta_df["timestamp"] < next_day_utc)&(ta_df["timestamp"]>=targ_date_utc)]

    ##Reshape dataframe so that TA_1 and TA_2 are adjacent columns per timestamp
    ta_df = ta_df.set_index(["timestamp","station_id"])
    ta1 = ta_df[ta_df["variable"]=="Tair_1_Avg"]
    ta2 = ta_df[ta_df["variable"]=="Tair_2_Avg"]
    ta1 = ta1.rename(columns={"value":"TA1"})
    ta2 = ta2.rename(columns=({"value":"TA2"}))
    ta1.loc[((ta1["TA1"]<lower_limit)|(ta1["TA1"]>upper_limit)),"TA1"] = np.nan
    ta2.loc[((ta2["TA2"]<lower_limit)|(ta2["TA2"]>upper_limit)),"TA2"] = np.nan
    joined_df = ta1[["station_name","lat","lng","elevation","interval_seconds","TA1"]].join(ta2["TA2"],how="inner")
    joined_df = joined_df.reset_index()

    #Station-by-station bad value filling
    #Part 1, dealing with stations with deviating sensors
    uni_stns = joined_df["station_id"].unique()
    all_stns = []
    for stn in uni_stns:
        stn_df = joined_df[joined_df["station_id"]==stn]
        stn_df = stn_df.dropna(how='all',subset=['TA1','TA2']).reset_index(drop=True)
        diff_inds = stn_df[abs(stn_df["TA1"]-stn_df["TA2"])>tolerance].index
        for i in diff_inds:
            if (i>0)&(i<stn_df.shape[0]):
                surrounding = stn_df.loc[[i-1,i+1],["TA1","TA2"]]
            elif i==0:
                surrounding = stn_df.loc[i+1,["TA1","TA2"]]
            elif i==stn_df.shape[0]:
                surrounding = stn_df.loc[i-1,["TA1","TA2"]]
            surrounding_avg = np.nanmean(surrounding.values.flatten())
            worse_one = ["TA1","TA2"][np.argmax(abs(stn_df.loc[i,["TA1","TA2"]]-surrounding_avg))]
            better_one = ["TA1","TA2"][np.argmin(abs(stn_df.loc[i,["TA1","TA2"]]-surrounding_avg))]
            stn_df.loc[i,worse_one] = stn_df.at[i,better_one]
        all_stns.append(stn_df)
    rejoined_df = pd.concat(all_stns,axis=0).reset_index(drop=True)
    #Part 2, Get station averaged measurement
    rejoined_df["TA"] = rejoined_df[["TA1","TA2"]].mean(axis=1)
    return rejoined_df[["timestamp","station_id","station_name","lat","lng","elevation","interval_seconds","TA"]]

def get_processed_temp(dt):
    req = handle_retry(make_request,[dt])
    #Check results of request
    if req.status_code != 200:
        print("API request failed")
        return
    bytes_data = req.content
    decoded = bytes_data.decode('utf-8')
    req_data = pd.read_json(StringIO(decoded),convert_dates=True)
    if req_data.empty:
        print("API return empty")
        return
    else:
        sorted_req = req_data.sort_values(by="timestamp")
    #Apply qa/qc to sorted_req and create daily aggregation to output as processed file
    processed_df = process_raw_feed(sorted_req,dt)
    #Get tmax and tmin from processed_df
    tmax_rows = []
    tmin_rows = []
    for stn in processed_df["station_id"].unique():
        stn_df = processed_df[processed_df["station_id"]==stn]
        expected = 86400/stn_df["interval_seconds"].unique()[0]
        percent_fill = stn_df.shape[0]/expected
        if percent_fill >= 0.95:
            tmax = stn_df["TA"].max()
            tmin = stn_df["TA"].min()
        else:
            tmax = np.nan
            tmin = np.nan
        tmax_rows.append([stn,tmax])
        tmin_rows.append([stn,tmin])
    tmax_day = pd.DataFrame(tmax_rows,columns=["station_id",dt])
    tmin_day = pd.DataFrame(tmin_rows,columns=["station_id",dt])
    #Use station_metadata.csv to convert mesonet ids to skn
    convert_table = pd.read_csv(conversion_url,index_col="station_id")
    tmax_day = tmax_day.set_index("station_id")
    tmin_day = tmin_day.set_index("station_id")
    merged_tmax = tmax_day.join(convert_table,how="left").reset_index()
    merged_tmin = tmin_day.join(convert_table,how="left").reset_index()
    merged_tmax = merged_tmax.set_index("skn")
    merged_tmax.index.name = "SKN"
    merged_tmin = merged_tmin.set_index("skn")
    merged_tmin.index.name = "SKN"
    master_df = pd.read_csv(master_meta_url,index_col="SKN")
    tmax_wide = merged_tmax[[dt]].join(master_df,how="left")
    tmax_wide = tmax_wide.sort_index()[list(master_df.columns)+[dt]]
    tmin_wide = merged_tmin[[dt]].join(master_df,how="left")
    tmin_wide = tmin_wide.sort_index()[list(master_df.columns)+[dt]]
    #Update existing table or start a new table if applicable
    date_code = dt.strftime("%Y_%m")
    output_dir = os.path.join(MASTER_DIR,"working_data/processed_data/",SOURCE_NAME)
    tmax_process_file = os.path.join(output_dir,"_".join(("Tmax",SOURCE_NAME,date_code,"processed.csv")))
    tmin_process_file = os.path.join(output_dir,"_".join(("Tmin",SOURCE_NAME,date_code,"processed.csv")))
    update_csv(tmax_process_file,tmax_wide.reset_index())
    update_csv(tmin_process_file,tmin_wide.reset_index())

if __name__=="__main__":
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        hst = pytz.timezone('HST')
        today = datetime.today().astimezone(hst)
        prev_day = today - timedelta(days=1)
        date_str = prev_day.strftime('%Y-%m-%d')
    dt = pd.to_datetime(date_str)
    get_processed_temp(dt)
