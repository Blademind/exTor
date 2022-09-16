import _thread
from socket import *
from select import *
import sqlite3
import pickle
import os


class Tracker:
    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.pieces = os.listdir('pieces/')
        self.have = {int(piece[1:], 16) - 170: piece for piece in self.pieces}
        readsock = [self.sock]
        self.conn = sqlite3.connect('state.db')
        self.conn.cursor().execute('CREATE TABLE IF NOT EXISTS Peers(IP TEXT, PORT number(4),'
                                   ' Pieces TEXT);')
        self.conn.close()

        self._BUF = 16384
        self.sock.bind(('192.168.1.196', 50000))
        self.sock.listen(5)
        self.listen(readsock)

    def listen(self, readsock):
        while 1:
            read, write, ex = select(readsock, [], [])
            for sock in read:
                if sock == self.sock:
                    conn, addr = self.sock.accept()
                    readsock.append(conn)
                    _thread.start_new_thread(self.connected_handler, (conn, addr))
                else:
                    try:
                        data = sock.recv(self._BUF)
                        datacontent = data.decode()
                        print(datacontent)
                        if 'REQUEST' in datacontent:
                            if int(datacontent[7:]) in self.have:
                                print(f'HAVE {datacontent[7:]}')
                                _thread.start_new_thread(self.send_piece, (sock, int(datacontent[7:])))
                        elif datacontent == 'QUIT':
                            print(sock.getsockname(), 'DISCONNECTED')
                            readsock.remove(sock)
                            break
                    except Exception as e:
                        print(e)
                        print(sock.getsockname(), 'DISCONNECTED')
                        readsock.remove(sock)
                        break

    def send_piece(self, sock, piece):
        s = 0
        size = os.path.getsize(f'pieces/{self.have[piece]}')
        block = 0
        check_size = size - s if size - s < self._BUF else self._BUF
        with open(f'pieces/{self.have[piece]}', 'r') as f:
            while s < size:
                text = f.read(self._BUF - 4 - len(str(check_size)))
                check_size = len(text) + 4 + len(str(check_size)) if len(text) + 4 + len(str(check_size)) < self._BUF else self._BUF
                sock.send(f'#0#{check_size}#{text}'.encode())
                s += check_size

    def connected_handler(self, conn, addr):
        print(addr, 'CONNECTED')
        conn.send('STATE'.encode())
        self.conn = sqlite3.connect('state.db')
        cursor = self.conn.cursor().execute('SELECT * FROM Peers')
        conn.send(pickle.dumps(cursor.fetchall()))
        self.conn.close()


if __name__ == '__main__':
    Tracker()
