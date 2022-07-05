import hashlib
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *


class Torrent:
    def __init__(self):
        with open('torrent.torrent', 'rb') as t:
            torrent = t.read()
        self.torrent = bencode.bdecode(torrent)
        self.url = urlparse(self.torrent['announce'])

    def generate_info_hash(self):
        info = bencode.encode(self.torrent['info'])
        return hashlib.sha1(info).digest()

    def size(self):
        return self.torrent['info']['piece length']
