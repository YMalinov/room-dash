#!/bin/bash

# The following file is run at each Raspberry boot-up. Wait a bit to ensure
# that LXDE has loaded.
sleep 3
export RASP_ENV='1'
/usr/bin/python3 /home/pi/src/room-dash/main.py
