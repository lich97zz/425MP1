import os, socket
servers = [] 

for port in portlist:
    ds = ("0.0.0.0", port)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(ds)
    server.listen(1)

    servers.append(server)

while True:
    # Wait for any of the listening servers to get a client
    # connection attempt
    readable,_,_ = select.select(servers, [], [])
    ready_server = readable[0]

    connection, address = ready_server.accept()
