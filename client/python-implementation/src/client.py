import socket
import threading
from src import logger

info_log_name = "info.log"
exception_log_name = "exception.log"

logger.setup_logger("exception", exception_log_name, logger.ERROR)
logger.setup_logger("info", info_log_name, logger.INFO)

exception_logger = logger.getLogger('exception')
info_logger = logger.getLogger('info')

def main():
    try:
        _main()
    except Exception as ex:
        exception_logger.exception(ex)

def _main():
    rendezvous = ('34.125.197.205', 55555)

    #Connect to rendezvous server

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 50001))
    sock.sendto(b'0', rendezvous)

    while True:
        data = sock.recv(1024).decode()

        if data.strip() == 'ready':
            info_logger.info('Connected to server.')
            break

    data = sock.recv(1024).decode()
    ip, sport, dport = data.split(' ')
    sport = int(sport)
    dport = int(dport)

    info_logger.info('Punching hole to peer')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', sport))
    sock.sendto(b'0', (ip, dport))
    sock.close()


    #Listen for messages
    def listen():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', sport))

        while True:
            data = sock.recv(1024)
            print('\rpeer: {}\n> '.format(data.decode()), end='')

    listener = threading.Thread(target=listen, daemon=True);
    listener.start()

    #Send messages
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', dport))

    while True:
        msg = input('> ')
        sock.sendto(msg.encode(), (ip, sport))

main()