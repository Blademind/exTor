import _thread
import os
import pickle
import threading
import time
from random import randbytes
from socket import *

import requests
import select
from download_master import TrackerTCP
from torrents_handler import info_torrent
from difflib import get_close_matches
from py1337x import py1337x
import torf
import bencode

def build_error_response(msg):
    message = (3).to_bytes(4, byteorder='big')  # action - connect
    message += randbytes(4)  # transaction_id
    message += msg.encode()
    return message


class Tracker:
    def __init__(self):
        self.torrents_search_object = py1337x()
        self.server_sock = self.init_udp_sock(55555)  # udp socket with given port
        self.__BUF = 1024
        self.read_udp, self.write_udp = [self.server_sock], []  # read write for select udp
        self.connection_ids = {}  # list of all connected clients
        self.ip_addresses = {}
        self.reset_ip_addresses()  # reset lists of ip addresses
        _thread.start_new_thread(self.deleter_timer, ())
        self.listen_udp()  # listen

    def deleter_timer(self):
        """
        removes ip after an hour (according to protocol)
        :return:
        """
        timer = 3600
        while 1:
            size_changed = False
            # adds all ips-times into one list
            for torrent in self.ip_addresses.values():
                if len(torrent) != 0:
                    for ip in torrent:
                        if time.time() - ip[1] >= timer:
                            self.ip_addresses[
                                list(self.ip_addresses.keys())[list(self.ip_addresses.values()).index(torrent)]].remove(
                                ip)
                            size_changed = True
                            break
                if size_changed:
                    break
            time.sleep(1)

    def reset_ip_addresses(self):
        for i in info_torrent.values():
            self.ip_addresses[i] = []

    def init_udp_sock(self, port):
        server_sock = socket(AF_INET, SOCK_DGRAM)
        server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_sock.bind(("0.0.0.0", port))
        return server_sock

    def listen_udp(self):
        """
        Listens to incoming communications
        """
        print("Server is now listening")
        while 1:
            readable, writeable, ex = select.select(self.read_udp, self.write_udp, [])
            for sock in readable:
                data, addr = sock.recvfrom(self.__BUF)
                if not data:
                    break
                if data == b'FIND LOCAL TRACKER':
                    sock.sendto(pickle.dumps((gethostbyname(gethostname()), 55555)), addr)
                else:
                    try:
                        datacontent = data.decode()
                        # MESSAGE FROM INFO SERVER
                    except:
                        datacontent = ""

                    if datacontent[:4] == "GET ":
                        torrent_files = os.listdir("torrents")
                        matches = get_close_matches(datacontent[4:], torrent_files)
                        if matches:
                            locals_ = [match for match in matches if match[-12:-8] == "_LOC"]
                            if locals_:
                                file_name = locals_[0]
                                threading.Thread(target=self.send_torrent_file, args=(file_name, addr)).start()
                                self.add_peer_to_LOC(file_name, addr)
                                # add the client inside loc file after sending the file
                            else:
                                file_name = matches[0]
                                threading.Thread(target=self.send_torrent_file, args=(file_name, addr)).start()
                                # send the client the file via udp

                        else:
                            # search 1337x for a torrent matching request, get the torrent and send it to the client
                            query = datacontent[4:]
                            try:
                                url = f'https://itorrents.org/torrent/{self.torrents_search_object.info(link=self.torrents_search_object.search(query)["items"][0]["link"])["infoHash"]}.torrent'
                                show = requests.get(url, headers={'User-Agent': 'Chrome'})
                                bdecoded_torrent = bencode.bdecode(show.content)
                                file_name = f"{bdecoded_torrent['info']['name']}.torrent"
                                with open(f"torrents\\{file_name}", "wb") as w:
                                    w.write(show.content)

                                threading.Thread(target=self.send_torrent_file, args=(file_name, addr)).start()
                            except IndexError:
                                print("no torrents matching query found")

                            pass

                    # request must be at least 16 bytes long
                    if len(data) >= 16:
                        try:
                            action = int.from_bytes(data[8:12], byteorder="big")  # action type
                            # action is connect
                            if action == 0:
                                print(f"New connection from {addr}")
                                sock.sendto(self.build_connect_response(), addr)  # send a connect response

                            # action is announce
                            elif action == 1:
                                connection_id = data[:8]  # connection id
                                # 2 minutes must have not passed from connect request to announce request
                                try:
                                    if 0 <= int(time.time() - self.connection_ids[connection_id]) <= 120:
                                        torrent_name = info_torrent[data[16:36]]
                                        self.ip_addresses[torrent_name].append((addr, time.time()))
                                        sock.sendto(self.build_announce_response(addr, torrent_name), addr)
                                    else:
                                        sock.sendto(build_error_response("announce timeout"), addr)

                                    del self.connection_ids[connection_id]  # action is announce, remove connection id
                                except Exception as e:
                                    print("sent connection id was not found")
                        except Exception as e:
                            print(e)
                            print("received unparsable data")

    def add_peer_to_LOC(self, file_name, addr):
        with open(f"torrents\\{file_name}", "rb") as f:
            torrent_data = bencode.bdecode(f.read())
        torrent_data["announce-list"].append(f"{addr[0]}:{addr[1]}")
        with open(f"torrents\\{file_name}", "wb") as f:
            f.write(bencode.bencode(torrent_data))

    def send_torrent_file(self, file_name, addr):
        print(f"Now sending torrent file to {addr}")
        sock = self.init_udp_sock(0)
        sock.sendto(file_name.encode(), addr)
        data = sock.recv(1024)

        if data == b"FLOW":
            length = os.path.getsize(f"torrents\\{file_name}")
            sock.sendto(pickle.dumps(length), addr)
            with open(f"torrents\\{file_name}", "rb") as f:
                sock.sendto(f.readline(1024), addr)
                while f:
                    data = sock.recv(1024)
                    if data == b"FLOW":
                        sock.sendto(f.readline(1024), addr)
                    else:
                        print(f"Error sending torrent file to {addr}")
                        break
        else:
            print("did not receive what was expected")

    def recv_files(self, sock):
        data = None
        try:
            data = sock.recv(self.__BUF)
        except:
            print("file name was not received on time")
        try:
            datacontent = data.decode()
            filename = datacontent
            if filename[-8:] != ".torrent":
                return
            sock.send("FLOW".encode())
            s = 0
            length = int(pickle.loads(sock.recv(self.__BUF)))

            while s != length:
                data = sock.recv(self.__BUF)
                s += len(data)
                with open(f"torrents\\{filename}", "ab") as f:
                    f.write(data)
                sock.send("FLOW".encode())
            sock.send("DONE".encode())
        except:
            return

    def build_announce_response(self, addr, torrent_name):
        message = (1).to_bytes(4, byteorder='big')  # action - announce
        message += randbytes(4)  # transaction_id
        message += (0).to_bytes(4, byteorder='big')  # interval - 0 so none
        message += (0).to_bytes(4, byteorder='big')  # leechers (TO DO)
        message += (0).to_bytes(4, byteorder='big')  # seeders (TO DO)
        for ip_port in self.ip_addresses[torrent_name]:
            if addr != ip_port[0]:
                message += inet_aton(ip_port[0][0])  # ip
                message += ip_port[0][1].to_bytes(2, byteorder='big')  # port
        return message

    def build_connect_response(self):
        message = (0).to_bytes(4, byteorder='big')  # action - connect
        message += randbytes(4)  # transaction_id
        connection_id = randbytes(8)
        self.connection_ids[connection_id] = time.time()  # time the moment id was added
        message += connection_id
        return message


if __name__ == '__main__':
    threading.Thread(target=TrackerTCP).start()
    Tracker()
