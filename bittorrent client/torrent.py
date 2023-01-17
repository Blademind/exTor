import hashlib
import os
import random
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *

import bencodepy.exceptions


class Torrent:
    def __init__(self):
        self.port = random.randint(6881, 6889)
        # torrents = os.listdir("torrents\\info_hashes")
        # for torrent in torrents:
        #     print(torrents.index(torrent), torrent)
        # index = input("what torrent would you like to download? ->\t")
        # with open(f'torrents\\info_hashes\\{torrents[int(index)]}', 'rb') as t:
        #     torrent = t.read()
        # self.torrent = bencode.bdecode(torrent)
        # print(self.torrent["announce-list"] is not None)

        torrent_name = input("what torrent would you like to download? ->\t")


        try:
            self.announce_list = self.torrent["announce-list"]
        except:
            self.announce_list = []
        self.announce_list.insert(0, [self.torrent["announce"]])
        self.url_yields = self.next_tracker()
        self.url = self.url_yields.__next__()

    def generate_info_hash(self):
        info = bencode.encode(self.torrent['info'])
        return hashlib.sha1(info).digest()

    def size(self):
        try:
            return self.torrent['info']['length']
        except:
            s = 0
            for file in self.torrent['info']['files']:
                s += file['length']
            return s

    def next_tracker(self):
        for tracker in self.announce_list:
            for sub in tracker:
                if 'udp' in sub:
                    yield urlparse(sub)
                elif 'http' in sub:
                    yield sub
                else:  # might be wss? not supported yet
                    yield
        yield

