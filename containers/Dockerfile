FROM ghcr.io/hcdp/task-base:latest
LABEL org.opencontainers.image.source="https://github.com/hcdp/task-preliminary-air-temperature-base"
LABEL org.opencontainers.image.description="Base Image for preliminary air temperature workflows."

## PACKAGE/LIBRARY INSTALLATIONS ##
# Fetch the latest apt repo information.
RUN apt update
# Let APT know that we don't have a terminal.
ENV DEBIAN_FRONTEND=noninteractive

# Install libgdal.
# This is experimental - The scripts had some
# issues with newer versions of gdal during previous c14n.
RUN apt install -y libgdal-dev

# Install a data package that allows for easily setting time zones in a shell script.
RUN apt install -y tzdata

# Install dependencies for the air temp workflows.
# Specific explanations of each library coming soon.
# Libraries are approximately ordered by dependency,
# then by time-to-install.
RUN python3 -m pip install numpy
RUN python3 -m pip install scipy
RUN python3 -m pip install gdal==$(gdal-config --version)
RUN python3 -m pip install rasterio
RUN python3 -m pip install matplotlib
RUN python3 -m pip install pandas
RUN python3 -m pip install affine
RUN python3 -m pip install pyproj==3.3.0
RUN python3 -m pip install statsmodels
RUN python3 -m pip install scikit-learn
RUN python3 -m pip install tiffile
RUN python3 -m pip install python-dotenv
RUN python3 -m pip install pathlib
RUN python3 -m pip install xarray
RUN python3 -m pip install requests

RUN mkdir -p /sync
RUN wget https://raw.githubusercontent.com/ikewai/data-uploader/main/upload.py -O /sync/upload.py

RUN mkdir -p /workspace/data_aqs
ADD /data_aqs /workspace/data_aqs

RUN mkdir -p /workspace/data_outputs
ADD /data_outputs /workspace/data_outputs

RUN mkdir -p /workspace/working_data
ADD /working_data /workspace/working_data

ADD /tools /sync