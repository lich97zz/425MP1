import time

def process_delivered():
    #process according to delivered_msg
    return

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
        organize_pending()
        sequence_num += 1
        send_back_str = pack_send_back_msg(parse_str, proposed_priority)
        send_back_str = msg_set_sender(send_back_str, self_node_name)
        to_send_msg.append((sender_id, send_back_str))
    elif msg_type == 1:
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
        if False not in msg_replied[dict_key]:
            parse_str_map[dict_key][1] = "delivered"
            pending_msg[i_flag][1] = "delivered"
            organize_pack_str = pack_send_back_msg(parse_str, new_priority, 2)
            organize_pack_str = msg_set_sender(organize_pack_str, self_node_name)
            to_send_msg.append(("Multicast", organize_pack_str))
            #record diff_time for graph and plot
        organize_pending()
    elif msg_type == 2:
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

        #record diff_time for graph and plot
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
    global pending_msg
    pending_msg.sort()
    for i in range(len(pending_msg)):
        if i >= len(pending_msg):
            return
        if pending_msg[i][1]=="delivered":
            parse_str = parse_msg(pending_msg[i][2])
            dict_key = remove_sender(parse_str)
            parse_str_map.pop(dict_key)
            if dict_key in msg_replied:
                msg_replied.pop(dict_key)
            delivered_msg.append(pending_msg[i][2].split('|')[-1])
            del pending_msg[i]
            i-=1
            
    
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

def print_info():
    print("parse_str_map:",parse_str_map,'\n')
    print("msg_replied:",msg_replied,'\n')
    print("pending_msg:",pending_msg,'\n')
    print("to_send_msg:",to_send_msg,'\n')
    print("delivered_msg:",delivered_msg,'\n')

parse_str_map = dict()
msg_replied = dict()
pending_msg = []
sequence_num = 0
to_send_msg = []
delivered_msg = []

file_name = "config_vm2"
self_port = 1234
connect_num = 0
name_list = []
ip_list = []
port_list = []
connected = []
socket_list = []

init("./"+file_name)

tmp_list = []
for i in range(connect_num+1):
    n_name = "node"+str(i+1)
    if n_name not in name_list:
        tmp_list.append(n_name)
self_node_name = str(tmp_list[0])