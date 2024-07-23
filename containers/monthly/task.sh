#!/bin/bash
echo "[task.sh] [1/4] Starting Execution."
export TZ="HST"
echo "It is currently $(date)."
if [ $CUSTOM_DATE ]; then
    export CUSTOM_DATE=$(date -d "$CUSTOM_DATE" +"%Y-%m-01")
    export CUSTOM_DATE=$(date -d "$CUSTOM_DATE +1 month -1 day" --iso-8601)
    echo "An aggregation date was provided by the environment. Setting to last day of provided month."
else
    export CUSTOM_DATE=$(date -d "-$(date +%d) days" --iso-8601)
    echo "No aggregation date was provided by the environment. Defaulting to last month."
fi
echo "Aggregation date is: " $CUSTOM_DATE

echo "[task.sh] [2/4] Mapping Airtemp data on the monthly timeframe."
cd /home/hawaii_climate_products_container/preliminary/air_temp/daily/
echo "---monthly_map_wget.py---"
python3 -W ignore /home/hawaii_climate_products_container/preliminary/air_temp/monthly/code/monthly_map_wget.py $CUSTOM_DATE
echo "---update_monthly_predictor.py---"
python3 -W ignore /home/hawaii_climate_products_container/preliminary/air_temp/monthly/code/update_monthly_predictor.py $CUSTOM_DATE
echo "---monthly_map_wrapper.py---"
python3 -W ignore /home/hawaii_climate_products_container/preliminary/air_temp/monthly/code/monthly_map_wrapper.py $CUSTOM_DATE
echo "---monthly_meta_wrapper.py---"
python3 -W ignore /home/hawaii_climate_products_container/preliminary/air_temp/monthly/code/monthly_meta_wrapper.py $CUSTOM_DATE
echo "---monthly_state_wrapper.py---"
python3 -W ignore /home/hawaii_climate_products_container/preliminary/air_temp/monthly/code/monthly_state_wrapper.py $CUSTOM_DATE
echo "---monthly_stn_data.py--- on Tmax"
python3 -W ignore /home/hawaii_climate_products_container/preliminary/air_temp/monthly/code/monthly_stn_data.py Tmax $CUSTOM_DATE
echo "---monthly_stn_data.py--- on Tmin"
python3 -W ignore /home/hawaii_climate_products_container/preliminary/air_temp/monthly/code/monthly_stn_data.py Tmin $CUSTOM_DATE
echo "[task.sh] [3/4] Preparing to upload data."
cd /sync
python3 inject_upload_config.py upload.json $CUSTOM_DATE

echo "[task.sh] [4/4] Uploading data."
python3 upload.py

echo "[task.sh] All done!"
