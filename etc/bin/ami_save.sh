#!/bin/bash
sudo systemctl stop worker agent websocket
sudo systemctl disable worker agent websocket
  
sudo rm /etc/systemd/system/worker.service
sudo rm /etc/systemd/system/agent.service
sudo rm /etc/systemd/system/websocket.service
		
sudo swapoff /swapfile
sudo rm /swapfile
cd /home/ubuntu/Snapyelp
git pull
export PYTHONPATH=`pwd`
python snapyelp/aws/ami.py