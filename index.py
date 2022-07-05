from socket import *
import bencode
from urllib.parse import urlparse
from socket import *
from tracker import Tracker
from torrent import Torrent
print('list of peers:', Torrent().torrent['announce-list'])