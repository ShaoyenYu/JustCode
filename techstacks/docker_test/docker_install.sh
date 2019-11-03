#!/bin/sh sh

# Install Docker CE on Ubuntu 18.04

# Uninstall old versions
# notice that contents of /var/lib/docker, including images, containers, volumes, networks, are preserved.
sudo apt-get remove docker docker-engine docker.io;

# INSTALL USING THE REPOSITORY
# 1. Update `apt` package index
sudo apt-get update;

# 2. Next, install a few prerequisite packages which let `apt` use packages over `HTTPS`
sudo apt-get install apt-transport-https \
  ca-certificates \
  curl software-properties-common;

# 3. Then add the GPG key for the official Docker repository to your system
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -;
# if you fucked up here, maybe it's your curl is compiled WITHOUT ssl protocol, try this:
#sudo apt-get install build-essential nghttp2 libnghttp2-dev libssl-dev
#wget https://curl.haxx.se/download/curl-7.58.0.tar.gz
#tar -xvf curl-7.58.0.tar.gz
#cd curl-7.58.0
#./configure --with-nghttp2 --prefix=/usr/local --with-ssl=/usr/local/ssl
#make
#sudo make install
#sudo ldconfig

# 4. Set up stable repository
sudo add-apt-repository \
  "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) \
  stable"

# INSTALL DOCKER CE
# 1. Update the `apt` package index
sudo apt-get update

# 2. install the latest version of Docker CE
sudo apt-get install docker-ce

# 3. or install a specific version
# sudo apt-get install docker-ce=<VERSION>

# 4. Verify that Docker CE is installed correctly by running the `hello-world` image
# this command downloads a test image and runs it in a contaier.
# When the container runs, it prints an informational message and exists.
sudo docker run hello-world
