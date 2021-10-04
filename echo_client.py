import socket
import os

HOST,PORT = tuple(os.sys.argv[1:3])

##HOST = '172.22.158.167'  # The server's hostname or IP address
##PORT = 1234  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, world')
    data = s.recv(1024)

print('Received', repr(data))
