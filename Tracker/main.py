import os
import pickle
import sys
import threading
import time
from socket import *
import requests
import select
from download_master import TrackerTCP
from difflib import get_close_matches
from py1337x import py1337x
import bencode
import urllib3
import settings
import redis


def errormng(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(e)
    return wrapper


def get_ip_addr():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 53))
    ip = s.getsockname()[0]
    s.close()
    return ip


class Tracker:
    def __init__(self):
        """
        Create a Tracker object
        """
        settings.init()
        self.torrents_search_object = py1337x(proxy="1337xx.to")

        self.server_sock = self.init_udp_sock(12345)  # udp socket with given port
        self.__BUF = 1024
        self.read_udp, self.write_udp = [self.server_sock], []  # read write for select udp

        redis_host = "localhost"
        redis_port = 6379
        self.r = redis.StrictRedis(host=redis_host, port=redis_port)
        threading.Thread(target=self.requests_check).start()
        self.listen_udp()  # listen

    def requests_check(self):
        while 1:
            requests_per_ip = settings.requests[1]
            for ip in requests_per_ip:
                requests_ip = requests_per_ip[ip]
                print(requests_ip, ip)
                if requests_ip >= 10:  # more than 10 requests in 5 seconds, Ban
                    settings.ban_ip(ip, self.r)
            time.sleep(5)

    def init_udp_sock(self, port):
        """
        Creates a udp sock listening on given port
        :param port: port of the socket
        :return: the end created socket
        """
        server_sock = socket(AF_INET, SOCK_DGRAM)
        server_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        server_sock.bind((get_ip_addr(), port))
        return server_sock

    def listen_udp(self):
        """
        Listens to incoming communications
        """
        print("UDP Server is now listening\n")
        while 1:
            readable, writeable, ex = select.select(self.read_udp, self.write_udp, [])
            for sock in readable:
                try:
                    data, addr = sock.recvfrom(self.__BUF)
                except Exception as e:
                    print("Force connection close")
                    data = b""
                if not data:
                    break
                # conn = sqlite3.connect("databases\\users.db")
                # curr = conn.cursor()
                # curr.execute("SELECT * FROM BannedIPs WHERE address=?;", (addr[0],))
                # banned = curr.fetchall()
                try:
                    banned_ips = self.r.lrange("banned", 0, -1)
                    if addr[0].encode() in banned_ips:
                        print(f"{addr} tried to contact, and is banned")
                        break

                except: pass
                # conn.close()

                try:
                    datacontent = data.decode()
                    # MESSAGE FROM INFO SERVER
                except:
                    try:
                        datacontent = pickle.loads(data)
                        if "INFORM_SHARED_PEERS " in datacontent[0]:
                            sharing_peers = datacontent[1]
                            file_name = datacontent[0][20:]

                            peers = [pickle.loads(p) for p in self.r.lrange(file_name, 0, -1)]
                            for peer in sharing_peers:
                                if peer in peers:
                                    self.r.set(pickle.dumps(peer), time.time())

                    except Exception as e:
                        print("(listen_udp) error exception handling: ", e)
                        pass
                    break

                settings.requests[0] += 1  # another request detected
                if addr[0] in settings.requests[1]:
                    settings.requests[1][addr[0]] += 1
                else:
                    settings.requests[1][addr[0]] = 1

                if datacontent == "FIND_LOCAL_TRACKER":
                    sock.sendto(pickle.dumps((sock.getsockname()[0], 12345)), addr)

                elif datacontent[:17] == "DONE DOWNLOADING ":
                    torrent_files = os.listdir("torrents")
                    local_file_name = datacontent[17:]

                    if local_file_name in torrent_files:
                        if local_file_name[-15:-8] == "_UPLOAD" or local_file_name[-12:-8] == "_LOC":
                            # HAS ALL PIECES (ALREADY ADDED TO LOCAL FILE THOUGH)
                            pass
                            # self.add_peer_to_LOC(local_file_name, addr)

                        else:  # local file was not already created
                            print("address added to new LOC file:", addr)
                            self.r.lpush(f"{local_file_name[:-8]}_LOC.torrent", pickle.dumps(addr))
                            self.r.set(pickle.dumps(addr), time.time())
                            if not os.path.exists(f"torrents\\{local_file_name[:-8]}_LOC.torrent"):
                                with open(f"torrents\\{local_file_name[:-8]}_LOC.torrent", "wb") as w:
                                    with open(f"torrents\\{local_file_name}", "rb") as f:
                                        torrent = bencode.bdecode(f.read())
                                        torrent["announce"] = ""
                                        torrent["announce-list"] = [addr]
                                        w.write(bencode.bencode(torrent))

                            # add peer to already created local file
                        sock.sendto(b"UPDATED", addr)

                    else:
                        print("given file name not in the torrents dir")

                elif "FETCH_REQUESTS" == datacontent:
                    if self.r.get("admin_ip") is not None and self.r.get("admin_ip").decode() == addr[0]:
                        all_requests = settings.requests  # all requests recorded not inc. current request.
                        sock.sendto(pickle.dumps(all_requests), addr)
                        settings.requests[0] = 0
                        settings.requests[1] = {}
                    else:
                        sock.sendto(b"DENIED not an Admin", addr)

                    # if addr[0] in settings.admin_ips:
                    #     all_requests = settings.requests  # all requests recorded not inc. current request.
                    #     sock.sendto(pickle.dumps(all_requests), addr)
                    #     settings.requests[0] = 0
                    #     settings.requests[1] = {}
                    # else:
                    #     sock.sendto(b"DENIED not an Admin", addr)

                elif datacontent == "DONE_ADMIN_OPERATION":
                    if self.r.get("admin_ip") is not None and self.r.get("admin_ip").decode() == addr[0]:
                        self.r.delete("admin_ip")
                        settings.requests[0] = 0
                        settings.requests[1] = {}
                        print("reset after admin quit")
                    else:
                        sock.sendto(b"DENIED not an Admin", addr)

                elif datacontent[:6] == "BAN_IP":
                    if self.r.get("admin_ip") is not None and self.r.get("admin_ip").decode() == addr[0]:
                        settings.ban_ip(datacontent[7:], self.server_sock)

                    else:
                        sock.sendto(b"DENIED not an Admin", addr)

                elif datacontent[:4] == "GET ":
                    torrent_files = os.listdir("torrents")
                    matches = get_close_matches(f"{datacontent[4:]}", torrent_files, n=1, cutoff=0.6)
                    if matches:
                        locals_ = get_close_matches(f"{datacontent[4:]}_LOC", torrent_files, n=1, cutoff=0.6)
                        locals_ = [local for local in locals_ if "_LOC" in local]

                        uploads = get_close_matches(f"{datacontent[4:]}_UPLOAD", torrent_files, n=1, cutoff=0.6)
                        uploads = [upload for upload in uploads if "_UPLOAD" in upload]

                        if locals_:
                            local_file_name = locals_[0]
                            global_file_name = None

                            for file in matches:
                                if file != local_file_name:
                                    global_file_name = file
                                    break

                            if not global_file_name:
                                query = datacontent[4:]
                                self.torrent_from_web(query, addr, sock)

                                for file in get_close_matches(query, torrent_files, n=1, cutoff=0.6):
                                    if file != local_file_name:
                                        global_file_name = file
                                        break

                            threading.Thread(target=self.send_files, args=(local_file_name, global_file_name, addr)).start()

                        elif uploads:
                            upload_file_name = uploads[0]
                            threading.Thread(target=self.send_torrent_file, args=(upload_file_name, addr, True)).start()

                        else:
                            on_disk_file_name = matches[0]
                            threading.Thread(target=self.send_torrent_file, args=(on_disk_file_name, addr)).start()
                            # send the client the file via udp

                    else:
                        # search 1337x for a torrent matching request, get the torrent and send it to the client
                        query = datacontent[4:]
                        self.torrent_from_web(query, addr, sock)

    def add_peer_to_LOC(self, file_name, addr):
        """
        Adds given peer to a local torrent file
        :param file_name: local file name
        :param addr: address of peer
        :return: None
        """

        print("address added:", addr)
        peers = self.r.lrange(file_name, 0, -1)
        in_peers = None
        for peer in peers:
            peer_decode = pickle.loads(peer)
            if peer_decode[0] == addr[0]:
                in_peers = peer
                break
        if in_peers:
            self.r.lrem(file_name, 0, in_peers)
            self.r.delete(in_peers)

        self.r.lpush(file_name, pickle.dumps(addr))
        self.r.set(pickle.dumps(addr), time.time())
        with open(f"torrents\\{file_name}", "rb") as f:
            torrent = bencode.bdecode(f.read())

        if addr not in torrent["announce-list"]:
            torrent["announce-list"].append(addr)

        with open(f"torrents\\{file_name}", "wb") as f:
            f.write(bencode.bencode(torrent))

    def send_files(self, file_name, file_name2, addr):
        """
        send 2 files, the first is local metadata file, the second is global metadata file
        :param file_name: local metadata file
        :param file_name2: global metadata file
        :param addr: address to send to
        :return: None
        """

        self.send_torrent_file(file_name, addr)
        time.sleep(1)
        self.send_torrent_file(file_name2, addr)

        # adds the client to the local file after sending the file
        self.add_peer_to_LOC(file_name, addr)

    def torrent_from_web(self, query, addr, sock):
        # search 1337x for a torrent matching request, get the torrent and send it to the client
        try:
            url = f'https://itorrents.org/torrent/{self.torrents_search_object.info(link=self.torrents_search_object.search(query)["items"][0]["link"])["infoHash"]}.torrent'
            # proxy_url = "http://1c59c97fd195fca0605225780a99d418f20829ed:@proxy.zenrows.com:8001"
            # proxy = {
            #     "http": proxy_url,
            #     "https": proxy_url
            # }
            new_url = f"https://api.scrapingant.com/v2/general?url={url}&x-api-key=266642c85dd149be820da858b00f58d0&browser=false"
            show = requests.get(new_url, headers={'User-Agent': 'Chrome'}, verify=False)  # proxies=proxy
            bdecoded_torrent = bencode.bdecode(show.content)
            file_name = f"{bdecoded_torrent['info']['name']}.torrent"
            with open(f"torrents\\{file_name}", "wb") as w:
                w.write(show.content)

            threading.Thread(target=self.send_torrent_file, args=(file_name, addr)).start()
        except Exception as e:
            sock.sendto(b"NO TORRENTS FOUND", addr)
            print("Search exception:", e)

        except IndexError:
            print(f"no torrents matching {query} found",addr)
            sock.sendto(b"NO TORRENTS FOUND", addr)

    @errormng
    def send_torrent_file(self, file_name, addr, upload=False):
        """
        Sends available torrent file to a peer requesting it
        :param upload:
        :param file_name: file name
        :param addr: address of peer
        :return: None
        """
        print(f"Now sending {file_name} file to {addr}")
        sock = self.init_udp_sock(0)
        sock.sendto(file_name.encode(), addr)
        data = sock.recv(self.__BUF)
        sock.settimeout(1)

        # wait for client's "FLOW" message to start sending content
        if data == b"FLOW":
            length = os.path.getsize(f"torrents\\{file_name}")
            sock.sendto(pickle.dumps(length), addr)
            with open(f"torrents\\{file_name}", "rb") as f:

                data_to_send = f.read(self.__BUF)
                sock.sendto(data_to_send, addr)

                while len(data_to_send) != 0:
                    try:
                        data = sock.recv(self.__BUF)

                        # wait for client's "FLOW" message to continue sending content
                        if data == b"FLOW":
                            data_to_send = f.read(self.__BUF)
                            sock.sendto(data_to_send, addr)
                        else:
                            print(f"Error sending torrent file to {addr}")
                            break

                    except Exception as e:
                        print("Error file sending:", e)
                        break


        else:
            print("did not receive what was expected")
        print(f"{file_name} file was sent to {addr}")

        if upload:
            self.add_peer_to_LOC(file_name, addr)

    # region TRASH
    # def build_announce_response(self, file_name, addr):
    #     """
    #     Builds announce response, sent after peer announcement
    #     :param file_name: file name
    #     :param addr: address of peer
    #     :return: announce message which will be sent to peer
    #     """
    #     message = (1).to_bytes(4, byteorder='big')  # action - announce
    #     message += randbytes(4)  # transaction_id
    #     message += (0).to_bytes(4, byteorder='big')  # interval - 0 so none
    #     message += (0).to_bytes(4, byteorder='big')  # leechers (TO DO)
    #     message += (0).to_bytes(4, byteorder='big')  # seeders (TO DO)
    #     records = self.curr.fetchall()
    #     for raw_ip_port, _ in records:
    #         ip_port = pickle.loads(raw_ip_port)
    #         if addr != ip_port:
    #             message += inet_aton(ip_port[0])  # ip
    #             message += ip_port[1].to_bytes(2, byteorder='big')  # port
    #     return message
    #
    # def build_connect_response(self):
    #     """
    #     Builds connect response, sent after peer connection request
    #     :return: connect message which will be sent to peer
    #     """
    #     message = (0).to_bytes(4, byteorder='big')  # action - connect
    #     message += randbytes(4)  # transaction_id
    #     connection_id = randbytes(8)
    #     self.connection_ids[connection_id] = time.time()  # time the moment id was added
    #     message += connection_id
    #     return message
    #
    # def build_error_response(self, msg):
    #     """
    #     Builds error response, sent when error has occurred
    #     :param msg: the message of the error
    #     :return: error response which will be sent to peer
    #     """
    #     message = (3).to_bytes(4, byteorder='big')  # action - connect
    #     message += randbytes(4)  # transaction_id
    #     message += msg.encode()
    #     return message
    # endregion


def exit_function():
    try:
        while 1:
            input()
    except UnicodeDecodeError:
        # for torrent in os.listdir(f"torrents"):

            # if torrent[-12:-8] == "_LOC" or torrent[-15:-8] == "_UPLOAD":
            #     os.remove(f"torrents\\{torrent}")

        print("\nprogram ended")


def test_database():
    redis_host = "localhost"
    redis_port = 6379
    r = redis.StrictRedis(host=redis_host, port=redis_port)
    try:
        r.ping()
    except:
        print("redis database is offline, cannot continue")
        sys.exit(0)


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    test_database()
    threading.Thread(target=TrackerTCP).start()
    threading.Thread(target=exit_function).start()
    Tracker()


