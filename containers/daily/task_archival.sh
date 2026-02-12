#!/bin/bash

echo "[task.sh] [2/5] Aggregating Airtemp data on the daily timeframe."

echo "---temp_agg_wget.py---"
python3 -W ignore /workspace/code/temp_agg_wget.py $CUSTOM_DATE
echo "---temp_map_wget.py---"
python3 -W ignore /workspace/code/temp_map_wget.py $CUSTOM_DATE
cp -rf dependencies/* /workspace/dependencies

echo "[task.sh] [3/5] Mapping Airtemp data on the daily timeframe."

echo "---update_predictor_table.py---"
python3 -W ignore /workspace/code/update_predictor_table.py $CUSTOM_DATE
echo "---county_map_wrapper.py---"
python3 -W ignore /workspace/code/county_map_wrapper.py $CUSTOM_DATE
echo "---meta_data_wrapper.py---"
python3 -W ignore /workspace/code/meta_data_wrapper.py $CUSTOM_DATE
echo "---state_wrapper.py---"
python3 -W ignore /workspace/code/state_wrapper.py $CUSTOM_DATE

echo "[task.sh] [4/5] Preparing to upload data."
cd /sync
python3 inject_upload_config.py config.json $CUSTOM_DATE

echo "[task.sh] [5/5] Uploading data."
python3 upload.py

echo "[task.sh] All done!"
