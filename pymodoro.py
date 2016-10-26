import wx
import threading
import time
import datetime

SCREEN_WIDTH = 300
SCREEN_HEIGHT = 300

ID_COUNT = wx.NewId()
ID_PAUSE = wx.NewId()
ID_TEXTBOX = wx.NewId()
myEVT_COUNT = wx.NewEventType()
EVT_COUNT = wx.PyEventBinder(myEVT_COUNT, 1)
POMODORO_FINISHED_MESSAGE = "Pomodoro Finished!"


class CountingFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, title="Pymodoro", size=(SCREEN_WIDTH, SCREEN_HEIGHT))

        self.__DoLayout()
        self.CreateStatusBar()


    def __DoLayout(self):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(CountingPanel(self), 1, wx.ALIGN_CENTER)
        self.SetSizer(sizer)
        self.SetMinSize((SCREEN_WIDTH,SCREEN_HEIGHT))


class CountingPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self._counter = wx.StaticText(self, label="25:00")
        self._counter.SetFont(wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL))

        self.__DoLayout()

        self.Bind(wx.EVT_BUTTON, self.OnPauseButton, self.pauseButton)
        self.Bind(wx.EVT_BUTTON, self.OnButton, self.startButton)
        self.Bind(EVT_COUNT, self.OnCount)


    def __DoLayout(self):
        self._sizer = wx.GridSizer(4, 1, 30)
        self.taskName = wx.TextCtrl(self, ID_TEXTBOX, "New Task", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.startButton = wx.Button(self, ID_COUNT, "Start")
        self.pauseButton = wx.Button(self, ID_PAUSE, "Pause")
        self._sizer.AddMany([(self.taskName, 0, wx.ALIGN_CENTER), (self.startButton, 0, wx.ALIGN_CENTER), (self._counter, 0, wx.ALIGN_CENTER), (self.pauseButton, 0, wx.ALIGN_CENTER)])
        self.SetSizer(self._sizer)


    def OnButton(self, evt):
        now = datetime.datetime.now()
        #in_25_mins = now + datetime.timedelta(minutes=25)
        in_25_mins = now + datetime.timedelta(seconds=3)
        worker = CountingThread(self, now, in_25_mins)
        self._worker = worker
        self.startButton.Disable()
        if self.startButton.GetLabel() == "Restart":
            self._counter.SetLabel("25:00")
            self._adjustCounterPosition('right')
        self._worker.start()


    def OnPauseButton(self, evt):
        self._worker.paused = not self._worker.paused
        if self._worker.paused:
            self.pauseButton.SetLabel("Resume")
            self._worker.startTime = datetime.datetime.now()
        else:
            self.pauseButton.SetLabel("Pause")
            end_timedelta = datetime.datetime.now() - self._worker.startTime
            self._worker.endTime = self._worker.endTime + datetime.timedelta(seconds=end_timedelta.seconds)


    def OnCount(self, evt):
        val = evt.GetTimeString()
        self._counter.SetLabel(unicode(val))
        if val == POMODORO_FINISHED_MESSAGE:
           self.OnPomodoroFinished()


    def OnPomodoroFinished(self):
        self._adjustCounterPosition('left')

        popup_message = wx.MessageDialog(self, "25 minutes is up, take a break!", "Pomodoro Finished!", wx.OK)
        popup_message.ShowModal()
        popup_message.Destroy()

        self.startButton.SetLabel("Restart")
        self.startButton.Enable()


    def _adjustCounterPosition(self, left_or_right):
        label_position = self._counter.GetPosition()
        new_x = label_position[0] - 80 if (left_or_right == 'left') else label_position[0] + 80
        self._sizer.GetItem(2).SetDimension((new_x, label_position[1]), (SCREEN_WIDTH, 30))


class CountEvent(wx.PyCommandEvent):
    def __init__(self, etype, eid, time_string="25:00"):
        wx.PyCommandEvent.__init__(self, etype, eid)
        self.time_string = time_string


    def GetTimeString(self):
        return self.time_string


class CountingThread(threading.Thread):
    def __init__(self, parent, start_time, end_time):
        threading.Thread.__init__(self)
        self._parent = parent
        self.paused = False
        self.startTime = start_time
        self.endTime = end_time


    def run(self):
        while datetime.datetime.now() < self.endTime:
            if not self.paused:
                time.sleep(0.2)
                td = self.endTime - datetime.datetime.now()
                hours, remainder = divmod(td.seconds, 3600)
                mins, secs = divmod(remainder, 60)
                time_string = '{:02d}:{:02d}'.format(mins, secs)
                self.time_string = time_string
                evt = CountEvent(myEVT_COUNT, -1, self.time_string)
                wx.PostEvent(self._parent, evt)
        evt = CountEvent(myEVT_COUNT, -1, POMODORO_FINISHED_MESSAGE)
        wx.PostEvent(self._parent, evt)


if __name__ == '__main__':
    APP = wx.App(False)
    FRAME = CountingFrame(None)
    FRAME.Show()
    APP.MainLoop()










