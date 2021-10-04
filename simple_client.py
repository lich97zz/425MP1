import os, socket
import time
import threading
import sys
import selectors
import types

#run on vm1 172.22.156.167 port=1234, send to vm2 172.22.158.167 port=1235

def client_func():
    #one to many send
    def multicast(msg):
##        print("init a multicast\n")
        for node_id in range(connect_num):
            if not connected[node_id]:
                continue
            send_msg(msg, node_id)
        return
    
    def send_msg(msg,node_id):
        print("To:"+str(node_id)+msg)
        msg=msg.encode('utf-8')
        totalsent = 0
        while totalsent < len(msg):
            s = socket_list[node_id]
            sent = s.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent
            
    global self_node_name   
    msg_index = 0
    while True:
        multicast("<"+self_node_name+"> sending msg #"+str(msg_index))
        time.sleep(1)
        msg_index += 1
    return
    
def establish_connection(node_id):
    if(connected[node_id]):
        return

    host_ip = ip_list[node_id]
    port = port_list[node_id]
    port = int(port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    socket_list[node_id] = s
    while True:
        try:
            print("Sending connection req to:"+host_ip+" "+str(port)+'\n')
            s.connect((host_ip, port))
            print("***Connected to "+name_list[node_id])
            connected[node_id] = True
            break
        except:
            print("...Can't connect to "+name_list[node_id]+", reconnect soon...\n")
            time.sleep(2)
            continue
    return
    
def server_func():
    global connect_num
    for i in range(connect_num):
        server_single_t = threading.Thread(target=server_func_single, args=(i,))
        server_single_t.start()
        
def server_func_single(node_id):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('',port_list[node_id]))
    print("trying to bind:"+str(port_list[node_id])+"\n")
    s.listen()
    conn, addr = s.accept()
    rec_socket_list[node_id] = s
    with conn:
        rec_connected[node_id] = True
        print("Connected by", addr)
        while True:
            data = conn.recv(1024)
            print("Received from "+str(addr)+":"+data.decode("utf-8"))
            if not data:
                break
            
        
    
def init(file_name):
    global connect_num
    with open(file_name, 'r') as f:
        connect_num = int(f.readline().split('\n')[0])
        for elm in f.readlines():
            if len(elm) <= 2:
                continue
            node_name, node_ip, node_port = elm.split(' ')
            name_list.append(str(node_name))
            ip_list.append(str(node_ip))
            port_list.append(int(node_port))
            connected.append(False)
            rec_connected.append(False)
            socket_list.append("")
            rec_socket_list.append("")


##file_name = str(os.sys.argv[1])
file_name = "config_vm1"
connect_num = 0
name_list = []
ip_list = []
port_list = []
connected = []
rec_connected = []
socket_list = []
rec_socket_list = []

init("./"+file_name)
tmp_list = []
for i in range(connect_num+1):
    n_name = "node"+str(i+1)
    if n_name not in name_list:
        tmp_list.append(n_name)
self_node_name = str(tmp_list[0])


for i in range(connect_num):
    connect_t = threading.Thread(target=establish_connection, args=(i,))
    connect_t.start()

send_t = threading.Thread(target=client_func, args=())
send_t.start()

receive_t = threading.Thread(target=server_func, args=())
receive_t.start()

