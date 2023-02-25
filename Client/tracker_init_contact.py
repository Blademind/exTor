from socket import *
import pickle


def find_local_tracker():
    msg = b'FIND LOCAL TRACKER'
    sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.settimeout(2)
    sock.bind((get_ip_addr(), 0))

    sock.sendto(msg, ("255.255.255.255", 55555))
    try:
        data = sock.recv(1024)
        try:
            ip = pickle.loads(data)
            test_open = sock.connect_ex(ip)
            if test_open != 0:
                print("tracker is not connectable")
                return
            print("found local tracker")
            return ip
        except KeyError:
            print("fatal error while searching for local tracker")
    except:
        print("no response from local tracker")
        return

def get_ip_addr():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8',53))
    ip = s.getsockname()[0]
    s.close()
    return ip