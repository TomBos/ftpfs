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


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(ftp_server)
if isVerbose:
    print("Connected:", sock)
    print(" ")

greeting = sock.recv(KiB*5)
if isVerbose:
    print("> ", greeting.decode())

# b => send byte encoded
# CLRF (\r\n) => Carriage Return + Line Feed => end ftp command
cmd = f"USER {ftp_user}\r\n"
invokeCMD(sock,cmd,isVerbose)

cmd = f"PASS {ftp_pass}\r\n"
invokeCMD(sock,cmd, 1)

cmd = f"PASV \r\n"
response = invokeCMD(sock,cmd, isVerbose)

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
response = invokeCMD(sock,cmd, isVerbose)

listing = b""
while True:
    chunk = pasv_sock.recv(4096)
    if not chunk:
        break
    listing += chunk

print(listing.decode())

pasv_sock.close()
sock.recv(KiB * 100)

sock.close()
