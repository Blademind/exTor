import time
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *
from tracker import Tracker
from torrent import Torrent
from peers import Peer


tracker = Tracker()
peers = tracker.peers
torrent = tracker.torrent

print('list of peers:', peers)

peer = Peer(tracker)
for peer_info in peers:
    try:
        peer.download(peer_info)
    except Exception as e:
        print(e)
        pass

