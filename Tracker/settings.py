import datetime
import math
import time
import sqlite3
import pickle


def init():
    global requests, admin_ips
    requests = [0, {}]
    admin_ips = []


def ban_ip(ip, tracker_sock):
    """
    Adds ip to banned ips text file,
    which will not be able to contact the tracker afterwards
    :param ip: ip to ban
    :param banned_ips: the banned ips list
    :return: None
    """
    if ip not in admin_ips:
        conn = sqlite3.connect("databases\\swarms_data.db")
        curr = conn.cursor()
        curr.execute("SELECT * FROM BannedIPS WHERE address=?", (ip,))
        exists = curr.fetchall()
        print(exists)
        if len(exists) == 0:
            curr.execute("INSERT INTO BannedIPs VALUES(?);", (ip,))
            conn.commit()

        curr.execute("SELECT name FROM sqlite_master WHERE type='table' AND name!='BannedIPs';")
        table_names = curr.fetchall()
        for file_name in table_names:
            curr.execute(f"""SELECT * FROM "{file_name[0]}" """)
            records = curr.fetchall()

            for raw_addr, _, _ in records:
                addr = pickle.loads(raw_addr)
                print(addr)
                tracker_sock.sendto(f"BAN_IP {ip}".encode(), addr)


        conn.close()


if __name__ == '__main__':
    requests = [0, {}]
    admin_ips = []
    init()
