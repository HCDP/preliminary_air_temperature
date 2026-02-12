# Start with the Air Temperature Preliminary Aggregation Base.
FROM ghcr.io/hcdp/task-preliminary-air-temperature-base:latest
LABEL org.opencontainers.image.source="https://github.com/hcdp/preliminary_air_temperature"
LABEL org.opencontainers.image.description="Monthly Air Temperature Aggregation and Mapping."

RUN mkdir -p /workspace
ADD /monthly /workspace

RUN mkdir -p /workspace/envs
ADD /envs/monthly/prod.env /workspace/envs

# Get the container's upload config as specified in the code repo.
ADD /containers/monthly/configs/upload.json /sync/config.json

# Add the task wrapper script.
ADD /containers/monthly/task.sh /workspace/task.sh

WORKDIR /workspace
# This container is intended to run the task wrapper at launch, unless otherwise specified at run-time.
CMD [ "/bin/bash", "task.sh" ]