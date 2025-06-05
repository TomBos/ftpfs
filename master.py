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

ftp_server = (ftp_host, ftp_port);

isVerbose = 0
if '-v' in sys.argv:
    isVerbose = 1
    print("\nVERBOSE OUTPUT ENABLED \n")


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

cmd = f"PASV \r\n"
response = invokeCMD(controllSocket,cmd, isVerbose)

start = response.index('(')
end = response.index(')')

if isVerbose:
    print(f"Server PASV info found at: {start} - {end}")

portInfo = response[start+1:end].split(',')

if isVerbose:
    print(portInfo)

pasv_ip = f"{portInfo[0]}.{portInfo[1]}.{portInfo[2]}.{portInfo[3]}" 
pasv_port =  int(portInfo[4]) * 256  + int(portInfo[5])
pasv_ftp_server = (pasv_ip, pasv_port)

print(f">  IP: {pasv_ip}:{pasv_port}")

pasv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pasv_sock.connect(pasv_ftp_server)
if isVerbose:
    print("Connected to data socket:", pasv_sock)
    print(" ")

cmd = f"LIST \r\n"
response = invokeCMD(controllSocket,cmd, isVerbose)

listing = b""
while True:
    chunk = pasv_sock.recv(4096)
    if not chunk:
        break
    listing += chunk

print(listing.decode())

pasv_sock.close()
controllSocket.recv(KiB * 100)

controllSocket.close()
