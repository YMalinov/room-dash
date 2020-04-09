import asyncio
import subprocess
from datetime import datetime

from routine import routine

REFRESH_INTERVAL = 5 # in secs
CMD = ['vcgencmd', 'display_power']

class monitor:
    def turn_on(self):
        self.output = True

        if self.is_rasp:
            print('Turning monitor on...')
            subprocess.run(CMD + ['1'])

    def turn_off(self):
        self.output = False

        if self.is_rasp:
            print('Turning monitor off...')
            subprocess.run(CMD + ['0'])

    # This method purposefully doesn't take into account the project's actual
    # routine (otherwise it would just return the state of self.output), as the
    # monitor's actual state can be overwritten by the _rouser-pi_ project's
    # routes for dealing with the monitor's power.
    def status(self):
        if not self.is_rasp: return True

        # result from the following cmd would be as follows:
        #   display_power=1
        cmd_result = subprocess.run(CMD, capture_output = True)

        # piping meant to transform the above result to a simple boolean
        pretty = cmd_result.stdout.decode('utf-8').strip().split('=')[1] == '1'
        return pretty

    async def update_state(self):
        while True:
            await asyncio.sleep(REFRESH_INTERVAL)

            now = datetime.now()
            in_routine = self.routine.in_routine(now)
            if in_routine and not self.output:
                self.turn_on()
            elif not in_routine and self.output:
                self.turn_off()

    def __init__(self, rout, is_rasp):
        if not isinstance(rout, routine):
            raise TypeError('rout isn\'t a routine.routine object')

        self.routine = rout
        self.is_rasp = is_rasp
        self.turn_off()
