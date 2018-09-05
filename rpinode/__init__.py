import socket, time
from .service import RpiNode, DiscoverCatcher

class App():
    counter = 0
    host = None
    port = 32001

    def __init__(self):
        self.catcher = DiscoverCatcher()

    def run(self):
        while True:
            self.host = self.catcher.catchIP()
            
            if self.host is not None:
                self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))

                node = RpiNode(self.sock)
                node.start()

                try:
                    while True:
                        print('sending')
                        self.sock.send("%s:%d" % (socket.gethostname(), self.counter))
                        self.counter += 1
                        time.sleep(2)

                except socket.error:
                    self.sock.close()
    