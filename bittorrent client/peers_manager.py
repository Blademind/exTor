class Downloader:
    def __init__(self, torrent):
        self.written = b""
        self.s_bytes = b""
        self.torrent = torrent
        try:
            self.files = self.torrent.torrent['info']['files']
        except:
            self.files = self.torrent.torrent['info']
        self.torrent_name = self.torrent.torrent['info']['name']
        self.pieces = self.torrent.torrent['info']['pieces']
        self.num_of_pieces = len(self.pieces) // 20  # number of pieces in torrent
        self.pointer = 0
        self.pieces_bytes = self.reset_pieces()

    def reset_pieces(self):
        ret = []
        for i in range(self.num_of_pieces):
            ret.append(b"")
        return ret

    def add_bytes(self, piece, piece_bytes):
        self.pieces_bytes[piece] = piece_bytes

    def s_bytes_handler(self):
        for i, b in enumerate(self.pieces_bytes[self.pointer:]):
            if not b:
                break
            self.pointer += 1
            self.s_bytes += b

    def download_files(self):
        """
        Requests next piece in line

        :return:
        """
        temp = 0
        to_download = []
        self.s_bytes_handler()
        for file in list(self.files):
            temp += file['length']
            if temp <= len(self.s_bytes):
                to_download.append((file['path'], file['length']))
                self.files = self.files[1:]
        for path in to_download:
            with open(f"torrents\\files\\{self.torrent_name}\\{path[0][0]}", 'wb') as w:
                w.write(self.s_bytes[:path[1]])
                self.written += self.s_bytes[:path[1]]
                self.s_bytes = self.s_bytes[path[1]:]
            print("done writing", path)


currently_connected = []
down = None
