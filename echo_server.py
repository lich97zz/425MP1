import socket
import os

HOST,PORT = tuple(os.sys.argv[1:3])
##HOST = '172.22.156.167'  # Standard loopback interface address (localhost)
##PORT = 1234        # Port to listen on (non-privileged ports are > 1023)
PORT = int(PORT)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()
while True:
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            stringdata = data.decode('utf-8')
            print("Received:",stringdata)
            if not data:
                break
            data = stringdata.encode('utf-8')
            conn.sendall(data)
