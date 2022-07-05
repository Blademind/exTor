import _thread
import pickle
import socket
import time
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *
from torrent import Torrent
from random import randbytes


class Tracker:
    def __init__(self):
        self.torrent = Torrent()
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.settimeout(10)
        # _thread.start_new_thread(self.listen, ())

        self.udp_send(self.build_conn_req())

    def udp_send(self, message):
        self.sock.sendto(message, (gethostbyname(self.torrent.url.hostname), self.torrent.url.port))
        self.listen()
        # ret = self.sock.recv(1024)
        # self.conn_id = ret[8:]
        # self.tran_id = ret[4:8]
        # self.sock.sendto(self.build_announce_req(), (gethostbyname(self.torrent.url.hostname), self.torrent.url.port))
        # ret = self.sock.recv(1024)
        # print(ret.hex())  # here

    def listen(self):
        ret = self.sock.recv(1024)
        if self.resp_type(ret) == 'connect':
            self.conn_id = ret[8:]
            self.tran_id = ret[4:8]
            self.udp_send(self.build_announce_req())

        elif self.resp_type(ret) == 'announce':
            print(ret.hex())

    def resp_type(self, ret):
        if int.from_bytes(ret[:4], 'big') == 0:
            return 'connect'
        elif int.from_bytes(ret[:4], 'big') == 1:
            return 'announce'

    def build_conn_req(self):
        message = bytes.fromhex('00 00 04 17 27 10 19 80')  # connection_id
        message += bytes.fromhex('00 00 00 00')  # action
        message += randbytes(4)  # transaction_id
        return message

    def generate_peerid(self):
        id = randbytes(20)
        return id

    def build_announce_req(self, port=6881):
        self.id = self.generate_peerid()
        message = self.conn_id  # connection_id
        message += (1).to_bytes(4, byteorder='big') # action
        message += self.tran_id  # transaction_id
        message += self.torrent.generate_info_hash()  # info_hash
        message += self.id  # peerid
        message += bytes.fromhex('00 00 00 00 00 00 00 00')  # downloaded
        message += self.torrent.size().to_bytes(8, byteorder='big')  # left
        message += bytes.fromhex('00 00 00 00 00 00 00 00')  # uploaded
        message += bytes.fromhex('00 00 00 00')  # event
        message += bytes.fromhex('00 00 00 00')  # ip_address
        message += randbytes(4)  # key
        message += (-1).to_bytes(4, byteorder='big', signed=True)
        message += (port).to_bytes(2, byteorder='big')
        return message


if __name__ == '__main__':
    Tracker()