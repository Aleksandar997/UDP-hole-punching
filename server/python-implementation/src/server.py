import socket
import threading
from src import logger
from flask import Flask
import os
import codecs

info_log_name = "info.log"
exception_log_name = "exception.log"

logger.setup_logger("exception", exception_log_name, logger.ERROR)
logger.setup_logger("info", info_log_name, logger.INFO)

exception_logger = logger.getLogger('exception')
info_logger = logger.getLogger('info')

app = Flask(__name__)

@app.route('/test_connection', methods = ['GET'])
def test_connection():
    return 'it works'

@app.route('/info_log', methods = ['GET'])
def get_info_log():
    return __get_log_file(info_log_name)

@app.route('/exception_log', methods = ['GET'])
def get_exception_log():
    return __get_log_file(exception_log_name)

def initApi():
    app.run(host='0.0.0.0', port=5001, debug=False)

def initRendezvousServer():
    server_thread = threading.Thread(target=_initRendezvousServer)
    server_thread.daemon = True
    server_thread.start()

def _initRendezvousServer():
    while True:
        try:
            known_port = 50002

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('0.0.0.0', 55555))

            while True:
                clients = []

                while True:
                    data, address = sock.recvfrom(128)
                    info_logger.info('connection from: {}'.format(address))
                    clients.append(address)

                    sock.sendto(b'ready', address)

                    if len(clients) == 2:
                        info_logger.info('Got 2 clients. Sending details to each client.')
                        break

                c1 = clients.pop()
                c1_addr, c1_port = c1
                c2 = clients.pop()
                c2_addr, c2_port = c2

                sock.sendto('{} {} {}'.format(c1_addr, c1_port, known_port).encode(), c2)
                sock.sendto('{} {} {}'.format(c2_addr, c2_port, known_port).encode(), c1)
        except Exception as ex:
            exception_logger.exception(ex)


def __get_log_file(file_name: str):
    file_contents = ''
    if os.path.exists(file_name):
        with codecs.open(file_name, "r", encoding="utf-8") as f:
            file_contents = f.read()

    if (file_contents == None or file_contents.strip() == ''):
        file_contents = '{} file is empty'.format(file_name)
    file_contents = file_contents.replace('\n', '<br>')
    return file_contents

initRendezvousServer()
info_logger.info('App is running')
initApi()
