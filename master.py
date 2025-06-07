#!/usr/bin/env python

from SocketManager import SocketManager as SM

import socket
import yaml
import sys

KiB = 1024

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

ftp_user = config["ftp"]["user"]
ftp_pass = config["ftp"]["pass"]
ftp_host = config["ftp"]["host"]
ftp_port = config["ftp"]["port"]
isVerbose = config["settings"]["verbosity"] or 0

if '-v' in sys.argv:
    isVerbose = 1
    print("\nVERBOSE OUTPUT ENABLED VIA ARGUMENT\n")


def invokeCMD(socketObject, command, isVerbose = 0, bufferSize = KiB):
    socketObject.sendall(command.encode())
    response = socketObject.recv(bufferSize) 
    if isVerbose:
        print("> ", response.decode().strip('\n'))
    return response.decode().strip('\n')

controllSocket = SM()
controllSocket.createSocket()
controllSocket.connectToHost(ftp_host)

if isVerbose:
    print(f"Connected: {controllSocket.socket} \n")

response = controllSocket.acceptIncomingMessage(KiB * 5)
if isVerbose:
    print(f">  {response}")

response = controllSocket.runCommand(f"USER {ftp_user}", KiB*5)
if isVerbose:
    print(f">  {response}")

response = controllSocket.runCommand(f"PASS {ftp_pass}", KiB*5)
print(f">  {response}")

response = controllSocket.runCommand(f"PASV", KiB*5)
if isVerbose:
    print(f">  {response}")

start = response.index('(')
end = response.index(')')

if isVerbose:
    print(f"Server PASV info found at: {start} - {end}")

portInfo = response[start+1:end].split(',')

if isVerbose:
    print(portInfo)

pasv_ip = f"{portInfo[0]}.{portInfo[1]}.{portInfo[2]}.{portInfo[3]}" 
pasv_port =  int(portInfo[4]) * 256  + int(portInfo[5])

print(f">  IP: {pasv_ip}:{pasv_port}")


passiveSocket = SM()
passiveSocket.createSocket()
passiveSocket.connectToHost(pasv_ip,pasv_port)

if isVerbose:
    print(f"Connected to passive socket: {passiveSocket.socket} \n")

response = controllSocket.runCommand("LIST", KiB*5)
if isVerbose:
    print(response)


response = passiveSocket.acceptIncomingMessage(KiB*5)
print(response)

passiveSocket.terminateSocket()
controllSocket.terminateSocket()
