#!/bin/bash

# Intended to be run as a systemd user service.
export RASP_ENV='1'

pip3 install -r /home/pi/src/room-dash/requirements.txt
/usr/bin/python3 /home/pi/src/room-dash/main.py
