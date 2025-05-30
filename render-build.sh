#!/usr/bin/env bash

apt-get update
apt-get install -y libxml2-dev libxmlsec1-dev libxmlsec1-openssl pkg-config

pip install -r requirements.txt
