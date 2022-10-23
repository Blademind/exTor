import os

import bencode
import hashlib

torrents = os.listdir("torrents")
info_torrent = {}

for torrent in torrents:
    with open("torrents\\"+torrent, "rb") as f:
        t = f.read()
        info = bencode.bdecode(t)["info"]
        t = hashlib.sha1(bencode.encode(info)).digest()
        info_torrent[t] = torrent
