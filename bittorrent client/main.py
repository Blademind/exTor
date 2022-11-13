import time
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *
from tracker import Tracker
from torrent import Torrent
from peers import Peer



try:
    tracker = Tracker()
    peers = tracker.peers
    torrent = tracker.torrent

    print('list of peers:', peers)

    peer = Peer(tracker)

    for peer_info in peers:
        try:
            peer.download(peer_info)
        except Exception as e:
            peer.create_new_sock()
            print(e)
            pass

    # peer.stop_thread = True
    print(peers)
except:
    print("Error fetching the file")

