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
response = controlSocket.acceptIncomingMessage(KiB * 5)
logs.log(response)


# === Authenticate using credentials ===
response = controlSocket.runCommand(f"USER {username}", KiB*5)
logs.log(response)

response = controlSocket.runCommand(f"PASS {password}", KiB*5)
logs.log(response, 1)

# === Create passive socket ===
passiveHostInfo = controlSocket.getNewPassivePort(logs, KiB*5)
passiveHostIP = passiveHostInfo["IP"]
passiveHostPort = passiveHostInfo["PORT"]

passiveSocket = SM()
passiveSocket.createSocket()
passiveSocket.connectToHost(passiveHostIP,passiveHostPort)
logs.log(f"Connected to passive socket: {passiveSocket.socket}")

# === List all files in FTP configuret root dir
response = controlSocket.runCommand("LIST", KiB*5)
logs.log(response)

response = passiveSocket.acceptIncomingMessage(KiB*5)
logs.log(response, 1)
response = controlSocket.acceptIncomingMessage(KiB*5)
logs.log(response,1)

response = controlSocket.runCommand(f"STOR htdocs/stores.php", KiB * 10)
logs.log(response,2)



# === Terminate Sockets === 
passiveSocket.terminateSocket()
controlSocket.terminateSocket()
