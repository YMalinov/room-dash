import tkinter as tk
from time import strftime
from queue import Queue
from enum import Enum, unique

@unique
class Label(Enum):
    clock = 1
    rasp_b = 2
    rasp_c = 3

def get_root():
    root = tk.Tk()
    root.configure(bg = 'black')
    root.title('routiner')

    root.rowconfigure(0, weight = 1) # empty
    root.rowconfigure(1, weight = 1) # clock
    root.rowconfigure(2, weight = 1) # readings
    root.rowconfigure(3, weight = 1) # empty

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
            self.construct_readings()
            self.refresh_ui()

        def construct_clock(self):
            def update_time():
                label = strftime('%H:%M:%S %p')
                self.queue.put((Label.clock, label))
                self.clock.after(500, update_time) # will be accurate up to +/- 500 ms

            self.clock = tk.Label(self.master,
                font = ('calibri', 90, 'bold'),
                background = 'black',
                foreground = 'white')

            self.clock.grid(row = 1, columnspan = 2, sticky = tk.N)

            update_time()

        def construct_readings(self):
            self.rasp_b = tk.Label(self.master,
                font = ('calibri', 20),
                background = 'black',
                foreground = 'white')

            self.rasp_b.config(justify = tk.LEFT)
            self.rasp_b.grid(row = 2, column = 0, sticky = tk.N)

            self.rasp_c = tk.Label(self.master,
                font = ('calibri', 20),
                background = 'black',
                foreground = 'white')

            self.rasp_c.config(justify = tk.LEFT)
            self.rasp_c.grid(row = 2, column = 1, sticky = tk.N)

        def process_incoming(self):
            while self.queue.qsize():
                try:
                    label, value = self.queue.get(0)
                    mapping = {
                        Label.clock: self.clock,
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
