import pickle
import socket
import threading
import time
from socket import *
import os
from main import Handler
import tracker_init_contact
import bencode
import hashlib
from torf import Torrent
import shutil
# print("Welcome to exTorrent upload service\n"
#       "Here you can upload your own file to a tracker\n"
#       "NOTE: SENDING CORRUPTED .torrent FILES WILL BAN YOU FROM THE SERVICE")

def get_ip_addr():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8',53))
    ip = s.getsockname()[0]
    s.close()
    return ip

class Upload:
    def __init__(self):
        self.local_tracker = tracker_init_contact.find_local_tracker()
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((get_ip_addr(), 0))
        try:
            if self.local_tracker:
                # c = 0
                # torrents = os.listdr("torrents\\info_hashes")
                # for t in torrents:
                #     print(c, t)
                #     c += 1

                self.path = input("Enter the path of the file\s you would like to upload -> ")
                self.torrent = self.create_metadata_file(self.path)
                while self.torrent is None:
                    print("torrent could not be created on this path, try again")
                    self.path = input("Enter the path of the file\s you would like to upload -> ")
                    self.torrent = self.create_metadata_file(self.path)

                # self.torrent = torrents[int(choice)]
                # print(self.torrent, "chosen")

                try:
                    self.sock.connect((self.local_tracker[0], 55556))  # tracker downloader ip (tcp)
                    self.sock.send(self.torrent.encode())
                    self.__BUF = 1024
                    self.listen()
                except:
                    print("Error connecting to Tracker")
        except Exception as e:
            print(e)

    def create_metadata_file(self, path):
        try:
            t = Torrent(
                path=path,
                trackers=[],
                comment='This file was created using the upload file algorithm')
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
                threading.Thread(target=Handler, args = (self.torrent,self.path)).start()
                break


if __name__ == '__main__':
    Upload()
