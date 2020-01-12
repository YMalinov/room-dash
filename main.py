#!/usr/bin/python3

import threading
import asyncio
import sys
import ui
import common as c
from routine import article, routine
from monitor import monitor
from readings import readings

root = ui.get_root()
app = ui.get_app(root)
ui.put_clock(root)
rasp_b, rasp_c = ui.put_readings(root)

monitor = monitor(c.morning_routine)
readings = readings(c.morning_routine, rasp_b, rasp_c)

def worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(monitor.update_state()) # turns on/off monitor
    loop.create_task(readings.update_state()) # reads sensor data
    loop.run_forever()

worker_thread = threading.Thread(target=worker)
try:
    worker_thread.start()
    app.mainloop()
except KeyboardInterrupt:
    monitor.turn_on()
    sys.exit()
