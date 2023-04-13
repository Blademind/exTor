import time
from socket import *
from random import randbytes


def build_conn_req():
    """Builds udp tracker request"""
    message = bytes.fromhex('00 00 04 17 27 10 19 80')  # connection_id (set id 41727101980)
    message += (0).to_bytes(4, byteorder='big')  # action - connect
    message += randbytes(4)  # transaction_id
    return message


sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(("0.0.0.0", 1234))
sock.sendto(build_conn_req(), (gethostbyname("9.rarbg.me"), 2980))

data = sock.recv(1024)
conn_id = data[8:]
tran_id = data[4:8]

print(data)