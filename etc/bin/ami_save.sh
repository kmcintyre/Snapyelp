#!/bin/bash
sudo swapoff /swapfile
sudo rm /swapfile
cd /home/ubuntu/Snapyelp
git pull
export PYTHONPATH=`pwd`
python snapyelp/aws/ami.py