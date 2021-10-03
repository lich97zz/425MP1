import os, socket
import time
#run on VM1
node_ip = "172.22.158.167"
port = 1234

#connect
while 1:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((node_ip, int(port)))
        break
    except:
        print("Connection failed, sleep an try again soon...")
        time.sleep(1)
        continue
    


def send_msg(msg):
    msg=msg.encode('utf-8')
    totalsent = 0
    while totalsent < len(msg):
        sent = s.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent

while 1:
    send_msg('sending msg...\n')
    time.sleep(1)
##for msg in os.sys.stdin:
##    print(msg,end = '')
##    send_msg(msg)

s.close()
