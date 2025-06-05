import socket
import yaml
import sys

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

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(ftp_server)
if isVerbose:
    print("Connected:", sock)

greeting = sock.recv(4096)
if isVerbose:
    print("Server says:", greeting.decode())

# b => send byte encoded
# CLRF (\r\n) => Carriage Return + Line Feed => end ftp command
cmd = f"USER {ftp_user}\r\n"
sock.sendall(cmd.encode())

response = sock.recv(4096)
if isVerbose:
    print("Server says:", response.decode())

cmd = f"PASS {ftp_pass}\r\n"
sock.sendall(cmd.encode())

response = sock.recv(4096)
print(response.decode())

sock.close()


