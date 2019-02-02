#!/bin/bash
rm -rf venv
mkdir venv
sudo apt install -y python-pip python3-pip libgetdns-dev
# sudo apt install -y authbind # to allow non-root users listen on port 53
# authbind configuration 
#sudo touch /etc/authbind/byport/53
#sudo chmod 500 /etc/authbind/byport/53
#
#sudo iptables -t nat -A OUTPUT -o lo -p udp --dport 53 -j REDIRECT --to-port 5053
pip3 install virtualenv
python3 -m virtualenv -p /usr/bin/python3 venv
