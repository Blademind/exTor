import datetime
import math
import time
import sqlite3
import pickle


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

        # conn = sqlite3.connect("databases\\users.db")
        # curr = conn.cursor()
        # curr.execute("SELECT * FROM BannedIPS WHERE address=?", (ip,))
        # exists = curr.fetchall()
        # print(exists)
        # if len(exists) == 0:
        #     curr.execute("INSERT INTO BannedIPs VALUES(?);", (ip,))
        #     conn.commit()
        #
        # curr.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='BannedIPs';")
        # table_names = curr.fetchall()
        # for file_name in table_names:
        #     curr.execute(f"""SELECT * FROM "{file_name[0]}" """)
        #     records = curr.fetchall()
        #
        #     for raw_addr, _, _ in records:
        #         addr = pickle.loads(raw_addr)
        #         print(addr)
        #         tracker_sock.sendto(f"BAN_IP {ip}".encode(), addr)
        #
        # conn.close()


requests = [0, {}]

if __name__ == '__main__':
    init()
