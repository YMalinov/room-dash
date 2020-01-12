import asyncio
from datetime import datetime, timedelta
import requests
from common import read_line_from
from routine import article, routine
from ui import Label

REFRESH_INTERVAL = 20 # in seconds
CACHE_LIFE = timedelta(minutes = 30)
URL = read_line_from('sensors_url.txt')
URL_OUT = URL +'/get?json'
URL_IN = URL + '/get?client=rasp_c&json'
ALLOWED_KEYS = [
    'client',
    'timestamp_pretty',
    # 'bme_humidity',
    # 'bme_pressure',
    'ds18_short_temp',
    'ds18_long_temp',
    'pm10_aqi_label',
    'pm25_aqi_label',
]

class readings:
    def get_data(self):
        max_exception_count = 3
        for i in range(max_exception_count):
            try:
                outside = requests.get(URL_OUT).json()
                inside = requests.get(URL_IN).json()
            except:
                natural = i + 1
                if natural == max_exception_count: raise
                print('Couldn\'t get info from server, attempt:', natural)

        return outside, inside

    def filter_json(self, json):
        output = {}
        for k, v in json.items():
            if k in ALLOWED_KEYS:
                output.update({k: v})

        return output

    def format_json(self, json):
        output = ''

        # get sorting from ALLOWED_KEYS
        for key in ALLOWED_KEYS:
            if key in json:
                output += '%s: %s\n' % (key, json[key])

        return output

    def update_readings(self):
        outside, inside = self.get_data()

        outside = self.filter_json(outside)
        inside = self.filter_json(inside)

        self.last_rasp_b = self.format_json(outside)
        self.last_rasp_c = self.format_json(inside)
        self.last_update = datetime.now()

    def cache_invalid(self):
        now = datetime.now()
        if now - self.last_update > CACHE_LIFE:
            return True

        return False

    async def update_state(self):
        while True:
            now = datetime.now()

            in_routine = self.routine.in_routine(now)
            if in_routine and self.cache_invalid():
                try:
                    self.update_readings()
                    self.queue.put((Label.rasp_b, self.last_rasp_b))
                    self.queue.put((Label.rasp_c, self.last_rasp_c))
                except:
                    # OK, so maybe no Internet then? Show an error and carry on.
                    self.queue.put((Label.rasp_b, 'Error getting data'))

            await asyncio.sleep(REFRESH_INTERVAL)

    def __init__(self, routine, queue):
        self.routine = routine
        self.queue = queue
        self.last_update = datetime.min
