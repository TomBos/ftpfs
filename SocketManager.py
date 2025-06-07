#!/usr/bin/env python
from LogsManager import LogsManager as LM

import socket

class SocketManager:
    def __init__(self):
        self.socket = None
        pass

    def createSocket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return self.socket 

    def checkIfSocketExists(self):
        if not self.socket:
            raise RuntimeError("Socket not created yet. Call createSocket() first.")

    def connectToHost(self, host, port = 21):
        self.checkIfSocketExists() 
        self.socket.connect((host,port))

    def acceptControlMessage(self, bufferSize = 1024):
        self.checkIfSocketExists()
        response = self.socket.recv(bufferSize)
        return response.decode().strip("\n")

    def acceptPassiveMessage(self, bufferSize=4096):
        self.checkIfSocketExists()
        chunks = []
        while True:
            chunk = self.socket.recv(bufferSize)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks).decode().strip("\n")

    def runControlCommand(self, command, bufferSize = 1024):
        self.checkIfSocketExists()
        command = (command + "\r\n").encode()
        self.socket.sendall(command)
        return self.acceptControlMessage(bufferSize)

    def terminateSocket(self):
        self.checkIfSocketExists()
        self.socket.close()

    def getNewPassivePort(self, LogsClass, commandBufferSize = 1024):
        self.checkIfSocketExists()
        response = self.runControlCommand(f"PASV", commandBufferSize)
        LogsClass.log(response)

        passiveHostStart = response.index('(')+1
        passiveHostEnd = response.index(')')

        LogsClass.log(f"Server PASV info found at: {passiveHostStart} - {passiveHostEnd}")

        parts = response[passiveHostStart:passiveHostEnd].split(',')
        LogsClass.log(parts)

        passiveHostIP = ".".join(parts[:4])
        passiveHostPort = int(parts[4]) * 256 + int(parts[5])
        LogsClass.log(f"passive connection IP: {passiveHostIP}:{passiveHostPort}")

        return [passiveHostIP, passiveHostPort]
    
    def runPassiveCommand(self, passiveCommand, LogsClass, commandBufferSize):
        self.checkIfSocketExists()
        passiveHostIP, passiveHostPort = self.getNewPassivePort(LogsClass, commandBufferSize)
        newPassiveSocket = SocketManager()
        newPassiveSocket.createSocket()
        newPassiveSocket.connectToHost(passiveHostIP,passiveHostPort)
        LogsClass.log(f"Connected to passive socket: {newPassiveSocket.socket}")

        commandResponse = self.runControlCommand(passiveCommand, commandBufferSize)
        LogsClass.log(commandResponse)

        passiveResponse = newPassiveSocket.acceptPassiveMessage(commandBufferSize)

        controlResponse = self.acceptControlMessage(commandBufferSize)
        LogsClass.log(controlResponse)

        newPassiveSocket.terminateSocket()
        return passiveResponse
