#!/bin/bash

set -u

echo "[task.sh] [1/8] Starting Execution."
export TZ="HST"
echo "It is currently $(date)."
if [ $CUSTOM_DATE ]; then
    echo "An aggregation date was provided by the environment."
else
    export CUSTOM_DATE=$(date -d "1 day ago" --iso-8601)
    echo "No aggregation date was provided by the environment. Defaulting to yesterday."
fi
echo "Aggregation date is: " $CUSTOM_DATE

source /workspace/envs/prod.env

echo "[task.sh] [2/8] Fetching dependencies and station data."
python3 -W ignore ${PROJECT_ROOT}code/monthly_map_wget.py $CUSTOM_DATE

echo "[task.sh] [3/8] Aggregating daily station to monthly and updating file."
python3 -W ignore ${PROJECT_ROOT}code/monthly_stn_data.py $CUSTOM_DATE

echo "[task.sh] [4/8] Running map workflow, all counties, all aggregations"
python3 -W ignore ${PROJECT_ROOT}code/monthly_from_daily.py bi max $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/monthly_from_daily.py ka max $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/monthly_from_daily.py mn max $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/monthly_from_daily.py oa max $CUSTOM_DATE

python3 -W ignore ${PROJECT_ROOT}code/monthly_from_daily.py bi min $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/monthly_from_daily.py ka min $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/monthly_from_daily.py mn min $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/monthly_from_daily.py oa min $CUSTOM_DATE

python3 -W ignore ${PROJECT_ROOT}code/monthly_from_daily.py bi mean $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/monthly_from_daily.py ka mean $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/monthly_from_daily.py mn mean $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/monthly_from_daily.py oa mean $CUSTOM_DATE

echo "[task.sh] [5/8] Creating county metadata, all aggregations"
python3 -W ignore ${PROJECT_ROOT}code/meta_data.py bi max $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/meta_data.py ka max $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/meta_data.py mn max $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/meta_data.py oa max $CUSTOM_DATE

python3 -W ignore ${PROJECT_ROOT}code/meta_data.py bi min $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/meta_data.py ka min $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/meta_data.py mn min $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/meta_data.py oa min $CUSTOM_DATE

python3 -W ignore ${PROJECT_ROOT}code/meta_data.py bi mean $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/meta_data.py ka mean $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/meta_data.py mn mean $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/meta_data.py oa mean $CUSTOM_DATE

echo "[task.sh] [6/8] Creating statewide mosaic, all aggregations"
python3 -W ignore ${PROJECT_ROOT}code/statewide_mosaic.py max $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/statewide_mosaic.py min $CUSTOM_DATE
python3 -W ignore ${PROJECT_ROOT}code/statewide_mosaic.py mean $CUSTOM_DATE

echo "[task.sh] [7/8] Preparing upload config."
cd /sync
python3 inject_upload_config.py config.json $CUSTOM_DATE

echo "[task.sh] [8/8] Uploading data."
python3 upload.py

echo "[task.sh] All done!"