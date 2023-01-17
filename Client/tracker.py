import os.path
import pickle
import socket
import time
from random import randbytes
from socket import *
from urllib.parse import ParseResult

import bencode
import requests

from torrent import Torrent


def resp_type(ret):
    if int.from_bytes(ret[:4], 'big') == 0:
        return 'connect'
    elif int.from_bytes(ret[:4], 'big') == 1:
        return 'announce'


def build_conn_req():
    """Builds udp tracker request"""
    message = bytes.fromhex('00 00 04 17 27 10 19 80')  # connection_id (set id 41727101980)
    message += (0).to_bytes(4, byteorder='big')  # action - connect
    message += randbytes(4)  # transaction_id
    return message


def generate_peer_id():
    return randbytes(20)


class Tracker:
    def __init__(self):
        self.__BUF = 1024
        self.local_tracker = self.find_local_tracker()
        self.tran_id = None  # the transaction id (later use)
        self.conn_id = None  # the connection id (later use)
        self.id = generate_peer_id()  # peer_id
        self.peers = []

        self.torrent = Torrent()
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.torrent.port))
        self.sock.settimeout(0.5)

        file_name = self.fetch_torrent_file()
        # the torrent file is not local
        if file_name[-12: -8] != "_LOC":
            self.torrent.init_torrent_seq(file_name)

        else:
            # the peers are in the torrent file, instead of trackers, each peer is a node in the local network, algorithm specified for that is required here
            pass


        try:
            self.yields = self.torrent.url_yields
            if type(self.torrent.url) is ParseResult:
                # Udp tracker
                self.udp_send(build_conn_req())
            else:
                # Http tracker
                self.http_send()
        except AttributeError:
            pass

    def udp_send(self, message):
        print(self.torrent.url)
        try:
            self.sock.sendto(message, (gethostbyname(self.torrent.url.hostname), self.torrent.url.port))
            self.listen()
            self.torrent.url = self.torrent.url_yields.__next__()
            if self.torrent.url:
                if type(self.torrent.url) is ParseResult:
                    # Udp tracker
                    self.udp_send(build_conn_req())
                else:
                    # Http tracker
                    self.http_send()

        except StopIteration:
            print("gone over all the trackers")
            pass
        except Exception as e:
            print(f'Error: {e}')
            self.torrent.url = self.torrent.url_yields.__next__()
            if self.torrent.url:
                print('Trying another tracker...')
                if type(self.torrent.url) is ParseResult:
                    # Udp tracker
                    self.udp_send(build_conn_req())
                else:
                    # Http tracker
                    self.http_send()

    def http_send(self):
        params = {
            'info_hash': self.torrent.generate_info_hash(),
            'peer_id': self.id,
            'uploaded': 0,
            'downloaded': 0,
            'port': 6881,
            'left': self.torrent.size(),
            'event': 'started'
        }
        try:
            answer_tracker = requests.get(self.torrent.url, params=params, timeout=5)
            list_peers = bencode.bdecode(answer_tracker.content)
            for peer in list_peers['peers']:
                self.peers.append((peer['ip'], peer['port']))
        except:
            print('Error, Trying another tracker...')
            self.torrent.url = self.torrent.url_yields.__next__()
            self.http_send()

    def listen(self):
        ret = self.sock.recv(1024)
        try:
            self.TCP_IP_PORT = pickle.loads(ret)
        except:
            if resp_type(ret) == 'connect':
                self.conn_id = ret[8:]
                self.tran_id = ret[4:8]
                self.udp_send(self.build_announce_req())

            elif resp_type(ret) == 'announce':
                n = 0
                while 24 + 6 * n <= len(ret):
                    ip = inet_ntoa(ret[20 + 6 * n: 24 + 6 * n])
                    port = int.from_bytes(ret[24 + 6 * n: 26 + 6 * n], 'big')

                    # only add peer if needed
                    if (ip, port) not in self.peers:
                        self.peers.append((ip, port))
                    n += 1
                print(self.peers)
            else:
                # Error code 3
                if int.from_bytes(ret[:4], byteorder='big') == 3:
                    print("=== ERROR ===")
                    print(ret[8:].decode())

    def build_announce_req(self, port=6881):
        message = self.conn_id  # connection_id
        message += (1).to_bytes(4, byteorder='big')  # action
        message += self.tran_id  # transaction_id
        message += self.torrent.generate_info_hash()  # info_hash
        message += self.id  # peer_id
        message += (0).to_bytes(8, byteorder='big')  # downloaded
        message += self.torrent.size().to_bytes(8, byteorder='big')  # left
        message += (0).to_bytes(8, byteorder='big')  # uploaded
        message += (0).to_bytes(4, byteorder='big')  # event
        message += (0).to_bytes(4, byteorder='big')  # ip_address
        message += randbytes(4)  # key
        message += (-1).to_bytes(4, byteorder='big', signed=True)
        message += port.to_bytes(2, byteorder='big')
        return message


    def find_local_tracker(self):
        interfaces = getaddrinfo(host=gethostname(), port=None, family=AF_INET)
        allips = [ip[-1][0] for ip in interfaces]
        msg = b'FIND LOCAL TRACKER'
        sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        sock.settimeout(2)
        sock.bind(("0.0.0.0", 0))
        for _ in allips:
            sock.sendto(msg, ("255.255.255.255", 55555))
        try:
            data = sock.recv(1024)
            try:
                ip = pickle.loads(data)
                test_open = sock.connect_ex(ip)
                if test_open != 0:
                    print("tracker is not connectable")
                    return
                print("found local tracker")
                return ip
            except KeyError:
                print("fatal error while searching for local tracker")
        except TimeoutError:
            print("no response from local tracker")
            return

    def fetch_torrent_file(self):
        file_name = input("What torrent would you like to download? -> ")
        self.sock.sendto(f"GET {file_name}".encode(), self.local_tracker)
        return self.recv_files()

    def recv_files(self):
        data = None
        try:
            data, addr = self.sock.recvfrom(self.__BUF)
        except:
            print("file name was not received on time")
        try:
            datacontent = data.decode()
            filename = datacontent
            if filename[-8:] != ".torrent":
                print("file is not torrent")
                return
            with open(f"torrents\\info_hashes\\{filename}", "wb") as f:
                f.write(b"")
            self.sock.sendto(b"FLOW", addr)
            s = 0
            length = int(pickle.loads(self.sock.recv(self.__BUF)))
            while s != length:
                data = self.sock.recv(self.__BUF)
                s += len(data)
                with open(f"torrents\\info_hashes\\{filename}", "ab") as f:
                    f.write(data)
                self.sock.sendto(b"FLOW", addr)
            print("received torrent file from local tracker")
            return filename
        except Exception as e:
            print(e)
            return




if __name__ == '__main__':
    Tracker()