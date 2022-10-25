from socket import *
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(("127.0.0.1", 55556))
data = sock.recv(1024)
