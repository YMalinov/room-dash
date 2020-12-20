import asyncio
import aiohttp
from datetime import datetime, timedelta

from common import read_line_from
from ui import Label

SERVER_TIMEOUT = aiohttp.ClientTimeout(total = 20) # in seconds
REFRESH_INTERVAL = 5 # in seconds
RETRIES = 5
CACHE_LIFE = timedelta(minutes = 14)

base_url = read_line_from('sensors_url.txt')
URLS = [
    f'{base_url}/get?json', # current readings

    f'{base_url}/get/min?json&client=rasp_b&hours=12', # min for past half day
    f'{base_url}/get/min?json&client=rasp_c&hours=12', # min for past half day
]

COL1 = {
    'bme_humidity': 'Living room humidity',
    'bme_pressure': 'Living room pressure',
    'ds18_short_temp': 'Living room temp',
    'ds18_long_temp': 'Bedroom temp',
    # 'pm25_aqi_label': 'PM2.5 label',
    # 'pm10_aqi_label': 'PM10 label',
    # 'mq7_carb_mono': 'Garage CO in ppm',
    '': '', # interpreted as empty line
    'ds18_short_temp_min': 'Living room temp min 1/2 day',
    'ds18_long_temp_min': 'Bedroom temp min 1/2 day',
}

COL2 = {
    # 'timestamp_pretty_rasp_a': 'rasp-a read',
    'timestamp_pretty_rasp_b': 'rasp-b read',
    'timestamp_pretty_rasp_c': 'rasp-c read',
    '': '',
    'last_update': 'Updated at',
}

class readings:

    async def get_url(self, url, session):
        for i in range(RETRIES):
            try:
                async with session.get(url, timeout=SERVER_TIMEOUT) as resp:
                    return await resp.json()
            except Exception as e:
                if i + 1 == RETRIES:
                    print('Exceeded retries, raising exception...')
                    raise

                continue

    async def get_data(self):
        results = []
        async with aiohttp.ClientSession() as session:
            for url in URLS:
                results.append(await self.get_url(url, session))

        return results

    def flatten(self, json):
        output = {}
        for entry in json:
            for k, v in entry.items():
                output.update({k: v})

        return output

    def format(self, json, col):
        output = ''

        # get sorting from col
        for key, value in col.items():
            if key in json:
                output += '%s: %s\n' % (value, json[key])
            elif not key:
                output += '\n'

        return output

    async def update_readings(self):
        readouts, min_rasp_b, min_rasp_c = await self.get_data()
        self.last_update = datetime.now()

        col1 = col2 = {}

        col1.update({**self.flatten(readouts)})

        # Add labels per last day average
        col1['ds18_short_temp_min'] = min_rasp_b[0]['ds18_short_temp']
        col1['ds18_long_temp_min'] = min_rasp_c[0]['ds18_long_temp']

        for readout in readouts:
            k = 'timestamp_pretty_' + readout['client']
            v = readout['timestamp_pretty']
            col2.update({k: v})

        # Also add time of last update
        col2['last_update'] = self.last_update.strftime('%H:%M:%S')

        self.queue.put((Label.col1, self.format(col1, COL1)))
        self.queue.put((Label.col2, self.format(col2, COL2)))

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
            monitor_on = self.monitor.status()
            if monitor_on and self.cache_old():
                try:
                    print('Readings cache expired @', datetime.now())

                    await self.update_readings()

                    print('Updated readings @', self.last_update)

                    # If we were successful in getting readings data, clear the
                    # error row.
                    self.queue.put((Label.row4, ''))
                except Exception as e:
                    # OK, so maybe spotty Internet connectivity? Display an
                    # error and carry on trying.
                    self.queue.put((
                        Label.row4,
                        'Error %s getting data, will retry in %d seconds' %
                            (type(e), REFRESH_INTERVAL)
                    ))

            await asyncio.sleep(REFRESH_INTERVAL)

    def __init__(self, monitor, queue):
        self.monitor = monitor
        self.queue = queue
        self.last_update = datetime.min
