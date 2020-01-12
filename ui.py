import tkinter as tk
from time import strftime

def get_root():
    root = tk.Tk()
    root.configure(bg = 'black')
    root.title = 'routine_tracker'

    root.rowconfigure(0, weight = 1) # empty
    root.rowconfigure(1, weight = 1) # clock
    root.rowconfigure(2, weight = 1) # readings
    root.rowconfigure(3, weight = 1) # empty

    root.columnconfigure(0, weight = 1)
    root.columnconfigure(1, weight = 1)

    return root

def get_app(root):
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

    return Application(master = root)

def put_clock(root):
    def update_time():
        label = strftime('%H:%M:%S %p')
        clocklbl.config(text = label)
        clocklbl.after(500, update_time) # will be accurate up to +/- 500 ms

    clocklbl = tk.Label(root,
        font = ('calibri', 90, 'bold'),
        background = 'black',
        foreground = 'white')

    clocklbl.grid(row = 1, columnspan = 2, sticky = tk.N)

    update_time()

def put_readings(root):
    rasp_b = tk.Label(root,
        font = ('calibri', 20),
        background = 'black',
        foreground = 'white')

    rasp_b.config(justify = tk.LEFT)
    rasp_b.grid(row = 2, column = 0, sticky = tk.N)

    rasp_c = tk.Label(root,
        font = ('calibri', 20),
        background = 'black',
        foreground = 'white')

    rasp_c.config(justify = tk.LEFT)
    rasp_c.grid(row = 2, column = 1, sticky = tk.N)

    return rasp_b, rasp_c
