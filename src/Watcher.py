#!/usr/bin/env python
import pyinotify

class fileWatcher(pyinotify.ProcessEvent):
    def __init__(self, socket, logs, dirMapping, maxBufferSize = 1024):
        self.socket = socket
        self.logs = logs
        self.dirMapping = dirMapping
        self.maximumBufferSize = maxBufferSize


    def process_IN_CREATE(self, event):
        localPath = event.pathname
        remotePath = self.getRemotePath(localPath) 
        
        if not event.dir:
            self.logs.log(f"Uploading {localPath} to {remotePath}")
            self.socket.overrideFile(localPath, remotePath, self.logs, self.maximumBufferSize)
        else:
            print(event.pathname)
            # self.logs.log(f"Creating directory on remote: {remotePath}")
            

    def process_IN_MODIFY(self, event):
        if not event.dir:
            print(f"Modified file: {event.pathname}")
        return 


    def process_IN_DELETE(self, event):
        if not event.dir:
            print(f"Deleted file: {event.pathname}")
        return


    def getRemotePath(self,localPath):
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
        return