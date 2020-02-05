import tkinter as tk
from datetime import datetime, timedelta
from queue import Queue
from enum import Enum, unique, auto

# will show the time with this offset applied
offset = timedelta(minutes = 1, seconds = 20)
time_format = '%H:%M:%S %p'
date_format = '%a %b %-d; week %-W of %Y' # the hyphens remove the trailing zeroes

@unique
class Label(Enum):
    clock = auto()
    date = auto()
    rasp_b = auto()
    rasp_c = auto()

def get_root():
    root = tk.Tk()
    root.configure(bg = 'black')
    root.title('routiner')

    root.rowconfigure(0, weight = 1) # empty
    root.rowconfigure(1, weight = 1) # clock
    root.rowconfigure(2, weight = 1) # date
    root.rowconfigure(3, weight = 1) # readings
    root.rowconfigure(4, weight = 1) # empty

    root.columnconfigure(0, weight = 1)
    root.columnconfigure(1, weight = 1)

    return root

def get_app():
    root = get_root()

    class Application(tk.Frame):
        def __init__(self, master=None):
            super().__init__(master)
            self.master = master
            pad = 3
            self._geom = '200x200+0+0'
            master.geometry("{0}x{1}+0+0".format(
                master.winfo_screenwidth() - pad,
                master.winfo_screenheight() - pad)
            )

            self.queue = Queue()
            self.construct_clock()
            self.construct_date()
            self.construct_readings()
            self.refresh_ui()

        def construct_clock(self):
            def update_time():
                now = datetime.now()
                massaged = now + offset
                label = massaged.strftime(time_format)
                self.queue.put((Label.clock, label))
                self.clock.after(100, update_time)

            self.clock = tk.Label(self.master,
                font = ('calibri', 100, 'bold'),
                background = 'black',
                foreground = 'white')

            self.clock.grid(row = 1, columnspan = 2, sticky = tk.N)
            update_time()

        def construct_date(self):
            def update_date():
                label = datetime.now().strftime(date_format)
                self.queue.put((Label.date, label))
                self.date.after(10000, update_date)

            self.date = tk.Label(self.master,
                font = ('calibri', 50, 'bold'),
                background = 'black',
                foreground = 'white')

            self.date.grid(row = 2, columnspan = 2, sticky = tk.N)
            update_date()

        def construct_readings(self):
            self.rasp_b = tk.Label(self.master,
                font = ('calibri', 20),
                background = 'black',
                foreground = 'white')

            self.rasp_b.config(justify = tk.LEFT)
            self.rasp_b.grid(row = 3, column = 0, sticky = tk.N)

            self.rasp_c = tk.Label(self.master,
                font = ('calibri', 20),
                background = 'black',
                foreground = 'white')

            self.rasp_c.config(justify = tk.LEFT)
            self.rasp_c.grid(row = 3, column = 1, sticky = tk.N)

        def process_incoming(self):
            while self.queue.qsize():
                try:
                    label, value = self.queue.get(0)
                    mapping = {
                        Label.clock: self.clock,
                        Label.date: self.date,
                        Label.rasp_b: self.rasp_b,
                        Label.rasp_c: self.rasp_c,
                    }

                    mapping[label].config(text = value)
                except Queue.Empty:
                    pass

        def refresh_ui(self):
            self.process_incoming()
            self.master.after(200, self.refresh_ui)

        def get_queue(self):
            return self.queue

    return Application(master = root)
