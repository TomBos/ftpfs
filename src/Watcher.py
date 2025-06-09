#!/usr/bin/env python
import pyinotify
import threading

class fileWatcher(pyinotify.ProcessEvent):
    def __init__(self, socket, logs, dirMapping, maxBufferSize=1024, debounce_delay=2):
        self.socket = socket
        self.logs = logs
        self.dirMapping = dirMapping
        self.maximumBufferSize = maxBufferSize
        self.debounce_delay = debounce_delay  # seconds
        self.timers = {}  # file_path -> Timer

    def debounce_upload(self, localPath, remotePath):
        # Cancel existing timer for this file if exists
        if localPath in self.timers:
            self.timers[localPath].cancel()

        # Create and start a new timer
        timer = threading.Timer(self.debounce_delay, self.upload_file, args=(localPath, remotePath))
        self.timers[localPath] = timer
        timer.start()

    def upload_file(self, localPath, remotePath):
        self.logs.log(f"Uploading {localPath} to {remotePath}")
        self.socket.overrideFile(localPath, remotePath, self.logs, self.maximumBufferSize)
        # Upload done, remove timer from dict
        self.timers.pop(localPath, None)

    def process_IN_CREATE(self, event):
        localPath = event.pathname
        remotePath = self.getRemotePath(localPath)

        if not event.dir:
            # debounce file upload
            self.debounce_upload(localPath, remotePath)
        else:
            self.logs.log(f"Creating directory on remote: {remotePath}")
            response = self.socket.createDirectory(remotePath, self.maximumBufferSize)
            if response.startswith('257'):
                self.logs.log(f"Created  : {remotePath}", 1)
            else:
                self.logs.log(f"Failed to create  : {remotePath}", 1)

    def process_IN_MODIFY(self, event):
        localPath = event.pathname
        remotePath = self.getRemotePath(localPath)

        if not event.dir:
            # debounce file upload
            self.debounce_upload(localPath, remotePath)

    def getRemotePath(self, localPath):
        relativePath = localPath.find(self.dirMapping["LOCAL"])
        localDirLen = len(self.dirMapping["LOCAL"])
        substrStart = relativePath + localDirLen
        remotePath = self.dirMapping["REMOTE"] + localPath[substrStart:]
        return remotePath

    def watchDir(self, localDir):
        wm = pyinotify.WatchManager()
        notifier = pyinotify.Notifier(wm, self)
        wm.add_watch(localDir, pyinotify.IN_CREATE | pyinotify.IN_MODIFY | pyinotify.IN_DELETE, rec=True)
        notifier.loop()
