import _thread
import select
import threading
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *
from torrent import Torrent
import message_handler as message
import bitstring
import hashlib
import os
from tracker import Tracker
"""
Made by Alon Levy
"""


class Peer:
    def __init__(self, tracker):
        self.s = 0  # pieces management
        self.c_piece = 0
        self.s_bytes = b''
        self.in_progress = False
        self.all_downloaded = 0  # downloaded files
        self.block = b''
        self.bitfield_progress = False
        self.length = 0
        self.written = b''
        self.tracker = tracker
        self.torrent = tracker.torrent
        self.size = self.torrent.size()
        self.buf = 16384
        self.record = 0
        print(self.size)

        self.block_len = 16384
        self.pieces = self.torrent.torrent['info']['pieces']
        self.piece_length = self.torrent.torrent['info']['piece length']
        try:
            self.files = self.torrent.torrent['info']['files']
        except:
            self.files = self.torrent.torrent['info']
        self.torrent_name = self.torrent.torrent['info']['name']
        os.mkdir(self.torrent_name) if not os.path.exists(self.torrent_name) else None
        self.left = [0, 0, b'']  # total / len / data
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.settimeout(1)
        self.sock.bind(('192.168.1.196', 6881))
        self.readable, self.writeable = [self.sock], []

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
            read, write, [] = select.select(self.readable, self.writeable, [])
            data = self.sock.recv(self.buf)
            if len(data) == 0:
                break
            if is_handshake(data):
                print(f'handshake received')
                self.sock.send(message.build_interested())
            else:
                msg_len = int.from_bytes(data, 'big')
                print("len-data:", data)
                print("length:", msg_len)
                data = self.sock.recv(msg_len)
                print(data)
                msg_type = self.msg_type2(data[0])
                if msg_type == 'bitfield':
                    msg = data[1:]
                    print('bitfield')
                    data = b''
                    # if len(msg[4:]) < int.from_bytes(msg[:4], 'big'):
                    #     data = self.sock.recv(16384)
                    # msg += data
                    print(msg)
                    data = bitstring.BitArray(msg)
                    print(data.bin, len(data.bin))
                # self.msg_handler(data, self.msg_type(data))
            self.buf = 4

    def msg_type2(self, msg):
        if msg == 0:
            return 'choke'
        elif msg == 1:
            return 'unchoke'
        elif msg == 5 and not self.bitfield_progress:
            self.bitfield_progress = True
            return 'bitfield'
        elif msg == 7:
            return 'piece'
        try:
            if msg[1:21].decode()[:19] == 'BitTorrent protocol':
                return 'handshake'
            return None
        except:
            return None

    def msg_type(self, msg):

        if len(msg) > 4:
            if msg[4] == 0 and int.from_bytes(msg[:4], 'big') == len(msg[4:]):
                return 'choke'
            elif msg[4] == 1 and int.from_bytes(msg[:4], 'big') <= len(msg[4:]):
                return 'unchoke'
            elif msg[4] == 5 and not self.bitfield_progress:
                self.bitfield_progress = True
                return 'bitfield'
            elif msg[4] == 7 and int.from_bytes(msg[:2], 'big') == 0:
                return 'piece'
            try:
                if msg[1:21].decode()[:19] == 'BitTorrent protocol':
                    return 'handshake'
                return None
            except:
                return None

    def request_next(self):
        self.s -= 9  # without starters (only the block itself)
        temp = 0
        to_download = []
        for file in list(self.files):
            temp += file['length']
            if temp <= len(self.s_bytes):
                print(file['path'])
                to_download.append((file['path'], file['length']))
                self.files = self.files[1:]
        for path in to_download:
            with open(f"{self.torrent_name}/{path[0][0]}", 'wb') as w:
                w.write(self.s_bytes[:path[1]])
                self.written += self.s_bytes[:path[1]]
                self.s_bytes = self.s_bytes[path[1]:]
        if hashlib.sha1((self.written+self.s_bytes)[self.c_piece*self.piece_length: self.c_piece*self.piece_length + self.piece_length]).digest() == self.pieces[self.c_piece * 20: 20*self.c_piece+20]:
            print(f"success piece #{self.c_piece}, total --> {len(self.s_bytes)}")
            self.c_piece += 1
            self.s = 0
        elif hashlib.sha1((self.written+self.s_bytes)[self.c_piece*self.piece_length:]).digest() == self.pieces[self.c_piece * 20: 20*self.c_piece+20]:
            print(f"last piece was downloaded, total --> {len(self.s_bytes)}")
        print(self.c_piece, self.s, self.block_len)
        self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))

    def msg_handler(self, msg, type):
        #print(len(msg), msg, msg[4], type)
        if type == 'unchoke' and not self.in_progress:
            self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
            self.in_progress = True
        elif self.is_handshake(msg):
            print(f'handshake received')
            self.sock.send(message.build_interested())
        elif type == 'bitfield':
            print(len(msg[4:]), msg[4:], int.from_bytes(msg[:4], 'big'))
            print('bitfield')
            data = b''
            if len(msg[4:]) < int.from_bytes(msg[:4], 'big'):
                data = self.sock.recv(16384)
            msg += data
            data = bitstring.BitArray(msg[5:int.from_bytes(msg[:4], 'big')+4])
            print(data.bin)
        elif type == 'piece':
            self.length = int.from_bytes(msg[:4], 'big')
            if len(msg[4:]) != self.length:
                self.left = [len(msg[4:]), self.length, msg[4:]]
                self.s += len(msg[4:])
            else:
                self.s_bytes += msg[9:]
                self.s += len(msg[9:])
                print("here 1: ", msg)
                self.request_next()
        elif type is None and len(msg) != 0:
            if self.left[0] != self.left[1]:  # if there is more left
                if len(msg) == self.left[1] - self.left[0] or len(msg) < self.left[1] - self.left[0]:  # msg[4:]?
                    self.left[0] += len(msg)
                    self.left[2] += msg
                    self.record += len(msg[9:])
                    self.s += len(msg)
                elif len(msg) > self.left[1] - self.left[0]:  # msg[4:]?
                    self.left[2] += msg[:self.left[1] - self.left[0]]
                    self.left[0] += len(msg[:self.left[1] - self.left[0]])

            #if len(self.s_bytes) + self.s + 16384 > self.size:  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            #    self.block_len = 16384 - ((len(self.s_bytes) + self.s + 16384) - self.size)
            #    print('passed -->', self.block_len)
            #print(f'{len(self.written)}, {len(self.s_bytes)}, {self.s}')
            if self.left[0] == self.left[1]:
                #print('total --> ', self.size - (self.left[0] - 9 + len(self.s_bytes) + len(self.written)))
                if self.size - (16384 + len(self.s_bytes) + len(self.written)) < 16384:  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    self.block_len = self.size - (16384 + len(self.s_bytes) + len(self.written))
                self.s_bytes += (self.left[2])[9:]
                print("here 2: ", msg)
                self.request_next()
                self.left = [0, 0, b'']
           # elif (self.c_piece - 1) * self.length + self.s - 9 == self.size:
           #     self.request_next()

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


