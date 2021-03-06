import os, socket
import time
import threading
import sys
import selectors
import types
import matplotlib.pyplot as plt
import numpy


def print_info():
    print("parse_str_map:",parse_str_map,'\n')
    print("msg_replied:",msg_replied,'\n')
    print("pending_msg:",pending_msg,'\n')
    print("to_send_msg:",to_send_msg,'\n')
    print("delivered_msg:",delivered_msg,'\n')
    
def client_func():
    def send_msg():
        if len(to_send_msg) == 0:
            return
        send_msg_len = len(to_send_msg)
        tmp_send_list = to_send_msg[:send_msg_len]
        for i in range(send_msg_len):
            del to_send_msg[0]
        for elm in tmp_send_list:

            if elm[0] == "Multicast":
                multicast(elm[1]+"#")
            else:
                unicast(elm[1]+"#", elm[0])
                
    def multicast(msg):
        for node_id in range(connect_num):
            if not connected[node_id]:
                continue
            unicast(msg, node_id)

        return
    
    def unicast(msg,node_id):
        global datacnt
        if not isinstance(i, int):
            return
        if connected[node_id] == False:
            return
        msg=msg.encode('utf-8')
        totalsent = 0
        while totalsent < len(msg):
            s = socket_list[node_id]
            try:
                sent = s.send(msg[totalsent:])
                datacnt += sys.getsizeof(sent)
                if sent == 0:
                    raise RuntimeError("socket connection broken")
                totalsent = totalsent + sent
            except:
                connected[node_id] = False
                break
            
            
    global self_node_name   

    while True:
        send_msg()
        time.sleep(0.001)

    return
    
def establish_connection(node_id):
    if(connected[node_id]):
        return

    host_ip = ip_list[node_id]
    port = port_list[node_id]
    port = int(port)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1)
    socket_list[node_id] = s
    while True:
        try:
            s.connect((host_ip, port))
            connected[node_id] = True
            break
        except:
            time.sleep(0.1)
            continue
    return


def server_func():
    #a many to one receive function
    #refer to python socket tutorial:
    #https://realpython.com/python-sockets/#multi-connection-client-and-server
    #https://github.com/realpython/materials/blob/master/python-sockets-tutorial/multiconn-server.py
    global self_port, end_of_program
    global received_msg
    sel = selectors.DefaultSelector()
    def accept_func(sock):
        conn, addr = sock.accept() 
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        sel.register(conn, events, data=data)


    def process_connection(key, mask):
        global datacnt, received_msg,receive_mtx
        data = key.data
        s = key.fileobj
        if mask & selectors.EVENT_READ:
            info = []
            recv_data = s.recv(2048)
            if not recv_data:
                sel.unregister(s)
                s.close()
            else:
                data.outb += recv_data

                lines = data.outb.split(b'#')
                data.outb = lines[-1]
                info = lines[:-1]
            
##            info = recv_data.decode('utf-8')
##Received info are merged, modify here
            
            for elm in info:
                elm = elm.decode('utf-8')
                if len(elm) < 3:
                    continue
                
                if len(elm.split('|')) < 5:
                    print("    Received:"+elm)
                    for i in range(50):
                        print(" ********************************")

                on_receiving(elm)
                datacnt += sys.getsizeof(elm)


    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', self_port))
    sock.listen()
    sock.setblocking(False)
    sel.register(sock, selectors.EVENT_READ, data=None)

    while True:
        if end_of_program:
            break
        elm = sel.select(timeout=None)
        for key, mask in elm:
            if key.data:
                process_connection(key, mask)
            else:
                accept_func(key.fileobj)
                
    sock.close()
    sel.close()


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
            socket_list.append("")




def process_to_send(msg):
    global connect_num,sequence_num
    global msg_replied,pending_msg
    
    req_pack_str = pack_msg(msg)
    parse_str = parse_msg(req_pack_str)
    dict_key = remove_sender(parse_str)
    msg_replied[dict_key] = connect_num*[False]
    proposed_priority = give_priority(req_pack_str)
    sequence_num+=1
    
    parse_str_map[dict_key] = [proposed_priority, "undelivered"]
    pending_msg.append([proposed_priority, "undelivered", req_pack_str])
    organize_pending()
    to_send_msg.append(("Multicast", req_pack_str))
    
