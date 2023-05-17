import pickle
from socket import *
import bencode
import os
def init():
    global requests
    requests = [0, {}]


def ban_ip(ip, r_server):
    """
    Adds ip to banned ips text file,
    which will not be able to contact the tracker afterwards
    :param ip: ip to ban
    :param banned_ips: the banned ips list
    :return: None
    """
    if r_server.get("admin_ip") is not None and r_server.get("admin_ip").decode() != ip:
        r_server.lrem("banned", 0, ip)
        r_server.lpush("banned", ip)
        print("Banned", ip)
        sock = socket(AF_INET, SOCK_DGRAM)
        sock.bind((get_ip_addr(), 0))
        file_names = []
        table_names = r_server.keys("*.torrent*")
        for file_name in table_names:
            print(file_name)
            records = r_server.lrange(file_name, 0, -1)
            for record in records:
                addr_peer = pickle.loads(record)
                print(addr_peer[0], ip)
                if addr_peer[0] == ip:
                    with open(f"torrents\\{file_name.decode()}", "rb") as f:
                        torrent_data = bencode.bdecode(f.read())

                    for i in torrent_data["announce-list"]:
                        if list(ip) == i:
                            torrent_data["announce-list"].remove(i)
                            break

                    if torrent_data["announce-list"]:
                        with open(f"torrents\\{file_name.decode()}", "wb") as f:
                            f.write(bencode.bencode(torrent_data))
                    else:
                        print("removed whole file:", file_name.decode())
                        os.remove(f"torrents\\{file_name.decode()}")

                    print(f"removed {ip} from {file_name.decode()}")
                    file_names.append(file_name)
                    break

        all_keys = r_server.keys("*")
        for key in all_keys:
            print(key)
            if b".torrent" in key:
                file_name = key
                records = r_server.lrange(file_name, 0, -1)
                for record in records:
                    created_ip = pickle.loads(record)
                    if created_ip[0] == ip:
                        r_server.lrem(file_name, 0, record)
                        print(f"removed {ip} from {file_name.decode()}")

            elif key != b"banned" and key != b"admin_ip":
                created_ip = pickle.loads(key)
                if ip == created_ip[0]:
                    r_server.delete(key)
                    print("deleted", created_ip)

        print(file_names)
        for file_name in file_names:
            records = r_server.lrange(file_name, 0, -1)
            for addr in records:
                addr_peer = pickle.loads(addr)
                print(addr_peer[0], ip[0])
                if addr_peer[0] != ip:
                    print(addr_peer)
                    sock.sendto(f"BAN_IP {ip}".encode(), addr_peer)
                    break


def get_ip_addr():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 53))
    ip = s.getsockname()[0]
    s.close()
    return ip


requests = [0, {}]

if __name__ == '__main__':
    init()
