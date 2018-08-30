from __future__ import print_function
import serial
import time, random, socket, json
import array
import os, sys
import threading, Queue
import requests
from app import so

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

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 32001))
        sock.listen(5)

        while True:
            conn, addr = sock.accept()
            node = RpiNode(conn, addr)
            node.start()

class RpiNode(threading.Thread):

    def __init__(self, conn, addr):
        threading.Thread.__init__(self)
        self.conn = conn
        self.addr = addr

    def run(self):
        print('New connection from ' + self.addr[0], file=sys.stderr)

        try:
            while True:
                data = self.conn.recv(1024)
                
                if data:
                    udata = data.decode("utf-8")
                    print('received: ' + udata, file=sys.stderr)
                    self.conn.send(data.upper())
                else:
                    self.conn.close()
                    print('Connection closed for ' + self.addr[0], file=sys.stderr)
                    break
        except:
            conn.close()
