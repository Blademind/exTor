import _thread
import random

import select
import threading
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *
from torrent import Torrent
import message
import bitstring
import hashlib
import os
import peers_manager
from tracker import Tracker


class Pieces:
    def __init__(self):
        self.pieces_peers = {}
        self.pieces = {}
        tracker = Tracker()
        self.peers = tracker.peers
        torrent = tracker.torrent
        self.pieces_num = len(torrent.torrent['info']['pieces']) // 20
        for i in range(self.pieces_num):
            self.pieces_peers[i] = []
        for peer in self.peers:
            try:
                bitfield = peers_manager.check(peer, tracker)[:self.pieces_num]
                for id in range(self.pieces_num):
                    if bitfield[id] == '1':
                        self.pieces_peers[id].append(peer)
            except Exception as e:
                print(e)
                pass
        peer = random.choice(self.pieces_peers[0])

        for i in range(self.pieces_num):
            peer = random.choice(self.pieces_peers[i])
            try:
                self.pieces[i] = peers_manager.Peer(tracker, i).download(peer)
            except:
                pass
        print(self.pieces)
    def request_next(self):
        # if self.s == self.torrent.torrent['info']['piece length']:
        self.s -= 9  # without starters (only the block itself)
        temp = 0
        to_download = []
        for file in list(self.files):
            temp += file['length']
            if temp <= self.s:
                to_download.append((file['path'], file['length']))
                self.files = self.files[1:]
        for path in to_download:
            with open(f"{self.torrent_name}/{path[0][0]}", 'wb') as w:
                w.write(self.s_bytes[:path[1]])
                self.written += self.s_bytes[:path[1]]
                self.s_bytes = self.s_bytes[path[1]:]
        # if len(self.written+self.s_bytes) % self.torrent.torrent['info']['piece length'] == 0:
        if hashlib.sha1((self.written + self.s_bytes)[
                        self.c_piece * self.torrent.torrent['info']['piece length']: self.c_piece *
                                                                                     self.torrent.torrent[
                                                                                         'info'][
                                                                                         'piece length'] +
                                                                                     self.torrent.torrent[
                                                                                         'info'][
                                                                                         'piece length']]).digest() == \
                self.torrent.torrent['info']['pieces'][self.c_piece * 20: 20 * self.c_piece + 20]:
            print(f"success piece #{self.c_piece}, total --> {len(self.s_bytes)}")
            self.c_piece += 1
            self.s = 0
        self.sock.send(message.build_request(self.c_piece, self.s, 16384))


if __name__ == '__main__':
    Pieces()