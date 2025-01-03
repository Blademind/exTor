import shutil
from collections import OrderedDict
import time
import os
import hashlib
import threading
from alive_progress import alive_bar
import select
from socket import *
import message_handler as message
import pickle


def reset_have(num_of_pieces):
    """
    resets have
    :return:
    """
    have = ""
    for i in range(num_of_pieces):
        have += "0"
    return have


def bitstring_to_bytes(s):
    while len(s) % 8 != 0:
        s = s.ljust(len(s) + 1, "0")
    return bytes(int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big'))


def get_ip_addr():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 53))
    ip = s.getsockname()[0]
    s.close()
    return ip


class Downloader:
    def __init__(self, torrent, tracker, ui):
        self.ui = ui
        self.count_bar = 0
        self.__BUF = 1024
        self.s_bytes = b""
        self.torrent = torrent
        self.tracker = tracker
        self.ui_sock = self.tracker.ui_sock

        self.path = self.tracker.path
        self.one_file = False  # there is only one target file in torrent
        try:
            self.files = self.torrent.torrent['info']['files']
            self.file_names = [list(self.files[i].items())[1][1][0] for i in range(len(self.files))]
        except Exception as e:
            print("exception:", e)
            self.one_file = True
            self.files = self.torrent.torrent['info']
            self.file_names = [list(self.files.items())[1][1]]

        self.listen_sock = socket(AF_INET, SOCK_STREAM)
        self.listen_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listen_sock.bind(('0.0.0.0', self.torrent.port))
        self.listen_sock.listen(5)

        self.udp_list_sock = socket(AF_INET, SOCK_DGRAM)
        self.udp_list_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.udp_list_sock.bind((get_ip_addr(), self.torrent.port))

        self.banned_ips = []

        self.readable, self.writable = [self.listen_sock], []
        self.BUFS = {}

        self.torrent_name = self.torrent.torrent['info']['name']
        self.pieces = self.torrent.torrent['info']['pieces']
        self.num_of_pieces = len(self.pieces) // 20  # number of pieces in torrent
        self.pointer = 0
        self.have = reset_have(self.num_of_pieces)  # what pieces I have
        self.info_hashes = self.generate_info_hashes()
        self.piece_length = self.torrent.torrent['info']['piece length']
        self.progress_flag = True

        if not self.path:
            if not os.path.exists(f"torrents\\files\\{self.torrent_name}"):
                os.makedirs(f"torrents\\files\\{self.torrent_name}")

        self.error_queue = []  # queue for errors from peers calls (used in main.py)

        self.file_piece = self.calculate_file_piece()

        if not self.path:
            self.files_data = {
                file_name: open(f"torrents\\files\\{self.torrent_name}\\{file_name}", "rb+") if os.path.exists(
                    f"torrents\\files\\{self.torrent_name}\\{file_name}") else open(
                    f"torrents\\files\\{self.torrent_name}\\{file_name}", "wb") for file_name in self.file_names}

            self.file_piece = OrderedDict([(el, self.file_piece[el]) for el in self.file_names if
                                           os.path.exists(f"torrents\\files\\{self.torrent_name}\\{el}")])

        else:
            self.files_data = {file_name: open(f"{self.path}\\{file_name}", "rb+") if os.path.exists(
                f"{self.path}\\{file_name}") else open(f"{self.path}\\{file_name}", "wb") for file_name in
                               self.file_names}

            self.file_piece = OrderedDict([(el, self.file_piece[el]) for el in self.file_names if
                                           os.path.exists(f"{self.path}\\{el}")])

        self.calculate_bitfield()

    def update_have(self, piece):
        with lock:
            temp = list(self.have)
            temp[piece] = "1"
            self.have = "".join(temp)

    def calculate_bitfield(self):
        """
        calls a function which calculates what pieces are present on disk
        :return:
        """
        threading.Thread(target=self.calculate_have_bitfield2).start()
        self.generate_progress_bar()  # PROGRESS

    def listen_seq(self):
        threading.Thread(target=self.listen_to_peers).start()
        threading.Thread(target=self.listen_to_tracker).start()

    def generate_download_bar(self):  # PROGRESS
        threading.Thread(target=self.generate_progress_bar).start()

    def listen_to_peers(self):
        print("Now listening to incoming connections...")

        while 1:
            read, write, [] = select.select(self.readable, self.writable, [])
            for sock in read:
                if self.listen_sock == sock:
                    conn, addr = self.listen_sock.accept()
                    if addr[0] in self.banned_ips:
                        conn.close()
                        break
                    print(f"Connected to {addr}")
                    self.BUFS[conn] = 68
                    self.readable.append(conn)
                else:
                    try:
                        data = sock.recv(self.BUFS[sock])
                        if self.banned_ips:
                            ip = sock.getpeername()[0]
                            if ip in self.banned_ips:
                                sock.close()
                                break
                    except:
                        if sock in self.readable:
                            self.readable.remove(sock)
                        break
                    if not data:
                        if sock in self.readable:
                            self.readable.remove(sock)
                        break
                    if not message.is_handshake(data):
                        data_len = int.from_bytes(data, 'big')
                        data = sock.recv(data_len)
                        if message.server_msg_type(data) == 'interested':  # message is interested
                            print("interested")
                            if len(self.readable) > 5:
                                sock.send(message.build_choke())
                            else:
                                sock.send(message.build_unchoke())
                        elif message.server_msg_type(data) == 'request':
                            try:
                                self.send_piece(data, sock)
                            except:
                                print("Exception occurred on piece sending")
                                pass

                    elif message.is_handshake(data):
                        print(f'handshake received')
                        sock.send(message.build_handshake(self.tracker))
                        sock.send(message.build_bitfield(bitstring_to_bytes(self.have)))
                        self.BUFS[sock] = 4

    def listen_to_tracker(self):
        global sharing_peers
        print("Now listening for tracker UDP queries...")
        while 1:
            data, addr = self.udp_list_sock.recvfrom(self.__BUF)
            if addr[0] == self.tracker.local_tracker[0]:
                if not data:
                    break
                try:
                    datacontent = data.decode()

                except:
                    datacontent = ""

                print("data from tracker:", datacontent)
                if datacontent == "UPDATED":
                    if self.tracker.current_file_status == "local file" or self.tracker.current_file_status == "upload file":
                        self.udp_list_sock.sendto(pickle.dumps((f"INFORM_SHARED_PEERS {self.tracker.file_name}", sharing_peers)),
                                         self.tracker.local_tracker)
                    print("Tracker was informed of downloaded file")
                if datacontent[:6] == "BAN_IP":
                    print("banned ip from tracker: ", datacontent[7:])
                    ip = datacontent[7:]
                    self.banned_ips.append(ip)

    def update_bar(self):
        with data_lock:
            if not self.ui:
                self.bar()  # PROGRESS
            self.count_bar += 1
            if self.ui_sock:
                msg = f"PROGRESS {int((self.count_bar / self.num_of_pieces) * 1000)}".encode()
                len_msg = len(msg).to_bytes(4, byteorder='big')
                time.sleep(0)
                self.ui_sock.send(len_msg + msg)

    def add_piece_data(self, piece_number, data):
        file_name, begin_piece, size = self.find_begin_piece_index(piece_number)
        file = self.files_data[file_name]
        total_current_piece_length = self.piece_length if piece_number != self.num_of_pieces - 1 else self.torrent.size() - self.piece_length * piece_number
        with bytes_file_lock:
            file.seek(begin_piece)
            file.write(data[:size])
        data = data[size:]
        while size != total_current_piece_length:
            file_name = self.file_names[self.file_names.index(file_name) + 1]
            file = self.files_data[file_name]
            begin_piece = 0
            current_size = 0
            for p, s in self.file_piece[file_name].items():
                if piece_number == p:
                    size += s
                    current_size = s
                    break
                begin_piece += s
            with bytes_file_lock:
                file.seek(begin_piece)
                file.write(data[:current_size])
            data = data[current_size:]
        threading.Thread(target=self.update_bar).start()

    def send_piece(self, data, sock):
        """Send given piece to a peer"""
        index = int.from_bytes(data[1: 5], "big")
        begin = int.from_bytes(data[5: 9], "big")
        length = int.from_bytes(data[9: 13], "big")
        if self.have[index]:
            file_name, begin_piece, size = self.find_begin_piece_index(index)
            total_current_piece_length = self.piece_length if index != self.num_of_pieces - 1 else self.torrent.size() - self.piece_length * index
            if not self.path:
                with open(f"torrents\\files\\{self.torrent_name}\\{file_name}", "rb") as f:
                    f.seek(begin_piece)
                    piece_data = f.read(size)
            else:
                with open(f"{self.path}\\{file_name}", "rb") as f:
                    f.seek(begin_piece)
                    piece_data = f.read(size)

            while size != total_current_piece_length:
                file_name = self.file_names[self.file_names.index(file_name) + 1]
                begin_piece = 0
                current_size = 0
                for p, s in self.file_piece[file_name].items():
                    if index == p:
                        size += s
                        current_size = s
                        break
                    begin_piece += s
                if not self.path:
                    with open(f"torrents\\files\\{self.torrent_name}\\{file_name}", "rb") as f:
                        f.seek(begin_piece)
                        piece_data += f.read(current_size)

                else:
                    with open(f"{self.path}\\{file_name}", "rb") as f:
                        f.seek(begin_piece)
                        piece_data += f.read(current_size)
            piece_to_send = piece_data[begin:]
            sock.send(message.build_piece(index, begin, piece_to_send[:length]))

    def find_begin_piece_index(self, index):
        for file, pieces in self.file_piece.items():
            begin = 0
            for piece, size in pieces.items():
                if index == piece:
                    return file, begin, size
                begin += size

    def generate_progress_bar(self):  # PROGRESS
        """
        Generates on-screen progress bar when checking pieces the user owns
        :return:
        """
        # start a new progress bar
        if not self.progress_flag:
            self.progress_flag = True
        if not self.ui:
            with alive_bar(self.num_of_pieces - self.count_bar, force_tty=True) as self.bar:
                while self.progress_flag:
                    time.sleep(1)
        else:
            while self.progress_flag:
                time.sleep(1)

    def generate_info_hashes(self):
        ret = []
        for i in range(0, len(self.pieces), 20):
            ret.append(self.pieces[i: i + 20])
        return ret

    def calculate_have_bitfield2(self):
        time.sleep(0.5)
        if not self.path:
            if os.path.exists(f"torrents\\files\\{self.torrent_name}"):
                err = False
                for piece in range(self.num_of_pieces):
                    piece_instances = self.check_piece_instances(piece)
                    piece_data = b""
                    for file in piece_instances.keys():
                        if os.path.exists(f"torrents\\files\\{self.torrent_name}\\{file}"):
                            begin = piece_instances[file][0]
                            length = piece_instances[file][1]
                            with open(f"torrents\\files\\{self.torrent_name}\\{file}", "rb") as f:
                                f.seek(begin)

                                data_to_add = f.read(length)
                                if len(data_to_add) == length:
                                    piece_data += data_to_add
                                else:
                                    err = True
                                    break
                        else:
                            err = True
                            break
                    if not err:
                        if hashlib.sha1(piece_data).digest() == self.pieces[
                                                                piece * 20: 20 * piece + 20]:
                            temp = list(self.have)
                            temp[piece] = "1"
                            self.have = "".join(temp)
                            if not self.ui:
                                self.bar()  # PROGRESS
                            self.count_bar += 1
                            if self.ui_sock:

                                msg = f"PROGRESS {int((self.count_bar / self.num_of_pieces) * 1000)}".encode()
                                len_msg = len(msg).to_bytes(4, byteorder='big')
                                self.ui_sock.send(len_msg + msg)
                                time.sleep(0)

                    err = False
        else:
            if os.path.exists(f"{self.path}"):
                err = False
                for piece in range(self.num_of_pieces):
                    piece_instances = self.check_piece_instances(piece)
                    piece_data = b""
                    for file in piece_instances.keys():
                        if os.path.exists(f"{self.path}\\{file}"):
                            begin = piece_instances[file][0]
                            length = piece_instances[file][1]
                            with open(f"{self.path}\\{file}", "rb") as f:
                                f.seek(begin)

                                data_to_add = f.read(length)
                                if len(data_to_add) == length:
                                    piece_data += data_to_add
                                else:
                                    err = True
                                    break
                        else:
                            err = True
                            break
                    if not err:
                        if hashlib.sha1(piece_data).digest() == self.pieces[
                                                                piece * 20: 20 * piece + 20]:
                            temp = list(self.have)
                            temp[piece] = "1"
                            self.have = "".join(temp)
                            if not self.ui:
                                self.bar()  # PROGRESS
                            self.count_bar += 1
                            if self.ui_sock:
                                msg = f"PROGRESS {int((self.count_bar / self.num_of_pieces) * 1000)}".encode()
                                len_msg = len(msg).to_bytes(4, byteorder='big')
                                self.ui_sock.send(len_msg + msg)
                                time.sleep(0)

                    err = False

        self.progress_flag = False  # PROGRESS

    def check_piece_instances(self, index):
        ret = {}
        begin = 0
        for file, pieces in self.file_piece.items():
            for piece, length in pieces.items():
                if index == piece:
                    ret[file] = (begin, length)
                begin += length
            begin = 0
        return ret

    def calculate_file_piece(self):
        file_piece = {}
        for file in self.file_names:
            file_piece[file] = {}

        files = self.file_names
        if not self.path:
            if not os.path.exists(f"torrents\\files\\{self.torrent_name}\\temp"):
                os.makedirs(f"torrents\\files\\{self.torrent_name}\\temp")
            files_dummy = {file_name: open(f"torrents\\files\\{self.torrent_name}\\temp\\{file_name}", "wb") for
                           file_name in self.file_names}
            read = 0  # whats left to next piece
            left = b""  # lasting bytes to next piece
            piece_number = 0  # what piece are we at?
            size = self.torrent.size()
            c = 0
            if not self.one_file:
                for file_name, file in files_dummy.items():
                    data = b"*" * self.files[c]["length"]
                    file.write(data)
                    c += 1
            else:
                for file_name, file in files_dummy.items():
                    data = b"*" * list(self.files.items())[0][1]
                    file.write(data)
                    break
            for file_name, f in files_dummy.items():
                f.close()
            for file in files:
                with open(f"torrents\\files\\{self.torrent_name}\\temp\\{file}", "rb") as f:
                    total_current_piece_length = self.piece_length if piece_number != self.num_of_pieces - 1 else size - self.piece_length * piece_number
                    fs_raw = left + f.read(total_current_piece_length - read)
                    if len(fs_raw) == total_current_piece_length:
                        file_piece[file][piece_number] = len(fs_raw) - len(left)
                        left = b""  # lasting bytes to next piece

                        flag = True

                        while len(fs_raw) == total_current_piece_length and piece_number != self.num_of_pieces - 1:
                            fs_raw = f.read(total_current_piece_length)
                            piece_number += 1
                            total_current_piece_length = self.piece_length if piece_number != self.num_of_pieces - 1 else size - self.piece_length * piece_number

                            if len(fs_raw) == total_current_piece_length:
                                file_piece[file][piece_number] = len(fs_raw) - len(left)
                                left = b""  # lasting bytes to next piece
                                flag = True
                            else:
                                if len(fs_raw) < total_current_piece_length:
                                    read = len(fs_raw)
                                    file_piece[file][piece_number] = read - len(left)
                                    left = fs_raw
                                    flag = False

                        if flag:
                            piece_number += 1
                    else:
                        read = len(fs_raw)
                        file_piece[file][piece_number] = read - len(left)

                        left = fs_raw
            shutil.rmtree(f"torrents\\files\\{self.torrent_name}\\temp")
            return file_piece
        else:
            if not os.path.exists(f"{self.path}\\temp"):
                os.makedirs(f"{self.path}\\temp")
            files_dummy = {file_name: open(f"{self.path}\\temp\\{file_name}", "wb") for
                           file_name in self.file_names}
            read = 0  # whats left to next piece
            left = b""  # lasting bytes to next piece
            piece_number = 0  # what piece are we at?
            size = self.torrent.size()
            c = 0
            if not self.one_file:
                for file_name, file in files_dummy.items():
                    data = b"*" * self.files[c]["length"]
                    file.write(data)
                    c += 1
            else:
                for file_name, file in files_dummy.items():
                    data = b"*" * list(self.files.items())[0][1]
                    file.write(data)
                    break

            for file_name, f in files_dummy.items():
                f.close()

            for file in files:
                with open(f"{self.path}\\temp\\{file}", "rb") as f:
                    total_current_piece_length = self.piece_length if piece_number != self.num_of_pieces - 1 else size - self.piece_length * piece_number
                    fs_raw = left + f.read(total_current_piece_length - read)
                    if len(fs_raw) == total_current_piece_length:
                        file_piece[file][piece_number] = len(fs_raw) - len(left)
                        left = b""  # lasting bytes to next piece

                        flag = True

                        while len(fs_raw) == total_current_piece_length and piece_number != self.num_of_pieces - 1:
                            fs_raw = f.read(total_current_piece_length)
                            piece_number += 1
                            total_current_piece_length = self.piece_length if piece_number != self.num_of_pieces - 1 else size - self.piece_length * piece_number

                            if len(fs_raw) == total_current_piece_length:
                                file_piece[file][piece_number] = len(fs_raw) - len(left)
                                left = b""  # lasting bytes to next piece
                                flag = True
                            else:
                                if len(fs_raw) < total_current_piece_length:
                                    read = len(fs_raw)
                                    file_piece[file][piece_number] = read - len(left)
                                    left = fs_raw
                                    flag = False

                        if flag:
                            piece_number += 1
                    else:
                        read = len(fs_raw)
                        file_piece[file][piece_number] = read - len(left)

                        left = fs_raw
            shutil.rmtree(f"{self.path}\\temp")
            return file_piece

    def add_sharing_peer(self, peer):
        """
        adds sharing peer to a list (then used at tracker side to validate sharing peers)
        :param peer:
        :return:
        """
        global sharing_peers
        file_status = self.tracker.current_file_status
        if file_status == "local file" or file_status == "upload file":
            if peer not in sharing_peers:
                sharing_peers.append(peer)
                print(peer, "added to sharing_peers list")

