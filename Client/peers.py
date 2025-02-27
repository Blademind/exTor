import socket
import time
import threading
from socket import *
import message_handler as message
import bitstring
import hashlib
import peers_manager as manager

"""
Made by Alon Levy
"""

class Peer:
    def __init__(self, tracker):
        self.peer_removed = False
        self.done_piece_download = False
        self.peer = None
        self.total_current_piece_length = None
        self.sock = None
        self.retry_peer = False
        self.s = 0  # pieces management
        self.c_piece = 0
        self.s_bytes = b''
        self.in_progress = False
        self.all_downloaded = 0  # downloaded files
        self.block = b''
        self.length = 0
        self.tracker = tracker
        self.torrent = tracker.torrent
        self.__BUF = 1024
        self.size = self.torrent.size()
        self.block_len = 16384
        self.pieces = self.torrent.torrent['info']['pieces']
        self.piece_length = self.torrent.torrent['info']['piece length']
        self.num_of_pieces = len(self.pieces) // 20  # number of pieces in torrent

        try:
            self.files = self.torrent.torrent['info']['files']
        except:
            self.files = self.torrent.torrent['info']

        self.torrent_name = self.torrent.torrent['info']['name']
        self.peers = tracker.peers

        self.sock = None
        self.sock = self.create_new_sock()
        self.buf = 68  # initial buffer size 68 for BitTorrent handshake message

    def change_timeout(self, timeout):
        self.sock.settimeout(timeout)

    def is_handshake_hash(self, handshake_msg):
        """
        does the handshake hash match desired torrent's hash?
        :param handshake_msg:
        :return:
        """
        return handshake_msg[28: 28 + len(self.torrent.generate_info_hash())] == self.torrent.generate_info_hash()

    def create_new_sock(self):
        if self.sock:
            self.sock.close()
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.settimeout(10)
        return sock

    def request_piece(self, piece_number):
        try:
            if self.in_progress:
                while 1:
                    if self.done_piece_download:
                        with manager.request_lock:
                            self.done_piece_download = False
                            break
                    if self.peer_removed:
                        raise Exception(f"Peer {self.peer} Removed")
                    time.sleep(0.01)

            if not self.peer_removed:
                with manager.lock:
                    manager.currently_connected.append(self.peer)
                self.c_piece = piece_number
                self.total_current_piece_length = self.piece_length if self.c_piece != self.num_of_pieces - 1 else self.size - self.piece_length * self.c_piece
                if self.c_piece == self.num_of_pieces - 1:
                    if self.total_current_piece_length >= self.block_len:
                        self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
                    else:
                        self.sock.send(message.build_request(self.c_piece, self.s, self.total_current_piece_length))
                else:
                    self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
            else:
                raise Exception(f"Peer {self.peer} Removed")

        except Exception as e:
            print("Error piece request:", e)
            # time.sleep(0.5)  # sleep
            with manager.lock:
                if self.peer in manager.currently_connected:
                    manager.currently_connected.remove(self.peer)
                manager.down.error_queue.append((self.peer, piece_number))
            self.peer_removed = True
            print(f"peer {self.peer} Actually removed")

    def download(self, peer, piece_number):
        try:
            self.peer = peer
            self.c_piece = piece_number
            self.total_current_piece_length = self.piece_length if self.c_piece != self.num_of_pieces - 1 else self.size - self.piece_length * self.c_piece
            print("Trying", peer[0], peer[1])
            self.sock.connect((peer[0], peer[1]))
            print(f'successfully connected to {peer[0]}:{peer[1]}')
            self.sock.send(message.build_handshake(self.tracker))
            self.listen_to_server()
        except Exception as e:
            print(e)
            with manager.lock:
                manager.currently_connected.remove(self.peer)
                manager.down.error_queue.append((self.peer, self.c_piece))
            self.peer_removed = True

    def listen_to_server(self):
        while 1:
            try:
                data = self.sock.recv(self.buf)

                if not data:
                    raise Exception("data length 0", self.c_piece)

                if manager.DONE:
                    break

                self.message_handler(data)

            except TimeoutError:
                if not self.done_piece_download:
                    print("Timeout", self.c_piece)
                    with manager.lock:
                        if self.peer in manager.currently_connected:
                            manager.currently_connected.remove(self.peer)
                        manager.down.error_queue.append((self.peer, self.c_piece))
                    self.peer_removed = True
                break

            except timeout:
                if not manager.DONE:
                    if not self.done_piece_download:
                        print("TIMEOUT")
                    else:
                        print("TIMEOUT (THOUGH WONT BE REMOVED)")
                else:
                    print("CLOSED CONNECTION (DONE)")

                if not self.done_piece_download or manager.DONE:
                    with manager.lock:
                        if self.peer in manager.currently_connected:
                            manager.currently_connected.remove(self.peer)
                        manager.down.error_queue.append((self.peer, self.c_piece))
                    self.peer_removed = True
                    break

                elif self.done_piece_download:
                    self.sock = self.create_new_sock()

            except Exception as e:
                print("peer exception:", print(e))
                # inside error, try another request
                if e == "data length mismatch":
                    self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))

                else:
                    # time.sleep(1)  # sleep
                    with manager.lock:
                        if self.peer in manager.currently_connected:
                            manager.currently_connected.remove(self.peer)
                        manager.down.error_queue.append((self.peer, self.c_piece))
                    self.peer_removed = True
                    print(f"peer {self.peer} Actually removed")

                    break

        if self.sock:
            self.sock.close()


    def message_handler(self, data):
        """

        :param data: Data received by the peer connected
        :return: DONE if done downloading all blocks required for a piece
        """
        message_type = message.msg_type(data)
        # message is piece
        if message_type == "piece":
            while len(data) != self.buf:
                data += self.sock.recv(self.buf)

            data = data[9:]
            self.s_bytes += data

            # data received for block must be requested block length
            if len(data) == self.block_len:
                self.s += len(data)
            else:
                if not self.c_piece == self.num_of_pieces - 1:
                    raise Exception("data length mismatch")
            self.buf = 4

            if self.s != self.piece_length:
                # a unique if statement for last piece
                if self.c_piece == self.num_of_pieces - 1:
                    if hashlib.sha1(self.s_bytes).digest() == self.pieces[self.c_piece * 20: self.c_piece * 20 + 20]:
                        print(f"success piece #{self.c_piece}, last piece", self.peer)
                        threading.Thread(target=manager.down.add_piece_data, args=(self.c_piece, self.s_bytes)).start()

                        # reset buffer, sum, and bytes sum
                        self.buf = 4
                        self.s = 0
                        self.s_bytes = b""

                        self.done_piece_download = True

                        threading.Thread(target=manager.down.update_have, args=(self.c_piece,)).start()  # updates "have"
                        threading.Thread(target=manager.remove_peer,
                                         args=(self.peer,)).start()  # removes peer from currently connected

                        threading.Thread(target=manager.down.add_sharing_peer,
                                         args=(self.peer,)).start()  # adds peer to sharing peers list

                        return

                    if self.total_current_piece_length >= self.block_len:
                        if self.total_current_piece_length - len(self.s_bytes) < self.block_len:
                            self.sock.send(message.build_request(self.c_piece, self.s,
                                                                 self.total_current_piece_length - len(self.s_bytes)))
                        else:
                            self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
                    else:
                        self.sock.send(message.build_request(self.c_piece, self.s, self.total_current_piece_length))
                else:
                    self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
            else:
                # checks if downloaded piece matches current piece hash
                if hashlib.sha1(self.s_bytes).digest() == self.pieces[
                                                          self.c_piece * 20: 20 * self.c_piece + 20]:
                    print(f"success piece #{self.c_piece}, total --> {self.s}", self.peer)
                    threading.Thread(target=manager.down.add_piece_data, args=(self.c_piece, self.s_bytes)).start()

                    # reset buffer, sum, and bytes sum
                    self.buf = 4
                    self.s = 0
                    self.s_bytes = b""

                    self.done_piece_download = True

                    threading.Thread(target=manager.down.update_have, args=(self.c_piece,)).start()  # updates "have"
                    threading.Thread(target=manager.remove_peer,
                                     args=(self.peer,)).start()  # removes peer from currently connected

                    threading.Thread(target=manager.down.add_sharing_peer,
                                     args=(self.peer,)).start()  # adds peer to sharing peers list

                    return
                    # self.have_msg()  # send have message to all connected peers
        # message is handshake
        elif message.is_handshake(data):
            # print("handshake", self.peer)
            self.buf = 4
            if self.is_handshake_hash(data):
                print("hash matches")
                self.sock.send(message.build_interested())

        # message is bitfield
        elif message_type == "bitfield":
            # print("bitfield")
            while len(data) != self.buf:
                data += self.sock.recv(self.buf)
            data = bitstring.BitArray(data[1:])

            print(data.bin)
            self.buf = 4

        # message is unchoke
        elif message_type == "unchoke":
            # print("unchoke")
            if not self.in_progress:
                # last piece algorithm
                if self.c_piece == self.num_of_pieces - 1:
                    if self.total_current_piece_length >= self.block_len:
                        self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
                    else:
                        self.sock.send(message.build_request(self.c_piece, self.s, self.total_current_piece_length))
                else:
                    self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
                self.in_progress = True
            self.buf = 4

        # message is choke
        elif message_type == "choke":
            # print("choke")
            raise Exception("choked")

        # message is have
        elif message_type == "have":
            # print("have")
            self.buf = 4

        # message is keep-alive
        elif message_type == "keep-alive" and self.buf == 4:
            # print("keep-alive")
            pass

        # message is next message length (no id)
        else:
            if len(data) != 0:
                msg_len = int.from_bytes(data, "big")
                self.buf = msg_len


