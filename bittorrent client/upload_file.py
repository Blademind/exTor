import pickle
import socket
import time
from socket import *
import os

import bencode

print("Welcome to exTorrent upload service\n"
      "Here you can upload your own file to a tracker\n"
      "NOTE: SENDING CORRUPTED .torrent FILES WILL BAN YOU FROM THE SERVICE")


class Upload:
    def __init__(self):
        c = 0
        torrents = os.listdir("torrents\\info_hashes")
        for t in torrents:
            print(c, t)
            c += 1
        choice = int(input("what torrent would you like to send?\n"))
        while choice >= len(torrents):
            print("invalid choice, try again")
            choice = int(input("what torrent would you like to send?\n"))
        self.torrent = torrents[choice]
        print(self.torrent, "chosen")
        self.sock = socket(AF_INET, SOCK_STREAM)
        try:
            self.sock.connect(("127.0.0.1", 55556))  # tracker upload ip
            self.sock.send(self.torrent.encode())
            self.__BUF = 1024
            self.listen()
        except:
            print("Error connecting to server")

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
                print("file already exists on tracker . . .")
                break
            if datacontent == "DONE":
                print(self.torrent, "successfully uploaded to tracker")
                break


if __name__ == '__main__':
    Upload()
