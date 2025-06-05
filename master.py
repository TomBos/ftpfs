import socket
import yaml
import sys

KB = 1024

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


def invokeCMD(socketObject, command, isVerbose=0, bufferSize=KB):
    socketObject.sendall(command.encode())
    response = socketObject.recv(bufferSize) 
    if isVerbose:
        print("Server says: ", response.decode())



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(ftp_server)
if isVerbose:
    print("Connected:", sock)
    print(" ")

greeting = sock.recv(4096)
if isVerbose:
    print("Server says:", greeting.decode())

# b => send byte encoded
# CLRF (\r\n) => Carriage Return + Line Feed => end ftp command
cmd = f"USER {ftp_user}\r\n"
invokeCMD(sock,cmd,isVerbose)

cmd = f"PASS {ftp_pass}\r\n"
invokeCMD(sock,cmd,isVerbose)

cmd = f"PWD \r\n"
invokeCMD(sock,cmd,isVerbose)

cmd = f"LS \r\n"
invokeCMD(sock,cmd,isVerbose)

sock.close()


