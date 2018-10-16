#!/usr/bin/env python3
import os, sys, json, time
import threading, socket

class DiscoverService(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        sys.stderr.write('Starting the discover service\n')
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            message = "s-hostname:%s" % socket.gethostname()
            sock.sendto(message.encode(), ('255.255.255.255', 32000))
            time.sleep(5)

class RpiNode(threading.Thread):

    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.hostname = None

    def getHostName(self):
        return self.hostname

    def pushButton(self, event):
        try:
            data = json.dumps({'event': 'pb', 'user_id': event.user_id, 'button_id': event.button_id})
            self.conn.send(data)
        except:
            pass
            # self.service.node_sevice.removeNode(self)

    def run(self):
        sys.stderr.write('New connection from %s\n' % self.addr[0])

        while True:
            try:
                data = self.conn.recv(1024)
                
                if data:
                    udata = data.decode()
                    splited_data = udata.split(':')
                    
                    if self.hostname == None:
                        self.hostname = splited_data[0]
                        
                        # if self.service.node_sevice.addNode(self) == False:
                        #     sys.stderr.write('hostname already exists\n')
                        #     self.conn.close()
                        #     break;
                    else:
                        pass
                        # sp = SocketParser(self.hostname, udata)
                        # sp.start()
                else:
                    # self.service.node_sevice.removeNode(self)
                    self.conn.close()
                    sys.stderr.write('Connection closed for %s\n' % self.addr[0])
                    break
            except Exception as e:
                # self.service.node_sevice.removeNode(self)
                self.conn.close()
                sys.stderr.write('Socket error, close connection\n')
                break

if __name__ == '__main__':
    sys.stderr.write('OK--------------------------\n')
    # discover_service = DiscoverService()
    # discover_service.start()
    sys.stderr.write('OK2222--------------------------\n')

    sys.stderr.write('Start\n')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sys.stderr.write('Start1\n')
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sys.stderr.write('Start2\n')
    sock.bind(('', 32001))        
    sys.stderr.write('Start3\n')
    sock.listen(5)
    sys.stderr.write('Start4\n')

    while True:
        sys.stderr.write('Bef\n')
        conn, addr = sock.accept()
        sys.stderr.write('Aft\n')
    #     node = RpiNode(conn, addr)
    #     node.start()
