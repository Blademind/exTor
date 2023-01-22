import os
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
"""
=====IMPORTANT=====
TRACKER SENDS THE CLIENT BOTH THE LOCAL AND THE NORMAL TORRENT FILE TOGETHER, NOT ONLY THE LOCAL FILE
THE CLIENT DECIDES TO CONTACT THE NORMAL TORRENT FILE GIVEN THE PEERS IN THE LOCAL TORRENT FILE ARE NOT RESPONDING
OR PIECES ARE MISSING.
"""
def create_new_sock():
    """
    Creates a TCP socket
    :return: created TCP socket with its settings
    """
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.settimeout(1)
    return sock


class Handler:
    def __init__(self):
        """
        Create Handler object
        """
        self.tracker = Tracker()
        self.peers = list(set([tuple(peer) for peer in self.tracker.peers]))
        self.torrent = self.tracker.torrent

        manager.down = manager.Downloader(self.torrent, self.tracker)

        self.peer_list = []

        self.peer_thread = {}
        self.pieces = {}
        for i in range(len(self.torrent.torrent["info"]["pieces"]) // 20):
            self.pieces[i] = []
        self.rarest_piece(self.peers, self.tracker)
        self.currently_connected = []
        # for key in sorted(self.pieces, key=lambda k: len(self.pieces[k])):
        #     print(key, end=" ")


        # start error check
        # threading.Thread(target=self.check_errors).start()

        self.go_over_pieces()

        while len(manager.currently_connected) != 0:
            time.sleep(1)
        manager.DONE = True

        manager.down.bytes_file.close()  # closes the bytes file
        os.remove(f"torrents\\files\\{manager.down.torrent_name}\\bytes_file")

        print("Completed Download!")

        self.tracker.done_downloading()
        # for peer, thread in self.peer_thread.items():
        #     thread.join()

        while self.peer_list:
            obj = self.peer_list.pop(0)
            del obj

    def go_over_pieces(self):
        """
        Goes over all the piece
        :return:
        """
        for piece, k in enumerate(sorted(self.pieces, key=lambda p: p)):  # enumerate(sorted(self.pieces, key=lambda p: len(self.pieces[p])))
            if manager.down.have[k] == "0":
                print(f"currently working on: {k}#")
                self.peer_list.append(Peer(self.tracker))
                peer = self.peer_list[-1]  # create a peer object
                current_piece_peers = self.pieces[k]
                # no peers holding current piece
                if len(current_piece_peers) == 0:
                    raise Exception("no peers holding piece")
                # go over all piece holders
                try:
                    self.peer_piece_assignment(peer, k, current_piece_peers)
                except:
                    time.sleep(0.5)
                    raise Exception("operation stopped by user")

    def peer_piece_assignment(self, peer, k, current_piece_peers):
        """
        goes over peers in order to get a piece downloaded
        :param peer:
        :param k:
        :param current_piece_peers: the peers assigned to this piece
        :return:
        """

        # go over errors if there are any
        while manager.down.error_queue:
            peer_piece = manager.down.error_queue.pop(0)
            peer_ip_port, piece = peer_piece[0], peer_piece[1]
            print(piece)
            self.peer_list.append(Peer(self.tracker))
            peer_error_object = self.peer_list[-1]  # create a peer object
            # deletes all peer instances
            for piece_number, peers_list in self.pieces.items():
                if peer_ip_port in peers_list:
                    self.pieces[piece_number].remove(peer_ip_port)

            piece_peers = self.pieces[piece]

            for piece_peer in piece_peers:
                if piece_peer not in manager.currently_connected:
                    if piece_peer in self.peer_thread.keys():
                        threading.Thread(target=self.peer_thread[piece_peer].request_piece, args=(piece,)).start()
                    else:
                        manager.currently_connected.append(piece_peer)
                        self.peer_thread[piece_peer] = peer_error_object
                        threading.Thread(target=peer_error_object.download, args=(piece_peer, piece)).start()
                    break
                else:
                    threading.Thread(target=self.peer_thread[piece_peer].request_piece(piece)).start()
                    break

        for p in current_piece_peers:
            if p not in manager.currently_connected:
                if p in self.peer_thread.keys():
                    threading.Thread(target=self.peer_thread[p].request_piece, args=(k,)).start()
                else:
                    manager.currently_connected.append(p)
                    self.peer_thread[p] = peer
                    threading.Thread(target=peer.download, args=(p, k)).start()
                break

            # last peer and was not caught beforehand - all conns in use
            if p == current_piece_peers[-1]:
                last_piece_length = len(manager.currently_connected)
                while len(manager.currently_connected) == last_piece_length:
                    time.sleep(0.01)
                    pass
                self.peer_piece_assignment(peer, k, current_piece_peers)
                break

    def connect_to_peer(self, peers, sock, current_peer, tracker):
        try:
            sock.connect(peers[current_peer])
            sock.send(message.build_handshake(tracker))
            data = sock.recv(68)  # read handshake
            if message.is_handshake(data):
                print("HANDSHAKE")
                msg_len = int.from_bytes(sock.recv(4), "big")
                data = sock.recv(msg_len)
                if message.msg_type(data) == 'bitfield':
                    # print(data)
                    data = bitstring.BitArray(data[1:])
                    print("BITFIELD", data , peers[current_peer])

                    # print(bitstring_to_bytes(data.bin))
                    # print(data.bin)
                    for t, i in enumerate(data.bin):
                        if i == "1":
                            self.pieces[t].append(sock.getpeername())
            sock.close()
        except:
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
        if len(socks) != 0:  # at least one peer is in swarms
            a = []
            current_peer = 0
            for sock in socks:
                a.append(threading.Thread(target=self.connect_to_peer, args=(peers, sock, current_peer, tracker)))
                current_peer += 1

            for thread in a:
                thread.start()
                time.sleep(0.01)  # create a small delay to create a gap
            a[-1].join()  # last thread has ended

        time.sleep(0.5)  # some peers are slow, gives them some time to delete client's instance from them
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