# region TRASH
#     def request_next_block(self):
#         """
#         Requests next piece in line
#
#         :return:
#         """
#         if self.s - 9 > 0:
#             self.s -= 9  # without starters (only the block itself)
#             temp = 0
#             to_download = []
#             for file in list(self.files):
#                 temp += file['length']
#                 if temp <= len(self.s_bytes):
#                     to_download.append((file['path'], file['length']))
#                     self.files = self.files[1:]
#             for path in to_download:
#                 with open(f"torrents\\files\\{self.torrent_name}\\{path[0][0]}", 'wb') as w:
#                     w.write(self.s_bytes[:path[1]])
#                     self.written += self.s_bytes[:path[1]]
#                     self.s_bytes = self.s_bytes[path[1]:]
#                 print("done writing", path)
#
#             # checks if downloaded piece matches current piece hash
#             if hashlib.sha1((self.written + self.s_bytes)[
#                             self.c_piece * self.piece_length: self.c_piece * self.piece_length + self.piece_length]).digest() == self.pieces[
#                                                                                                                                  self.c_piece * 20: 20 * self.c_piece + 20]:
#                 print(f"success piece #{self.c_piece}, total --> {len(self.s_bytes)}")
#                 temp = list(self.have)
#                 temp[self.c_piece] = "1"
#                 self.have = "".join(temp)
#                 self.have_msg()
#
#                 self.c_piece += 1
#                 self.s = 0
#
#             # a unique if statement for last piece
#             elif hashlib.sha1(self.written[self.c_piece * self.piece_length:]).digest() == self.pieces[
#                                                                                            self.c_piece * 20: 20 * self.c_piece + 20]:
#                 temp = list(self.have)
#                 temp[self.c_piece] = "1"
#                 self.have = "".join(temp)
#
#                 print(f"success piece #{self.c_piece}, last piece")
#
#             self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
#         else:
#             self.request_again(self.s)  # data was received incorrectly, request again.
#
#     def request_next_block2(self):
#         """
#         Requests next piece in line
#
#         :return:
#         """
#         print(self.s)
#         if self.s - 9 > 0:
#             self.s -= 9  # without starters (only the block itself)
#             # temp = 0
#             # to_download = []
#             # for file in list(self.files):
#             #     temp += file['length']
#             #     if temp <= len(self.s_bytes):
#             #         to_download.append((file['path'], file['length']))
#             #         self.files = self.files[1:]
#             # for path in to_download:
#             #     with open(f"torrents\\files\\{self.torrent_name}\\{path[0][0]}", 'wb') as w:
#             #         w.write(self.s_bytes[:path[1]])
#             #         self.written += self.s_bytes[:path[1]]
#             #         self.s_bytes = self.s_bytes[path[1]:]
#             #     print("done writing", path)
#
#             # checks if downloaded piece matches current piece hash
#             if hashlib.sha1(self.s_bytes).digest() == self.pieces[self.c_piece * 20: 20 * self.c_piece + 20]:
#                 print(f"success piece #{self.c_piece}, total --> {len(self.s_bytes)}")
#                 self.piece_downloaded = True
#                 manager.currently_connected.remove(self.sock.getpeername())
#                 # self.have_msg()  # send have message to all connected peers
#                 # self.c_piece += 1
#                 # self.s = 0
#
#             # a unique if statement for last piece
#             elif hashlib.sha1(self.s_bytes).digest() == self.pieces[self.c_piece * 20: 20 * self.c_piece + 20]:
#                 temp = list(self.have)
#                 temp[self.c_piece] = "1"
#                 self.have = "".join(temp)
#                 print(f"success piece #{self.c_piece}, last piece")
#             else:
#                 self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
#         else:
#             self.request_again(self.s)  # data was received incorrectly, request again.
#
#     def request_again(self, block):
#         self.sock.send(message.build_request(self.c_piece, block, self.block_len))
#     def msg_handler(self, msg, type):
#         if type == 'unchoke' and not self.in_progress:
#             self.sock.send(message.build_request(self.c_piece, self.s, self.block_len))
#             self.in_progress = True
#         elif message.is_handshake(msg):
#             print(f'handshake received')
#             self.sock.settimeout(5)
#             if self.is_handshake_hash(msg):
#                 print("hash matches, started downloading")
#                 self.sock.send(message.build_interested())
#
#             else:
#                 print("hash does not match")
#         elif type == 'bitfield':
#             print(len(msg[4:]), msg[4:], int.from_bytes(msg[:4], 'big'))
#             print('bitfield')
#             data = b''
#             if len(msg[4:]) < int.from_bytes(msg[:4], 'big'):
#                 data = self.sock.recv(16384)
#             msg += data
#             data = bitstring.BitArray(msg[5:int.from_bytes(msg[:4], 'big') + 4])
#             print(data.bin)
#
#         elif type == 'piece':
#             self.length = int.from_bytes(msg[:4], 'big')
#             if len(msg[4:]) != self.length:
#                 self.left = [len(msg[4:]), self.length, msg[4:]]
#                 self.s += len(msg[4:])
#             else:
#                 self.s_bytes += msg[9:]
#                 self.s += len(msg[9:])
#                 self.request_next_block2()
#
#         elif type is None and len(msg) != 0:
#             if self.left[0] != self.left[1]:  # if there is more left
#                 print("HERE1")
#                 if len(msg) == self.left[1] - self.left[0] or len(msg) < self.left[1] - self.left[0]:  # msg[4:]?
#                     self.left[0] += len(msg)
#                     self.left[2] += msg
#                     self.s += len(msg)
#                 elif len(msg) > self.left[1] - self.left[0]:  # msg[4:]?
#                     self.left[2] += msg[:self.left[1] - self.left[0]]
#                     self.left[0] += len(msg[:self.left[1] - self.left[0]])
#             print(self.left)
#             if self.left[0] == self.left[1]:
#                 print("HERE2")
#                 # if self.size - (
#                 #         16384 + len(self.s_bytes) + len(self.written)) < 16384:
#                 #     self.block_len = self.size - (16384 + len(self.s_bytes) + len(self.written))
#                 self.s_bytes += (self.left[2])[9:]
#                 # print("here 2: ", msg)
#                 self.request_next_block2()
#                 self.left = [0, 0, b'']
#
#         if len(msg) != int.from_bytes(msg[:4], 'big') + 4 and len(msg) != 0 and type not in [None, 'piece']:
#             if message.is_handshake(msg):
#                 self.msg_handler(msg[68:], message.msg_type(msg[68:]))
#
#             elif type == 'bitfield':
#                 self.msg_handler(msg[int.from_bytes(msg[:4], 'big') + 4:],
#                                  message.msg_type(msg[int.from_bytes(msg[:4], 'big') + 4:]))
#             else:
#                 if type == 'keep-alive':
#                     self.msg_handler(msg[4:], message.msg_type(msg[4:]))
#
#                 else:
#                     self.msg_handler(msg[5:], message.msg_type(msg[5:]))
    # def calculate_have_bitfield(self):
    #     time.sleep(0.5)
    #     if os.path.exists(f"torrents\\files\\{self.torrent_name}"):
    #         files = os.listdir(f"torrents\\files\\{self.torrent_name}")
    #         read = 0  # whats left to next piece
    #         left = b""  # lasting bytes to next piece
    #         piece_number = 0  # what piece are we at?
    #         for file in files:
    #             with open(f"torrents\\files\\{self.torrent_name}\\{file}", "rb") as f:
    #                 fs_raw = left + f.read(self.piece_length - read)
    #                 file_length = os.path.getsize(f"torrents\\files\\{self.torrent_name}\\{file}")
    #                 if len(fs_raw) == self.piece_length:
    #                     # while file_length - (self.piece_length + read) > 0:
    #                     #     last =
    #                     if hashlib.sha1(fs_raw).digest() == self.pieces[piece_number * 20: 20 * piece_number + 20]:
    #                         temp = list(self.have)
    #                         temp[piece_number] = "1"
    #                         self.have = "".join(temp)
    #                         # print(f"validated piece #{piece_number}, current bitfield progress:")
    #                         self.bar()
    #                     while len(fs_raw) == self.piece_length:
    #                         # print("here")
    #                         fs_raw = f.read(self.piece_length)
    #                         if len(fs_raw) == self.piece_length:
    #                             piece_number += 1
    #                             if hashlib.sha1(fs_raw).digest() == self.pieces[
    #                                                                 piece_number * 20: 20 * piece_number + 20]:
    #                                 temp = list(self.have)
    #                                 temp[piece_number] = "1"
    #                                 self.have = "".join(temp)
    #                                 self.bar()
    #
    #                                 # print(f"validated piece #{piece_number}, current bitfield progress:")
    #                                 # print(self.have)
    #                         else:
    #                             if len(fs_raw) < self.piece_length:
    #                                 read = len(fs_raw)
    #                                 left = fs_raw
    #                             else:
    #                                 read = 0
    #                     piece_number += 1
    #                 else:
    #                     read = len(fs_raw)
    #                     left = fs_raw
    #     self.progress_flag = False
    # def generate_info_hashes(self):
    #     """
    #     TO BE DELETED
    #     :return:
    #     """
    #     ret = []
    #     for i in range(0, len(self.pieces), 20):
    #         ret.append(self.pieces[i: i + 20])
    #     return ret
    #
    # def generate_progress_bar(self):
    #     """
    #     TO BE DELETED
    #     :return:
    #     """
    #     with alive_bar(self.num_of_pieces, force_tty=True) as self.bar:
    #         while self.progress_flag:
    #             time.sleep(0.01)
    # def calculate_have_bitfield2(self):
    #     """
    #     TO BE DELETED
    #     :return:
    #     """
    #     time.sleep(0.1)
    #     if os.path.exists(f"torrents\\files\\{self.torrent_name}"):
    #         files = os.listdir(f"torrents\\files\\{self.torrent_name}")
    #         files_raw = b""
    #         for file in files:
    #             with open(f"torrents\\files\\{self.torrent_name}\\{file}", "rb") as f:
    #                 files_raw += f.read()
    #         files_len = len(files_raw)
    #         for i in range(files_len):
    #             # print(len(files_raw))
    #             if len(files_raw[:self.piece_length]) < self.piece_length:
    #                 break
    #
    #             if hashlib.sha1(files_raw[:self.piece_length]).digest() in self.info_hashes:
    #                 temp = list(self.have)
    #                 temp[self.info_hashes.index(hashlib.sha1(files_raw[:self.piece_length]).digest())] = "1"
    #                 self.have = "".join(temp)
    #                 self.bar()
    #                 files_raw = files_raw[self.piece_length:]
    #             else:
    #                 files_raw = files_raw[1:]
    #         self.progress_flag = False
    # def listen_to_peers(self):
    #
    #     print("Now listening to incoming connections...")
    #
    #     while 1:
    #         read, write, [] = select.select(self.readable, self.writable, [])
    #         for sock in read:
    #             if self.listen_sock == sock:
    #                 conn, addr = self.listen_sock.accept()
    #                 print(f"Connected to {addr}")
    #                 self.readable.append(conn)
    #             else:
    #                 data = sock.recv(self.__BUF)
    #                 if not data:
    #                     if sock in self.readable:
    #                         self.readable.remove(sock)
    #                     break
    #
    #                 if not message.is_handshake(data):
    #                     data_len = int.from_bytes(data, 'big')
    #                     print("data length:", data_len)
    #                     data = sock.recv(data_len)
    #                     print(data)
    #                     if message.server_msg_type(data) == 'interested':  # message is interested
    #                         if len(self.readable) != 5:
    #                             sock.send(message.build_choke())
    #                         else:
    #                             sock.send(message.build_unchoke())
    #                     elif message.server_msg_type(data) == 'request':
    #                         self.send_piece(data, sock)
    #
    #                 elif message.is_handshake(data):
    #                     print(f'handshake received')
    #                     sock.send(message.build_handshake(self.tracker))
    #                     sock.send(message.build_bitfield(self.have))
    #                     self.__BUF = 4
    # def have_msg(self):
    #     """
    #     TODO: SEND HAVE MESSAGE TO ALL CONNECTED PEERS ON ALL SOCKETS
    #     :return:
    #     """
    #     have_str = manager.down.have
    #     conn = self.listen_sock.getpeername()
    #     print(conn)
    #     if conn:
    #         pass
    # def send_piece(self, data, sock):
    #     """Send given piece to a peer"""
    #     index = int.from_bytes(data[1: 5], "big")
    #     begin = int.from_bytes(data[5: 9], "big")
    #     length = int.from_bytes(data[9: 13], "big")
    #
    #     if self.have[index]:
    #         with manager.lock:
    #             piece_to_send = manager.down.pieces_bytes[index][begin:]
    #             sock.send(message.build_piece(index, begin, piece_to_send[:length]))


#endregion