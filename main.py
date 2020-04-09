#!/usr/bin/python3

import threading
import asyncio
import sys
import ui
import os

import common as c
from monitor import monitor
from readings import readings

# Get current environment - is it a Raspberry or another PC? Non-Raspberry PCs
# don't understand the Raspberry-specific commands for monitor control.
RASP_ENV = os.getenv('RASP_ENV', '') == '1'

app = ui.get_app()

monitor = monitor(c.routine, RASP_ENV)
readings = readings(monitor, app.get_queue())

def worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(monitor.update_state()) # turns on/off monitor
    loop.create_task(readings.update_state()) # reads data from home-sensors
    loop.run_forever()

worker_thread = threading.Thread(target = worker)
worker_thread.daemon = True # ensures cleaner exit on SIGINT
try:
    worker_thread.start()
    app.mainloop()
except KeyboardInterrupt:
    monitor.turn_on()
    sys.exit()
