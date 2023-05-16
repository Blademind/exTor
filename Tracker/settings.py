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


requests = [0, {}]

if __name__ == '__main__':
    init()
