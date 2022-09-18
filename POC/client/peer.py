import _thread
import pickle
import select
import time
from socket import *
from select import *
import hashlib


class Peer:
    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.s_bytes = ""
        self._BUF = 16384
        with open('file_info.txt', 'r') as f:
            text = f.read()
            self.pieces = text[text.find('PIECES_HASH: ') + 13: len(text) - len(text[text.find('PIECES_HASH: ') + 13:])+text[text.find('PIECES_HASH: ') + 13:].find('\n')].split('#')
            # self.size = int(text[text.find('FILE_SIZE: ') + 11: len(text[:text.find('FILE_SIZE: ') + 11]) + text[text.find('FILE_SIZE: ') + 11:].find('\n')])
        self.validate_piece = ""
        self.total_bytes = 0
        self.requested = []
        self.sock.bind(('192.168.1.160', 50001))
        self.current_server = 0
        self.desired_piece = 0
        self.SERVERS = [('192.168.1.160', 50000), ('192.168.1.160', 50003), ('192.168.1.160', 50002)]
        self.sock.connect(self.SERVERS[0])
        self.listen()

    def listen(self):
        while 1:
            data = self.sock.recv(self._BUF)
            if not data:
                break
            if data.decode() == 'STATE':
                print(self.requested)
                data = self.sock.recv(self._BUF)
                peers = pickle.loads(data)
                print(peers)
                for peer in peers:
                    if peer[2][self.desired_piece] == '1' and self.desired_piece not in self.requested:
                        self.requested.append(self.desired_piece)
                        self.request(self.desired_piece)
                        break
                #if self.desired_piece in self.requested:
                #    self.desired_piece += 1
                #self.close_open_new()                                  # !!!!!!!!!!!! IMPORTANT !!!!!!!!!!!!
                #self.sock.connect(self.SERVERS[self.current_server])
                #if self.current_server < len(self.SERVERS) - 1:
                #    self.current_server += 1
                else:
                    print('DONE, all servers scrolled')
                    break
            else:
                datacontent = data.decode()
                if datacontent[:3] == '#0#':  # block
                    print('PIECE', len(datacontent))
                    block_size = int(datacontent[3: datacontent.rfind('#')])
                    self.validate_piece += datacontent[datacontent.rfind('#') + 1: block_size]
                    self.total_bytes += block_size
                    if hashlib.sha1(self.validate_piece.encode()).hexdigest() == self.pieces[self.desired_piece]:
                        self.total_bytes = 0
                        print(f'Piece #{self.desired_piece} done')
                        self.validate_piece = ""
                        self.s_bytes += self.validate_piece
                        self.close_open_new()
                        self.sock.connect(self.SERVERS[self.current_server])
                        self.desired_piece += 1
                        # if self.current_server < len(self.SERVERS) - 1:
                        # with open('file', 'a') as f:
                        #     f.write(datacontent[datacontent.rfind('#') + 1:])
                    else: self.sock.send('FLOW'.encode())

    def request(self, piece):
        self.sock.send(f'REQUEST {piece}'.encode())

    def close_open_new(self):
        self.current_server += 1
        self.sock.send('QUIT'.encode())
        self.sock.close()
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind(('192.168.1.160', 50001))


if __name__ == '__main__':
    Peer()


