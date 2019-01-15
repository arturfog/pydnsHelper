#!/bin/bash
rm -rf venv
mkdir venv
sudo apt install -y python-pip
pip install virtualenv
python3 -m virtualenv -p /usr/bin/python3 venv
