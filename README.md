# Pymodoro
###A simple wxWidgets Pomodoro tracker

##Dependencies
wxWidgets (aka wxPython)

##How to use
Run with `python pymodoro.py`
N.B. Pymodoro is built with wxWidgets, so requires python2

1. Enter a task name in the input box
2. Press 'Start' to begin the 25 minute countdown
3. Use 'Pause' if you _need_ to pause working (Ideally pomodoros are unbroken concentration, but life happens)
4. Use 'Stop' to finish a task early

##Log
Pymodoro comes with a log in the form of a sqlite database. This will be created in the same directory as pymodoro.py upon first run

####Viewing the log
`Log` -> `View Log` or `Ctrl+L`
The log is in a tabbed window, with a tab per day.

####What's in the log
The log holds:
- The name of each task
- The date/time it was started
- Whether or not the full 25-minute pomodoro was finished (or the task was finished manually)
- A delete button
- A 'mark finished' / 'mark unfinished' button to manually flip the 'Finished?' value




##Todo
- Manually set tab frequency in the log (week view, month view etc.)
