import os, socket
thisnode_name,logger_ip,logger_port = tuple(os.sys.argv[1:4])

# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# now connect to the web server on port 80 - the normal http port
s.connect((logger_ip, int(logger_port)))

def send_msg(msg):
    msg=msg.encode('utf-8')
    totalsent = 0
    while totalsent < len(msg):
        sent = s.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("socket connection broken")
        totalsent = totalsent + sent


send_msg(str(thisnode_name)+'\n')

#read from generate.py


for msg in os.sys.stdin:
    print(msg,end = '')
    send_msg(msg)

s.close()
