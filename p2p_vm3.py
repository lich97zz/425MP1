import os, socket
import time
import threading

#send to vm1 172.22.156.167 port=1234, run on vm2 172.22.158.167 port=1235
def client_func():
    #send
    def send_msg(msg):
        msg=msg.encode('utf-8')
        totalsent = 0
        while totalsent < len(msg):
            sent = s.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
    host_ip = "172.22.156.167"
    port = 1234
    port = int(port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host_ip, port))
##    while True:
##        try:
##            s.connect((host_ip, port))
##            break
##        except:
##            print("Can't connect to node 1, reconnect in 1 second...\n")
##            time.sleep(1)
##            continue

    msg_index = 0
    while True:
        send_msg('<VM3>:sending message with index:'+str(msg_index)+' \n')
        time.sleep(2)

    s.close()


def server_func():
    #receive
##    host_ip = '172.22.156.167'  # Standard loopback interface address (localhost)
    port = 1234        # Port to listen on (non-privileged ports are > 1023)
    port = int(port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by node 1 '+addr+"\n")
        while True:
            data = conn.recv(1024)
            data_content = data.decode('utf-8')
            print("received from node 1:"+data_content+"\n")
            if not data:
                break


receive_t = threading.Thread(target=server_func, args=())
receive_t.start()



##send_t = threading.Thread(target=client_func, args=())
##send_t.start()

