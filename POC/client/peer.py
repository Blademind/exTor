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
        self.sock.settimeout(2)
        self._BUF = 16384
        with open('file_info.txt', 'r') as f:
            text = f.read()
            self.pieces = text[text.find('PIECES_HASH: ') + 13: len(text) - len(text[text.find('PIECES_HASH: ') + 13:])+text[text.find('PIECES_HASH: ') + 13:].find('\n')].split('#')
            self.needed = [True for piece in self.pieces]
            # self.size = int(text[text.find('FILE_SIZE: ') + 11: len(text[:text.find('FILE_SIZE: ') + 11]) + text[text.find('FILE_SIZE: ') + 11:].find('\n')])
        self.validate_piece = ""
        self.queue = []
        self.desired_piece = 0
        self.total_bytes = 0
        self.requested = {}
        self.sock.bind(('192.168.1.196', 50001))
        self.current_server = 0
        self.SERVERS = [('192.168.1.196', 50000), ('192.168.1.196', 50003), ('192.168.1.196', 50002)]
        self.sock.connect(self.SERVERS[0])
        self.listen()

    def listen(self):
        while 1:
            try:
                data = self.sock.recv(self._BUF)
            except:
                print('ERROR')
                if self.current_server < len(self.SERVERS) - 1:
                    print('Trying another tracker...')
                    self.close_open_new()
                    self.sock.connect(self.SERVERS[self.current_server])
                else:
                    print('No more trackers available, file cannot be downloaded.')
                data = b''
            try:
                datacontent = data.decode()
            except:
                datacontent = pickle.loads(data)
            if 'STATE' in datacontent:
                peers = datacontent[1]
                print(peers)
                for peer in peers:
                    for index, piece in enumerate(self.needed):
                        if piece and index not in self.queue:
                            if peer[2][index] == '1' and index not in self.requested:
                                self.desired_piece = index
                                self.queue.append(self.desired_piece)
                if len(self.queue) != 0:
                    self.desired_piece = self.queue[0]
                    self.request(self.queue[0])

                #if len(self.pieces) == len(self.requested):
                #    self.requested = dict(sorted(self.requested.items()))
                #    with open('end_file', 'w') as file:
                #        for element in self.requested:
                #            file.write(element)
                #if self.desired_piece in self.requested:
                #    self.desired_piece += 1
                #self.close_open_new()                                  # !!!!!!!!!!!! IMPORTANT !!!!!!!!!!!!
                #self.sock.connect(self.SERVERS[self.current_server])
                #if self.current_server < len(self.SERVERS) - 1:
                #    self.current_server += 1
                #else:
                #    print('DONE, all servers scrolled')
                #    break
            else:
                if datacontent[:3] == '#0#':  # block
                    print('PIECE', len(datacontent))
                    block_size = int(datacontent[3: datacontent.rfind('#')])
                    self.validate_piece += datacontent[datacontent.rfind('#') + 1: block_size]
                    self.total_bytes += block_size
                    if hashlib.sha1(self.validate_piece.encode()).hexdigest() == self.pieces[self.desired_piece]:
                        self.total_bytes = 0
                        self.requested[self.desired_piece] = self.validate_piece
                        self.needed[self.desired_piece] = False
                        print(f'Piece #{self.desired_piece} done')
                        self.validate_piece = ""
                        if len(self.queue) != 0:
                            self.desired_piece = self.queue[0]
                            self.request(self.queue[0])
                        elif self.current_server != len(self.SERVERS) - 1:
                            if len(self.pieces) != len(self.requested):
                                self.close_open_new()

                                self.sock.connect(self.SERVERS[self.current_server])
                            else:
                                print('DONE, not all servers scrolled')
                                if len(self.pieces) == len(self.requested):
                                    print('FILE SUCCESS')
                                    self.requested = dict(sorted(self.requested.items()))
                                    with open('end_file', 'w') as file:
                                        for key, value in self.requested.items():
                                            file.write(value)
                                break
                        else:
                            self.sock.send('QUIT'.encode())
                            print('DONE, all servers scrolled')
                            if len(self.pieces) == len(self.requested):
                                print('FILE SUCCESS')
                                self.requested = dict(sorted(self.requested.items()))
                                with open('end_file', 'w') as file:
                                    for key, value in self.requested.items():
                                        file.write(value)
                            else:
                                print('Was not able to retrieve the file.')
                            break
                        # if self.current_server < len(self.SERVERS) - 1:
                        # with open('file', 'a') as f:
                        #     f.write(datacontent[datacontent.rfind('#') + 1:])
                    else: self.sock.send('FLOW'.encode())

    def request(self, piece):
        self.queue.pop(0)
        self.sock.send(f'REQUEST {piece}'.encode())

    def close_open_new(self):
        self.current_server += 1
        self.sock.send('QUIT'.encode())
        try:
            self.sock.close()
        except: pass
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(2)
        self.sock.bind(('192.168.1.196', 50001))


if __name__ == '__main__':
    Peer()


