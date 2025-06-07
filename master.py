#!/usr/bin/env python

from SocketManager import SocketManager as SM
from LogsManager import LogsManager as LM

import yaml
import sys

KiB = 1024

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

ftp_user = config["ftp"]["user"]
ftp_pass = config["ftp"]["pass"]
ftp_host = config["ftp"]["host"]
ftp_port = config["ftp"]["port"]


if '-v' in sys.argv:
    verbosityLevel = 2
    print("\nVERBOSE OUTPUT ENABLED VIA ARGUMENT\n")
else:
    verbosityLevel = config["settings"].get("verbosity")
    if verbosityLevel is None:
        verbosityLevel = 2


logs = LM(verbosityLevel)
controllSocket = SM()
controllSocket.createSocket()
controllSocket.connectToHost(ftp_host)

logs.log(f"Connected: {controllSocket.socket}")

# === Initial Handshake ===
response = controllSocket.acceptIncomingMessage(KiB * 5)
logs.log(response)


# === Authenticate using credentials ===
response = controllSocket.runCommand(f"USER {ftp_user}", KiB*5)
logs.log(response)

response = controllSocket.runCommand(f"PASS {ftp_pass}", KiB*5)
logs.log(response, 1)


# === Get info on where to open passive mode socket ===
response = controllSocket.runCommand(f"PASV", KiB*5)
logs.log(response)

start = response.index('(')
end = response.index(')')

logs.log(f"Server PASV info found at: {start} - {end}")

portInfo = response[start+1:end].split(',')
logs.log(portInfo)

pasv_ip = f"{portInfo[0]}.{portInfo[1]}.{portInfo[2]}.{portInfo[3]}" 
pasv_port =  int(portInfo[4]) * 256  + int(portInfo[5])
logs.log(f"passive connection IP: {pasv_ip}:{pasv_port}", 1)


# === Create passive socket ===
passiveSocket = SM()
passiveSocket.createSocket()
passiveSocket.connectToHost(pasv_ip,pasv_port)
logs.log(f"Connected to passive socket: {passiveSocket.socket}")

# === List all files in FTP configuret root dir
response = controllSocket.runCommand("LIST", KiB*5)
logs.log(response)

response = passiveSocket.acceptIncomingMessage(KiB*5)
logs.log(response, 1)


# === Terminate Sockets === 
passiveSocket.terminateSocket()
controllSocket.terminateSocket()
