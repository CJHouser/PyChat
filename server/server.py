#!/usr/bin/env python3


import argparse
import socket
import threading


clients = set()
debug = lambda *args, **kw: None
lock = threading.Lock()


class Client(threading.Thread):
    def __init__(self, connection, address):
        threading.Thread.__init__(self)
        self.name = 'anon'
        self.connection = connection
        self.address = address
    
    def getConnection(self):
        return self.connection

    def getName(self):
        return self.name

    def command(self, decodedData):
        parsedCommand = decodedData.split(' ')
        if parsedCommand[0] == '/whoisthere':
            with lock:
                for client in clients:
                    name = client.getName() + '\n'
                    self.connection.sendall(name.encode())
        elif parsedCommand[0] =='/setname':
            self.name = parsedCommand[1]
        else:
            self.connection.sendall('SERVER: Unrecognized command\n'.encode())
   
    def run(self):
        while True:
            try:
                recvData = self.connection.recv(256)
            except socket.timeout:
                try:
                    self.connection.sendall(b'1')
                    continue
                except OSError:
                    debug('DEBUG  - client gone: {}'.format(self.address))
                    break
            except OSError: # can be client too
                debug('DEBUG  - server gone: {}'.format(self.address))
                break
            decodedData = recvData.decode().rstrip('\n')
            if not decodedData:     # What a disgraceful client socket
                packetType = 'null'
                debug('DEBUG  - {} from {}'.format(packetType, self.address))
                break
            elif decodedData[0] == '/':
                self.command(decodedData)
                packetType = 'command'
            else:
                namedMessage = '{}: {}\n'.format(self.name, decodedData).encode()
                sendToAllClients(namedMessage)
                packetType = 'message'
            debug('DEBUG  - {} from {}'.format(packetType, self.address))
        self.connection.close()
        with lock:
            clients.remove(self)


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
    clientConnection, clientAddress = sock.accept()
    debug('DEBUG  - new connection: {}'.format(clientAddress))
    clientConnection.settimeout(300)
    client = Client(clientConnection, clientAddress)
    with lock:
        clients.add(client)
    client.start()


def sendToAllClients(data):
    with lock:
        for client in clients:
            client.getConnection().sendall(data)


def cleanupClients():
    with lock:
        for client in clients:
            client.getConnection().close()


if __name__ == '__main__':
    debug = print
    parser = argparse.ArgumentParser(description='PyChat Service')
    parser.add_argument('host', help='IPv4 address of host')
    parser.add_argument('port', type=int, help='chat service port')
    args = parser.parse_args()
    sock = makeSocket(args.host, args.port)
    serveRequests(sock)
