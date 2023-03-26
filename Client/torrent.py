import hashlib
import random
import time

import bencode
from urllib.parse import urlparse
from contextlib import closing
from socket import *

class Torrent:
    """
    The Torrent object, everything regarding the torrent is located here
    """
    def __init__(self, port = None):
        self.url = None
        self.url_yields = None
        self.announce_list = None
        self.torrent = None
        if not port:
            self.port = random.randint(6881, 6889)

            s = socket(AF_INET, SOCK_DGRAM)
            try:
                s.bind(("0.0.0.0", self.port))
            except:
                open_port = self.find_open_port(s)
                print("open port:", open_port)

                self.port = open_port
        else:
            self.port = port
        # torrents = os.listdir("torrents\\info_hashes")
        # for torrent in torrents:
        #     print(torrents.index(torrent), torrent)
        # index = input("what torrent would you like to download? ->\t")

    def find_open_port(self, s):
        s.bind(("0.0.0.0", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    def init_torrent_seq(self, file_name, local):
        print(file_name)
        with open(f'torrents\\info_hashes\\{file_name}', 'rb') as t:
            torrent = t.read()
        self.torrent = bencode.bdecode(torrent)
        # print(self.torrent["announce-list"] is not None)

        if not local:
            try:
                self.announce_list = self.torrent["announce-list"]
            except:
                self.announce_list = []
            self.announce_list.insert(0, [self.torrent["announce"]])  # there is usually one more tracker in announce whether than in announce list, pop him in
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

