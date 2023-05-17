import os
import socket
import threading
import time
from socket import *
from tracker import Tracker
from peers import Peer
import message_handler as message
import bitstring
import peers_manager as manager
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from multiprocessing import *
import datetime
import ui
import select
import ssl
import pickle
import tracker_init_contact
from torf import Torrent


def create_new_sock():
    """
    Creates a TCP socket
    :return: created TCP socket with its settings
    """
    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.settimeout(2)
    return sock


def errormng(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result

        except Exception as e:
            print(e)
    return wrapper


class Handler:

    def __init__(self, given_name=None, path=None, port=None, ui_given_name=None, ui=False, interrupt_event=None):
        """
        Create Handler object
        """
        if interrupt_event:
            threading.Thread(target=self.interrupt_handler, args=(interrupt_event, )).start()

        self.ui_sock = None if not ui else socket(AF_INET, SOCK_STREAM)
        self.pieces = None
        self.peer_thread = []
        self.tracker = None
        self.global_switched = False
        self.entry_created = False
        self.responded_peers = []
        self.ui_file_name = None
        self.ui_given_name = ui_given_name

        if not os.path.exists("torrents"):
            os.makedirs("torrents\\info_hashes")
            os.makedirs("torrents\\files")

        if not os.path.exists("torrents\\info_hashes"):
            os.makedirs("torrents\\info_hashes")

        if not os.path.exists("torrents\\files"):
            os.makedirs("torrents\\files")
        try:
            if not given_name:
                if ui:
                    self.tracker = Tracker(ui_given_name=ui_given_name, ui_sock=self.ui_sock)
                else:
                    self.tracker = Tracker(ui_given_name=ui_given_name)

            elif given_name:
                if ui:
                    self.tracker = Tracker(given_name=given_name, path=path, port=port, ui_sock=self.ui_sock)
                else:
                    self.tracker = Tracker(given_name=given_name, path=path, port=port)

            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.bind((get_ip_addr(), 0))
            self.sock = ssl.wrap_socket(self.sock, server_side=False, keyfile='private-key.pem', certfile='cert.pem')
            self.sock.connect((self.tracker.local_tracker[0], 55556))

            if given_name or self.tracker.local_tracker:  # local tracker must be found for a download to start (or a
                # name of a file which already is present on disk was given)
                if ui:
                    self.ui_sock.connect(("127.0.0.1", 9999))
                    self.ui_file_name = self.tracker.file_name
                    msg = f"CREATE_ENTRY NAME, {self.tracker.file_name}".encode()
                    self.ui_sock.send(len(msg).to_bytes(4, byteorder="big") + msg)
                    self.entry_created = True
                    threading.Thread(target=self.update_widget_peers).start()
                self.torrent = self.tracker.torrent
                manager.down = manager.Downloader(self.torrent, self.tracker, ui)

                # There are pieces which can be downloaded
                if manager.down.num_of_pieces - manager.down.count_bar != 0:
                    self.tracker.contact_trackers()
                    for thread in self.tracker.threads:
                        thread.join()

                    self.peers = list(set(self.tracker.peers))  # list of peers fetched from trackers
                    print(self.peers)
                    manager.down.listen_seq()  # listen to peers (for pieces sharing)
                    manager.down.generate_download_bar()  # PROGRESS
                    self.download()

                # All pieces present on disk
                else:
                    for name, file in manager.down.files_data.items():
                        file.close()

                    manager.down.progress_flag = False
                    manager.DONE = True
                    manager.down.listen_seq()  # listen to peers (for pieces sharing)
                    self.tracker.done_downloading(manager.sharing_peers)
                    if ui:
                        msg = b"UPDATE_STATUS Seeding..."
                        self.ui_sock.send(len(msg).to_bytes(4, byteorder='big') + msg)
                        if self.tracker.file_name[-12:-8] != "_LOC":
                            self.tracker.file_name = self.tracker.file_name[:-8] + '_LOC.torrent'
                            msg = f"NAME {self.tracker.file_name}".encode()
                            self.ui_sock.send(len(msg).to_bytes(4, byteorder='big') + msg)

        except TypeError:
            # a name of file was not given before program was closed by the user
            pass
        except Exception as e:
            print("Exception (at main):", e)

            try:
                manager.down.progress_flag = False
                self.responded_peers = []
            except: pass

            if self.tracker and self.tracker.global_flag:
                try:
                    self.global_switched = True

                    self.tracker.contact_trackers()
                    self.peers = list(set(self.tracker.peers))
                    self.torrent = self.tracker.torrent
                    manager.reset_to_default()
                    manager.down.generate_download_bar()  # PROGRESS

                    if ui:
                        msg = f"NAME {self.tracker.global_file}".encode()
                        self.ui_sock.send(len(msg).to_bytes(4, byteorder='big') + msg)
                        self.ui_file_name = self.tracker.global_file
                        threading.Thread(target=self.update_widget_peers).start()

                    self.download()
                except:
                    try:
                        manager.down.progress_flag = False

                        manager.DONE = True
                        if manager.down.files_data:
                            for name, file in manager.down.files_data.items():
                                file.close()
                        print(e)
                        try:
                            if self.ui_sock and self.entry_created:
                                msg2 = f"NOTIFICATION {self.ui_file_name}, Removed: {e}".encode()
                                self.ui_sock.send(len(msg2).to_bytes(4, byteorder="big") + msg2)

                                msg = b"REMOVE_ENTRY"
                                self.ui_sock.send(len(msg).to_bytes(4, byteorder="big") + msg)
                            self.remove()
                        except:
                            pass

                    except:
                        pass
            else:
                if manager.down and manager.down.files_data:
                    for name, file in manager.down.files_data.items():
                        file.close()
                print(e)
                try:
                    if self.ui_sock:
                        if self.entry_created:
                            msg = f"NOTIFICATION {self.ui_file_name}, Removed: {e}".encode()
                            self.ui_sock.send(len(msg).to_bytes(4, byteorder="big") + msg)
                            msg = b"REMOVE_ENTRY"
                            self.ui_sock.send(len(msg).to_bytes(4, byteorder="big") + msg)
                        else:
                            self.ui_sock.connect(("127.0.0.1", 9999))
                            msg = f"NOTIFICATION {self.ui_given_name}, Not added: {e}".encode()
                            self.ui_sock.send(len(msg).to_bytes(4, byteorder="big") + msg)
                except: pass

    def update_widget_peers(self):
        while 1:
            if self.ui_sock and not manager.DONE:
                msg = f"PEERS {len(manager.currently_connected)} {len(self.responded_peers)}".encode()
                self.ui_sock.send(len(msg).to_bytes(4, byteorder="big") + msg)
            else:
                break
            time.sleep(1)

        if self.ui_sock:
            msg = f"PEERS".encode()
            self.ui_sock.send(len(msg).to_bytes(4, byteorder="big") + msg)

    def download(self):
        self.peer_thread = {}
        self.pieces = {}
        for i in range(len(self.torrent.torrent["info"]["pieces"]) // 20):
            self.pieces[i] = []
        self.rarest_piece(self.peers, self.tracker)
        self.go_over_pieces()

        while len(manager.currently_connected) != 0:
            self.check_errors()

        self.check_errors()
        print(manager.down.count_bar, manager.down.num_of_pieces)
        if manager.down.count_bar != manager.down.num_of_pieces:
            raise Exception("not all pieces downloaded")

        for name, file in manager.down.files_data.items():
            file.close()

        manager.DONE = True
        print("Completed Download!")
        if self.ui_sock:
            msg = b"UPDATE_STATUS Seeding..."
            self.ui_sock.send(len(msg).to_bytes(4, byteorder='big') + msg)

        manager.down.progress_flag = False
        self.tracker.done_downloading(manager.sharing_peers)
        if self.global_switched:
            if self.ui_sock:
                msg = f"NAME {self.tracker.file_name[:-8] + '_LOC.torrent'}".encode()
                self.ui_sock.send(len(msg).to_bytes(4, byteorder='big') + msg)

    def go_over_pieces(self):
        """
        Goes over all the piece
        :return:
        """
        if self.ui_sock:
            msg = b"UPDATE_STATUS Downloading and Seeding..."
            self.ui_sock.send(len(msg).to_bytes(4, byteorder='big') + msg)

        for piece, k in enumerate(sorted(self.pieces, key=lambda p: len(self.pieces[p]))):
            if manager.down.have[k] == "0":
                peer = Peer(self.tracker)  # create a peer object
                current_piece_peers = self.pieces[k]
                # no peers holding current piece
                if len(current_piece_peers) == 0:
                    raise Exception("no peers holding piece")
                # go over all piece holders
                try:
                    self.peer_piece_assignment(peer, k, current_piece_peers)
                except:
                    time.sleep(0.5)
                    raise Exception("operation stopped by user")

    def remove_peer_instances(self, peer_ip_port):
        del self.peer_thread[peer_ip_port]
        for piece_number, peers_list in self.pieces.items():
            if peer_ip_port in peers_list:
                self.pieces[piece_number].remove(peer_ip_port)

    def check_errors(self):

        if manager.down.error_queue:
            while manager.down.error_queue:
                peer_piece = manager.down.error_queue.pop(0)
                peer_ip_port, piece = peer_piece[0], peer_piece[1]
                print("error handling:", piece)
                if self.ui_sock:
                    msg = f"NOTIFICATION {self.tracker.file_name}, Error: Peer {peer_ip_port[0]}: {peer_ip_port[1]} - piece {piece}".encode()
                    self.ui_sock.send(len(msg).to_bytes(4, byteorder='big') + msg)

                peer_error_object = Peer(self.tracker)  # create a peer object

                self.remove_peer_instances(peer_ip_port)

                piece_peers = self.pieces[piece]  # all peers sharing that piece
                self.peer_piece_assignment(peer_error_object, piece, piece_peers)

    def peer_piece_assignment(self, peer, k, current_piece_peers):
        """
        goes over peers in order to get a piece downloaded
        :param peer:
        :param k:
        :param current_piece_peers: the peers assigned to this piece
        :return:
        """

        # go over errors if there are any
        self.check_errors()
        for p in current_piece_peers:
            if p not in manager.currently_connected:
                if p in self.peer_thread.keys():
                    threading.Thread(target=self.peer_thread[p].request_piece, args=(k,)).start()
                else:
                    manager.currently_connected.append(p)
                    self.peer_thread[p] = peer
                    threading.Thread(target=peer.download, args=(p, k)).start()

                self.check_errors()
                break

            # last peer and was not caught beforehand - all conns in use
            if p == current_piece_peers[-1]:
                last_piece_length = len(manager.currently_connected)
                while len(manager.currently_connected) == last_piece_length:
                    time.sleep(0)

                self.peer_piece_assignment(peer, k, current_piece_peers)
                break

    def connect_to_peer(self, peers, sock, current_peer, tracker):
        try:
            sock.connect(peers[current_peer])
            sock.send(message.build_handshake(tracker))
            data = sock.recv(68)  # read handshake
            if message.is_handshake(data):
                print("HANDSHAKE")
                msg_len = int.from_bytes(sock.recv(4), "big")
                data = sock.recv(msg_len)
                if message.msg_type(data) == 'bitfield':
                    data = bitstring.BitArray(data[1:])
                    print("BITFIELD", data.bin, peers[current_peer])

                    rarest_piece_lock.lock()
                    self.responded_peers.append(sock.getpeername())
                    for t, i in enumerate(data.bin):
                        if i == "1":
                            self.pieces[t].append(sock.getpeername())
                    rarest_piece_lock.unlock()
            sock.close()

        except:
            return

    def rarest_piece(self, peers, tracker):
        """
        finds all pieces and their rarity.
        :param peers:
        :param tracker:
        :return:
        """
        if self.ui_sock:
            msg = b"UPDATE_STATUS Mapping pieces held by peers..."
            self.ui_sock.send(len(msg).to_bytes(4, byteorder='big') + msg)
        socks = [create_new_sock() for _ in range(len(peers))]
        if len(socks) != 0:  # at least one peer is in swarms
            a = []
            current_peer = 0
            for sock in socks:
                th = threading.Thread(target=self.connect_to_peer, args=(peers, sock, current_peer, tracker))
                a.append(th)
                th.start()
                current_peer += 1

            for thread in a:
                thread.join()

        time.sleep(4)  # some peers are slow, gives them some time to delete client's instance from them

    def remove(self):
        if self.tracker.file_name[-15: -8] == "_UPLOAD" or self.tracker.file_name[-12: -8] == "_LOC":
            print("FILENAME", self.tracker.file_name)
            self.sock.send(f"REMOVE {self.tracker.file_name}".encode())
            os.remove(f"torrents\\info_hashes\\{self.tracker.file_name}")

    def interrupt_handler(self, interrupt_event):
        interrupt_event.wait()
        try:
            self.remove()
        except:
            pass
        os._exit(0)


class Upload:
    def __init__(self, path, interrupt_event):

        task = threading.Thread(target=self.interrupt_handler, args=(interrupt_event,))
        task.start()

        self.ui_sock = socket(AF_INET, SOCK_STREAM)
        self.ui_sock.connect(("127.0.0.1", 9999))
        self.path = path
        self.local_tracker = tracker_init_contact.find_local_tracker()
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.bind((get_ip_addr(), 0))

        self.sock = ssl.wrap_socket(self.sock, server_side=False, keyfile='private-key.pem', certfile='cert.pem')
        try:
            if self.local_tracker:
                self.torrent = self.create_metadata_file(self.path)
                if self.torrent is None or folders_in(self.path):
                    msg = f"NOTIFICATION {self.path[self.path.rfind('/') + 1:]}, Error: torrent could not be created on this path".encode()
                    self.ui_sock.send(len(msg).to_bytes(4, byteorder='big') + msg)
                    self.ui_sock.close()
                else:
                    try:
                        self.sock.connect((self.local_tracker[0], 55556))  # tracker downloader ip (tcp)
                        self.sock.send(self.torrent.encode())  # sends torrent name (to start upload)
                        self.__BUF = 1024
                        self.listen()
                    except:
                        print("Error connecting to Tracker")
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(e)

    def interrupt_handler(self, interrupt_event):
        interrupt_event.wait()
        try:
            self.sock.send(f"REMOVE {self.torrent}".encode())
            if self.torrent:
                print(self.torrent)
                os.remove(f"torrents\\info_hashes\\{self.torrent}")
        except:
            pass
        os._exit(0)

    def create_metadata_file(self, path):
        try:
            t = Torrent(
                path=path,
                trackers=[],
                comment='This file was created using the upload file algorithm by Alon Levy')
            t.generate()
            torrent_name = f"{os.path.split(os.path.basename(path))[1]}_UPLOAD.torrent"
            print(torrent_name)

            t.write(f"torrents\\info_hashes\\{torrent_name}")

            return torrent_name

        except Exception as e:
            print(e)
            return

    def listen(self):
        while 1:
            data = self.sock.recv(self.__BUF)
            if not data:
                break
            try:
                datacontent = data.decode()
            except:
                break
            if datacontent == "FLOW":
                length = os.path.getsize(f"torrents\\info_hashes\\{self.torrent}")
                s = 0
                self.sock.send(pickle.dumps(length))
                with open(f"torrents\\info_hashes\\{self.torrent}", "rb") as f:
                    while f:
                        if datacontent == "FLOW":
                            file_data = f.read(self.__BUF)
                            s += len(file_data)
                            self.sock.send(file_data)
                        elif datacontent == "DONE":
                            break

                        datacontent = self.sock.recv(self.__BUF).decode()

            elif datacontent == "FILE_EXISTS":
                print("file already exists on tracker")
                break

            if datacontent == "DONE":
                print(self.torrent, "successfully uploaded to tracker")

                threading.Thread(target=Handler, args=(self.torrent, self.path, self.sock.getsockname()[1], None, True)).start()

                msg = f"NOTIFICATION {self.torrent}, SUCCESS: uploaded and sharing torrent".encode()
                self.ui_sock.send(len(msg).to_bytes(4, byteorder='big') + msg)
                break


class WorkerThread(QThread):
    data_progress = pyqtSignal(bytes, int)

    def __init__(self, parent=None):
        super(WorkerThread, self).__init__(parent)
        self.tcp_sock = socket(AF_INET, SOCK_STREAM)
        self.tcp_sock.bind(("0.0.0.0", 9999))
        self.tcp_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.tcp_sock.listen(5)
        self.read_tcp, self.write_tcp = [self.tcp_sock], []  # read write for select udp

    def run(self):
        BUFS = {}
        entries = []
        while 1:
            readable, writeable, _ = select.select(self.read_tcp, self.write_tcp, [])
            for sock in readable:
                if sock == self.tcp_sock:
                    lock.lock()
                    conn, addr = self.tcp_sock.accept()
                    self.read_tcp.append(conn)
                    BUFS[conn] = 4
                    lock.unlock()
                else:
                    data = sock.recv(BUFS[sock])
                    if BUFS[sock] == 4:
                        BUFS[sock] = int.from_bytes(data, 'big')

                    else:
                        lock.lock()
                        if data[:12] == b"CREATE_ENTRY":
                            entries.insert(0, sock)
                        if sock in entries:
                            self.data_progress.emit(data, entries.index(sock))
                        else:
                            self.data_progress.emit(data, None)

                        if data == b"REMOVE_ENTRY":
                            entries.remove(sock)
                        else:
                            BUFS[sock] = 4


class MainWindow(QMainWindow):
    def __init__(self, tracker):
        QMainWindow.__init__(self)

        self.ui_main = ui.Ui_MainWindow()
        self.ui_main.setupUi(self)
        self.local_tracker = tracker
        self.file_name = ""
        self.ui_main.pushButton_BtnServico.clicked.connect(lambda x:self.click_button('Upload'))
        self.ui_main.home_button.clicked.connect(lambda x:self.click_button('Home'))
        self.ui_main.action.triggered.connect(self.torrent_triggered)
        self.processes = []

        self.spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.ui_main.folder_button.clicked.connect(self.launch_folder_dialog)

        self.ui_main.textEdit_TxtTopSearch.returnPressed.connect(
            self.torrent_triggered)

        self.interrupt_event = Event()
        self.set_dash_value()
        self.show()
        self.worker_thread = WorkerThread()
        self.worker_thread.data_progress.connect(self.update)
        self.worker_thread.start()

    def launch_folder_dialog(self):
        self.folder_name = QFileDialog.getExistingDirectory(self.ui_main.frame_2, 'Select Folder')
        if self.folder_name:
            p = Process(target=Upload, args=(self.folder_name, self.interrupt_event))
            p.start()
            self.processes.append(p)

    def click_button(self,value):
        if value == "Home":
            self.ui_main.label_TitleDash.setText("Download")
            self.ui_main.label_SubTitleDash.hide()
            self.ui_main.folder_button.hide()
            self.ui_main.download_list.show()
            self.ui_main.verticalLayout_9.removeItem(self.spacerItem)

        elif value == "Upload":
            self.ui_main.label_TitleDash.setText("Upload")
            self.ui_main.label_SubTitleDash.show()
            self.ui_main.folder_button.show()
            self.ui_main.download_list.hide()
            self.ui_main.verticalLayout_9.addItem(self.spacerItem)

    def update(self, data, item_place):
        try: datacontent = data.decode()
        except: datacontent = ""
        try:
            if datacontent[:12] == "CREATE_ENTRY":
                name = datacontent[13:].split(", ")[1]

                widget = TorrentListWidgetItem()

                item = QListWidgetItem()

                item.setSizeHint(widget.sizeHint())

                self.ui_main.download_list.insertItem(0, item)
                self.ui_main.download_list.setItemWidget(item, widget)

                item = self.ui_main.download_list.item(item_place)
                widget = self.ui_main.download_list.itemWidget(item)
                _name_label = widget._name_label
                _name_label.setText(name)

            elif datacontent[:12] == "REMOVE_ENTRY":
                self.ui_main.download_list.takeItem(item_place)
            elif datacontent[:12] == "NOTIFICATION":
                title_message = datacontent[13:].split(", ")
                self.ui_main.notification.setNotify(title_message[0], title_message[1])

            elif datacontent[:5] == "PEERS":
                if len(datacontent) == 5:
                    item = self.ui_main.download_list.item(item_place)
                    widget = self.ui_main.download_list.itemWidget(item)
                    if widget:
                        _lower_status_label = widget._lower_status_label
                        _lower_status_label.setText(None)
                else:
                    values = datacontent[6:].split(" ")
                    item = self.ui_main.download_list.item(item_place)
                    widget = self.ui_main.download_list.itemWidget(item)
                    if widget:
                        _lower_status_label = widget._lower_status_label
                        _lower_status_label.setText(f"Downloading from {values[0]} Peers out of {values[1]} responded Peers")

            elif datacontent[:8] == "PROGRESS":

                item = self.ui_main.download_list.item(item_place)
                widget = self.ui_main.download_list.itemWidget(item)
                if widget:
                    _progress_bar = widget._progress_bar

                    percentage = int(datacontent[9:])
                    _progress_bar.setValue(percentage)

            elif datacontent[:4] == "NAME":
                item = self.ui_main.download_list.item(item_place)
                widget = self.ui_main.download_list.itemWidget(item)
                if widget:
                    _name_label = widget._name_label
                    _name_label.setText(datacontent[5:])

            elif datacontent[:13] == "UPDATE_STATUS":
                item = self.ui_main.download_list.item(item_place)
                widget = self.ui_main.download_list.itemWidget(item)
                if widget:
                    _upper_status_label = widget._upper_status_label
                    _upper_status_label.setText(datacontent[14:])
        except: pass
        lock.unlock()

    def torrent_triggered(self):
        query = self.ui_main.textEdit_TxtTopSearch.text()
        if query:
            print(query)
            self.ui_main.textEdit_TxtTopSearch.setText(None)
            p = Process(target=Handler, args=(None, None, None, query, True, self.interrupt_event))
            p.start()
            self.processes.append(p)

    def set_dash_value(self):
        self.ui_main.label_TxtTopDataUserType.setText("User")
        self.ui_main.date_widget.setText(self.date_now())

    def date_now(self):
        now = datetime.datetime.now()
        return str(now.strftime("%A %d/%m/%Y")).capitalize()

# region ASYNC SOLUTION
#     async def conn_task(self, peers, current_peer, tracker):
#         try:
#             conn = asyncio.open_connection(peers[current_peer][0], peers[current_peer][1])
#             reader, writer = await asyncio.wait_for(conn, timeout=1)
#             writer.write(message.build_handshake(tracker))
#             await writer.drain()
#             data = await asyncio.wait_for(reader.read(68), timeout=1) # read handshake
#
#             if message.is_handshake(data):
#                 msg_len = int.from_bytes(await reader.read(4), "big")
#                 data = await reader.read(msg_len)
#                 if message.msg_type(data) == 'bitfield':
#                     data = bitstring.BitArray(data[1:])
#                     # print(bitstring_to_bytes(data.bin))
#                     # print(data.bin)
#                     for t, i in enumerate(data.bin):
#                         if i == "1":
#                             self.pieces[t].append(peers[current_peer])
#             conn.close()
#             return
#         except (ConnectionResetError, TimeoutError, ConnectionRefusedError):
#             return
#
#     async def connect_to_peer(self, peers, current_peer, tracker):
#         # print(peers[current_peer])
#         # print(f"connected to {current_peer}")
#
#         await self.conn_task(peers, current_peer, tracker)
#
#     async def peer_instances(self, peers, tracker):
#         peer_connections = [self.connect_to_peer(peers, current_peer, tracker) for current_peer in range(len(peers))]
#         await asyncio.gather(*peer_connections)

    # def rarest_piece(self, peers, tracker):
        #     """
        #     finds all pieces and their rarity.
        #     :param peers:
        #     :param tracker:
        #     :return:
        #     """
        #     socks = []
        #     for i in range(len(peers)):
        #         socks.append(create_new_sock())
        #     current_peer = 0
        #     a = []
        # asyncio.run(self.peer_instances(socks, peers, tracker))
# endregion


class TorrentListWidgetItem(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("QWidget{\n"
                                           "\n"
                                           "color:#E7E7E7;\n"
                                           "border:0px;\n"
                                           "font-size:15px;\n"
                                           "font-weight: bold;\n"
                                           "}")

        vbox = QVBoxLayout(self)

        self._name_label = QLabel()
        vbox.addWidget(self._name_label)

        self._upper_status_label = QLabel()
        vbox.addWidget(self._upper_status_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setMaximum(1000)
        vbox.addWidget(self._progress_bar)

        self._progress_bar.setValue(0)
        self._lower_status_label = QLabel()
        vbox.addWidget(self._lower_status_label)

    def update_percents(self, number):
        self._progress_bar.setValue(number)

@errormng
def init_udp_sock():
    """
    Creates a udp sock listening on given port
    :param port: port of the socket
    :return: the end created socket
    """

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
    sock.settimeout(1)

    sock.bind((get_ip_addr(), 0))
    return sock


def get_ip_addr():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(('8.8.8.8', 53))
    ip = s.getsockname()[0]
    s.close()
    return ip
    return sock


def folders_in(path_to_parent):
    for fname in os.listdir(path_to_parent):
        if os.path.isdir(os.path.join(path_to_parent,fname)):
            return True
    return False

lock = QMutex()
rarest_piece_lock = QMutex()
updates = []

# region TRASH
# self._add_action = self.ui_main.toolbar.addAction('Add')
# self._add_action.triggered.connect(self.torrent_triggered)
#
#
# self._pause_action = self.ui_main.toolbar.addAction('Pause')
# self._pause_action.setEnabled(False)
# self._pause_action.triggered.connect(partial(self._control_action_triggered, control.pause))
#
# self._resume_action = self.ui_main.toolbar.addAction('Resume')
# self._resume_action.setEnabled(False)
# self._resume_action.triggered.connect(partial(self._control_action_triggered, control.resume))
#
# self._remove_action = self.ui_main.toolbar.addAction('Remove')
# self._remove_action.setEnabled(False)
# self._remove_action.triggered.connect(partial(self._control_action_triggered, control.remove))
# endregion

if __name__ == '__main__':
    Handler()
