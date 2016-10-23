import wx
import threading
import time
import datetime

ID_COUNT = wx.NewId()
ID_PAUSE = wx.NewId()
myEVT_COUNT = wx.NewEventType()
EVT_COUNT = wx.PyEventBinder(myEVT_COUNT, 1)


class CountingFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Pymodoro", size=(300,300))

        self.__DoLayout()
        self.CreateStatusBar()


    def __DoLayout(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(CountingPanel(self), 1, wx.ALIGN_CENTER)
        self.SetSizer(sizer)
        self.SetMinSize((300,300))


class CountingPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self.POMODORO_DURATION = 2

        self._counter = wx.StaticText(self, label="25:00")
        self._counter.SetFont(wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL))

        self.__DoLayout()

        self.Bind(wx.EVT_BUTTON, self.OnPauseButton, self.pauseButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.startButton)
        self.Bind(EVT_COUNT, self.OnCount)


    def __DoLayout(self):
        self._sizer = wx.GridSizer(3, 1, 30)
        self.startButton = wx.Button(self, ID_COUNT, "Start")
        self.pauseButton = wx.Button(self, ID_PAUSE, "Pause")
        self._sizer.AddMany([(self.startButton, 0, wx.ALIGN_CENTER), (self._counter, 0, wx.ALIGN_CENTER), (self.pauseButton, 0, wx.ALIGN_CENTER)])
        self.SetSizer(self._sizer)


    def OnButton(self, evt):
        worker = CountingThread(self, self.POMODORO_DURATION)
        self._worker = worker
        self._worker.start()
        self.startButton.Disable()


    def OnPauseButton(self, evt):
        self._worker.paused = not self._worker.paused
        if self._worker.paused:
            self.pauseButton.SetLabel("Resume")
        else:
            self.pauseButton.SetLabel("Pause")


    def OnCount(self, evt):
        val = evt.GetTimeString()
        self._counter.SetLabel(unicode(val))
        if val == "Pomodoro Finished!":
            print(self._sizer.GetItem(1).GetPosition())
            self._sizer.GetItem(1).SetDimension((37, 67), (300,300))


class CountEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, value=None, time_string="25:00"):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self._value = value
        self.time_string = time_string


    def GetValue(self):
        return self._value


    def GetTimeString(self):
        return self.time_string


class CountingThread(threading.Thread):
    def __init__(self, parent, value):
        threading.Thread.__init__(self)
        self._parent = parent
        self._value = value
        self.paused = False


    def run(self):
        while self._value > -1:
            if not self.paused:
                time.sleep(1)
                mins, secs = divmod(self._value, 60)
                time_string = '{:02d}:{:02d}'.format(mins, secs)
                self.time_string = time_string
                self._value -= 1
                evt = CountEvent(myEVT_COUNT, -1, self._value, self.time_string)
                wx.PostEvent(self._parent, evt)
        evt = CountEvent(myEVT_COUNT, -1, self._value, "Pomodoro Finished!")
        wx.PostEvent(self._parent, evt)


if __name__ == '__main__':
    APP = wx.App(False)
    FRAME = CountingFrame(None)
    FRAME.Show()
    APP.MainLoop()










