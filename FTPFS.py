#!/usr/bin/env python

from SocketManager import SocketManager as SM
from LogsManager import LogsManager as LM

import yaml
import sys

KiB = 1024

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

username = config["ftp"]["user"]
password = config["ftp"]["pass"]
masterHost = config["ftp"]["host"]
masterPort = config["ftp"]["port"]


if '-v' in sys.argv:
    verbosityLevel = 2
    print("\nVERBOSE OUTPUT ENABLED VIA ARGUMENT\n")
else:
    verbosityLevel = config["settings"].get("verbosity")
    if verbosityLevel is None:
        verbosityLevel = 2


logs = LM(verbosityLevel)
controlSocket = SM()
controlSocket.createSocket()
controlSocket.connectToHost(masterHost,masterPort)

logs.log(f"Connected: {controlSocket.socket}")

# === Initial Handshake ===
response = controlSocket.acceptControlMessage(KiB * 5)
logs.log(response)


# === Authenticate using credentials ===
response = controlSocket.runControlCommand(f"USER {username}", KiB*5)
logs.log(response)

response = controlSocket.runControlCommand(f"PASS {password}", KiB*5)
logs.log(response, 1)

# === Invoke Passive Commands ===
response = controlSocket.runPassiveCommand("LIST", logs, KiB*100)
logs.log(response, 1)


# === Kill master connection 
controlSocket.terminateSocket()
