import _thread
from socket import *
from select import *
import sqlite3
import pickle


class Tracker:
    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        readsock = [self.sock]
        self.conn = sqlite3.connect('state.db')
        self.conn.cursor().execute('CREATE TABLE IF NOT EXISTS Peers(IP TEXT, PORT number(4),'
                                   ' Pieces TEXT);')
        self.conn.close()

        self._BUF = 16384
        self.sock.bind(('192.168.1.196', 50002))
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
                        if not data:
                            print(sock.getsockname(), 'DISCONNECTED')
                            readsock.remove(sock)
                            break
                        print(data.decode())
                        if data.decode == 'REQUEST':
                            


                    except:
                        print(sock.getsockname(), 'DISCONNECTED')
                        readsock.remove(sock)
                        break

    def connected_handler(self, conn, addr):
        print(addr, 'CONNECTED')
        conn.send('STATE'.encode())
        self.conn = sqlite3.connect('state.db')
        cursor = self.conn.cursor().execute('SELECT * FROM Peers')
        conn.send(pickle.dumps(cursor.fetchall()))
        self.conn.close()


if __name__ == '__main__':
    Tracker()
