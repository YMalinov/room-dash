from datetime import datetime

class article:
    def __init__(self, start, end, action = ''):
        if not isinstance(start, datetime):
            raise TypeError('given start isn\'t a time object')

        if not isinstance(end, datetime):
            raise TypeError('given start isn\'t a time object')

        if start > end:
            raise ValueError('start can\'t be after end')

        if not isinstance(action, str):
            raise TypeError('given action isn\'t a str object')

        self.start = start
        self.end = end
        self.action = action

    def in_bounds(self, input):
        if self.start.time() <= input.time() <= self.end.time():
            return True

        return False

class routine:
    def __init__(self, schedule, weekdays):
        if not isinstance(schedule, list):
            raise TypeError('routine isn\'t a list object')

        if not isinstance(weekdays, dict):
            raise TypeError('weekdays isn\'t a dict object')

        self.schedule = schedule
        self.weekdays = weekdays

    def get_article(self, time):
        for item in self.schedule:
            if item.in_bounds(time):
                return item

        return False

    def weekday_permits(self):
        current = datetime.now().weekday()
        return self.weekdays[current]

    def in_routine(self, time):
        if not self.weekday_permits():
            return False

        beginning = self.schedule[0].start
        end = self.schedule[-1].end
        if beginning.time() <= time.time() <= end.time():
            return True

        return False
