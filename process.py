import os
import threading

def os_func():
    for osmsg in os.sys.stdin:
        print(osmsg,end = '')
        osmsg_content = osmsg.split('\n')[0]
        print("info:"+osmsg_content)
        #process_to_send(osmsg_content)
        delivered_msg.append(osmsg_content)

def process_delivered():
    while True:
        if not len(delivered_msg):
            continue
        delivered_msg_len = len(delivered_msg)
        delivered_list = delivered_msg[:delivered_msg_len]
        for i in range(delivered_msg_len):
            del delivered_msg[0]
        for d in delivered_list:
            process_transaction(d)

def process_transaction(msg):
    if len(msg)<6:
        return
    success = False
    operation = msg.split(' ')
    if operation == "DEPOSIT":
        _,account,amount = msg.split(' ')
        if not account in balance:
            balance[account] = 0
        balance[account] += amount
        success = True
    elif operation == "TRANSFER":
        _,account1,_,account2,amount = msg.split(' ')
        if account1 in balance:
            if balance[account1] >= amount:
                balance[account1] -= amount
                if not account2 in balance:
                    balance[account2] = 0
                balance[account2] -= amount
                success = True
    if success:
        print_balance()

def print_balance():
    print("BALANCES ")
    for acc in balance:
        print(str(acc)+":"+str(balance[acc])+" ",end = '')

print("aa")  
balance = dict()
delivered_msg = []

os_t = threading.Thread(target=os_func, args=())
os_t.start()

process_delivered_t = threading.Thread(target=process_delivered, args=())
process_delivered_t.start()
print("bb")
