import asyncio
import os
from datetime import datetime
import common as c
from routine import article, routine

REFRESH_INTERVAL = 5 # in secs

class monitor:
    def turn_on(self):
        print('Turning monitor on...')
        # TODO: check if perma-off is enabled; maybe have it as a file, created
        # or destroyed by rouser-pi server.

        self.output = True

        # TODO: check if os.system is a blocking operation
        return os.system('vcgencmd display_power 1')

    def turn_off(self):
        print('Turning monitor off...')

        self.output = False

        return os.system('vcgencmd display_power 0')

    def weekday_permits(self):
        current = datetime.now().weekday()
        return self.weekdays[current]

    async def update_state(self):
        while True:
            await asyncio.sleep(REFRESH_INTERVAL)

            now = datetime.now()
            in_routine = self.routine.in_routine(now)
            if in_routine and not self.output:
                self.turn_on()
            elif not in_routine and self.output:
                self.turn_off()

    def __init__(self, rout):
        if not isinstance(rout, routine):
            raise TypeError('rout isn\'t a routine.routine object')

        self.routine = rout
        self.turn_off()
