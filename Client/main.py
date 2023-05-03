import os
import socket
import sqlite3
import threading
import time
from socket import *
from tracker import Tracker
from peers import Peer
import message_handler as message
import bitstring
import peers_manager as manager
import atexit
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
    sock.settimeout(2)
    return sock


class Handler:
    def __init__(self, given_name=None, path=None, port=None, ui_given_name=None):
        """
        Create Handler object
        """
        self.currently_connected = None
        self.pieces = None
        self.peer_thread = None
        self.peer_list = None
        self.tracker = None
        self.c = 0
        if not os.path.exists("torrents"):
            os.makedirs("torrents\\info_hashes")
            os.makedirs("torrents\\files")

        if not os.path.exists("torrents\\info_hashes"):
            os.makedirs("torrents\\info_hashes")

        if not os.path.exists("torrents\\files"):
            os.makedirs("torrents\\files")
        try:
            if not given_name:
                print("not given name")
                self.tracker = Tracker(ui_given_name=ui_given_name)
            else:
                print("given name")
                self.tracker = Tracker(given_name=given_name, path=path, port=port)

            if given_name or self.tracker.local_tracker:  # local tracker must be found for a download to start (or a
                # name of a file which already is present on disk was given)
                self.torrent = self.tracker.torrent

                manager.down = manager.Downloader(self.torrent, self.tracker)

                # There are pieces which can be downloaded
                if manager.down.num_of_pieces - manager.down.count_bar != 0:
                    self.tracker.contact_trackers()
                    for thread in self.tracker.threads:
                        thread.join()

                    self.peers = list(set(self.tracker.peers))  # list of peers fetched from trackers
                    print(self.peers)
                    manager.down.listen_seq()  # listen to peers (for pieces sharing)
                    manager.down.generate_download_bar()  # PROGRESS
                    self.download()

                # All pieces present on disk
                else:
                    for name, file in manager.down.files_data.items():
                        file.close()
                    manager.down.progress_flag = False

                    manager.down.listen_seq()  # listen to peers (for pieces sharing)
                    self.tracker.done_downloading(manager.sharing_peers)

        except TypeError:
            # a name of file was not given before program was closed by the user
            pass
        except Exception as e:
            print("Exception (at main):", e)
            try:
                manager.down.progress_flag = False

                manager.DONE = True
            except: pass

            if self.tracker and self.tracker.global_flag:
                try:
                    self.tracker.contact_trackers()
                    self.peers = list(set(self.tracker.peers))
                    self.torrent = self.tracker.torrent
                    manager.reset_to_default()
                    manager.down.generate_download_bar()  # PROGRESS
                    self.download()
                except:
                    try:
                        manager.down.progress_flag = False

                        manager.DONE = True
                        if manager.down.files_data:
                            for name, file in manager.down.files_data.items():
                                file.close()
                        print(e)
                    except:
                        pass
            else:
                if manager.down and manager.down.files_data:
                    for name, file in manager.down.files_data.items():
                        file.close()
                print(e)

    def download(self):
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
            self.check_errors()

        self.check_errors()


        # manager.down.bytes_file.close()  # closes the bytes file
        # os.remove(f"torrents\\files\\{manager.down.torrent_name}\\bytes_file")

        for name, file in manager.down.files_data.items():
            file.close()

        manager.DONE = True
        print("Completed Download!")

        manager.down.progress_flag = False
        self.tracker.done_downloading(manager.sharing_peers)

    def go_over_pieces(self):
        """
        Goes over all the piece
        :return:
        """
        for piece, k in enumerate(sorted(self.pieces, key=lambda p: len(self.pieces[p]))):
            # print(piece, self.pieces[k])
            if manager.down.have[k] == "0":
                peer = Peer(self.tracker)  # create a peer object
                current_piece_peers = self.pieces[k]
                # no peers holding current piece
                if len(current_piece_peers) == 0:
                    raise Exception("no peers holding piece")
                # print(piece)
                # go over all piece holders
                try:
                    self.peer_piece_assignment(peer, k, current_piece_peers)
                except:
                    time.sleep(0.5)
                    raise Exception("operation stopped by user")

    def remove_peer_instances(self, peer_ip_port):
        for piece_number, peers_list in self.pieces.items():
            if peer_ip_port in peers_list:
                self.pieces[piece_number].remove(peer_ip_port)

    def check_errors(self):

        if manager.down.error_queue:
            while manager.down.error_queue:
                peer_piece = manager.down.error_queue.pop(0)
                peer_ip_port, piece = peer_piece[0], peer_piece[1]
                print("error handling:", piece)
                peer_error_object = Peer(self.tracker)  # create a peer object

                self.remove_peer_instances(peer_ip_port)

                piece_peers = self.pieces[piece]  # all peers sharing that piece
                self.peer_piece_assignment(peer_error_object, piece, piece_peers)

    def peer_piece_assignment(self, peer, k, current_piece_peers):
        """
        goes over peers in order to get a piece downloaded
        :param peer:
        :param k:
        :param current_piece_peers: the peers assigned to this piece
        :return:
        """

        # go over errors if there are any
        self.check_errors()
        for p in current_piece_peers:
            if p not in manager.currently_connected:
                if p in self.peer_thread.keys():
                    threading.Thread(target=self.peer_thread[p].request_piece, args=(k,)).start()
                else:
                    manager.currently_connected.append(p)
                    self.peer_thread[p] = peer
                    threading.Thread(target=peer.download, args=(p, k)).start()

                self.check_errors()
                break

            # last peer and was not caught beforehand - all conns in use
            if p == current_piece_peers[-1]:
                last_piece_length = len(manager.currently_connected)
                while len(manager.currently_connected) == last_piece_length:
                    time.sleep(0)

                self.peer_piece_assignment(peer, k, current_piece_peers)
                break

    def connect_to_peer(self, peers, sock, current_peer, tracker):
        flag = False
        try:
            sock.connect(peers[current_peer])
            sock.send(message.build_handshake(tracker))
            data = sock.recv(68)  # read handshake
            if message.is_handshake(data):
                print("HANDSHAKE")
                flag = True
                msg_len = int.from_bytes(sock.recv(4), "big")
                data = sock.recv(msg_len)
                if message.msg_type(data) == 'bitfield':
                    data = bitstring.BitArray(data[1:])
                    print("BITFIELD", data.bin, peers[current_peer])
                    for t, i in enumerate(data.bin):
                        if i == "1":
                            self.pieces[t].append(sock.getpeername())
            sock.close()

        # risky
        except timeout:
            if flag:
                for i in range(manager.down.num_of_pieces):
                    self.pieces[i].append(sock.getpeername())

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
        socks = [create_new_sock() for _ in range(len(peers))]
        if len(socks) != 0:  # at least one peer is in swarms
            a = []
            current_peer = 0
            for sock in socks:
                a.append(threading.Thread(target=self.connect_to_peer, args=(peers, sock, current_peer, tracker)))
                current_peer += 1

            for thread in a:
                thread.start()
                time.sleep(0.01)  # create a small delay to create a gap
            for thread in a:
                thread.join()
            # a[-1].join()  # last thread has ended

        time.sleep(1)  # some peers are slow, gives them some time to delete client's instance from them

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


# def exit_function():
#     dir = "torrents\\info_hashes"
#     info_hashes = os.listdir(dir)
#     for metadata in info_hashes:
#         if metadata[-15:-8] == "_UPLOAD":
#             os.remove(f"{dir}\\{metadata}")


if __name__ == '__main__':
    # atexit.register(exit_function,)

    Handler()
