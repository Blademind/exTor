import os
import hashlib
files = os.listdir("tray")
if len(files) == 0:
    print('No files found in tray')
else:
    print('Here are all the files in tray')
    for index, file in enumerate(files):
        print(index, file)
    sol = int(input('What file would you like to create?: '))
    if 0 <= sol < len(files):
        CHUNK_SIZE = int(input('What would you like the piece length to be?: '))
        file_number = 0
        with open(f'tray/{files[sol]}', 'rb') as f:
            file_name = files[sol][:files[sol].rfind(".")]
            if not os.path.exists(f'results/{file_name}_{CHUNK_SIZE}'):
                os.makedirs(f'results/{file_name}_{CHUNK_SIZE}')
                dir_name = f'results/{file_name}_{CHUNK_SIZE}'
                chunk = f.read(CHUNK_SIZE)
                pieces_hash = []
                while chunk:
                    pieces_hash.append(hashlib.sha1(chunk).hexdigest())
                    with open(f'{dir_name}/{file_name}_{str(file_number)}{files[sol][files[sol].rfind("."):]}', 'ab') as chunk_file:
                        chunk_file.write(chunk)
                    file_number += 1
                    chunk = f.read(CHUNK_SIZE)
                with open(f"infos/{file_name}_info.txt", 'w') as path:
                    path.write(f'FILENAME: {files[sol]}\n'
                               f"TRACKERS: ('192.168.1.196', 50000), ('192.168.1.196', 50002), ('192.168.1.196', 50003)\n"  # Change accordingly
                               f"PIECES_HASH: {'#'.join(pieces_hash)}\n")
                print('Done.')
            else:
                print('file has already been split')
