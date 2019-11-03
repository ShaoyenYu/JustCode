# Use an official Python runtime as a parent image
FROM python:3.6.7-slim

LABEL maintainer="ysy@yingpei.com"

WORKDIR /root/tmp

# Copy the current directory contents into the container at /root/tmp
COPY . /root/tmp

# WARNING: apt does not have a stable CLI interface. Use with caution in scripts.
RUN apt update && apt -y install curl wget libssl-dev libcurl4-openssl-dev build-essential unixodbc-dev gcc
# some packages need:
# GMP: GNU Multiple Precision Arithmetic Library
# MPFR: GNU Multiple-precision floating-point rounding library
# MPC: GNU Multiple-precision C libraryRUN
RUN apt -y install libgmp-dev libmpfr-dev libmpc-dev

# Install any needed packages specified in requrements.txt
RUN pip install -ihttps://pypi.douban.com/simple/ -r requirements.txt && pip install -f https://download.mosek.com/stable/wheel/index.html Mosek --user
# specially step for installing talib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && cd ta-lib/ && \
  ./configure --prefix=/usr && make && make install
RUN rm -R ta-lib ta-lib-0.4.0-src.tar.gz
