import pickle
import time
from socket import *
import os

import bencode

print("Welcome to file uploader\n"
      "Here you can upload your own file to a tracker")


class Upload:
    def __init__(self):
        tempsock = socket(AF_INET, SOCK_DGRAM)
        self.upload_immense(tempsock, ("127.0.0.1", 55555))
        ip_port = pickle.loads(tempsock.recv(1024))
        c = 0
        torrents = os.listdir("torrents")
        for t in torrents:
            print(c, t)
            c += 1
        try:
            self.torrent = torrents[int(input("what torrent would you like to send?\n"))]
            print(self.torrent, "chosen")
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(ip_port)
            self.sock.send("START".encode())
            time.sleep(0.1)
            self.sock.send(self.torrent.encode())
            self.__BUF = 1024
            self.listen()
        except TypeError:
            print("not valid")

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
                length = os.path.getsize(f"torrents\\{self.torrent}")
                print(length)
                s = 0
                self.sock.send(pickle.dumps(length))
                with open(f"torrents\\{self.torrent}", "rb") as f:
                    while f:
                        if datacontent == "FLOW":
                            file_data = f.read(self.__BUF)
                            print(file_data)
                            s += len(file_data)
                            print(s)
                            self.sock.send(file_data)
                        datacontent = self.sock.recv(self.__BUF).decode()
            print(data)

    def upload_immense(self, temp, addr):
        temp.sendto("TCP_SERVER".encode(), addr)


if __name__ == '__main__':
    Upload()
