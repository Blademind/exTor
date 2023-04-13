import hashlib
import struct
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *


def is_handshake(msg):
    try:
        return msg[1:20].decode()[:19] == 'BitTorrent protocol'
    except:
        return False


def msg_type(msg):
    if not int.from_bytes(msg, 'big'):
        return "keep-alive"
    id_ = msg[0]
    if len(msg) == 1 and id_ == 0:
        return 'choke'
    elif len(msg) == 1 and id_ == 1:
        return 'unchoke'
    elif len(msg) == 5 and id_ == 4:
        return 'have'
    elif id_ == 5:
        return 'bitfield'
    elif id_ == 7:
        return 'piece'
    return
    # try:
    #     if msg[1:21].decode()[:19] == 'BitTorrent protocol':
    #         return 'handshake'
    #     return None
    # except:
    #     return None
    # else:
    #     if len(msg) == 4:
    #         if int.from_bytes(msg[:4], 'big') == 0:
    #             return 'keep-alive'


def server_msg_type(msg):
    id = msg[0]
    try:
        if id == 2:
            return 'interested'
        elif id == 6:
            return 'request'
    except:
        return


def build_handshake(tracker):
    message = (19).to_bytes(1, byteorder='big')  # pstrlen (const)
    message += "BitTorrent protocol".encode()  # pstr (const)
    message += (0).to_bytes(8, byteorder='big')  # reserved
    message += tracker.torrent.generate_info_hash()  # torrent info hash
    message += tracker.id  # peer_id
    return message


def build_keep_alive():
    return (0).to_bytes(4, byteorder='big')


def build_choke():
    message = (1).to_bytes(4, byteorder='big')  # len
    message += (0).to_bytes(1, byteorder='big')  # id
    return message


def build_unchoke():
    message = (1).to_bytes(4, byteorder='big')  # len
    message += (1).to_bytes(1, byteorder='big')  # id
    return message


def build_interested():
    message = (1).to_bytes(4, byteorder='big')  # len
    message += (2).to_bytes(1, byteorder='big')  # id
    return message


def build_not_interested():
    message = (1).to_bytes(4, byteorder='big')  # len
    message += (3).to_bytes(1, byteorder='big')  # id
    return message


def build_have(payload):
    message = (5).to_bytes(4, byteorder='big')  # len
    message += (4).to_bytes(1, byteorder='big')  # id
    message += struct.pack('>I', payload)
    return message


def build_bitfield(bitfield):
    print(bitfield)
    message = (1 + len(bitfield)).to_bytes(4, byteorder='big')  # len
    message += (5).to_bytes(1, byteorder='big')  # id
    message += bitfield
    return message


def build_request(index, begin, length):
    # print(index, begin, length)
    message = (13).to_bytes(4, byteorder='big')  # len
    message += (6).to_bytes(1, byteorder='big')  # id
    message += (index).to_bytes(4, byteorder='big')
    message += (begin).to_bytes(4, byteorder='big')
    message += (length).to_bytes(4, byteorder='big')
    return message


def build_piece(index, begin, block):
    message = (9+len(block)).to_bytes(4, byteorder='big')  # len
    message += (7).to_bytes(1, byteorder='big')  # id
    message += index.to_bytes(4, byteorder='big')
    message += begin.to_bytes(4, byteorder='big')
    message += block
    return message


def build_cancel(payload):
    message = (13).to_bytes(4, byteorder='big')  # len
    message += (8).to_bytes(1, byteorder='big')  # id
    message += (payload.index).to_bytes(4, byteorder='big')  #
    message += (payload.begin).to_bytes(4, byteorder='big')
    message += (len(payload)).to_bytes(4, byteorder='big')
    return message


def build_port(payload):
    message = (3).to_bytes(4, byteorder='big')  # len
    message += (9).to_bytes(1, byteorder='big')  # id
    message += payload.to_bytes(2, byteorder='big')  # listen port
    return message

