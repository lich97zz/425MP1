import os, socket
import matplotlib.pyplot as plt
import numpy
import time
##thisnode_name,logger_ip,logger_port = tuple(os.sys.argv[1:4])
### node node1 10.0.0.1 1234
### create an INET, STREAMing socket
##s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
### now connect to the web server on port 80 - the normal http port
##s.connect((logger_ip, int(logger_port)))
##
##def send_msg(msg):
##    msg=msg.encode('utf-8')
##    totalsent = 0
##    while totalsent < len(msg):
##        sent = s.send(msg[totalsent:])
##        if sent == 0:
##            raise RuntimeError("socket connection broken")
##        totalsent = totalsent + sent
##
##
##send_msg(str(thisnode_name)+'\n')

#read from generate.py
datacnt_list = []
time_lag_list = []


plt.ion()
fig = plt.figure()
ax2 = plt.subplot(111)
ax3 = ax2.twinx()
ax2.title.set_text("Bandwidth and Average Time Delay")
ax3.set_ylabel("Response time[ms]", color='k')
ax2.set_ylabel("Bandwidth[bps]", color='k')
ax2.set_xlabel('Time elapsed[s]', color='k')
plot_time = []

cur_time = 0
while True:
    l1, = ax2.plot(plot_time, datacnt_list, color='g', label='Bandwidth[bps]')
    l2, = ax3.plot(plot_time, time_lag_list, color='b', label='Response time[s]')
    ax2.legend((l1,l2),('Bandwidth','Response time'),loc='upper right')

    plt.draw()
    cur_time+=1
    plot_time.append(cur_time)
    datacnt_list.append(50-cur_time)
    time_lag_list.append(0.25+cur_time*0.01)
    plt.pause(0.1)
    time.sleep(1)
    if plot_time[-1] % 10 == 0:
        plt.savefig(str(plot_time[-1]))



