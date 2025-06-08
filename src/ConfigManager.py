#!/usr/bin/env python
import yaml
import os

class ConfigManager:
    def __init__(self, configFilePath):
        self.configFile = configFilePath
        self.servers = None
        self.settings = None
        pass

    def loadConfig(self):
        if not os.path.exists(self.configFile):
            raise FileNotFoundError(f"Config file '{self.configFile}' not found.")

        with open(f"{self.configFile}", "r") as f:
            config = yaml.safe_load(f)

        if config:
            self.servers = config["servers"]
            self.settings = config["settings"]
        return
    
    def getServerNames(self):
        return list(self.servers.keys())

    def getServerCredentials(self, serverName):
        if serverName in self.servers:
            return self.servers.get(serverName, {})

    def selectServer(self, selection = -1):
        servers = self.getServerNames() 
        
        if selection == -1:
            if len(servers) == 1:
                return self.getServerCredentials(servers[0])

            print("")
            for index,server in enumerate(servers):
                self.createBox(server,index)

            selectedServer = input("Select server: ")
            self.selectServer(int(selectedServer))
            return

        else:
            if selection > len(servers) -1 or selection < 0:
                self.selectServer()

            return self.getServerCredentials(servers[selection])

    def createBox(self, variable, index):
        border = "+" + "-" * (len(variable) + 2) + "+"
        print(f"{index}:") 
        print(border)
        print(f"| {variable} |")
        print(f"{border}\n") 
        return  