def msg_type(msg):

    if len(msg) > 4:
        if msg[4] == 0 and int.from_bytes(msg[:4], 'big') == len(msg[4:]):
            return 'choke'
        elif msg[4] == 1 and int.from_bytes(msg[:4], 'big') <= len(msg[4:]):
            return 'unchoke'
        elif msg[4] == 5 and int.from_bytes(msg[:4], 'big') <= len(msg[4:]):
            return 'bitfield'
        elif msg[4] == 7 and int.from_bytes(msg[:2], 'big') == 0:
            return 'piece'
        try:
            if msg[1:21].decode()[:19] == 'BitTorrent protocol':
                return 'handshake'
            return None
        except:
            return None


def check(peer, tracker):
    print(peer[0], peer[1])
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.settimeout(1)
    sock.bind(('192.168.1.196', 6881))
    sock.connect((peer[0], peer[1]))
    sock.send(message.build_handshake(tracker))
    msg = sock.recv(16384)
    try:
        msg += sock.recv(16384)
    except: pass
    sock.close()
    return bitfield_handler(msg, msg_type(msg))


def bitfield_handler(msg, type):
    if type == 'bitfield':
        data = b''
        if len(msg[4:]) < int.from_bytes(msg[:4], 'big'):
            data = sock.recv(16384)
        msg += data
        data = bitstring.BitArray(msg[5:])
        print(f'bitfield received --> {data.bin}')
        return data.bin
    if len(msg) != int.from_bytes(msg[:4], 'big') + 4 and len(msg) != 0 and type not in [None, 'piece']:
        if is_handshake(msg):
            return bitfield_handler(msg[68:], msg_type(msg[68:]))
        elif type == 'bitfield':
            return bitfield_handler(msg[int.from_bytes(msg[:4], 'big') + 4:],
                             msg_type(msg[int.from_bytes(msg[:4], 'big') + 4:]))
        else:
            return bitfield_handler(msg[5:], msg_type(msg[5:]))


def is_handshake(msg):
    try:
        return msg[1:21].decode()[:19] == 'BitTorrent protocol'
    except:
        return False
