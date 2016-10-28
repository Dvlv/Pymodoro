import wx
import wx.lib.scrolledpanel
import threading
import time
import datetime
import sqlite3
import os

SCREEN_WIDTH = 300
SCREEN_HEIGHT = 300

ID_COUNT = wx.NewId()
ID_PAUSE = wx.NewId()
ID_TEXTBOX = wx.NewId()
ID_LOGBUTTON = wx.NewId()

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

        menuBar = wx.MenuBar()
        logButton = wx.Menu()
        logItem = logButton.Append(ID_LOGBUTTON, 'View Log', 'View previous pomodoross')
        menuBar.Append(logButton, 'Log')
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.viewLog, logItem)


    def viewLog(self, _):
        log_frame = LogFrame()
        log_frame.Show()


class CountingPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        self._counter = wx.StaticText(self, label="25:00")
        self._counter.SetFont(wx.Font(16, wx.MODERN, wx.NORMAL, wx.NORMAL))

        self.__DoLayout()

        self.Bind(wx.EVT_BUTTON, self.OnPauseButton, self.pauseButton)
        self.Bind(wx.EVT_BUTTON, self.OnStartButton, self.startButton)
        self.Bind(EVT_COUNT, self.OnCount)


    def __DoLayout(self):
        self._sizer = wx.GridSizer(4, 1, 30)
        self.taskName = wx.TextCtrl(self, ID_TEXTBOX, "New Task", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.startButton = wx.Button(self, ID_COUNT, "Start")
        self.pauseButton = wx.Button(self, ID_PAUSE, "Pause")
        self._sizer.AddMany([(self.taskName, 0, wx.ALIGN_CENTER), (self.startButton, 0, wx.ALIGN_CENTER), (self._counter, 0, wx.ALIGN_CENTER), (self.pauseButton, 0, wx.ALIGN_CENTER)])
        self.SetSizer(self._sizer)


    def OnStartButton(self, evt):
        if not hasattr(self, '_worker'):
            now = datetime.datetime.now()
            #in_25_mins = now + datetime.timedelta(minutes=25)
            in_25_mins = now + datetime.timedelta(seconds=8)
            worker = CountingThread(self, now, in_25_mins)
            self._worker = worker
            self._startTime = now

        if self.startButton.GetLabel() == "Finish":
            self.startButton.SetLabel('Restart')
            self._worker.endNow = True
            self._markTaskCompleted()
            self.taskName.Enable()

        elif self.startButton.GetLabel() == "Restart":
            self._counter.SetLabel("25:00")
            self._adjustCounterPosition('right')
            self._addTaskToDb()
            self._worker.start()

        else:
            self.taskName.Disable()
            self.startButton.SetLabel('Finish')
            self._addTaskToDb()
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

        self._markTaskCompleted()

        popup_message = wx.MessageDialog(self, "25 minutes is up, take a break!", "Pomodoro Finished!", wx.OK)
        popup_message.ShowModal()
        popup_message.Destroy()

        self.startButton.SetLabel("Restart")
        self.startButton.Enable()
        self.taskName.Enable()


    def _adjustCounterPosition(self, left_or_right):
        label_position = self._counter.GetPosition()
        new_x = label_position[0] - 80 if (left_or_right == 'left') else label_position[0] + 80
        self._sizer.GetItem(2).SetDimension((new_x, label_position[1]), (SCREEN_WIDTH, 30))


    def _addTaskToDb(self):
        insert_string = 'INSERT INTO pymodoros VALUES (?, 0, ?)'
        task_name = self.taskName.GetValue()
        date_now = self._startTime.strftime("%Y-%m-%d %H:%M")
        _runQuery(insert_string, (task_name, date_now))


    def _markTaskCompleted(self):
        update_string = 'UPDATE pymodoros SET finished = 1 WHERE task = ? and date = ?'
        task_name = self.taskName.GetValue()
        date_now = self._startTime.strftime("%Y-%m-%d %H:%M")
        _runQuery(update_string, (task_name, date_now))



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
        self.endNow = False
        self.paused = False
        self.startTime = start_time
        self.endTime = end_time


    def run(self):
        while True:
            if not self.paused and not self.endNow:
                self.main_loop()
                if datetime.datetime.now() >= self.endTime:
                    evt = CountEvent(myEVT_COUNT, -1, POMODORO_FINISHED_MESSAGE)
                    wx.PostEvent(self._parent, evt)
                    break
            elif self.endNow:
                evt = CountEvent(myEVT_COUNT, -1, POMODORO_FINISHED_MESSAGE)
                wx.PostEvent(self._parent, evt)
                break
            else:
                continue


    def main_loop(self):
        while datetime.datetime.now() < self.endTime:
            time.sleep(0.2)
            td = self.endTime - datetime.datetime.now()
            hours, remainder = divmod(td.seconds, 3600)
            mins, secs = divmod(remainder, 60)
            time_string = '{:02d}:{:02d}'.format(mins, secs)
            self.time_string = time_string
            evt = CountEvent(myEVT_COUNT, -1, self.time_string)
            wx.PostEvent(self._parent, evt)
            if self.paused or self.endNow:
                print('breaking')
                break



class LogFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Previous Pomodoros")

        self._panel = wx.Panel(self)
        self._notebook = wx.Notebook(self._panel)

        self.__DoLayout()
        self.CreateStatusBar()


    def __DoLayout(self):
        date_select = 'SELECT DISTINCT date FROM pymodoros ORDER BY date DESC'
        dates = _runQuery(date_select, None, True)

        for index, date in enumerate(dates):
            dates[index] = date[0].split(" ")[0]

        dates = set(dates)

        for date in dates:
            page = LogPanel(self._notebook, date)
            self._notebook.AddPage(page, date)

        sizer = wx.BoxSizer()
        sizer.Add(self._notebook, 1, wx.EXPAND)
        self._panel.SetSizer(sizer)



            #sizer = wx.BoxSizer(wx.HORIZONTAL)
            #sizer.Add(LogPanel(self), 1, wx.ALIGN_CENTER)
            #self.SetSizer(sizer)
            #self.SetMinSize((SCREEN_WIDTH,SCREEN_HEIGHT))


class LogPanel(wx.lib.scrolledpanel.ScrolledPanel):
    def __init__(self, parent, date):
        wx.lib.scrolledpanel.ScrolledPanel.__init__(self, parent)
        self.SetupScrolling()

        get_previous = 'SELECT * FROM pymodoros WHERE date LIKE ?'
        data = (unicode(date + '%'),)
        self._previous_tasks = _runQuery(get_previous, data, True)

        self.__DoLayout()


    def __DoLayout(self):
        self._sizer = wx.GridSizer(len(self._previous_tasks) + 1, 3, 5)

        boldFont = wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD)
        taskNameHeader = wx.StaticText(self, -1, "Task Name")
        dateHeader = wx.StaticText(self, -1, "Date")
        completedHeader = wx.StaticText(self, -1, "Completed?")

        taskNameHeader.SetFont(boldFont)
        dateHeader.SetFont(boldFont)
        completedHeader.SetFont(boldFont)


        self._sizer.AddMany([(taskNameHeader, 0, wx.ALIGN_CENTER), (dateHeader, 0, wx.ALIGN_CENTER), (completedHeader, 0, wx.ALIGN_CENTER)])

        for task, finished, date in self._previous_tasks:
            taskLabel = wx.StaticText(self, -1, task)
            date_and_time = date.split(' ')
            backwards_date = date_and_time[0]
            time = date_and_time[1]
            date_parts = backwards_date.split('-')
            date_nice = '/'.join([date_parts[2], date_parts[1], date_parts[0]])
            date_complete = ' '.join([date_nice, time])
            dateLabel = wx.StaticText(self, -1, date_nice)
            finished_text = 'Yes' if finished else 'No'
            finishedLabel = wx.StaticText(self, -1, finished_text)
            self._sizer.AddMany([(taskLabel, 0, wx.ALIGN_CENTER), (dateLabel, 0, wx.ALIGN_CENTER), (finishedLabel, 0, wx.ALIGN_CENTER)])

        self.SetSizer(self._sizer)


def _runQuery(sql, data=None, receive=False):
    conn = sqlite3.connect('pymodoro.db')
    cursor = conn.cursor()
    if data:
        cursor.execute(sql, data)
    else:
        cursor.execute(sql)

    if receive:
        return cursor.fetchall()
    else:
        conn.commit()

    conn.close()


def _firstTimeDB():
    create_tables = 'CREATE TABLE pymodoros (task text, finished integer, date text)'
    _runQuery(create_tables)

if __name__ == '__main__':
    if not os.path.isfile('pymodoro.db'):
        _firstTimeDB()

    APP = wx.App(False)
    FRAME = CountingFrame(None)
    FRAME.Show()
    APP.MainLoop()










