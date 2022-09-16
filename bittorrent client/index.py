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
for peer in peers:
    try:
        if peer[0] != '221.230.166.76':
            Peer(tracker).download(peer)
            break
    except Exception as e:
        print(e)
        pass

