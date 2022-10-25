import _thread
import os.path
import pickle
import threading
import time
from random import randbytes
from socket import *

import select

from torrents_handler import info_torrent


def build_error_response(msg):
    message = (3).to_bytes(4, byteorder='big')  # action - connect
    message += randbytes(4)  # transaction_id
    message += msg.encode()
    return message


class TrackerTCP:
    def __init__(self):
        self.server_sock = None  # udp sock
        self.init_tcp_sock()
        self.__BUF = 1024
        self.read_tcp, self.write_tcp = [self.server_sock], []  # read write for select udp

        threading.Thread(target=self.listen_tcp).start()

    def init_tcp_sock(self):
        self.server_sock = socket(AF_INET, SOCK_STREAM)
        self.server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_sock.bind(("0.0.0.0", 55556))
        self.server_sock.listen(5)

    def get_ip_port(self):
        return gethostbyname(gethostname()), self.server_sock.getsockname()[1]

    def listen_tcp(self):
        while 1:
            readable, writeable, ex = select.select(self.read_tcp, self.write_tcp, [])
            for sock in readable:
                if sock == self.server_sock:
                    conn, addr = self.server_sock.accept()
                    print(f"Connection from {addr}")
                    conn.settimeout(5.0)
                    readable.append(conn)
                else:
                    try:
                        data = sock.recv(self.__BUF)
                        if not data:
                            readable.remove(sock)
                            break
                    except:
                        readable.remove(sock)
                        break
                    datacontent = data.decode()
                    if datacontent == "START":
                        threading.Thread(target=self.recv_files, args=(sock, )).start()

    def recv_files(self, sock):
        data = None
        try:
            data = sock.recv(self.__BUF)
        except:
            print("file name was not received on time")
        try:
            datacontent = data.decode()
            filename = datacontent
            print(filename)
            if filename[-8:] != ".torrent":
                return
            if not os.path.exists(f"torrents\\{filename}"):
                sock.send("FLOW".encode())

                s = 0
                length = int(pickle.loads(sock.recv(self.__BUF)))
                print(length)
                while s != length:
                    data = sock.recv(self.__BUF)
                    print(data)
                    s += len(data)
                    print(s)
                    with open(f"torrents\\{filename}", "ab") as f:
                        f.write(data)
                    sock.send("FLOW".encode())
                sock.send("DONE".encode())
        except:
            return


if __name__ == '__main__':
    TrackerTCP()
