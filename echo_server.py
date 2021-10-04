import socket
import os

HOST,PORT = tuple(os.sys.argv[1:3])
##HOST = '172.22.156.167'  # Standard loopback interface address (localhost)
##PORT = 1234        # Port to listen on (non-privileged ports are > 1023)
PORT = int(PORT)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
