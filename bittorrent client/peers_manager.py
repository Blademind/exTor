import time
import os
import hashlib
import threading
from alive_progress import alive_bar
import select
from socket import *
import message_handler as message
def reset_have(num_of_pieces):
    """
    resets have
    :return:
    """
    have = ""
    for i in range(num_of_pieces):
        have += "0"
    return have


class Downloader:
    def __init__(self, torrent, tracker):
        self.written = b""
        self.s_bytes = b""
        self.torrent = torrent
        self.tracker = tracker
        try:
            self.files = self.torrent.torrent['info']['files']
            self.file_names = [list(self.files[i].items())[1][1][0] for i in range(len(self.files))]
        except Exception as e:
            print(e)
            self.files = self.torrent.torrent['info']
        self.listen_sock = socket(AF_INET, SOCK_STREAM)
        self.listen_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listen_sock.bind(('0.0.0.0', self.torrent.port))
        self.listen_sock.listen(5)
        self.readable, self.writable = [self.listen_sock], []
        self.BUFS = {}

        self.torrent_name = self.torrent.torrent['info']['name']
        self.pieces = self.torrent.torrent['info']['pieces']
        self.num_of_pieces = len(self.pieces) // 20  # number of pieces in torrent
        self.pointer = 0
        self.pieces_bytes = self.reset_pieces()
        self.have = reset_have(self.num_of_pieces)  # what pieces I have
        self.info_hashes = self.generate_info_hashes()
        self.buf = 68
        self.piece_length = self.torrent.torrent['info']['piece length']
        self.progress_flag = True
        threading.Thread(target=self.calculate_have_bitfield2).start()
        self.generate_progress_bar()
        print(self.have)
        threading.Thread(target=self.listen_to_peers).start()

    def listen_to_peers(self):
        print("Now listening to incoming connections...")

        while 1:
            read, write, [] = select.select(self.readable, self.writable, [])
            for sock in read:
                if self.listen_sock == sock:
                    conn, addr = self.listen_sock.accept()
                    print(f"Connected to {addr}")
                    self.BUFS[conn] = 68
                    self.readable.append(conn)
                else:
                    data = sock.recv(self.BUFS[sock])
                    if not data:
                        if sock in self.readable:
                            self.readable.remove(sock)
                        break
                    if not message.is_handshake(data):
                        data_len = int.from_bytes(data, 'big')
                        print("data length:", data_len)
                        data = sock.recv(data_len)
                        print(data)
                        if message.server_msg_type(data) == 'interested':  # message is interested
                            print("interested")
                            if len(self.readable) > 5:
                                sock.send(message.build_choke())
                            else:
                                sock.send(message.build_unchoke())
                        elif message.server_msg_type(data) == 'request':
                            self.send_piece(data, sock)

                    elif message.is_handshake(data):
                        print(f'handshake received')
                        sock.send(message.build_handshake(self.tracker))
                        sock.send(message.build_bitfield(self.bitstring_to_bytes(self.have)))
                        self.BUFS[sock] = 4

    def send_piece(self, data, sock):
        """Send given piece to a peer"""
        index = int.from_bytes(data[1: 5], "big")
        begin = int.from_bytes(data[5: 9], "big")
        length = int.from_bytes(data[9: 13], "big")

        if self.have[index]:
            piece_to_send = self.pieces_bytes[index][begin:]
            sock.send(message.build_piece(index, begin, piece_to_send[:length]))

    def bitstring_to_bytes(self, s):
        return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

    def generate_progress_bar(self):
        """
        Generates on-screen progress bar when checking pieces the user owns
        :return:
        """
        with alive_bar(self.num_of_pieces, force_tty=True) as self.bar:
            while self.progress_flag:
                time.sleep(0.1)

    def generate_info_hashes(self):
        ret = []
        for i in range(0, len(self.pieces), 20):
            ret.append(self.pieces[i: i + 20])
        return ret

    def calculate_have_bitfield2(self):
        time.sleep(0.1)
        if os.path.exists(f"torrents\\files\\{self.torrent_name}"):
            files = sorted(os.listdir(f"torrents\\files\\{self.torrent_name}"), key=self.file_names.index)  # ordered file names
            files_raw = b""
            for file in files:
                with open(f"torrents\\files\\{self.torrent_name}\\{file}", "rb") as f:
                    files_raw += f.read()
            files_len = len(files_raw)
            while files_raw:
                if hashlib.sha1(files_raw[:self.piece_length]).digest() in self.info_hashes:
                    temp = list(self.have)
                    index_of_piece = self.info_hashes.index(hashlib.sha1(files_raw[:self.piece_length]).digest())
                    self.info_hashes[index_of_piece] = None
                    temp[index_of_piece] = "1"
                    self.have = "".join(temp)
                    self.add_bytes(index_of_piece, files_raw[:self.piece_length])
                    self.check_files()
                    # print(self.have)
                    self.bar()
                    self.pieces_bytes[index_of_piece] = files_raw[:self.piece_length]
                    if len(files_raw[:self.piece_length]) == self.piece_length:
                        files_raw = files_raw[self.piece_length:]
                    elif len(files_raw[:self.piece_length]) < self.piece_length:
                        break
                else:
                    break
                    # files_raw = files_raw[1:]
            self.progress_flag = False

    def reset_pieces(self):
        ret = []
        for i in range(self.num_of_pieces):
            ret.append(b"")
        return ret

    def add_bytes(self, piece, piece_bytes):
        self.pieces_bytes[piece] = piece_bytes

    def s_bytes_handler(self):
        for i, b in enumerate(self.pieces_bytes[self.pointer:]):
            if not b:
                break
            self.pointer += 1
            self.s_bytes += b

    def download_files(self):
        """
        Requests next piece in line

        :return:
        """

        temp = 0
        to_download = []
        self.s_bytes_handler()
        for file in list(self.files):
            temp += file['length']
            if temp <= len(self.s_bytes):
                to_download.append((file['path'], file['length']))
                self.files = self.files[1:]
        for path in to_download:
            with open(f"torrents\\files\\{self.torrent_name}\\{path[0][0]}", 'wb') as w:
                w.write(self.s_bytes[:path[1]])
                self.written += self.s_bytes[:path[1]]
                self.s_bytes = self.s_bytes[path[1]:]
            print("done writing", path)

    def check_files(self):
        temp = 0
        to_download = []
        self.s_bytes_handler()
        for file in list(self.files):
            temp += file['length']
            if temp <= len(self.s_bytes):
                to_download.append((file['path'], file['length']))
                self.files = self.files[1:]
        for path in to_download:
            with open(f"torrents\\files\\{self.torrent_name}\\{path[0][0]}", 'rb'):
                # w.write(self.s_bytes[:path[1]])
                self.written += self.s_bytes[:path[1]]
                self.s_bytes = self.s_bytes[path[1]:]
            print("done checking", path)


currently_connected = []
down = None
