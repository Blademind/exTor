import threading
import time
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *
from tracker import Tracker
from torrent import Torrent
from peers import Peer


def rarest_piece(peers):
    socks = []
    for i in range(len(peers)):
        socks.append(create_sock())
    current_peer = 0
    for sock in socks:
        threading.Thread(target=connect_to_peer, args=(peers, sock, current_peer)).start()
        current_peer += 1

    return


def connect_to_peer(peers, sock, current_peer):
    try:
        print(peers[current_peer])
        sock.connect(peers[current_peer])
        print(f"connected to {current_peer}")
    except Exception as e:
        print(e)
        pass


def create_sock():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    return sock

try:
    tracker = Tracker()
    peers = tracker.peers
    torrent = tracker.torrent

    pieces = rarest_piece(peers)

    print(pieces)
    print('list of peers:', peers)

    peer = Peer(tracker)

    for peer_info in peers:
        try:
            peer.download(peer_info, 1)
        except Exception as e:
            peer.create_new_sock()
            print(e)
            pass

    # peer.stop_thread = True
    print(peers)
except Exception as e:
    print("Error fetching the file")

