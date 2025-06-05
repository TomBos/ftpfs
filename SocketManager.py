#!/usr/bin/env python
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

    def acceptIncomingMessage(self, bufferSize = 1024):
        self.checkIfSocketExists()
        response = self.socket.recv(bufferSize)
        return response.decode()

