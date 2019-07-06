#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, thread

def send (conn, addr):
    print("New connection from " + addr[0])

    while True:
        data = conn.recv(1024)
    
        if data:
            udata = data.decode("utf-8")
            print udata
            conn.send(data.upper())
        else:
            conn.close()
            print("Connection closed for " + addr[0])
            break

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 9090))
sock.listen(5)

try:
    while 1:
        conn, addr = sock.accept()
        thread.start_new_thread(send, (conn,addr))
        

except KeyboardInterrupt:
    conn.close()
