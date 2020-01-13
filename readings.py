import asyncio
from datetime import datetime, timedelta
import requests
from common import read_line_from
from routine import article, routine
from ui import Label

REFRESH_INTERVAL = 10 # in seconds
CACHE_LIFE = timedelta(minutes = 20)
URL = read_line_from('sensors_url.txt')
URL_OUT = URL + '/get?json'
URL_OUT_AVG = URL + '/get?json&days=1' # average for last day
URL_IN = URL + '/get?client=rasp_c&json'
KEYS = {
    'client': 'Client',
    'timestamp_pretty': 'When',
    # 'bme_humidity': 'Humidity',
    # 'bme_pressure': 'Pressure',
    'ds18_short_temp': 'Outside temp',
    'ds18_long_temp': 'Inside temp',
    'pm25_aqi_label': 'PM2.5 label',
    'pm25_aqi_label_avg': 'PM2.5 label day avg',
    'pm10_aqi_label': 'PM10 label',
    'pm10_aqi_label_avg': 'PM10 label day avg',
}

class readings:
    def get_data(self):
        max_exception_count = 3
        for i in range(max_exception_count):
            try:
                outside = requests.get(URL_OUT).json()
                avg_outside = requests.get(URL_OUT_AVG).json()
                inside = requests.get(URL_IN).json()
            except requests.exceptions.RequestException:
                natural = i + 1
                if natural == max_exception_count: raise
                print('Couldn\'t get info from server, attempt:', natural)

        return outside, avg_outside, inside

    def format(self, json):
        output = ''

        # get sorting from KEYS
        for key, value in KEYS.items():
            if key in json:
                output += '%s: %s\n' % (value, json[key])

        return output

    def update_readings(self):
        outside, avg_outside, inside = self.get_data()

        # Add labels per last day average.
        outside['pm25_aqi_label_avg'] = avg_outside['pm25_aqi_label']
        outside['pm10_aqi_label_avg'] = avg_outside['pm10_aqi_label']

        self.last_rasp_b = self.format(outside)
        self.last_rasp_c = self.format(inside)
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
                except requests.exceptions.RequestException:
                    # OK, so maybe no Internet then? Show an error and carry on.
                    self.queue.put((Label.rasp_b, 'Error getting data'))

            await asyncio.sleep(REFRESH_INTERVAL)

    def __init__(self, routine, queue):
        self.routine = routine
        self.queue = queue
        self.last_update = datetime.min
