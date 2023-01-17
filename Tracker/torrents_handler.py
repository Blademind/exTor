import os

import bencode
import hashlib

torrents = os.listdir("torrents")
info_torrent = {}

if len(torrents) != 0:
    for torrent in torrents:
        with open("torrents\\"+torrent, "rb") as f:
            t = f.read()
            try:
                info = bencode.bdecode(t)["info"]
                t = hashlib.sha1(bencode.encode(info)).digest()
                info_torrent[t] = torrent
            except bencode.exceptions.BencodeDecodeError:
                f.close()
                print(torrent, "is corrupted, removing file")
                os.remove("torrents\\"+torrent)
                print(torrent, "removed")


if __name__ == '__main__':
    print(info_torrent)