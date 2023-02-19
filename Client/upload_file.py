import pickle
import socket
import threading
import time
from socket import *
import os
from main import Handler
import tracker_init_contact
import bencode

# print("Welcome to exTorrent upload service\n"
#       "Here you can upload your own file to a tracker\n"
#       "NOTE: SENDING CORRUPTED .torrent FILES WILL BAN YOU FROM THE SERVICE")


class Upload:
    def __init__(self):
        self.local_tracker = tracker_init_contact.find_local_tracker()
        try:
            if self.local_tracker:
                c = 0
                torrents = os.listdir("torrents\\info_hashes")
                for t in torrents:
                    print(c, t)
                    c += 1

                choice = input("what torrent would you like to send? -> ")
                while not choice.isnumeric() or int(choice) >= len(torrents):
                    print("invalid choice, try again")
                    choice = input("what torrent would you like to send? -> ")

                self.torrent = torrents[int(choice)]
                print(self.torrent, "chosen")

                self.sock = socket(AF_INET, SOCK_STREAM)
                try:
                    self.sock.connect((self.local_tracker[0], 55556))  # tracker downloader ip (tcp)
                    self.sock.send(self.torrent.encode())
                    self.__BUF = 1024
                    self.listen()
                except:
                    print("Error connecting to Tracker")
        except Exception as e:
            print(e)

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
                threading.Thread(target=Handler, args = (self.torrent,)).start()
                break


if __name__ == '__main__':
    Upload()
