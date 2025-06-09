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
        return

    def connectToHost(self, host, port = 21):
        self.checkIfSocketExists() 
        self.socket.connect((host,port))


    def acceptControlMessage(self, bufferSize = 1024):
        self.checkIfSocketExists()
        response = self.socket.recv(bufferSize)
        return response.decode().strip("\n")


    def acceptPassiveMessage(self, bufferSize = 4096):
        self.checkIfSocketExists()

        # Read away incomming buffer and return decoded data
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
        return


    def getNewPassivePort(self, LogsClass, commandBufferSize = 1024):
        self.checkIfSocketExists()

        # Try openning passive connection
        response = self.runControlCommand(f"PASV", commandBufferSize)
        LogsClass.log(response)

        # Parse out Host IP + PORT
        passiveHostStart = response.index('(')+1
        passiveHostEnd = response.index(')')

        LogsClass.log(f"Server PASV info found at: {passiveHostStart} - {passiveHostEnd}")

        parts = response[passiveHostStart:passiveHostEnd].split(',')
        LogsClass.log(parts)

        passiveHostIP = ".".join(parts[:4])
        passiveHostPort = int(parts[4]) * 256 + int(parts[5])
        LogsClass.log(f"passive connection IP: {passiveHostIP}:{passiveHostPort}")

        # Return info
        return [passiveHostIP, passiveHostPort]


    def runPassiveCommand(self, passiveCommand, LogsClass, commandBufferSize):
        self.checkIfSocketExists()

        # Create new passive socket
        passiveHostIP, passiveHostPort = self.getNewPassivePort(LogsClass, commandBufferSize)
        newPassiveSocket = SocketManager()
        newPassiveSocket.createSocket()
        newPassiveSocket.connectToHost(passiveHostIP,passiveHostPort)
        LogsClass.log(f"Connected to passive socket: {newPassiveSocket.socket}")

        # Run command
        commandResponse = self.runControlCommand(passiveCommand, commandBufferSize)
        LogsClass.log(commandResponse)

        # Get response for passive socket
        passiveResponse = newPassiveSocket.acceptPassiveMessage(commandBufferSize)

        # Get response for controll socket
        controlResponse = self.acceptControlMessage(commandBufferSize)
        LogsClass.log(controlResponse)

        # Terminate passive socket
        newPassiveSocket.terminateSocket()
        return passiveResponse
    

    def overrideFile(self, localFilePath, remoteFilePath, LogsClass, bufferSize = 1024):
        self.checkIfSocketExists()

        # Create new passive socket
        passiveHostIP, passiveHostPort = self.getNewPassivePort(LogsClass, 1024)
        newPassiveSocket = SocketManager()
        newPassiveSocket.createSocket()
        newPassiveSocket.connectToHost(passiveHostIP,passiveHostPort)
        LogsClass.log(f"Connected to passive socket: {newPassiveSocket.socket}")

        # Ask for permission to send file
        response = self.runControlCommand(f"STOR {remoteFilePath}", bufferSize)
        LogsClass.log(response)

        # Log errors
        if not response.startswith('150'):
            LogsClass.log("Server did not accept STOR command, aborting upload.")
            newPassiveSocket.terminateSocket()
            return

        # Send file splitted by bufferSize
        with open(f"{localFilePath}", "rb") as f:
            while True:
                chunk = f.read(bufferSize)
                if not chunk:
                    break
                newPassiveSocket.socket.sendall(chunk)

        # Terminate passive socket
        newPassiveSocket.terminateSocket()
        LogsClass.log(f"Passive socket closed after file transfer")

        # Print out success message
        finalResponse = self.acceptControlMessage(bufferSize)
        if finalResponse.startswith('226'):
            LogsClass.log(f"Uploaded: {remoteFilePath}  ", 1) 
        return


    def createDirectory(self, dirPath, commandBufferSize):
        self.checkIfSocketExists()
        return self.runControlCommand(f"MKD {dirPath}", commandBufferSize)
