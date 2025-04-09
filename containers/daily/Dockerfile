# Start with the Air Temperature Preliminary Aggregation Base.
FROM ghcr.io/hcdp/task-preliminary-air-temperature-base:latest
LABEL org.opencontainers.image.source="https://github.com/hcdp/task-preliminary-air-temperature-daily"
LABEL org.opencontainers.image.description="Daily Air Temperature Aggregation and Mapping."

RUN mkdir -p /home/hawaii_climate_products_container/preliminary/air_temp/daily
ADD /daily /home/hawaii_climate_products_container/preliminary/air_temp/daily

# Get the container's upload config as specified in the code repo.
ADD /containers/daily/configs/upload.json /sync/config.json

# Add the task wrapper script.
ADD /containers/daily/task.sh /actor/task.sh
ADD /containers/daily/task_archival.sh /actor/task_archival.sh
ADD /containers/daily/task_current.sh /actor/task_current.sh

# This container is intended to run the task wrapper at launch, unless otherwise specified at run-time.
CMD [ "/bin/bash", "/actor/task.sh" ]
