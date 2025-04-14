#!/bin/bash

echo "[task.sh] [1/5] Starting Execution."
export TZ="HST"
echo "It is currently $(date)."
if [ $CUSTOM_DATE ]; then
    echo "An aggregation date was provided by the environment."
else
    export CUSTOM_DATE=$(date -d "1 day ago" --iso-8601)
    echo "No aggregation date was provided by the environment. Defaulting to yesterday."
fi
echo "Aggregation date is: " $CUSTOM_DATE

if [[ $(date -d "$CUSTOM_DATE" +%s) -lt $(date -d "2019-01-01" +%s) ]]; then
  echo "Using archival workflow"
  bash $(dirname $0)/task_archival.sh
else
  bash $(dirname $0)/task_current.sh
fi