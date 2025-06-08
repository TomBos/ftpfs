#!/usr/bin/env python
from SocketManager import SocketManager as SM
from LogsManager import LogsManager as LM
from ConfigManager import ConfigManager as CM
from Watcher import fileWatcher as FW

import sys
import os

KiB = 1024

configPath = os.path.expanduser("~/.config/FTPFS/config.yaml")
if os.path.exists(configPath):
    configManager = CM(configPath)
else:
    configManager = CM("config.example.yaml")

configManager.loadConfig()
credentials = configManager.selectServer()
settings = configManager.getSettings()

username = credentials["user"]
password = credentials["pass"]
masterHost = credentials["host"]
masterPort = credentials["port"]
mappings = credentials["mapping"]

if '-v' in sys.argv:
    verbosityLevel = 2
    print("\nVERBOSE OUTPUT ENABLED VIA ARGUMENT\n")
else:
    verbosityLevel = settings.get("verbosity")
    if verbosityLevel is None:
        verbosityLevel = 2


# === Create class for logs ===
logs = LM(verbosityLevel)


# === Create Master Socket === 
controlSocket = SM()
controlSocket.createSocket()
controlSocket.connectToHost(masterHost,masterPort)


# === Initial Handshake ===
response = controlSocket.acceptControlMessage(KiB*4)
logs.log(response)


# === Authenticate using credentials ===
response = controlSocket.runControlCommand(f"USER {username}", KiB*4)
logs.log(response)

response = controlSocket.runControlCommand(f"PASS {password}", KiB*4)
logs.log(response, 1)

# === Start Auto sync ===
path = os.path.expandvars(mappings['watch_dir'])

mapping = {
    "LOCAL": mappings['local_root'],
    "REMOTE": mappings['remote_root']
}

watcher = FW(controlSocket, logs, mapping, KiB*4)
watcher.watchDir(path)


# === Kill master connection 
controlSocket.terminateSocket()