def on_receiving(msg):
    if len(msg)<5:
        return
    global sequence_num,self_node_name
    msg_type = give_type(msg)
    if msg_type not in [0,1,2]:
        return
    
    parse_str = parse_msg(msg)
    msg_priority = give_priority(msg)
    msg_priority = round(msg_priority,1)
    sender_id = give_sender_id(msg)
    dict_key = remove_sender(parse_str)
    if msg_type == 0:
        
        my_priority = sequence_num+0.1*int(self_node_name[-1])
        my_priority = round(my_priority,1)
        
        proposed_priority = max(msg_priority, my_priority)
        if dict_key in parse_str_map:
            return
                
        parse_str_map[dict_key] = [proposed_priority, "undelivered"]
        pending_msg.append([proposed_priority, "undelivered", msg])
        sequence_num += 1
        send_back_str = pack_send_back_msg(parse_str, proposed_priority)
        send_back_str = msg_set_sender(send_back_str, self_node_name)
        to_send_msg.append((sender_id, send_back_str))
    elif msg_type == 1:
        if dict_key not in msg_replied:
            return
        msg_replied[dict_key][sender_id] = True
        new_priority = max(msg_priority, parse_str_map[dict_key][0])        
        original_priority = parse_str_map[dict_key][0]
        parse_str_map[dict_key][0] = new_priority
        i_flag = 0
        for i in range(len(pending_msg)):
            if pending_msg[i][0] == original_priority:
                pending_msg[i][0] = new_priority
                i_flag = i
                break

        candeliver = False
        if False not in msg_replied[dict_key]:
            candeliver = True
        if connected.count(False) == 1:
            err_id = connected.index(False)
            if msg_replied[dict_key][err_id] == False:
                candeliver = True
        if candeliver:
            parse_str_map[dict_key][1] = "delivered"
            pending_msg[i_flag][1] = "delivered"
            organize_pack_str = pack_send_back_msg(parse_str, new_priority, 2)
            organize_pack_str = msg_set_sender(organize_pack_str, self_node_name)
            to_send_msg.append(("Multicast", organize_pack_str))
            time_diff.append(time.time()-float(dict_key.split('|')[0]))
            organize_pending()
    elif msg_type == 2:
        if dict_key not in parse_str_map:
            return
        original_priority = parse_str_map[dict_key][0]
        new_priority = msg_priority
        i_flag = 0
        for i in range(len(pending_msg)):
            if pending_msg[i][0] == original_priority:
                pending_msg[i][0] = new_priority
                i_flag = i
                break
        parse_str_map[dict_key] = [new_priority, "delivered"]
        pending_msg[i_flag][1] = "delivered"
        organize_pending()
    return


def remove_sender(parse_str):
    pos = parse_str.find('|')
    return parse_str[pos+1:]

def pack_send_back_msg(parse_str, priority, msg_type=1):
    back_msg = str(msg_type)+'|'+parse_str
    pos = back_msg.rfind('|')
    back_msg = back_msg[:pos+1] + str(priority)+'|'+back_msg[pos+1:]
    return back_msg

def msg_set_sender(msg, sender):
    back_msg = msg
    pos = back_msg.find('|')
    pos1 = back_msg.find('|',pos+1)
    back_msg = back_msg[:pos+1] + str(sender)+back_msg[pos1:]
    return back_msg

    
def organize_pending():
    #sort pending_msg, and pop out leading delivered msg to delivered_msg
    global pending_msg,delivered_seq_num
    pending_msg.sort()
    while len(pending_msg):
        i = 0
        if pending_msg[i][1]=="delivered":
            parse_str = parse_msg(pending_msg[i][2])
            delivered_priority = pending_msg[i][0]
            dict_key = remove_sender(parse_str)
            
            parse_str_map.pop(dict_key)
            if dict_key in msg_replied:
                msg_replied.pop(dict_key)
            delivered_msg.append(pending_msg[i][2].split('|')[-1])
            del pending_msg[i]
            continue
        else:
            if connected.count(False) == 1:
                err_id = connected.index(False)
                for j in range(len(pending_msg)):
                    parse_str = parse_msg(pending_msg[j][2])
                    delivered_priority = pending_msg[j][0]
                    dict_key = remove_sender(parse_str)
                    if dict_key not in msg_replied:
                        continue
                    msg_replied[dict_key][err_id] = True
                    priority = parse_str_map[dict_key][0]      
                    i_flag = 0
                    for k in range(len(pending_msg)):
                        if pending_msg[k][0] == priority:
                            i_flag = i
                            break
                    parse_str_map[dict_key][1] = "delivered"
                    pending_msg[i_flag][1] = "delivered"
                    organize_pack_str = pack_send_back_msg(parse_str, priority, 2)
                    organize_pack_str = msg_set_sender(organize_pack_str, self_node_name)
                    to_send_msg.append(("Multicast", organize_pack_str))
                return
            return

            
    
def pack_msg(msg, msg_type=0):
    global self_node_name,sequence_num
    priority_suffix = int(self_node_name[-1])
    priority = sequence_num+0.1*priority_suffix
    priority = round(priority,1)

    return str(msg_type)+'|'+self_node_name+'|'+str(time.time())+'|'+str(priority)+'|'+msg

def give_sender_id(msg):
    contents = msg.split('|')
    if len(contents) < 5:
        print("Err in give_sender function:"+msg)
        return -1
    sender = str(contents[1])
    return name_list.index(sender)

