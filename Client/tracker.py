import pickle
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
    def __init__(self, given_name=None, path=None, port=None, ui_given_name=None, ui_sock=None):

        self.ui_sock = ui_sock

        self.given_name = given_name
        self.path = path
        self.local_tracker = None  # set local_tracker to none (was not yet found)
        if not given_name:
            self.local_tracker = tracker_init_contact.find_local_tracker()  # find local tracker
        if self.local_tracker or given_name:  # local tracker was found or a name was given
            self.global_flag = False
            self.peers = None
            self.sock = None
            self.id = None
            self.global_file = None
            self.file_name = None
            self.tran_id = None  # the transaction id (later use)
            self.conn_id = None  # the connection id (later use)
            self.current_file_status = None  # file status: global \ local \ upload
            self.__BUF = 1024
            self.torrent = Torrent(port=port)  # create a torrent object
            self.id = generate_peer_id()  # peer_id
            self.peers = []
            self.threads = []  # use later

            self.sock = socket(AF_INET, SOCK_DGRAM)
            self.sock.bind(("0.0.0.0", self.torrent.port))
            self.sock.settimeout(20)

            if ui_given_name:
                self.file_name = self.fetch_torrent_file(file_name=ui_given_name)
                self.file_names()

            elif not given_name:
                self.file_name = self.fetch_torrent_file()
                self.file_names()

            else:
                self.file_name = given_name
                self.torrent.init_torrent_seq(self.file_name, True)

    def file_names(self):
        """
        Takes care of local and global metadata files
        :return:
        """
        print("file_name:", self.file_name)
        if self.file_name[-12: -8] == "_LOC":  # the torrent is local metadata (which is based on global metadata)
            print("local file")
            self.current_file_status = "local file"
            self.global_file = self.recv_files()
            self.torrent.init_torrent_seq(self.file_name, True)

        elif self.file_name[-15:-8] == "_UPLOAD":  # the torrent was uploaded by a user, this is a local file not having global metadata
            print("upload file")
            self.current_file_status = "upload file"
            self.torrent.init_torrent_seq(self.file_name, True)

        else:
            print("global file")
            self.current_file_status = "global file"
            self.torrent.init_torrent_seq(self.file_name, False)

    def contact_trackers(self):
        # previous methods did not prove useful to get pieces, time to contact global trackers for peers
        if self.global_flag:
            self.torrent.init_torrent_seq(self.global_file, False)
            if self.ui_sock:
                msg = b"UPDATE_STATUS Contacting Trackers..."
                self.ui_sock.send(len(msg).to_bytes(4, byteorder='big') + msg)

            try:
                self.trackers = self.torrent.trackers
                print("Trying Trackers....")
                for tracker_url in self.trackers:

                    if type(tracker_url) is ParseResult:
                        print(tracker_url)
                        th = threading.Thread(target=self.contact_udp, args=(build_conn_req(), tracker_url))
                        self.threads.append(th)
                        th.start()
                    else:
                        # Http tracker
                        th = threading.Thread(target=self.http_send, args=(tracker_url, ))
                        self.threads.append(th)
                        th.start()
                for thr in self.threads:
                    thr.join()
            except AttributeError:
                pass

        elif self.local_tracker or self.given_name:
            # the torrent file is not local torrent
            if self.file_name[-12: -8] != "_LOC" and self.file_name[-15: -8] != "_UPLOAD":
                self.trackers = self.torrent.trackers
                print("Trying Trackers....")
                for tracker_url in self.trackers:

                    if type(tracker_url) is ParseResult:
                        print(tracker_url)
                        th = threading.Thread(target=self.contact_udp, args=(build_conn_req(), tracker_url))
                        self.threads.append(th)
                        th.start()
                    else:
                        # Http tracker
                        th = threading.Thread(target=self.http_send, args=(tracker_url,))
                        self.threads.append(th)
                        th.start()
                for thr in self.threads:
                    thr.join()

            elif self.file_name != "_UPLOAD":
                self.global_flag = True  # used in case the program is unable to retrieve pieces from local network
                print("LOCAL FILE")
                with open(f"torrents\\info_hashes\\{self.file_name}", "rb") as f:
                    peers = bencode.bdecode(f.read())["announce-list"]
                self.peers = [tuple(peer) for peer in peers]
                print(self.peers)
            else:
                print("cannot download")

    def contact_udp(self, message, url):
        self.udp_send(message, url)

    def udp_send(self, message, url, sock=None):
        try:
            if not sock:
                sock = socket(AF_INET, SOCK_DGRAM)
                sock.bind(("0.0.0.0", 0))
                sock.settimeout(4)
            sock.sendto(message, (gethostbyname(url.hostname), url.port))
            self.listen(sock, url)

        except StopIteration:
            pass

        except Exception as e:
            print(f'Error: {e}')

    def http_send(self, url):
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
            answer_tracker = requests.get(url, params=params, timeout=4)
            list_peers = bencode.bdecode(answer_tracker.content)
            for peer in list_peers['peers']:
                self.peers.append((peer['ip'], peer['port']))
        except Exception as e:
            print(f'Error: {e}')

    def listen(self, sock, url):
        try:
            ret = sock.recv(self.__BUF)
        except: return

        try:
            self.TCP_IP_PORT = pickle.loads(ret)
        except:
            if resp_type(ret) == 'connect':
                print("connect")
                lock.acquire()
                self.conn_id = ret[8:16]
                self.tran_id = ret[4:8]
                announce_req = self.build_announce_req()
                lock.release()
                self.udp_send(announce_req,url, sock=sock)
            elif resp_type(ret) == 'announce':
                print("announce")
                n = 0
                while 24 + 6 * n <= len(ret):
                    ip = inet_ntoa(ret[20 + 6 * n: 24 + 6 * n])
                    port = int.from_bytes(ret[24 + 6 * n: 26 + 6 * n], 'big')
                    # only add peer if needed
                    lock.acquire()
                    if (ip, port) not in self.peers:
                        self.peers.append((ip, port))
                    n += 1
                    lock.release()
                print(self.peers)
            else:
                # Error code 3
                if int.from_bytes(ret[:4], byteorder='big') == 3:
                    print("=== ERROR ===")
                    print(ret[8:].decode())
                else:
                    print("WAIT WHAT?")

    def build_announce_req(self):
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
        message += self.torrent.port.to_bytes(2, byteorder='big')
        return message

    def init_tcp_sock(self):
        file_sock = socket(AF_INET, SOCK_STREAM)
        file_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        file_sock.bind(("0.0.0.0", self.torrent.port))
        file_sock.listen(5)
        return file_sock

    def fetch_torrent_file(self, file_name=None):
        try:
            if not file_name:
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
            return

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

            # creates a clean file with given file name
            with open(f"torrents\\info_hashes\\{filename}", "wb") as w:
                w.write(b"")

            self.sock.sendto(b"FLOW", addr)  # start flow of metadata content
            s = 0
            length = int(pickle.loads(self.sock.recv(self.__BUF)))
            print(length)
            while s != length:
                data = self.sock.recv(self.__BUF)

                s += len(data)
                with open(f"torrents\\info_hashes\\{filename}", "ab") as f:
                    f.write(data)
                self.sock.sendto(b"FLOW", addr)  # continue flow of metadata content

            print("received torrent file from local tracker")
            return filename

    def done_downloading(self, downloaded_peers):
        self.sock.sendto(f"DONE DOWNLOADING {self.file_name}".encode(), self.local_tracker)


lock = threading.Lock()

if __name__ == '__main__':
    Tracker()
