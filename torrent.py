import hashlib
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *


class Torrent:
    def __init__(self):
        with open('KNOPPIX.torrent', 'rb') as t:
            torrent = t.read()
        self.torrent = bencode.bdecode(torrent)
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
        try:
            for tracker in self.torrent['announce-list']:
                for sub in tracker:
                    if 'udp' in sub:
                        try:
                            yield urlparse(sub)
                        except GeneratorExit:
                            break
                    elif 'http' in sub:
                        yield sub
        except:
            yield urlparse(self.torrent['announce']) if 'udp' in self.torrent['announce'] else self.torrent['announce']
