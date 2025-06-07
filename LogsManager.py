#!/usr/bin/env python
from datetime import date, datetime

class LogsManager:
    def __init__(self, verbosity = 2):
        self.verbosity = verbosity
        pass

    def log(self, msg, vebosityOverride = 0):
        if self.verbosity >= 1 or vebosityOverride >= 1:
            print(f">  {msg}")
            if self.verbosity > 1 or vebosityOverride > 1:
                self.logIntoFile(msg)

    def logIntoFile(self, msg):
        with open(f"{date.today()}.log", "a") as logFile:
            logFile.write(f"[{datetime.now()}] {msg}\n")

