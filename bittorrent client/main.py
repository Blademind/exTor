import socket
import threading
import time
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *
from tracker import Tracker
from torrent import Torrent
from peers import Peer
import message_handler as message
import bitstring
import peers_manager as manager
import asyncio


def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')


def create_new_sock():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.settimeout(1)
    return sock


class Handler:
    def __init__(self):
        try:
            self.tracker = Tracker()
            self.peers = self.tracker.peers
            self.torrent = self.tracker.torrent
            self.pieces = {}
            self.peer_objs = []
            for i in range(len(self.torrent.torrent["info"]["pieces"]) // 20):
                self.pieces[i] = []
            self.rarest_piece(self.peers, self.tracker)
            self.currently_connected = []
            # print(self.pieces)

            for k in sorted(self.pieces, key=lambda k: len(self.pieces[k])):
                peer = Peer(self.tracker)  # create a peer object
                self.peer_objs.append(peer)
                self.current_piece_peers = self.pieces[k]

                # no peers holding current piece
                if len(self.current_piece_peers) == 0:
                    raise Exception("no peers holding piece")

                # go over all piece holders
                for p in self.current_piece_peers:
                    # print(p)
                    if p not in manager.currently_connected:
                        manager.currently_connected.append(p)
                        threading.Thread(target=peer.download, args=(p, k, self.current_piece_peers)).start()
                        break

                    # last peer and was not caught beforehand - all conns in use
                    if p == self.current_piece_peers[-1]:
                        last_piece_length = len(manager.currently_connected)
                        while len(manager.currently_connected) == last_piece_length:
                            time.sleep(0.1)

        except Exception as e:
            print(e)
            pass

    def connect_to_peer(self, peers, sock, current_peer, tracker):
        try:
            sock.connect(peers[current_peer])
            sock.send(message.build_handshake(tracker))
            data = sock.recv(68)  # read handshake

            if message.is_handshake(data):
                msg_len = int.from_bytes(sock.recv(4), "big")
                data = sock.recv(msg_len)
                if message.msg_type(data) == 'bitfield':
                    data = bitstring.BitArray(data[1:])
                    # print(bitstring_to_bytes(data.bin))
                    # print(data.bin)
                    for t, i in enumerate(data.bin):
                        if i == "1":
                            self.pieces[t].append(sock.getpeername())

        except Exception as e:
            return

    def rarest_piece(self, peers, tracker):
        """
        finds all pieces and their rarity.
        :param peers:
        :param tracker:
        :return:
        """
        # asyncio.run(self.peer_instances(peers, tracker))
        socks = [create_new_sock() for i in range(len(peers))]
        a = []
        current_peer = 0
        for sock in socks:
            a.append(threading.Thread(target=self.connect_to_peer, args=(peers, sock, current_peer, tracker)))
            current_peer += 1

        for thread in a:
            thread.start()
            time.sleep(0.01)  # create a small delay to create a gap
        a[-1].join()  # last thread has ended

# region ASYNC SOLUTION
#     async def conn_task(self, peers, current_peer, tracker):
#         try:
#             conn = asyncio.open_connection(peers[current_peer][0], peers[current_peer][1])
#             reader, writer = await asyncio.wait_for(conn, timeout=1)
#             writer.write(message.build_handshake(tracker))
#             await writer.drain()
#             data = await asyncio.wait_for(reader.read(68), timeout=1) # read handshake
#
#             if message.is_handshake(data):
#                 msg_len = int.from_bytes(await reader.read(4), "big")
#                 data = await reader.read(msg_len)
#                 if message.msg_type(data) == 'bitfield':
#                     data = bitstring.BitArray(data[1:])
#                     # print(bitstring_to_bytes(data.bin))
#                     # print(data.bin)
#                     for t, i in enumerate(data.bin):
#                         if i == "1":
#                             self.pieces[t].append(peers[current_peer])
#             conn.close()
#             return
#         except (ConnectionResetError, TimeoutError, ConnectionRefusedError):
#             return
#
#     async def connect_to_peer(self, peers, current_peer, tracker):
#         # print(peers[current_peer])
#         # print(f"connected to {current_peer}")
#
#         await self.conn_task(peers, current_peer, tracker)
#
#     async def peer_instances(self, peers, tracker):
#         peer_connections = [self.connect_to_peer(peers, current_peer, tracker) for current_peer in range(len(peers))]
#         await asyncio.gather(*peer_connections)

    # def rarest_piece(self, peers, tracker):
        #     """
        #     finds all pieces and their rarity.
        #     :param peers:
        #     :param tracker:
        #     :return:
        #     """
        #     socks = []
        #     for i in range(len(peers)):
        #         socks.append(create_new_sock())
        #     current_peer = 0
        #     a = []
        # asyncio.run(self.peer_instances(socks, peers, tracker))
# endregion


if __name__ == '__main__':
    Handler()
