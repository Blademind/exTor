import pickle
import socket
import threading
from socket import *
import os
from main import Handler
import tracker_init_contact
from torf import Torrent
import ssl
import warnings


def get_ip_addr():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8',53))
    ip = s.getsockname()[0]
    s.close()
    return ip


def folders_in(path_to_parent):
    for fname in os.listdir(path_to_parent):
        if os.path.isdir(os.path.join(path_to_parent,fname)):
            return True
    return False


class Upload:
    def __init__(self, ui=False):
        global torrent
        if ui:
            self.ui_sock = socket(AF_INET, SOCK_STREAM)
            self.ui_sock.connect(("127.0.0.1", 9999))
        else:
            self.ui_sock = None

        self.local_tracker = tracker_init_contact.find_local_tracker()
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((get_ip_addr(), 0))
        self.sock = ssl.wrap_socket(self.sock, server_side=False, keyfile='private-key.pem', certfile='cert.pem')
        try:
            if self.local_tracker:
                self.path = input("Enter the path of the file\s you would like to upload -> ")
                self.torrent = self.create_metadata_file(self.path)

                while self.torrent is None or folders_in(self.path):
                    print("torrent could not be created on this path")
                    self.path = input("Enter the path of the file\s you would like to upload -> ")
                    self.torrent = self.create_metadata_file(self.path)

                threading.Thread(target=self.exit_function).start()

                try:
                    self.sock.connect((self.local_tracker[0], 55556))  # tracker downloader ip (tcp)
                    self.sock.send(self.torrent.encode())
                    self.__BUF = 1024
                    self.listen()
                except:
                    print("Error connecting to Tracker")
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)

    def create_metadata_file(self, path):
        try:
            t = Torrent(
                path=path,
                trackers=[],
                comment='This file was created using the upload file algorithm by Alon Levy')
            t.generate()
            torrent_name = f"{os.path.split(os.path.basename(path))[1]}_UPLOAD.torrent"
            print(torrent_name)

            t.write(f"torrents\\info_hashes\\{torrent_name}")

            return torrent_name

        except Exception as e:
            print(e)
            return

    def listen(self):
        while 1:
            data = self.sock.recv(self.__BUF)
            if not data:
                break
            try:
                datacontent = data.decode()
            except:
                break
            if datacontent == "FLOW":
                length = os.path.getsize(f"torrents\\info_hashes\\{self.torrent}")
                s = 0
                self.sock.send(pickle.dumps(length))
                with open(f"torrents\\info_hashes\\{self.torrent}", "rb") as f:
                    while f:
                        if datacontent == "FLOW":
                            file_data = f.read(self.__BUF)
                            s += len(file_data)
                            self.sock.send(file_data)
                        elif datacontent == "DONE":
                            break

                        datacontent = self.sock.recv(self.__BUF).decode()

            elif datacontent == "FILE_EXISTS":
                print("file already exists on tracker")
                break

            if datacontent == "DONE":
                print(self.torrent, "successfully uploaded to tracker")
                threading.Thread(target=Handler, args = (self.torrent,self.path, self.sock.getsockname()[1])).start()
                break

    def exit_function(self):
        try:
            while 1:
                input()
        except UnicodeDecodeError:
            try:
                self.sock.send(f"REMOVE {self.torrent}".encode())
            except:
                pass
            if self.torrent:
                print(self.torrent)
                os.remove(f"torrents\\info_hashes\\{self.torrent}")
            print("\nprogram ended")


if __name__ == '__main__':
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    Upload()
