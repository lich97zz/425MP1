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
            print("Received:"+stringdata)
            if not data:
                break
            data = stringdata.encode('utf-8')
            conn.sendall(data)

##
##def cli_node_handler(clientsocket,address):
##
##    def msg_iter():
##        global datacnt
##        buffer=b''
##        while True:
##            received = clientsocket.recv(1024)
##            
##            with datacnt_mtx:
##                datacnt += len(received)
##            
##            buffer += received
##                
##            if not buffer:
##                break
##            else:
##                lines = buffer.split(b'\n')
##                buffer=lines[-1]
##                
##                for i in lines[0:-1]:
##                    yield i.decode('utf-8')
##        clientsocket.close()
##    
##    msgs=msg_iter()
##    nodename=next(msgs)

    

        
        with msg_storage_mtx:
            msg_storage.append((cli_time,recv_time,event_hash))

    with print_mtx:
        print("%s - %s disconnected" % (time.time(), nodename))
