import _thread
import asyncio
import socket
import time

import select
import threading
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *

from alive_progress import alive_bar

from torrent import Torrent
import message_handler as message
import bitstring
import hashlib
import os
import peers_manager as manager
from tracker import Tracker

"""
Made by Alon Levy
"""


def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')


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
        # print(f"my port is: {self.listen_sock.getsockname()[1]}")
        self.peers = tracker.peers
        self.readable, self.writable = [self.listen_sock], []
        self.current_piece_peers = []
        self.piece_downloaded = False

        # self.have = reset_have(self.num_of_pieces)  # what pieces I have
        # self.info_hashes = self.generate_info_hashes()
        self.buf = 68
        # self.progress_flag = True
        # threading.Thread(target=self.calculate_have_bitfield).start()
        # self.generate_progress_bar()
        # print(self.have)

        # th = threading.Thread(target=self.listen_to_peers)
        # th.start()

    def generate_info_hashes(self):
        ret = []
        for i in range(0, len(self.pieces), 20):
            ret.append(self.pieces[i: i + 20])
        return ret

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

    def calculate_have_bitfield2(self):
        time.sleep(0.1)
        if os.path.exists(f"torrents\\files\\{self.torrent_name}"):
            files = os.listdir(f"torrents\\files\\{self.torrent_name}")
            files_raw = b""
            for file in files:
                with open(f"torrents\\files\\{self.torrent_name}\\{file}", "rb") as f:
                    files_raw += f.read()
            files_len = len(files_raw)
            for i in range(files_len):
                # print(len(files_raw))
                if len(files_raw[:self.piece_length]) < self.piece_length:
                    break

                if hashlib.sha1(files_raw[:self.piece_length]).digest() in self.info_hashes:
                    temp = list(self.have)
                    temp[self.info_hashes.index(hashlib.sha1(files_raw[:self.piece_length]).digest())] = "1"
                    self.have = "".join(temp)
                    self.bar()
                    files_raw = files_raw[self.piece_length:]
                else:
                    files_raw = files_raw[1:]
            self.progress_flag = False

    def is_handshake_hash(self, handshake_msg):
        """
        does the handshake hash match desired torrent's hash?
        :param handshake_msg:
        :return:
        """
        return handshake_msg[28: 28 + len(self.torrent.generate_info_hash())] == self.torrent.generate_info_hash()

    async def download(self, peer, piece_number, current_piece_peers):

        self.c_piece = piece_number
        self.current_piece_peers = current_piece_peers

        host, port = peer[0], peer[1]
        print("Trying", host, port)
        reader, writer = await asyncio.open_connection(host, port)
        print(f'successfully connected to {peer[0]}:{peer[1]}')
        writer.write(message.build_handshake(self.tracker))
        await writer.drain()
        asyncio.run(self.listen_to_server(reader, writer))

    async def listen_to_server(self, reader, writer):
        s_bytes = b""
        while 1 and not self.piece_downloaded:
            try:
                data = await reader.read(self.buf)
                # print(len(data), data, self.sock.getpeername())
                if not data:
                    raise ValueError
                if message.is_handshake(data):
                    print("handshake")
                    self.buf = 4
                    if self.is_handshake_hash(data):
                        # print("hash matches")
                        writer.write(message.build_interested())
                        await writer.drain()
                elif message.msg_type(data) == "bitfield":
                    print("bitfield")
                    data = bitstring.BitArray(data[1:])
                    # print(data.bin)
                    self.buf = 4
                elif message.msg_type(data) == "unchoke":
                    print("unchoke")
                    if not self.in_progress:
                        writer.write(message.build_request(self.c_piece, self.s, self.block_len))
                        await writer.drain()
                        self.in_progress = True
                    self.buf = 4
                elif message.msg_type(data) == "choke":
                    print("choke")
                    self.buf = 4
                    raise ValueError

                elif message.msg_type(data) == "piece":
                    # print("piece")
                    while len(data) != self.buf:
                        data += self.sock.recv(self.buf)
                    data = data[9:]
                    s_bytes += data
                    self.s += len(data)
                    self.buf = 4
                    if self.s != self.piece_length:
                        self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
                    else:
                        # checks if downloaded piece matches current piece hash
                        if hashlib.sha1(s_bytes).digest() == self.pieces[
                                                             self.c_piece * 20: 20 * self.c_piece + 20]:
                            print(f"success piece #{self.c_piece}, total --> {self.s}")
                            self.piece_downloaded = True
                            manager.currently_connected.remove(self.sock.getpeername())
                            # self.have_msg()  # send have message to all connected peers

                        # a unique if statement for last piece
                        elif hashlib.sha1(s_bytes).digest() == self.pieces[
                                                               self.c_piece * 20: 20 * self.c_piece + 20]:
                            temp = list(self.have)
                            temp[self.c_piece] = "1"
                            self.have = "".join(temp)
                            print(f"success piece #{self.c_piece}, last piece")

                elif message.msg_type(data) == "have":
                    print("have")
                    self.buf = 4
                elif message.msg_type(data) == "keep-alive":
                    pass
                    print("keep-alive")
                else:
                    if len(data) != 0:
                        msg_len = int.from_bytes(data, "big")
                        self.buf = msg_len

            except Exception as e:
                print(e)


    def listen_to_peers(self):
        print("Now listening to incoming connections...")
        while 1:
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
                        break

                    if not message.is_handshake(data):
                        data_len = int.from_bytes(data, 'big')
                        print("data length:", data_len)
                        data = sock.recv(data_len)
                        print(data)
                        if message.server_msg_type(data) == 'announce':  # message is announce
                            pass

                    elif message.is_handshake(data):
                        print(f'handshake received')
                        sock.send(message.build_handshake(self.tracker))
                        sock.send(message.build_bitfield(self.have))
                        self.__BUF = 4
