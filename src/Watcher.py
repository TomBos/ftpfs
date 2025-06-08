#!/usr/bin/env python
import pyinotify

class fileWatcher(pyinotify.ProcessEvent):
    def __init__(self, socket, logs, maxBufferSize = 1024):
        self.socket = socket
        self.logs = logs
        self.maximumBufferSize = maxBufferSize

    def process_IN_CREATE(self, event):
        if not event.dir:
            print(f"Created file: {event.pathname}")
            self.socket.overrideFile("2025-06-07.log", "htdocs/myfile2.txt", self.logs, self.maximumBufferSize)

    def process_IN_MODIFY(self, event):
        if not event.dir:
            print(f"Modified file: {event.pathname}")
    
    
    def process_IN_DELETE(self, event):
        if not event.dir:
            print(f"Deleted file: {event.pathname}")

    
    def watchDir(self, localDir):
        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm, self)
        wm.add_watch(localDir, pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_DELETE, rec=True)
        notifier.loop()
