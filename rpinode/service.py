import threading, socket
from app.models import Radio

class DiscoverCatcher():

    def catchIP(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('', 32000))

        data, addr = sock.recvfrom(1024)
        data = data.split(':')
        host = data[1]
        sock.close()

        # Check if IPv4 is valid
        try:
            socket.inet_aton(host)
            return host

        except socket.error:
            return None

class RpiNode(threading.Thread):

    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        print('Strat listening')

        try:
            while True:
                data = self.sock.recv(1024)
                
                if data:
                    udata = data.decode("utf-8")
                    print('received: ' + udata)
                    
                else:
                    self.sock.close()
                    print('Connection closed')
                    break

        except socket.error:
            self.sock.close()
