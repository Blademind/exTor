import _thread
import threading
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *
from torrent import Torrent
import message
import bitstring
import hashlib


class Peer:
    def __init__(self, tracker):
        self.s = 0  # pieces management
        self.c_piece = 0
        self.s_bytes = b''
        self.all_downloaded = 0  # downloaded files
        self.requested = []
        self.block = b''
        self.tracker = tracker
        self.torrent = tracker.torrent
        self.size = self.torrent.size
        try:
            self.files = self.torrent.torrent['info']['files']
        except:
            self.files = self.torrent.torrent['info']
        self.left = 0
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(1)
        self.sock.bind(('192.168.1.196', 6882))
        self.peers = tracker.peers

    def download(self, peer):
        print(peer[0], peer[1])
        self.sock.connect((peer[0], peer[1]))
        self.sock.settimeout(None)
        print(f'successfully connected to {peer[0]}:{peer[1]}')
        self.sock.send(message.build_handshake(self.tracker))
        threading.Thread(target=self.listen).start()

    def listen(self):
        while 1:
            data = self.sock.recv(16384)
            if len(data) == 0:
                break
            self.msg_handler(data, self.msg_type(data))

    #def manage_pieces(self):

        # all = b''
        # while self.s != self.size:
        #     if self.s - self.all_downloaded != self.files[0]['length']:
        #         with open(self.files[0]['path'][0], 'wb') as file:
        #             file.write(self.s_bytes[:self.files[0]['length']])
        #         all += self.s_bytes
        #         self.s_bytes = self.s_bytes[self.files[0]['length']:]
        #         self.all_downloaded += self.files[0]['length']
        #         del self.files[0]
        #     if self.s // (self.c_piece+1) >= self.torrent.torrent['info']['piece length']:
        #         print(self.s // (self.c_piece+1))
        #         print(hashlib.sha1(all).digest())
        #         self.c_piece += 1

    def msg_type(self, msg):
        if len(msg) > 4:
            if int.from_bytes(msg[:4], 'big') + 4 != len(msg):
                return None
            elif msg[4] == 0:
                return 'choke'
            elif msg[4] == 1:
                return 'unchoke'
            elif msg[4] == 5:
                return 'bitfield'
            elif msg[4] == 7:
                return 'piece'
            try:
                if msg[1:21].decode()[:19] == 'BitTorrent protocol':
                    return 'handshake'
                return None
            except:
                return None

    def request_next(self):
        if self.s == self.torrent.torrent['info']['piece length']:
            self.requested.append(self.s_bytes)
            print('bytes -- >', self.s_bytes)
            self.s_bytes = b''
            self.c_piece += 1
            self.s = 0
        else:
            self.s += 16384
        self.sock.send(message.build_request(self.c_piece, self.s, 16384))

    def msg_handler(self, msg, type):
        if type == 'unchoke':
            self.sock.send(message.build_request(0, 0, 16384))
            #_thread.start_new_thread(self.manage_pieces, ())
        elif self.is_handshake(msg):
            print(f'handshake received')
            self.sock.send(message.build_interested())
        elif type == 'bitfield':
            print('bitfield')
            data = b''
            if len(msg[5:]) < int.from_bytes(msg[:4], 'big'):
                data = self.sock.recv(16384)
            msg += data
            data = bitstring.BitArray(msg[5:])
            pieces_num = len(self.torrent.torrent['info']['pieces']) // 20
            print(f'bitfield received --> {data.bin[:pieces_num]}')
        elif type == 'piece':
            print('piece ->', msg)
            self.request_next()
        elif type == None and type != 'choke':
            self.s_bytes += msg
            print(f'block received -> {len(msg)}, total -> {self.s}, {msg}')

        if len(msg) != int.from_bytes(msg[:4], 'big') + 4 and len(msg) != 0 and type not in [None, 'piece']:
            if self.is_handshake(msg):
                self.msg_handler(msg[68:], self.msg_type(msg[68:]))
            elif type == 'bitfield':
                self.msg_handler(msg[int.from_bytes(msg[:4], 'big') + 4:], self.msg_type(msg[int.from_bytes(msg[:4], 'big') + 4:]))
            else:
                self.msg_handler(msg[5:], self.msg_type(msg[5:]))

    def is_handshake(self, msg):
        try:
            return msg[1:21].decode()[:19] == 'BitTorrent protocol'
        except:
            return False
