import socket
import os
import time

HOST,PORT = tuple(os.sys.argv[1:3])
PORT = int(PORT)
##HOST = '172.22.158.167'  # The server's hostname or IP address
##PORT = 1234  # The port used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def send_msg(msg):
    msg=msg.encode('utf-8')
    totalsent = 0
    while totalsent < len(msg):
        sent = s.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent


while True:
    send_msg("send a msg")
    data = s.recv(1024)
    print('Received'+repr(data).decode('utf-8'))
    time.sleep(1)
    
