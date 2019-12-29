#!/usr/bin/env python3


import argparse
import socket
import threading


clients = set()
debug = lambda *args, **kw: None
lock = threading.Lock()


def makeSocket(host, port):
    sock = socket.socket()
    sock.bind((host, port))
    sock.listen(1000)
    return sock


def serveRequests(sock):
    while True:
        try:
            acceptConnection(sock)
        except KeyboardInterrupt:
            sock.close()
            cleanupClients()
            break


def acceptConnection(sock):
    global clients
    connection, clientAddress = sock.accept()
    debug('DEBUG  - new connection: {}'.format(clientAddress))
    connection.settimeout(30)
    clientThread = threading.Thread(target=serveClient,
                                    args=(connection, clientAddress))
    with lock:
        clients.add(connection)
    clientThread.start()


def serveClient(connection, clientAddress):
    while True:
        try:
            recvData = connection.recv(1024)
        except socket.timeout:
            try:
                connection.sendall(b'1')
                continue
            except OSError:
                debug('DEBUG  - client gone: {}'.format(clientAddress))
                break
        except OSError:
            debug('DEBUG  - server gone: {}'.format(clientAddress))
            break
        decodedData = recvData.decode()[:-1]    # Ignore newline character
        if not decodedData:     # What a disgraceful little client socket...
            packetType = 'null'
            debug('DEBUG  - {} from {}'.format(packetType, clientAddress))
            break
        elif decodedData == 'message':
            packetType = 'message'
        elif decodedData[0] == '/':
            packetType = 'command'
        else:
            packetType = 'unrecognized'
        debug('DEBUG  - {} from {}'.format(packetType, clientAddress))
    connection.close()
    with lock:
        clients.remove(connection)


def cleanupClients():
    with lock:
        for client in clients:
            client.close()


if __name__ == '__main__':
    debug = print
    parser = argparse.ArgumentParser(description='PyChat Service')
    parser.add_argument('--host', dest='host', help='IPv4 address of host')
    parser.add_argument('--port', dest='port', type=int, help='chat service port')
    args = parser.parse_args()
    sock = makeSocket(args.host, args.port)
    serveRequests(sock)
