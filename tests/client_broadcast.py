import socket, thread

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(('', 9090))

try:
    while True:
        data, addr = s.recvfrom(1024)
        print("New connection from " + addr[0])
        print("received message: %s" % data)

except KeyboardInterrupt:
    s.close()
    print("exit")
