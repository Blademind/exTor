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
import bencode

class Tracker:
    def __init__(self):
        """
        Create a Tracker object
        """
        self.torrents_search_object = py1337x()

        self.server_sock = self.init_udp_sock(55555)  # udp socket with given port
        self.__BUF = 1024
        self.read_udp, self.write_udp = [self.server_sock], []  # read write for select udp


        self.connection_ids = {}  # list of all connected clients
        self.ip_addresses = {}
        self.reset_ip_addresses()  # reset lists of ip addresses

        _thread.start_new_thread(self.deleter_timer, ())  # remove peer after set time
        self.listen_udp()  # listen

    def deleter_timer(self):
        """
        removes ip after an hour (according to protocol)
        :return: None
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
        """
        Puts an empty list on each of the owned files, will be filled with peers
        :return: None
        """
        for i in info_torrent.values():
            self.ip_addresses[i] = []

    def init_udp_sock(self, port):
        """
        Creates a udp sock listening on given port
        :param port: port of the socket
        :return: the end created socket
        """
        server_sock = socket(AF_INET, SOCK_DGRAM)
        server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_sock.bind(("0.0.0.0", port))
        return server_sock

    def listen_udp(self):
        """
        Listens to incoming communications
        """
        print("UDP Server is now listening\n")
        while 1:
            readable, writeable, ex = select.select(self.read_udp, self.write_udp, [])
            for sock in readable:
                data, addr = sock.recvfrom(self.__BUF)
                if not data:
                    break
                try:
                    datacontent = data.decode()
                    # MESSAGE FROM INFO SERVER
                except:
                    datacontent = ""

                if datacontent == "FIND LOCAL TRACKER":
                    sock.sendto(pickle.dumps((gethostbyname(gethostname()), 55555)), addr)

                elif datacontent[:17] == "DONE DOWNLOADING ":
                    torrent_files = os.listdir("torrents")
                    file_name = datacontent[17:]
                    if file_name in torrent_files:
                        # create a local file
                        if not os.path.exists(f"torrents\\{file_name[:-8]}_LOC.torrent"):
                            with open(f"torrents\\{file_name[:-8]}_LOC.torrent", "wb") as w:
                                with open(f"torrents\\{file_name}", "rb") as f:
                                    torrent = bencode.bdecode(f.read())
                                    torrent["announce"] = ""
                                    torrent["announce-list"] = [addr]
                                    w.write(bencode.bencode(torrent))
                        else:
                            with open(f"torrents\\{file_name[:-8]}_LOC.torrent", "rb+") as f:
                                torrent = bencode.bdecode(f.read())
                                if addr not in torrent["announce-list"]:
                                    torrent["announce-list"].append(addr)
                                f.write(bencode.bencode(torrent))
                            # add peer to already created local file
                        sock.sendto(b"UPDATED", addr)

                    else:
                        print("given file name not in the torrents dir")

                elif datacontent[:4] == "GET ":
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

                # # request must be at least 16 bytes long
                # if len(data) >= 16:
                #     try:
                #         action = int.from_bytes(data[8:12], byteorder="big")  # action type
                #         # action is connect
                #         if action == 0:
                #             print(f"New connection from {addr}")
                #             sock.sendto(self.build_connect_response(), addr)  # send a connect response
                #
                #         # action is announce
                #         elif action == 1:
                #             connection_id = data[:8]  # connection id
                #             # 2 minutes must have not passed from connect request to announce request
                #             try:
                #                 if 0 <= int(time.time() - self.connection_ids[connection_id]) <= 120:
                #                     torrent_name = info_torrent[data[16:36]]
                #                     self.ip_addresses[torrent_name].append((addr, time.time()))
                #                     sock.sendto(self.build_announce_response(file_name, addr), addr)
                #                 else:
                #                     sock.sendto(self.build_error_response("announce timeout"), addr)
                #
                #                 del self.connection_ids[connection_id]  # action is announce, remove connection id
                #             except Exception as e:
                #                 print("sent connection id was not found")
                #     except Exception as e:
                #         print(e)
                #         print("received unparsable data")

    def add_peer_to_LOC(self, file_name, addr):
        """
        Adds given peer to a local torrent file
        :param file_name: local file name
        :param addr: address of peer
        :return: None
        """
        with open(f"torrents\\{file_name}", "rb") as f:
            torrent_data = bencode.bdecode(f.read())

        torrent_data["announce-list"].append(f"{addr[0]}:{addr[1]}")

        with open(f"torrents\\{file_name}", "wb") as f:
            f.write(bencode.bencode(torrent_data))

    def send_torrent_file(self, file_name, addr):
        """
        Sends available torrent file to a peer requesting it
        :param file_name: file name
        :param addr: address of peer
        :return: None
        """
        print(f"Now sending torrent file to {addr}")
        sock = self.init_udp_sock(0)
        sock.sendto(file_name.encode(), addr)
        data = sock.recv(self.__BUF)

        if data == b"FLOW":
            length = os.path.getsize(f"torrents\\{file_name}")
            sock.sendto(pickle.dumps(length), addr)
            with open(f"torrents\\{file_name}", "rb") as f:
                sock.sendto(f.readline(self.__BUF), addr)
                while f:
                    data = sock.recv(self.__BUF)
                    if data == b"FLOW":
                        sock.sendto(f.readline(self.__BUF), addr)
                    else:
                        print(f"Error sending torrent file to {addr}")
                        break
        else:
            print("did not receive what was expected")

    def build_announce_response(self, file_name, addr):
        """
        Builds announce response, sent after peer announcement
        :param file_name: file name
        :param addr: address of peer
        :return: announce message which will be sent to peer
        """
        message = (1).to_bytes(4, byteorder='big')  # action - announce
        message += randbytes(4)  # transaction_id
        message += (0).to_bytes(4, byteorder='big')  # interval - 0 so none
        message += (0).to_bytes(4, byteorder='big')  # leechers (TO DO)
        message += (0).to_bytes(4, byteorder='big')  # seeders (TO DO)
        for ip_port in self.ip_addresses[file_name]:
            if addr != ip_port[0]:
                message += inet_aton(ip_port[0][0])  # ip
                message += ip_port[0][1].to_bytes(2, byteorder='big')  # port
        return message

    def build_connect_response(self):
        """
        Builds connect response, sent after peer connection request
        :return: connect message which will be sent to peer
        """
        message = (0).to_bytes(4, byteorder='big')  # action - connect
        message += randbytes(4)  # transaction_id
        connection_id = randbytes(8)
        self.connection_ids[connection_id] = time.time()  # time the moment id was added
        message += connection_id
        return message

    def build_error_response(self, msg):
        """
        Builds error response, sent when error has occurred
        :param msg: the message of the error
        :return: error response which will be sent to peer
        """
        message = (3).to_bytes(4, byteorder='big')  # action - connect
        message += randbytes(4)  # transaction_id
        message += msg.encode()
        return message

if __name__ == '__main__':
    threading.Thread(target=TrackerTCP).start()
    Tracker()
