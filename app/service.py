from __future__ import print_function
import serial
import time, random, socket, json
import array
import os, sys
import threading
from app import helpers

class Service():

    def __init__(self, config):
        self.config = config
        self.first_request = None
        self.node_sevice = None
        self.discover_service = None

    def activateDiscoverService(self):
        self.discover_service = DiscoverService(self.config)
        self.discover_service.start()
    
    def activateNodeService(self):
        self.node_sevice = NodeService(self.config)
        self.node_sevice.start()

class DiscoverService(threading.Thread):

    def __init__(self, config):
        self.config = config
        threading.Thread.__init__(self)

    def run(self):
        sys.stderr.write('Starting the discover service\n')
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            message = "s-hostname:%s" % socket.gethostname()
            sock.sendto(message.encode(), (self.config.BROADCAST_MASK, self.config.BROADCAST_PORT))
            time.sleep(self.config.BROADCAST_INTERVAL)

class NodeService(threading.Thread):

    nodes = {}

    def __init__(self, config):
        self.config = config
        threading.Thread.__init__(self)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.config.SOCKET_BIND_ADDRESS, self.config.SOCKET_BIND_PORT))        
        sock.listen(self.config.SOCKET_CONNECTIONS)

        while True:
            conn, addr = sock.accept()
            node = RpiNode(self, conn, addr)
            node.start()
    
    def addNode(self, node):
        nh = helpers.NodeHelper()
        host_name = node.getHostName()
        
        if host_name in self.nodes:
            return False

        if nh.getNodeByName(host_name) is None:
            node = nh.createNode({'name': None, 'host_name': host_name, 'order': None})

        self.nodes[host_name] = node
        return True

    def pushToNode(self, event):
        if event.host_name in self.nodes:
            self.nodes[event.host_name].pushButton(event)
            return True
        else:
            sys.stderr.write('no node\n')
            return False

    def removeNode(self, node):
        if node.getHostName() in self.nodes:
            del self.nodes[node.getHostName()]

class RpiNode(threading.Thread):

    def __init__(self, service, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.hostname = None
        self.service = service

    def getHostName(self):
        return self.hostname

    def pushButton(self, event):
        try:
            data = json.dumps({'event': 'pb', 'user_id': event.user_id, 'button_id': event.button_id})
            self.conn.send(data.encode())
        except Exception as e:
            self.conn.close()
            self.service.removeNode(self)

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
                        
                        if self.service.addNode(self) == False:
                            sys.stderr.write('hostname already exists\n')
                            self.conn.close()
                            break;
                    else:
                        sp = SocketParser(self, udata)
                        sp.start()
                else:
                    self.service.removeNode(self)
                    self.conn.close()
                    sys.stderr.write('Connection closed for %s\n' % self.addr[0])
                    break
            except Exception as e:
                self.service.removeNode(self)
                self.conn.close()
                sys.stderr.write('Socket error, close connection\n')
                break

class SocketParser(threading.Thread):

    def __init__(self, rpi_node, data):
        threading.Thread.__init__(self)
        self.hostname = rpi_node.hostname
        self.data = data
        self.service = rpi_node.service
        
    def run(self):
        data = json.loads(self.data)

        if 'type' in data and data['type'] == 'response':
            sys.stderr.write('%s received: %s\n' % (self.hostname, self.data))
        elif 'type' in data and data['type'] == 'event':
            sensors_data = dict(s.split(' ') for s in data['message'].split(','))
            params = {}
            tags = {'hostname': self.hostname}

            if 'h' in sensors_data:
                params['humiValue'] = float(sensors_data['h'])
            if 't' in sensors_data:
                params['tempValue'] = float(sensors_data['t'])
            if 'b' in sensors_data:
                params['batValue'] = float(sensors_data['b'])
            
            if 'port' in data:
                tags['port'] = data['port']
            if 'r' in sensors_data:
                tags['radio'] = '0x%s' % sensors_data['r']

            message = [params, tags]
            dump = '%s\n' % json.dumps(message)
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.connect((self.service.config.NODE_RED_HOST, self.service.config.NODE_RED_PORT))
            sock.send(dump.encode())

    def parseMessage(data):
        message = {}

        return message
