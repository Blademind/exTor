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
        self.tran_id = None  # the transaction id (later use)
        self.conn_id = None  # the connection id (later use)
        self.id = generate_peer_id()  # peer_id
        self.peers = []
        self.torrent = Torrent()
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", self.torrent.port))
        self.sock.settimeout(0.5)
        if type(self.torrent.url) is ParseResult:
            # Udp tracker
            self.udp_send(build_conn_req())
        else:
            # Http tracker
            self.http_send()

    def udp_send(self, message):
        print(self.torrent.url)
        try:
            self.sock.sendto(message, (gethostbyname(self.torrent.url.hostname), self.torrent.url.port))
            self.listen()
        except:
            print('Error, Trying another tracker...')
            self.torrent.url = self.torrent.url_yields.__next__()
            self.udp_send(build_conn_req())

    def http_send(self):
        print(self.torrent.url)
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


if __name__ == '__main__':
    Tracker()