def reset_to_default():
    global currently_connected, DONE
    currently_connected = []
    DONE = False


def remove_peer(peer):
    with lock:
        currently_connected.remove(peer)




# region TRASH
# def bytes_file_length(self):
#     self.bytes_file.seek(0)
#     size = len(self.bytes_file.read())
#     self.bytes_file.seek(0)
#     return size


# def start_download(self):
#         for piece, k in enumerate(sorted(self.pieces, key=lambda p: len(self.pieces[p]))):
#
#             if self.have[piece] == "0":
#                 peer = Peer(self.tracker)  # create a peer object
#                 self.current_piece_peers = self.pieces[k]
#                 # no peers holding current piece
#                 if len(self.current_piece_peers) == 0:
#                     raise Exception("no peers holding piece")
#
#                 # go over all piece holders
#                 self.recursive_peers(peer, k)
#         print("Completed Download!")
# def recursive_peers(self, peer, k):
#     """
#     goes over peers recursively in order to get a piece downloaded
#     :param peer:
#     :param k:
#     :return:
#     """
#     global currently_connected
#
#     for p in self.current_piece_peers:
#         # print(p)
#         if p not in currently_connected:
#             currently_connected.append(p)
#             threading.Thread(target=peer.download, args=(p, k, self.current_piece_peers)).start()
#             break
#
#         # last peer and was not caught beforehand - all conns in use
#         if p == self.current_piece_peers[-1]:
#             last_piece_length = len(currently_connected)
#             while len(currently_connected) == last_piece_length:
#                 time.sleep(0.1)
#             self.recursive_peers(peer, k)

