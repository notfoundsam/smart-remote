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

    first_request = None
    node_sevice = None
    discover_service = None

    def activateDiscoverService(self):
        self.discover_service = DiscoverService()
        self.discover_service.start()
    
    def activateNodeService(self):
        self.node_sevice = NodeService()
        self.node_sevice.start()

    def generateFirstRequest(self):
        if self.first_request is None:
            self.first_request = FirstRequest()
            self.first_request.start()

class FirstRequest(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        time.sleep(2)
        r = requests.get('http://127.0.0.1:5000/')

class DiscoverService(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        sys.stderr.write('Starting the discover service\n')
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while True:
            message = "s-hostname:%s" % socket.gethostname()
            sock.sendto(message, ('255.255.255.255', 32000))
            time.sleep(5)

class NodeService(threading.Thread):

    nodes = {}

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr
        self.hostname = None
        self.service = Service.Instance()

    def getHostName(self):
        return self.hostname

    def pushButton(self, event):
        try:
            data = json.dumps({'event': 'pb', 'user_id': event.user_id, 'button_id': event.button_id})
            self.conn.send(data)
        except:
            self.service.node_sevice.removeNode(self)

    def run(self):
        sys.stderr.write('New connection from %s\n' % self.addr[0])

        while True:
            try:
                data = self.conn.recv(1024)
                
                if data:
                    udata = data.decode("utf-8")
                    splited_data = data.split(':')
                    
                    if self.hostname == None:
                        self.hostname = splited_data[0]
                        
                        if self.service.node_sevice.addNode(self) == False:
                            sys.stderr.write('hostname already exists\n')
                            self.conn.close()
                            break;
                    else:
                        sp = SocketParser(self.hostname, udata)
                        sp.start()
                else:
                    self.service.node_sevice.removeNode(self)
                    self.conn.close()
                    sys.stderr.write('Connection closed for %s\n' % self.addr[0])
                    break
            except:
                self.service.node_sevice.removeNode(self)
                self.conn.close()
                sys.stderr.write('Socket error, close connection\n')
                break

class SocketParser(threading.Thread):

    def __init__(self, hostname, data):
        threading.Thread.__init__(self)
        self.hostname = hostname
        self.data = data
        
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
            sys.stderr.write('%s\n' % dump)
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.connect(('192.168.100.100', 9090))
            sock.send(dump)

    def parseMessage(data):
        message = {}

        return message
