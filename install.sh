#!/bin/bash
rm -rf venv
mkdir venv
sudo apt install -y python-pip 
sudo apt install -y authbind # to allow non-root users listen on port 53
# authbind configuration 
sudo touch /etc/authbind/byport/53
sudo chmod 500 /etc/authbind/byport/53
#
pip install virtualenv
python3 -m virtualenv -p /usr/bin/python3 venv