# def add_bytes(self, piece, piece_bytes):
#     with testing_lock:
#         self.pieces_bytes[piece] = piece_bytes

# def bytes_file_handler(self):
#     """
#     Checks already downloaded pieces and adds their bytes to a file
#     :return:
#     """
#     with testing_lock:
#         for i, b in enumerate(self.pieces_bytes[self.pointer:]):
#             if not b:
#                 break
#             self.pieces_bytes[self.pointer] = b"T"
#             self.pointer += 1
#             with bytes_file_lock:
#                 self.bytes_file_length += len(b)
#                 self.bytes_file.write(b)
#         # self.s_bytes += b

# def download_files(self):
#     """
#     Requests next piece in line
#
#     :return:
#     """
#     # downloaded_files = os.listdir(f"torrents\\files\\{self.torrent_name}")
#     #
#     # # solution for mid-flight deletion
#     #
#     # if len(downloaded_files) != len(self.file_data.keys()):
#     #     for file_name, file_data in self.file_data.items():
#     #         if file_name not in downloaded_files:
#     #             with open(f"torrents\\files\\{self.torrent_name}\\{file_name}", 'wb') as w:
#     #                 w.write(file_data)
#     temp = 0
#     to_download = []
#     self.bytes_file_handler()
#     with bytes_file_lock:
#         bytes_file_length = self.bytes_file_length
#     # with bytes_file_lock:
#
#     for file in list(self.files):
#         temp += file['length']
#         if temp <= bytes_file_length:
#             to_download.append((file['path'], file['length']))
#             self.files = self.files[1:]
#         else:
#             break
#
#     for path in to_download:
#         with open(f"torrents\\files\\{self.torrent_name}\\{path[0][0]}", 'wb') as w:
#             with bytes_file_lock:
#                 self.bytes_file.seek(0)
#                 write_data = self.bytes_file.read(path[1])
#
#                 # w.write(write_data)
#                 # # w.write(self.s_bytes[:path[1]])
#                 #
#                 # self.file_data[path[0][0]] = write_data
#             w.write(write_data)
#             self.file_data[path[0][0]] = write_data
#
#
#                 # self.file_data[path[0][0]] = self.s_bytes[:path[1]]
#
#                 # self.written += self.s_bytes[:path[1]]
#
#             with bytes_file_lock:
#                 self.bytes_file_length -= path[1]
#                 self.bytes_file.seek(0)
#                 new_f = self.bytes_file.read()
#                 self.bytes_file.seek(0)
#                 self.bytes_file.write(new_f[path[1]:])
#                 self.bytes_file.truncate()
#                 #
#                 # self.bytes_file.truncate(0)
#                 # self.bytes_file.write(self.s_bytes[path[1]:])
#
#
#         print("done writing", path)
#
#
# def check_files(self):
#     temp = 0
#     to_download = []
#     self.bytes_file_handler()
#
#     # bytes_file_length = self.bytes_file_length()
#     for file in list(self.files):
#         temp += file['length']
#         if temp <= self.bytes_file_length:
#             to_download.append((file['path'], file['length']))
#             self.files = self.files[1:]
#         else:
#             break
#     for path in to_download:
#         # with open(f"torrents\\files\\{self.torrent_name}\\{path[0][0]}", 'rb'):
#         #     # w.write(self.s_bytes[:path[1]])
#         #     # self.written += self.s_bytes[:path[1]]
#         #
#
#         self.bytes_file_length -= path[1]
#         self.bytes_file.seek(0)
#         new_f = self.bytes_file.read()
#         self.bytes_file.seek(0)
#         self.bytes_file.write(new_f[path[1]:])
#         self.bytes_file.truncate()
#
#         # self.s_bytes = self.s_bytes[path[1]:]
#         print("done checking", path)

    # def calculate_have_bitfieldv1(self):
    #     time.sleep(0.5)
    #     if os.path.exists(f"torrents\\files\\{self.torrent_name}"):
    #         base_files = [file for file in os.listdir(f"torrents\\files\\{self.torrent_name}") if file != "bytes_file"]
    #         files = sorted(base_files,
    #                        key=self.file_names.index)  # ordered file names
    #         read = 0  # whats left to next piece
    #         left = b""  # lasting bytes to next piece
    #         piece_number = 0  # what piece are we at?
    #         size = self.torrent.size()
    #         for file in files:
    #             with open(f"torrents\\files\\{self.torrent_name}\\{file}", "rb") as f:
    #                 total_current_piece_length = self.piece_length if piece_number != self.num_of_pieces - 1 else size - self.piece_length * piece_number
    #                 fs_raw = left + f.read(total_current_piece_length - read)
    #                 if len(fs_raw) == total_current_piece_length:
    #                     temp = list(self.have)
    #                     temp[piece_number] = "1"
    #                     self.have = "".join(temp)
    #                     # self.add_bytes(piece_number, fs_raw)
    #                     left = b""  # lasting bytes to next piece
    #                     # self.check_files()
    #                     self.bar()
    #                     self.count_bar += 1
    #                     flag = True
    #
    #                     while len(fs_raw) == total_current_piece_length and piece_number != self.num_of_pieces - 1:
    #                         fs_raw = f.read(total_current_piece_length)
    #                         piece_number += 1
    #                         total_current_piece_length = self.piece_length if piece_number != self.num_of_pieces - 1 else size - self.piece_length * piece_number
    #
    #                         if len(fs_raw) == total_current_piece_length:
    #                             if hashlib.sha1(fs_raw).digest() == self.pieces[
    #                                                                 piece_number * 20: 20 * piece_number + 20]:
    #                                 temp = list(self.have)
    #                                 temp[piece_number] = "1"
    #                                 self.have = "".join(temp)
    #                                 # self.add_bytes(piece_number, fs_raw)
    #                                 left = b""  # lasting bytes to next piece
    #
    #                                 # self.check_files()
    #                                 self.bar()
    #                                 self.count_bar += 1
    #                                 flag = True
    #                         else:
    #                             if len(fs_raw) < total_current_piece_length:
    #                                 read = len(fs_raw)
    #                                 left = fs_raw
    #                                 flag = False
    #
    #                     if flag:
    #                         piece_number += 1
    #                 else:
    #                     read = len(fs_raw)
    #                     left = fs_raw
    #
    #         # print(file_piece)
    #     self.progress_flag = False
    # def calculate_have_bitfield2(self):
    #     time.sleep(0.1)
    #     base_files = [file for file in os.listdir(f"torrents\\files\\{self.torrent_name}") if file != "bytes_file"]
    #     files = sorted(base_files, key=self.file_names.index)  # ordered file names
    #     files_raw = b""
    #
    #     for file in files:
    #         with open(f"torrents\\files\\{self.torrent_name}\\{file}", "rb") as f:
    #             files_raw += f.read()
    #     # files_len = len(files_raw)
    #
    #     while files_raw:
    #         if hashlib.sha1(files_raw[:self.piece_length]).digest() in self.info_hashes:
    #             temp = list(self.have)
    #             index_of_piece = self.info_hashes.index(hashlib.sha1(files_raw[:self.piece_length]).digest())
    #             self.info_hashes[index_of_piece] = None
    #             temp[index_of_piece] = "1"
    #             self.have = "".join(temp)
    #             self.add_bytes(index_of_piece, files_raw[:self.piece_length])
    #             self.check_files()
    #             # print(self.have)
    #             self.bar()
    #             # self.pieces_bytes[index_of_piece] = files_raw[:self.piece_length]
    #             if len(files_raw[:self.piece_length]) == self.piece_length:
    #                 files_raw = files_raw[self.piece_length:]
    #             elif len(files_raw[:self.piece_length]) < self.piece_length:
    #                 break
    #         else:
    #             break
    #             # files_raw = files_raw[1:]
    #     self.progress_flag = False

    # def reset_pieces(self):
    #     ret = []
    #     for i in range(self.num_of_pieces):
    #         ret.append(b"")
    #     return ret
# end region



sharing_peers = []
testing_lock = threading.Lock()
lock = threading.Lock()
request_lock = threading.Lock()
bytes_file_lock = threading.Lock()
currently_connected = []
data_lock = threading.Lock()
DONE = False
down = None
