from alive_progress import alive_bar
import time

flag = True
with alive_bar(1000, force_tty=True) as bar:
    while flag:
        pass