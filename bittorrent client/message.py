import hashlib
import struct
from socket import *
import bencode
from urllib.parse import urlparse
from socket import *


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
    message = (1 + len(bitfield)).to_bytes(4, byteorder='big')  # len
    message += (5).to_bytes(1, byteorder='big')  # id
    message += bitfield
    return message


def build_request(index, begin, length):
    print(index, begin, length)
    message = (13).to_bytes(4, byteorder='big')  # len
    message += (6).to_bytes(1, byteorder='big')  # id
    message += (index).to_bytes(4, byteorder='big')
    message += (begin).to_bytes(4, byteorder='big')
    message += (length).to_bytes(4, byteorder='big')
    return message


def build_piece(payload):
    message = (9+len(payload.block)).to_bytes(4, byteorder='big')  # len
    message += (7).to_bytes(1, byteorder='big')  # id
    message += (payload.index).to_bytes(4, byteorder='big')
    message += (payload.begin).to_bytes(4, byteorder='big')
    message += payload.block
    return message


def build_cancel(payload):
    message = (13).to_bytes(4, byteorder='big')  # len
    message += (8).to_bytes(1, byteorder='big')  # id
    message += (payload.index).to_bytes(4, byteorder='big')  #
    message += (payload.begin).to_bytes(4, byteorder='big')
    message += (len(payload)).to_bytes(4, byteorder='big')
    return message


def build_port(self, payload):
    message = (3).to_bytes(4, byteorder='big')  # len
    message += (9).to_bytes(1, byteorder='big')  # id
    message += payload.to_bytes(2, byteorder='big')  # listen port
    return message

