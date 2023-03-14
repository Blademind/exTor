# import _thread
import os.path
import pickle
import threading
# import time
from random import randbytes
from socket import *

import bencode

# from torrents_handler import info_torrent

import select
import sqlite3
import ssl
import time
def build_error_response(msg):
    """
    Builds error response, sent when error has occurred
    :param msg: the message of the error
    :return: error response which will be sent to peer
    """
    message = (3).to_bytes(4, byteorder='big')  # action - connect
    message += randbytes(4)  # transaction_id
    message += msg.encode()
    return message


def ban_ip(ip, banned_ips):
    """
    Adds ip to banned ips text file,
    which will not be able to contact the tracker afterwards
    :param ip: ip to ban
    :param banned_ips: the banned ips list
    :return: None
    """
    conn = sqlite3.connect("databases\\users.db")
    curr = conn.cursor()
    curr.execute("INSERT INTO BannedIPs VALUES (?)", ip[0])
    conn.close()

    # if ip[0] not in banned_ips:
    #     with open("banned_ips.txt", "a") as f:
    #         f.write(f"{ip[0]}\n")


class TrackerTCP:
    """
    Create a Download Master object
    """
    def __init__(self):
        with open("banned_ips.txt", "r") as f:
            self.banned_ips = f.read().split("\n")
        self.server_sock = None  # udp sock
        self.init_tcp_sock()
        self.__BUF = 1024
        self.read_tcp, self.write_tcp = [self.server_sock], []  # read write for select udp

        conn = sqlite3.connect("databases\\users.db")
        curr = conn.cursor()
        curr.execute(f"""CREATE TABLE IF NOT EXISTS BannedIPs
         (address TEXT)""")
        conn.close()

        threading.Thread(target=self.listen_tcp).start()

    def init_tcp_sock(self):
        self.server_sock = socket(AF_INET, SOCK_STREAM)
        self.server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_sock.bind(("0.0.0.0", 55556))
        self.server_sock.listen(5)
        self.server_sock = ssl.wrap_socket(self.server_sock, server_side=True, keyfile='private-key.pem', certfile='cert.pem')

    def get_ip_port(self):
        return gethostbyname(gethostname()), self.server_sock.getsockname()[1]

    def listen_tcp(self):
        print("TCP Server is now listening\n")
        while 1:
            readable, writeable, ex = select.select(self.read_tcp, self.write_tcp, [])
            for sock in readable:
                if sock == self.server_sock:
                    conn, addr = self.server_sock.accept()

                    conn_db = sqlite3.connect("databases\\users.db")
                    curr = conn_db.cursor()
                    curr.execute("SELECT * FROM BannedIPs")
                    self.banned_ips = curr.fetchall()
                    conn_db.close()
                    print("banned ips:",self.banned_ips)
                    # with open("banned_ips.txt", "r") as f:
                    #     self.banned_ips = f.read().split("\n")
                    if addr[0] in self.banned_ips:
                        conn.close()
                        break

                    print(f"Connection from {addr}")
                    conn.settimeout(5.0)
                    readable.append(conn)

                else:
                    try:
                        data = sock.recv(self.__BUF)
                        if not data:
                            readable.remove(sock)
                            break
                    except:
                        readable.remove(sock)
                        break
                    datacontent = data.decode()
                    print(datacontent)
                    # file upload immensing
                    if datacontent[-8:] == ".torrent":
                        threading.Thread(target=self.recv_files, args=(sock, datacontent)).start()
                    elif datacontent == "ADMIN":
                        sock.send(b"FUCK YOU ADMIN!")

    def recv_files(self, sock, filename):
        try:
            if not os.path.exists(f"torrents\\{filename}"):
                sock.send("FLOW".encode())
                s = 0
                length = int(pickle.loads(sock.recv(self.__BUF)))  # awaiting client to send the file's length
                print(f"{filename} download has started ({length} bytes)")
                while s != length:
                    data = sock.recv(self.__BUF)
                    s += len(data)
                    with open(f"torrents\\{filename}", "ab") as f:
                        f.write(data)
                    if length != s:
                        sock.send("FLOW".encode())
                print(f"Done downloading {filename}")
                sock.send("DONE".encode())
                with open(f'torrents\\{filename}', 'rb') as t:
                    torrent = t.read()
                torrent = bencode.bdecode(torrent)
                torrent["announce-list"] = [sock.getpeername()]
                torrent["announce"] = []
                print(torrent["announce-list"])
                with open(f'torrents\\{filename}', 'wb') as t:
                    t.write(bencode.bencode(torrent))

                conn = sqlite3.connect("databases\\torrent_swarms.db")
                curr = conn.cursor()
                curr.execute(f"""CREATE TABLE IF NOT EXISTS "{filename}"
                 (address BLOB, time REAL)""")

                curr.execute(f"""INSERT INTO "{filename}" VALUES 
                (?, ?)""", (pickle.dumps(sock.getpeername()), time.time()))
                conn.commit()
                conn.close()
                self.check_newly_added_file(filename, sock)
            else:
                sock.send("FILE_EXISTS".encode())
        except Exception as e:
            print("Exception:", e)
            return

    def check_newly_added_file(self, filename, sock):
        with open(f"torrents\\{filename}", "rb") as f:
            try:
                bencode.bdecode(f.read())
            except bencode.exceptions.BencodeDecodeError:
                print(filename, "is corrupted, removing")
                f.close()
                os.remove(f"torrents\\{filename}")

                conn = sqlite3.connect("databases\\torrent_swarms.db")
                curr = conn.cursor()
                curr.execute(f"""DELETE FROM "{filename}" WHERE address=?""", (sock.getpeername(),))
                conn.commit()
                conn.close()

                print(filename, "removed")
                print("Banning", sock.getpeername()[0])
                ban_ip(sock.getpeername(), self.banned_ips)


if __name__ == '__main__':
    TrackerTCP()
