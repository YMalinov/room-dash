from datetime import datetime
from routine import routine, article
import os

time_format = '%H:%M'
time_format_sec = '%H:%M:%S'

# Expecting format to be either '09:00' or '09:01:32'
def get_time(string):
    if string.count(':') == 1:
        return datetime.strptime(string, time_format)
    elif string.count(':') == 2:
        return datetime.strptime(string, time_format_sec)

    raise ValueError('unexpected datetime format', string)

MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
morning_routine = routine(
    # schedule = [ article(get_time('08:00'), get_time('09:00')) ],
    schedule = [ article(get_time('20:50:00'), get_time('20:50:30')) ],
    weekdays = {
        MON: True,
        TUE: True,
        WED: True,
        THU: True,
        FRI: True,
        SAT: False,
        # SUN: False,
        SUN: True,
    }
)

def get_abs_path(file_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(script_dir, file_name)

def read_line_from(path):
    with open(get_abs_path(path), 'r') as file:
        return file.readline().strip()
