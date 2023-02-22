import pickle
import socket
import threading

from random import randbytes
from socket import *
from urllib.parse import ParseResult

import bencode
import requests

from torrent import Torrent

import tracker_init_contact

def resp_type(ret):
    if int.from_bytes(ret[:4], 'big') == 0:
        return 'connect'
    elif int.from_bytes(ret[:4], 'big') == 1:
        return 'announce'


def build_conn_req():
    """Builds udp tracker request"""
    message = bytes.fromhex('00 00 04 17 27 10 19 80')  # connection_id (set id 41727101980)
    message += (0).to_bytes(4, byteorder='big')  # action - connect
    message += randbytes(4)  # transaction_id
    return message


def generate_peer_id():
    return randbytes(20)


class Tracker:
    def __init__(self, given_name=None, path=None):
        self.given_name = given_name
        self.path = path
        print(self.path)
        self.local_tracker = None  # set local_tracker to none (was not yet found)
        if not given_name:
            self.local_tracker = tracker_init_contact.find_local_tracker()  # find local tracker

        if self.local_tracker or given_name:  # local tracker was found or a name was given
            self.global_flag = False
            self.peers = None
            self.yields = None
            self.sock = None
            self.id = None
            self.global_file = None
            self.file_name = None
            self.tran_id = None  # the transaction id (later use)
            self.conn_id = None  # the connection id (later use)
            self.__BUF = 1024
            self.torrent = Torrent()  # create a torrent object
            self.file_name = None

            self.id = generate_peer_id()  # peer_id
            self.peers = []

            self.sock = socket(AF_INET, SOCK_DGRAM)
            self.sock.bind(("0.0.0.0", self.torrent.port))
            self.sock.settimeout(5)

            if not given_name:
                self.file_name = self.fetch_torrent_file()
                self.file_names()

            else:
                self.file_name = given_name
                self.torrent.init_torrent_seq(self.file_name, True)

        # threading.Thread(target=self.contact_trackers, args=(file_name,)).start()
        # self.contact_trackers()
    def file_names(self):
        """
        Takes care of local and global metadata files
        :return:
        """
        if self.file_name[-12: -8] == "_LOC":  # the torrent is local metadata (which is based on global metadata)
            self.global_file = self.recv_files()
            self.torrent.init_torrent_seq(self.file_name, True)

        elif self.file_name[-15:-8] == "_UPLOAD":  # the torrent was uploaded by a user, this is a local file not having global metadata
            self.torrent.init_torrent_seq(self.file_name, True)

        else:

            self.torrent.init_torrent_seq(self.file_name, False)


    def contact_trackers(self):
        # previous methods did not prove useful to get pieces, time to contact global trackers for peers
        if self.global_flag:
            # self.torrent.init_torrent_seq(self.file_name, False)
            self.sock.settimeout(1)  # going over trackers, less timeout for more speed
            try:
                self.yields = self.torrent.url_yields
                if type(self.torrent.url) is ParseResult:
                    # Udp tracker
                    self.udp_send(build_conn_req())
                else:
                    # Http tracker
                    self.http_send()
            except AttributeError:
                pass

        elif self.local_tracker or self.given_name:
            #
            # self.id = generate_peer_id()  # peer_id
            # self.peers = []
            #
            # self.sock = socket(AF_INET, SOCK_DGRAM)
            # self.sock.bind(("0.0.0.0", self.torrent.port))
            # self.sock.settimeout(5)
            #
            # file_name = self.fetch_torrent_file()
            #
            # # if not os.path.exists(f"torrents\\files\\{file_name}"):
            # #     os.mkdir(f"torrents\\files\\{file_name}")
            # self.torrent.init_torrent_seq(file_name)

            # the torrent file is not local torrent
            if self.file_name[-12: -8] != "_LOC" and self.file_name[-15: -8] != "_UPLOAD":
                # self.torrent.init_torrent_seq(self.file_name, False)
                self.sock.settimeout(1)  # going over trackers, less timeout for more speed
                try:
                    self.yields = self.torrent.url_yields
                    if type(self.torrent.url) is ParseResult:
                        # Udp tracker
                        self.udp_send(build_conn_req())
                    else:
                        # Http tracker
                        self.http_send()
                except AttributeError:
                    pass
            else:
                # self.torrent.init_torrent_seq(self.global_file, True)
                # the peers are in the torrent file, instead of trackers, each peer is a node in the local network, algorithm specified for that is required here
                self.global_flag = True  # used in case the program is unable to retrieve pieces from local network
                # self.global_file = self.recv_files()
                print("LOCAL FILE")
                with open(f"torrents\\info_hashes\\{self.file_name}", "rb") as f:
                    peers = bencode.bdecode(f.read())["announce-list"]
                self.peers = [tuple(peer) for peer in peers]
                print(self.peers)

    def udp_send(self, message):
        print(self.torrent.url)
        try:
            self.sock.sendto(message, (gethostbyname(self.torrent.url.hostname), self.torrent.url.port))
            self.listen()
            self.torrent.url = self.torrent.url_yields.__next__()
            if self.torrent.url:
                if type(self.torrent.url) is ParseResult:
                    # Udp tracker
                    self.udp_send(build_conn_req())
                else:
                    # Http tracker
                    self.http_send()

        except StopIteration:
            pass

        except Exception as e:
            print(f'Error: {e}')
            self.torrent.url = self.torrent.url_yields.__next__()
            if self.torrent.url:
                print('Trying another tracker...')
                if type(self.torrent.url) is ParseResult:
                    # Udp tracker
                    self.udp_send(build_conn_req())
                else:
                    # Http tracker
                    self.http_send()

    def http_send(self):
        params = {
            'info_hash': self.torrent.generate_info_hash(),
            'peer_id': self.id,
            'uploaded': 0,
            'downloaded': 0,
            'port': 6881,
            'left': self.torrent.size(),
            'event': 'started'
        }
        try:
            answer_tracker = requests.get(self.torrent.url, params=params, timeout=5)
            list_peers = bencode.bdecode(answer_tracker.content)
            for peer in list_peers['peers']:
                self.peers.append((peer['ip'], peer['port']))
        except:
            print('Error, Trying another tracker...')
            self.torrent.url = self.torrent.url_yields.__next__()
            self.http_send()

    def listen(self):
        ret = self.sock.recv(self.__BUF)
        try:
            self.TCP_IP_PORT = pickle.loads(ret)
        except:
            if resp_type(ret) == 'connect':
                self.conn_id = ret[8:]
                self.tran_id = ret[4:8]
                self.udp_send(self.build_announce_req())

            elif resp_type(ret) == 'announce':
                n = 0
                while 24 + 6 * n <= len(ret):
                    ip = inet_ntoa(ret[20 + 6 * n: 24 + 6 * n])
                    port = int.from_bytes(ret[24 + 6 * n: 26 + 6 * n], 'big')

                    # only add peer if needed
                    if (ip, port) not in self.peers:
                        self.peers.append((ip, port))
                    n += 1
                print(self.peers)
            else:
                # Error code 3
                if int.from_bytes(ret[:4], byteorder='big') == 3:
                    print("=== ERROR ===")
                    print(ret[8:].decode())

    def build_announce_req(self, port=6881):
        message = self.conn_id  # connection_id
        message += (1).to_bytes(4, byteorder='big')  # action
        message += self.tran_id  # transaction_id
        message += self.torrent.generate_info_hash()  # info_hash
        message += self.id  # peer_id
        message += (0).to_bytes(8, byteorder='big')  # downloaded
        message += self.torrent.size().to_bytes(8, byteorder='big')  # left
        message += (0).to_bytes(8, byteorder='big')  # uploaded
        message += (0).to_bytes(4, byteorder='big')  # event
        message += (0).to_bytes(4, byteorder='big')  # ip_address
        message += randbytes(4)  # key
        message += (-1).to_bytes(4, byteorder='big', signed=True)
        message += port.to_bytes(2, byteorder='big')
        return message

    def init_tcp_sock(self):
        file_sock = socket(AF_INET, SOCK_STREAM)
        file_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        file_sock.bind(("0.0.0.0", self.torrent.port))
        file_sock.listen(5)
        return file_sock

    def fetch_torrent_file(self):
        try:
            file_name = input("What torrent would you like to download? -> ")
            self.sock.sendto(f"GET {file_name}".encode(), self.local_tracker)
            return self.recv_files()

        except KeyboardInterrupt:
            print("\nprogram ended")

    def recv_files(self):
        data = None
        try:
            while not data:
                data, addr = self.sock.recvfrom(self.__BUF)
        except:
            print("file name was not received on time")

        try:
            datacontent = data.decode()
            if datacontent == "NO TORRENTS FOUND":
                raise Exception("no torrents matching query found on tracker")
            else:
                # matching query found, proceed to download it
                filename = datacontent
                print(filename)
                if filename[-8:] != ".torrent":
                    print("file is not torrent")
                    return
                self.file_name = filename

                # creates a clean file with given file name
                with open(f"torrents\\info_hashes\\{filename}", "wb") as w:
                    w.write(b"")

                self.sock.sendto(b"FLOW", addr)  # start flow of metadata content
                s = 0
                length = int(pickle.loads(self.sock.recv(self.__BUF)))
                while s != length:
                    data = self.sock.recv(self.__BUF)
                    s += len(data)
                    with open(f"torrents\\info_hashes\\{filename}", "ab") as f:
                        f.write(data)
                    self.sock.sendto(b"FLOW", addr)  # continue flow of metadata content

                print("received torrent file from local tracker")
                return filename
        except Exception as e:
            print(e)
            return

    def done_downloading(self):
        self.sock.sendto(f"DONE DOWNLOADING {self.file_name if self.file_name[-8:-12] != '_LOC' else self.file_name[:-8]}".encode(),self.local_tracker)
        data = self.sock.recv(self.__BUF)
        if data == b"UPDATED":
            print("Tracker was informed of downloaded file")





if __name__ == '__main__':
    Tracker()
