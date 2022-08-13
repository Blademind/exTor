import _thread
import pickle
import socket
import time
from socket import *
import bencode
from urllib.parse import urlparse, ParseResult
from socket import *
from torrent import Torrent
from random import randbytes
import requests


class Tracker:
    def __init__(self):
        self.id = self.generate_peerid()  # peer_id
        self.peers = []
        self.torrent = Torrent()
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.settimeout(0.5)
        # _thread.start_new_thread(self.listen, ())
        if type(self.torrent.url) is ParseResult:
            self.udp_send(self.build_conn_req())
        else:
            self.http_send()

    def udp_send(self, message):
        print(self.torrent.url)
        try:
            self.sock.sendto(message, (gethostbyname(self.torrent.url.hostname), self.torrent.url.port))
            self.listen()
        except:
            print('Error, Trying another tracker...')
            self.torrent.url = self.torrent.url_yields.__next__()
            self.udp_send(self.build_conn_req())

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
        if self.resp_type(ret) == 'connect':
            self.conn_id = ret[8:]
            self.tran_id = ret[4:8]
            self.udp_send(self.build_announce_req())

        elif self.resp_type(ret) == 'announce':
            n = 0
            while 24 + 6*n <= len(ret):
                ip = inet_ntoa(ret[20+6*n: 24+6*n])
                port = int.from_bytes(ret[24+6*n: 26+6*n], 'big')
                self.peers.append((ip, port))
                n += 1

    def resp_type(self, ret):
        if int.from_bytes(ret[:4], 'big') == 0:
            return 'connect'
        elif int.from_bytes(ret[:4], 'big') == 1:
            return 'announce'

    def build_conn_req(self):
        message = bytes.fromhex('00 00 04 17 27 10 19 80')  # connection_id
        message += (0).to_bytes(4, byteorder='big')  # action
        message += randbytes(4)  # transaction_id
        return message

    def generate_peerid(self):
        id = randbytes(20)
        return id

    def build_announce_req(self, port=6881):
        message = self.conn_id  # connection_id
        message += (1).to_bytes(4, byteorder='big') # action
        message += self.tran_id  # transaction_id
        message += self.torrent.generate_info_hash()  # info_hash
        message += self.id  # peer_id
        message += (0).to_bytes(8, byteorder='big') # downloaded
        message += self.torrent.size().to_bytes(8, byteorder='big')  # left
        message += (0).to_bytes(8, byteorder='big')  # uploaded
        message += (0).to_bytes(4, byteorder='big')  # event
        message += (0).to_bytes(4, byteorder='big') # ip_address
        message += randbytes(4)  # key
        message += (-1).to_bytes(4, byteorder='big', signed=True)
        message += (port).to_bytes(2, byteorder='big')
        return message


if __name__ == '__main__':
    Tracker()