def give_priority(msg):
    contents = msg.split('|')
    if len(contents) < 5:
        print("Err in give_priority function:"+msg)
        return -1
    priority = float(contents[3])
    return priority

def give_type(msg):
    contents = msg.split('|')
    if len(contents) < 1:
        print("Err in give_type function:"+msg)
        return -1
    msg_type = int(contents[0])
    if msg_type in [0,1,2]:
        return msg_type
    print("Err in give_type function:"+msg)
    return -1

def parse_msg(msg):
    contents = msg.split('|')
    if len(contents) < 5:
        print("Err in parse_msg function:"+msg)
        return ""
    return contents[1]+'|'+contents[2]+'|'+contents[4]

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
            socket_list.append("")




def os_func():
    for osmsg in os.sys.stdin:
        osmsg_content = osmsg.split('\n')[0]
        process_to_send(osmsg_content)

def process_delivered():
    while True:
        if len(delivered_msg) == 0:
            continue
        delivered_msg_len = len(delivered_msg)
        delivered_list = delivered_msg[:delivered_msg_len]
        for i in range(delivered_msg_len):
            del delivered_msg[0]
        for d in delivered_list:
##            print("delivered:"+d)
            process_transaction(d)

def process_transaction(msg):
    if len(msg)<5:
        return
    success = False
    operation = msg.split(' ')[0]
    if operation == "DEPOSIT":
        _,account,amount = msg.split(' ')
        amount = int(amount)
        if not account in balance:
            balance[account] = 0
        balance[account] += amount
        success = True
    elif operation == "TRANSFER":
        _,account1,_,account2,amount = msg.split(' ')
        amount = int(amount)
        if account1 in balance:
            if balance[account1] >= amount:
                balance[account1] -= amount
                if not account2 in balance:
                    balance[account2] = 0
                balance[account2] += amount
                success = True
    if success:
        print_balance()

def print_balance():
    temp = []
    balance_cp = balance
    for acc in balance:
        temp.append((acc,balance[acc]))
    temp.sort()
    print("BALANCES ", end='')

    for elm in temp:
        print(str(elm[0])+":"+str(elm[1])+" ",end = '')
    print()




datacnt = 0
datacnt_list = []
time_diff = []
time_lag_list = []
balance = dict()
delivered_msg = []
received_msg = b''
receive_mtx = threading.Lock()

parse_str_map = dict()
msg_replied = dict()
pending_msg = []
sequence_num = 0
to_send_msg = []
delivered_msg = []

self_node_name = str(os.sys.argv[1])
self_port = int(os.sys.argv[2])
file_name = str(os.sys.argv[3])

connect_num = 0
name_list = []
ip_list = []
port_list = []
connected = []
socket_list = []
delivered_seq_num = 0
end_of_program = False

init("./"+file_name)


plt.ion()
fig = plt.figure()
ax2 = plt.subplot(111)
ax3 = ax2.twinx()
ax2.title.set_text("Bandwidth and Average Time Delay")
ax3.set_ylabel("Response time[s]", color='k')
ax2.set_ylabel("Bandwidth[bps]", color='k')
ax2.set_xlabel('Time elapsed[s]', color='k')
plot_time = []

cur_time = 0


try:
    
    receive_t = threading.Thread(target=server_func, args=())
    receive_t.start()

    for i in range(connect_num):
        connect_t = threading.Thread(target=establish_connection, args=(i,))
        connect_t.start()

    send_t = threading.Thread(target=client_func, args=())
    send_t.start()

    while True:
        if False not in connected:
            break
    print("Fully Connected...Start in 5 seconds...")
    time.sleep(5)
    if False not in connected:
        os_t = threading.Thread(target=os_func, args=())
        os_t.start()
        
        process_delivered_t = threading.Thread(target=process_delivered, args=())
        process_delivered_t.start()


        while True:
            #Plot
            time_lag = 0
            if len(time_diff):
                time_lag = round(sum(time_diff)/len(time_diff),2)
                time_diff = []
            time_lag_list.append(time_lag)
            datacnt_list.append(datacnt)
            plot_time.append(cur_time)
            datacnt = 0

            l1, = ax2.plot(plot_time, datacnt_list, color='g', label='Bandwidth[bps]')
            l2, = ax3.plot(plot_time, time_lag_list, color='b', label='Response time[s]')
            ax2.legend((l1,l2),('Bandwidth','Response time'),loc='upper right')

            plt.draw()
            cur_time+=1

            plt.pause(0.1)
            time.sleep(1)
            if plot_time[-1] % 10 == 0:
                plt.savefig(str(plot_time[-1]))


    time.sleep(500)
except KeyboardInterrupt:
    print("")
finally:
    for s in socket_list:
        end_of_program = True
        s.close()
