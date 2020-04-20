from datetime import datetime
from routine import routine, article
import os

time_format = '%H:%M'
time_format_sec = '%H:%M:%S'

# Expecting format to be either '09:00' or '09:01:32'
def time(string):
    if string.count(':') == 1:
        return datetime.strptime(string, time_format)
    elif string.count(':') == 2:
        return datetime.strptime(string, time_format_sec)

    raise ValueError('unexpected datetime format', string)

MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
routine = routine(
    # Won't work if start time is still on the previous day.
    schedule = [
        # article(time('07:50'), time('09:00')),
        # article(time('20:00'), time('22:30')),
        article(time('08:20'), time('10:30')),
        article(time('19:15'), time('20:00')),
    ],
    weekdays = {
        MON: True,
        TUE: True,
        WED: True,
        THU: True,
        FRI: True,
        SAT: True,
        SUN: True,
    }
)

def get_abs_path(file_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_dir, file_name)

def read_line_from(path):
    with open(get_abs_path(path), 'r') as file:
        return file.readline().strip()
