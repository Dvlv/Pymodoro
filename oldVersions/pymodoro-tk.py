import time
from datetime import datetime, timedelta
import tkinter as tk
import threading

class Pymodoro(tk.Frame):
  def __init__(self, master=None):
    super().__init__(master)
    self.pack()
    self.add_widgets()
    self.time_set = 0
    self.paused = 0

  def add_widgets(self):
    self.time_label = tk.Label(self, text='Countdown', padx=20, pady=20)
    self.time_label.pack(side='top')

    self.button = tk.Button(self, text="start", command=self.countdown, pady=20, padx=20)
    self.button.pack(side='bottom')

  def start(self):
    self.time_set = datetime.now() + timedelta(minutes = 10)
    self.time_label.configure(text=str(datetime.now() - self.time_set))
    self.time_label.update()

#  def countdown(self, time_range=1500):
#    if not self.time_left:
#      self.time_left = time_range
#
#    self.pause = 0
#    self.button.configure(text='stop', command=self.pause_countdown)
#    def callback(self):
#      mins, secs = divmod(self.time_left, 60)
#      time_string = '{:02d}:{:02d}'.format(mins, secs)
#      self.time_label.configure(text=time_string)
#      self.time_label.update_idletasks()
#      self.button.update_idletasks()
#      self.time_left -= 1
#      threading.Timer(1, callback)
#    threading.Timer(1, callback)
#
#  def pause_countdown(self):
#    self.pause = 1


root = tk.Tk()
app = Pymodoro(master=root)
app.mainloop()