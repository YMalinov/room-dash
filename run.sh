#!/bin/bash

# The following file is run at each Raspberry boot-up. Wait a bit to ensure
# that LXDE has fully loaded.
sleep 3
export RASP_ENV='1'

pip3 install -r /home/pi/src/room-dash/requirements.txt
/usr/bin/python3 /home/pi/src/room-dash/main.py
