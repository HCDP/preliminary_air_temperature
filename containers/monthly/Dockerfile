# Start with the Air Temperature Preliminary Aggregation Base.
FROM ghcr.io/hcdp/task-preliminary-air-temperature-base:latest
LABEL org.opencontainers.image.source="https://github.com/ikewai/c14n"
LABEL org.opencontainers.image.description="Monthly Air Temperature Aggregation and Mapping."

RUN mkdir -p /home/hawaii_climate_products_container/preliminary/air_temp/monthly
ADD /monthly /home/hawaii_climate_products_container/preliminary/air_temp/monthly

# Get the container's upload config as specified in the code repo.
ADD /containers/monthly/configs/upload.json /sync/config.json

# Add the task wrapper script.
ADD /containers/monthly/task.sh /actor/task.sh

# This container is intended to run the task wrapper at launch, unless otherwise specified at run-time.
CMD [ "/bin/bash", "/actor/task.sh" ]