import socket, thread, time

counter = 0

def receving (sock):
    while True:
        recvmsg = sock.recv(1024)
        print recvmsg.decode("utf-8")

host = socket.gethostbyname(socket.gethostname())
port = 0

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("192.168.100.50",9090))

thread.start_new_thread(receving, (s,))

try:
    while True:
        s.send("client 2 : %d" % counter)
        counter += 1
        time.sleep(1)

except KeyboardInterrupt:
    s.close()

