import asyncio
import aiohttp
from aiohttp import web
from aiohttp.client_exceptions import ClientError
from ssl import SSLError
from datetime import datetime, timedelta

from common import read_line_from
from ui import Label

SERVER_TIMEOUT = aiohttp.ClientTimeout(total = 20) # in seconds
REFRESH_INTERVAL = 5 # in seconds
CACHE_LIFE = timedelta(minutes = 14)

base_url = read_line_from('sensors_url.txt')
URLS = [
    f'{base_url}/get?client=rasp_b&json', # current readings outside
    f'{base_url}/get?client=rasp_c&json', # current readings inside
    f'{base_url}/get?client=rasp_b&json&days=1', # averages for past day (outside)
]

KEYS = {
    'client': 'Client',
    'timestamp_pretty': 'Collected',
    # 'bme_humidity': 'Humidity',
    # 'bme_pressure': 'Pressure',
    'ds18_short_temp': 'Outside temp',
    'ds18_long_temp': 'Inside temp',
    'pm25_aqi_label': 'PM2.5 label',
    'pm25_aqi_label_avg': 'PM2.5 label day avg',
    'pm10_aqi_label': 'PM10 label',
    'pm10_aqi_label_avg': 'PM10 label day avg',
    'last_update': 'Updated at',
}

class readings:
    async def get_data(self):
        results = []
        async with aiohttp.ClientSession() as session:
            for url in URLS:
                async with session.get(url, timeout = SERVER_TIMEOUT) as resp:
                    results.append(await resp.json())

        return results

    def format(self, json):
        output = ''

        # get sorting from KEYS
        for key, value in KEYS.items():
            if key in json:
                output += '%s: %s\n' % (value, json[key])

        return output

    async def update_readings(self):
        outside, inside, avg_outside = await self.get_data()

        self.last_update = datetime.now()

        # Add labels per last day average.
        outside['pm25_aqi_label_avg'] = avg_outside['pm25_aqi_label']
        outside['pm10_aqi_label_avg'] = avg_outside['pm10_aqi_label']

        # Also add time of last update
        inside['last_update'] = self.last_update.strftime('%H:%M:%S')

        self.queue.put((Label.rasp_b, self.format(outside)))
        self.queue.put((Label.rasp_c, self.format(inside)))

    def cache_old(self):
        now = datetime.now()
        if now - self.last_update > CACHE_LIFE:
            return True

        return False

    # We get these readings from the _home-sensors_ project, which is served on
    # a free-quota-using Google Cloud server. In order to remain within the free
    # quota indefinitely, let's try to hit it as less frequently as possible. We
    # can use two ways of achieving that:
    #   1. Use a cache for the readings received - considering their values
    #   don't currently get updated often, it's OK to have this set at a
    #   CACHE_LIFE time delta.
    #   2. Only update the cache while the monitor showing it is actually
    #   powered (regardless of its routine).
    async def update_state(self):
        while True:
            now = datetime.now()

            monitor_on = self.monitor.status()
            if monitor_on and self.cache_old():
                tries = 3 # to connect with server
                for i in range(tries):
                    try:
                        print('Readings cache expired @', datetime.now())

                        await self.update_readings()

                        print('Updated readings @', self.last_update)

                        break
                    except (ClientError, SSLError):

                        # OK, so maybe spotty Internet connectivity? Display an
                        # error and carry on trying.
                        self.queue.put((
                            Label.rasp_b,
                            'Error getting data, try: %i' % (i + 1)
                        ))

            await asyncio.sleep(REFRESH_INTERVAL)

    def __init__(self, monitor, queue):
        self.monitor = monitor
        self.queue = queue
        self.last_update = datetime.min
