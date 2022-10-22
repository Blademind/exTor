import _thread
import pickle
import time
from random import randbytes

import select
import threading
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *
import bitstring
import hashlib
import os


class Tracker:
    def __init__(self):
        self.server_sock2 = None  # tcp sock
        self.server_sock = None  # udp sock
        self.init_tcp_sock()
        self.init_udp_sock()
        self.__BUF = 1024
        self.read_udp, self.write_udp = [self.server_sock], []  # read write for select udp
        self.read_tcp, self.write_tcp = [self.server_sock2], []  # read write for select udp

        self.connection_ids = {}  # list of all connected clients
        self.ip_addresses = [("192.168.1.196", 1234)]
        _thread.start_new_thread(self.listen_tcp, ())
        self.listen_udp()  # listen

    def init_udp_sock(self):
        self.server_sock = socket(AF_INET, SOCK_DGRAM)
        self.server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_sock.bind(("192.168.1.196", 55555))

    def init_tcp_sock(self):
        self.server_sock2 = socket(AF_INET, SOCK_STREAM)
        self.server_sock2.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_sock2.bind(("192.168.1.196", 55556))

    def listen_udp(self):
        """
        Listens to incoming communications
        """
        while 1:
            readable, writeable, ex = select.select(self.read_udp, self.write_udp, [])
            for sock in readable:
                data, addr = sock.recvfrom(self.__BUF)
                if not data:
                    break
                try:
                    datacontent = data.decode()
                    if datacontent == "TCP_SERVER":
                        sock.sendto(pickle.dumps(gethostbyname(gethostname())), addr)
                except:
                    pass
                # request must be at least 16 bytes long
                if len(data) >= 16:
                    try:
                        action = int.from_bytes(data[8:12], byteorder="big")  # action type
                        # action is connect
                        if action == 0:
                            print(f"New connection from {addr}")
                            sock.sendto(self.build_connect_response(), addr)  # send a connect response

                        # action is announce
                        elif action == 1:
                            connection_id = data[:8]  # connection id
                            # 2 minutes must have not passed
                            try:
                                if 0 <= int(time.time() - self.connection_ids[connection_id]) <= 120:
                                    sock.sendto(self.build_announce_response(), addr)
                            except KeyError:
                                print("sent connection id was not found")
                    except Exception as e:
                        print(e)
                        print("received unparsable data")

    def listen_tcp(self):
        while 1:
            read, write, ex = select.select(self.read_tcp, self.write_tcp, [])
            for sock in read:
                if sock == self.server_sock2:
                    conn, addr = self.server_sock2.accept()
                    conn.settimeout(5.0)
                    read.append(conn)
                else:
                    data = sock.recv(self.__BUF)
                    if not data:
                        break
                    try:
                        datacontent = data.decode()
                    except:
                        break
                    if datacontent == "START":
                        _thread.start_new_thread(self.recv_files, (sock, ))

    def recv_files(self, sock):
        data = None
        try:
            data = sock.recv(self.__BUF)
        except:
            print("file name was not received on time")
        try:
            datacontent = data.decode()
            filename = datacontent
            if filename[-8:] != ".torrent":
                return
            sock.send("FLOW".encode())
            s = 0
            length = int(pickle.loads(sock.recv(self.__BUF)))

            while s != length:
                data = sock.recv(self.__BUF)
                s += len(data)
                with open(f"torrents\\{filename}", "ab") as f:
                    f.write(data)
                sock.send("FLOW".encode())
            sock.send("DONE".encode())
        except:
            return

    def build_announce_response(self):
        message = (1).to_bytes(4, byteorder='big')  # action - announce
        message += randbytes(4)  # transaction_id
        message += (0).to_bytes(4, byteorder='big')  # interval - 0 so none
        message += (0).to_bytes(4, byteorder='big')  # leechers (TO DO)
        message += (0).to_bytes(4, byteorder='big')  # seeders (TO DO)
        for ip_port in self.ip_addresses:
            message += inet_aton(ip_port[0])  # ip

            message += ip_port[1].to_bytes(2, byteorder='big')  # port

        return message

    def build_connect_response(self):
        message = (0).to_bytes(4, byteorder='big')  # action - connect
        message += randbytes(4)  # transaction_id
        connection_id = randbytes(8)
        self.connection_ids[connection_id] = time.time()  # time the moment id was added
        message += connection_id
        return message


if __name__ == '__main__':
    Tracker()
