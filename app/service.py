from __future__ import print_function
import serial
import time, random, socket, json
import array
import os, sys
import threading, Queue
import requests
import helpers

class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.

    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.

    To get the singleton instance, use the `Instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.

    """

    def __init__(self, decorated):
        self._decorated = decorated

    def Instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.

        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@Singleton
class Service():
    fr = None
    node_sevice = None

    def activateDiscoverService(self):
        dservice = DiscoverService()
        dservice.start()
    
    def activateNodeService(self):
        self.node_sevice = NodeService()
        self.node_sevice.start()

    def generateFirstRequest(self):
        if self.fr is None:
            self.fr = FirstRequest()
            self.fr.start()

class FirstRequest(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        time.sleep(2)
        r = requests.get('http://127.0.0.1:5000/')
        print('Send first request to flask', file=sys.stderr)

class DiscoverService(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            message = "s-ip:%s" % socket.gethostbyname(socket.gethostname())
            sock.sendto(message, ('255.255.255.255', 32000))
            time.sleep(5)

class NodeService(threading.Thread):

    nodes = {}

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        time.sleep(2)
        sock.bind(('', 32001))
        sock.listen(5)

        while True:
            conn, addr = sock.accept()
            node = RpiNode(conn, addr)
            node.start()
    
    def addNode(self, node):
        nh = helpers.NodeHelper()
        host_name = node.getHostName()
        
        if host_name in self.nodes:
            print(self.nodes, file=sys.stderr)
            return False

        if nh.getNodeByName(host_name) is None:
            node = nh.createNode({'name': None, 'host_name': host_name, 'order': None})
            print(node, file=sys.stderr)

        self.nodes[host_name] = node
        print(self.nodes, file=sys.stderr)
        return True

    def pushToNode(self, host_name, button_id):
        if host_name in self.nodes:
            self.nodes[host_name].pushButton(button_id)
            return True
            # print(self.nodes[host_name], file=sys.stderr)
        else:
            print("no node", file=sys.stderr)
            return False

    def removeNode(self, node):
        if node.getHostName() in self.nodes:
            del self.nodes[node.getHostName()]
            print(self.nodes, file=sys.stderr)

class RpiNode(threading.Thread):

    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.hostname = None
        self.service = Service.Instance()

    def getHostName(self):
        return self.hostname

    def pushButton(self, button_id):
        try:
            self.conn.send('pb:%r' % button_id)
        except:
            self.service.node_sevice.removeNode(self)

    def run(self):
        print('New connection from ' + self.addr[0], file=sys.stderr)

        try:
            while True:
                data = self.conn.recv(1024)
                
                if data:
                    udata = data.decode("utf-8")
                    splited_data = data.split(':')
                    print('received: ' + udata, file=sys.stderr)
                    
                    if self.hostname == None:
                        self.hostname = splited_data[0]
                        
                        if self.service.node_sevice.addNode(self) == False:
                            print('hostname already exists', file=sys.stderr)
                            self.conn.close()
                            break;
                    self.conn.send(data.upper())
                else:
                    self.service.node_sevice.removeNode(self)
                    self.conn.close()
                    print('Connection closed for ' + self.addr[0], file=sys.stderr)
                    break
        except:
            self.service.node_sevice.removeNode(self)
            self.conn.close()
