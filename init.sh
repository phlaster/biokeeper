#! /bin/bash

apt update;
apt upgrade -y;
apt install -y git python3 python3-pip;
git clone https://$GIT_TOKEN@github.com/phlaster/opd.git;
cd opd;
git checkout backend;
pip install -r requirements.txt
python3 src/run.py
