import _thread
import time

import select
import threading
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *

from alive_progress import alive_bar

from torrent import Torrent
import message
import bitstring
import hashlib
import os
from tracker import Tracker

"""
Made by Alon Levy
"""


def is_handshake(msg):
    try:
        return msg[1:21].decode()[:19] == 'BitTorrent protocol'
    except:
        return False


def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')


def server_msg_type(msg):
    id = msg[0]
    try:
        if int.from_bytes(id, "big") == 2:
            return 'announce'
    except:
        return


def reset_have(num_of_pieces):
    """
    resets have
    :return:
    """
    have = ""
    for i in range(num_of_pieces):
        have += "0"
    return have


class Peer:
    def __init__(self, tracker):
        self.sock = None
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
        self.__BUF = 1024
        self.size = self.torrent.size()
        self.record = 0
        self.stop_thread = False
        self.block_len = 16384
        self.pieces = self.torrent.torrent['info']['pieces']
        self.piece_length = self.torrent.torrent['info']['piece length']
        self.num_of_pieces = len(self.pieces) // 20  # number of pieces in torrent


        try:
            self.files = self.torrent.torrent['info']['files']
        except:
            self.files = self.torrent.torrent['info']
        self.torrent_name = self.torrent.torrent['info']['name']
        os.mkdir(f"torrents\\files\\{self.torrent_name}") if not os.path.exists(
            f"torrents\\files\\{self.torrent_name}") else None
        self.left = [0, 0, b'']  # total / len / data
        self.listen_sock = socket(AF_INET, SOCK_STREAM)
        self.listen_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listen_sock.bind(('0.0.0.0', self.torrent.port))
        self.listen_sock.listen(5)
        self.create_new_sock()
        print(f"my port is: {self.listen_sock.getsockname()[1]}")
        self.peers = tracker.peers
        self.readable, self.writable = [self.listen_sock], []

        self.have = reset_have(self.num_of_pieces)  # what pieces I have

        self.progress_flag = True
        threading.Thread(target=self.calculate_have_bitfield).start()
        self.generate_progress_bar()
        print(self.have)

        th = threading.Thread(target=self.listen_to_peers)
        th.start()

    def generate_progress_bar(self):
        with alive_bar(self.num_of_pieces, force_tty=True) as self.bar:
            while self.progress_flag:
                time.sleep(0.01)

    def calculate_have_bitfield(self):
        time.sleep(0.5)
        if os.path.exists(f"torrents\\files\\{self.torrent_name}"):
            files = os.listdir(f"torrents\\files\\{self.torrent_name}")
            read = 0  # whats left to next piece
            left = b""  # lasting bytes to next piece
            piece_number = 0  # what piece are we at?
            for file in files:
                with open(f"torrents\\files\\{self.torrent_name}\\{file}", "rb") as f:
                    fs_raw = left + f.read(self.piece_length - read)
                    file_length = os.path.getsize(f"torrents\\files\\{self.torrent_name}\\{file}")
                    if len(fs_raw) == self.piece_length:
                        # while file_length - (self.piece_length + read) > 0:
                        #     last =
                        if hashlib.sha1(fs_raw).digest() == self.pieces[piece_number * 20: 20 * piece_number + 20]:
                            temp = list(self.have)
                            temp[piece_number] = "1"
                            self.have = "".join(temp)
                            # print(f"validated piece #{piece_number}, current bitfield progress:")
                            self.bar()
                        while len(fs_raw) == self.piece_length:
                            # print("here")
                            fs_raw = f.read(self.piece_length)
                            if len(fs_raw) == self.piece_length:
                                piece_number += 1
                                if hashlib.sha1(fs_raw).digest() == self.pieces[
                                                                    piece_number * 20: 20 * piece_number + 20]:
                                    temp = list(self.have)
                                    temp[piece_number] = "1"
                                    self.have = "".join(temp)
                                    self.bar()

                                    # print(f"validated piece #{piece_number}, current bitfield progress:")
                                    # print(self.have)
                            else:
                                if len(fs_raw) < self.piece_length:
                                    read = len(fs_raw)
                                    left = fs_raw
                                else:
                                    read = 0
                        piece_number += 1
                    else:
                        read = len(fs_raw)
                        left = fs_raw
        self.progress_flag = False
    def is_handshake_hash(self, handshake_msg):
        """
        does the handshake hash match desired torrent?
        :param handshake_msg:
        :return:
        """
        return handshake_msg[27: 27 + len(self.torrent.generate_info_hash())] == self.torrent.generate_info_hash

    def create_new_sock(self):
        if self.sock:
            self.sock.close()
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sock.settimeout(1)

    def download(self, peer):
        print("Trying", peer[0], peer[1])
        self.sock.connect((peer[0], peer[1]))
        print(f'successfully connected to {peer[0]}:{peer[1]}')
        self.sock.send(message.build_handshake(self.tracker))
        self.listen_to_server()

    def listen_to_server(self):
        while 1:
            data = self.sock.recv(16384)
            if len(data) == 0:
                break
            print(data)
            self.msg_handler(data, self.msg_type(data))

    def listen_to_peers(self):
        print("Now listening to incoming connections...")
        while 1 and not self.stop_thread:
            read, write, [] = select.select(self.readable, self.writable, [])
            for sock in read:
                if self.listen_sock == sock:
                    conn, addr = self.listen_sock.accept()
                    print(f"Connected to {addr}")
                    self.readable.append(conn)
                else:
                    data = sock.recv(self.__BUF)
                    if not data:
                        if sock in self.readable:
                            self.readable.remove(sock)

                    if not is_handshake(data):
                        data_len = int.from_bytes(data, 'big')
                        print("data length:", data_len)
                        data = sock.recv(data_len)
                        print(data)
                        if server_msg_type(data) == 'announce':  # message is announce
                            pass
                    elif is_handshake(data):
                        print(f'handshake received')
                        self.calculate_have_bitfield()
                        sock.send(message.build_handshake(self.tracker))
                        self.__BUF = 4
        print("Stopped listening to incoming connections...")

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
        else:
            if len(msg) == 4:
                if int.from_bytes(msg[:4], 'big') == 0:
                    return 'keep-alive'

    def request_next(self):
        """
        Requests next piece in line

        :return:
        """
        if self.s - 9 > 0:
            self.s -= 9  # without starters (only the block itself)
            temp = 0
            to_download = []
            for file in list(self.files):
                temp += file['length']
                if temp <= len(self.s_bytes):
                    to_download.append((file['path'], file['length']))
                    self.files = self.files[1:]
            for path in to_download:
                with open(f"torrents\\files\\{self.torrent_name}\\{path[0][0]}", 'wb') as w:
                    w.write(self.s_bytes[:path[1]])
                    self.written += self.s_bytes[:path[1]]
                    self.s_bytes = self.s_bytes[path[1]:]
                print("done writing", path)

            if hashlib.sha1((self.written + self.s_bytes)[
                            self.c_piece * self.piece_length: self.c_piece * self.piece_length + self.piece_length]).digest() == self.pieces[
                                                                                                                                 self.c_piece * 20: 20 * self.c_piece + 20]:
                print(f"success piece #{self.c_piece}, total --> {len(self.s_bytes)}")
                self.c_piece += 1
                self.s = 0
            elif hashlib.sha1(self.written[self.c_piece * self.piece_length:]).digest() == self.pieces[
                                                                                           self.c_piece * 20: 20 * self.c_piece + 20]:
                print(f"success piece #{self.c_piece}, last piece")

            self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
        else:
            self.request_again(self.s)

    def request_again(self, block):
        self.sock.send(message.build_request(self.c_piece, block, self.block_len))

    def msg_handler(self, msg, type):
        if type == 'unchoke' and not self.in_progress:
            self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
            self.in_progress = True
        elif is_handshake(msg):
            print(f'handshake received')
            self.sock.settimeout(5)
            if self.is_handshake_hash(msg):
                print("hash matches, started downloading")
                self.sock.send(message.build_interested())
        elif type == 'bitfield':
            print(len(msg[4:]), msg[4:], int.from_bytes(msg[:4], 'big'))
            print('bitfield')
            data = b''
            if len(msg[4:]) < int.from_bytes(msg[:4], 'big'):
                data = self.sock.recv(16384)
            msg += data

            data = bitstring.BitArray(msg[5:int.from_bytes(msg[:4], 'big') + 4])
            print(bitstring_to_bytes(data.bin))
        elif type == 'piece':
            self.length = int.from_bytes(msg[:4], 'big')
            if len(msg[4:]) != self.length:
                self.left = [len(msg[4:]), self.length, msg[4:]]
                self.s += len(msg[4:])
            else:
                self.s_bytes += msg[9:]
                self.s += len(msg[9:])
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

            if self.left[0] == self.left[1]:
                if self.size - (
                        16384 + len(self.s_bytes) + len(self.written)) < 16384:
                    self.block_len = self.size - (16384 + len(self.s_bytes) + len(self.written))
                self.s_bytes += (self.left[2])[9:]
                print("here 2: ", msg)
                self.request_next()
                self.left = [0, 0, b'']

        if len(msg) != int.from_bytes(msg[:4], 'big') + 4 and len(msg) != 0 and type not in [None, 'piece']:
            if is_handshake(msg):
                self.msg_handler(msg[68:], self.msg_type(msg[68:]))

            elif type == 'bitfield':
                self.msg_handler(msg[int.from_bytes(msg[:4], 'big') + 4:],
                                 self.msg_type(msg[int.from_bytes(msg[:4], 'big') + 4:]))
            else:
                if type == 'keep-alive':
                    self.msg_handler(msg[4:], self.msg_type(msg[4:]))

                else:
                    self.msg_handler(msg[5:], self.msg_type(msg[5:]))


def msg_type(msg):
    if len(msg) > 4:  # message is longer than its length, very weird if not
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
