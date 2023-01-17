# from alive_progress import alive_bar
# import time
#
# flag = True
# with alive_bar(1000, force_tty=True) as bar:
#     while flag:
#         pass


# from socket import gethostbyname, gethostname
#
# print(gethostbyname(gethostname()))

#
# import torf
# magnet = torf.Magnet
# magnet = magnet.from_string("magnet:?xt=urn:btih:7EB262107594A8AAA982F96A4EB3D6A59F480057&dn=Harry.Potter.20th.Anniversary.Return.to.Hogwarts.2022.1080p.WEBRip.x264&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce&tr=udp%3A%2F%2F9.rarbg.me%3A2720%2Fannounce&tr=udp%3A%2F%2F9.rarbg.to%3A2760%2Fannounce&tr=udp%3A%2F%2Ftracker.thinelephant.org%3A12770%2Fannounce&tr=udp%3A%2F%2Ftracker.fatkhoala.org%3A13770%2Fannounce&tr=udp%3A%2F%2Ftracker.zer0day.to%3A1337%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Fcoppersurfer.tk%3A6969%2Fannounce")
# #
import bencode
import requests

def get_metadata(magnet_link):
    torrent_hash = "7EB262107594A8AAA982F96A4EB3D6A59F480057"
    params = {'xt': 'urn:btih:' + torrent_hash}
    data = requests.get(magnet.tr[3], params=params).content
    metadata = bencode.bdecode(data)
    return metadata

magnet_link = "magnet:?xt=urn:btih:7EB262107594A8AAA982F96A4EB3D6A59F480057"
metadata = get_metadata(magnet_link)
print(metadata)
