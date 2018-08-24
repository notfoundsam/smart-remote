import socket, time

s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

try:
    while True:
        message = "s-ip:%s" % socket.gethostbyname(socket.gethostname())
        s.sendto(message, ('255.255.255.255', 9090))
        print("sent")
        time.sleep(5)

except KeyboardInterrupt:
    s.close()
