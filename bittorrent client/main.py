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


# TODO: Before starting download make contact with info server, do not contact the trackers in file before checking
#  with LAN tracker, make contact with the outside only when needed
class Handler:
    def __init__(self):
        try:
            self.tracker = Tracker()
            self.peers = list(set(self.tracker.peers))
            self.torrent = self.tracker.torrent
            manager.down = manager.Downloader(self.torrent, self.tracker)
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
            for piece, k in enumerate(sorted(self.pieces, key=lambda p: len(self.pieces[p]))):
                # print("test:",piece,k)
                # print(f"piece no. {k} is {manager.down.have[k] == '0'}*")
                if manager.down.have[k] == "0":
                    print(f"currently working on: {k}#")
                    peer = Peer(self.tracker)  # create a peer object
                    self.current_piece_peers = self.pieces[k]
                    # no peers holding current piece
                    if len(self.current_piece_peers) == 0:
                        raise Exception("no peers holding piece")

                    # go over all piece holders
                    self.recursive_peers(peer, k)
            while len(manager.currently_connected) != 0:
                time.sleep(1)
            manager.DONE = True
            print("Completed Download!")

        except Exception as e:
            print("exception: ", e)
            pass

    def recursive_peers(self, peer, k):
        """
        TODO: SOMEWHERE IN THIS FUNCTION THE DOWNLOAD GETS STUCK
        goes over peers recursively in order to get a piece downloaded
        :param peer:
        :param k:
        :return:
        """
        for p in self.current_piece_peers:
            # print(p)
            if p not in manager.currently_connected:

                if p in self.peer_thread.keys():
                    threading.Thread(target=self.peer_thread[p].request_piece, args=(k,)).start()
                else:
                    manager.currently_connected.append(p)
                    self.peer_thread[p] = peer
                    threading.Thread(target=peer.download, args=(p, k)).start()
                break

            # last peer and was not caught beforehand - all conns in use
            if p == self.current_piece_peers[-1]:
                last_piece_length = len(manager.currently_connected)
                while len(manager.currently_connected) == last_piece_length:
                    time.sleep(0.5)

                while manager.down.error_queue:
                    peer_piece = manager.down.error_queue.pop(0)
                    peer_ip_port, piece = peer_piece[0], peer_piece[1]
                    peer_error_object = Peer(self.tracker)  # create a peer object
                    # deletes all peer instances
                    for piece_number, peers_list in self.pieces.items():
                        for peer_id in peers_list:
                            if peer_id == peer_ip_port:
                                self.pieces[piece_number].remove(peer_id)
                    current_piece_peers = self.pieces[piece]

                    for piece_peer in current_piece_peers:
                        # print(p)
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

                last_piece_length = len(manager.currently_connected)
                while len(manager.currently_connected) == last_piece_length:
                    time.sleep(0.5)

                self.current_piece_peers = self.pieces[k]
                for p3 in self.current_piece_peers:
                    # print(p)
                    if p3 not in manager.currently_connected:

                        if p3 in self.peer_thread.keys():
                            threading.Thread(target=self.peer_thread[p3].request_piece, args=(k,)).start()
                        else:
                            manager.currently_connected.append(p3)
                            self.peer_thread[p3] = peer
                            threading.Thread(target=peer.download, args=(p3, k)).start()
                        break

                break

    def connect_to_peer(self, peers, sock, current_peer, tracker):
        try:
            sock.connect(peers[current_peer])
            sock.send(message.build_handshake(tracker))
            data = sock.recv(68)  # read handshake
            if message.is_handshake(data):
                # print("HANDSHAKE")
                msg_len = int.from_bytes(sock.recv(4), "big")
                data = sock.recv(msg_len)
                if message.msg_type(data) == 'bitfield':
                    # print(data)
                    data = bitstring.BitArray(data[1:])
                    # print(bitstring_to_bytes(data.bin))
                    # print(data.bin)
                    for t, i in enumerate(data.bin):
                        if i == "1":
                            self.pieces[t].append(sock.getpeername())

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

    # def check_errors(self):
    #     while 1:
    #         while manager.down.error_queue:
    #             peer_piece = manager.down.error_queue.pop(0)
    #             peer, piece = peer_piece[0], peer_piece[1]
    #
    #             # deletes peer instances
    #             for k,v in self.pieces.items():
    #                 for p in v:
    #                     if p == peer:
    #                         self.pieces[k].remove(p)
    #
    #             current_piece_peers = self.pieces[piece]
    #             for p in current_piece_peers:
    #                 # print(p)
    #                 if p not in manager.currently_connected:
    #                     manager.currently_connected.append(p)
    #                     threading.Thread(target=peer.download, args=(p, k, self.current_piece_peers)).start()
    #                     break
    #
    #             peer = Peer(self.tracker)  # create a peer object
    #             threading.Thread(target=peer.download, args=(peer, piece, self.current_piece_peers)).start()
    #
    #         time.sleep(0.5)

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
