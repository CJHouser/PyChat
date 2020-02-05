#!/usr/bin/env python3


from argparse import ArgumentParser
from socket import socket
from select import select

listener = None
incoming = []
clients = {}


def disconnect(fd):
    username = clients[fd]
    incoming.remove(fd)
    del clients[fd]
    fd.close()
    broadcast('{} left'.format(username))


def handleCommand(fd, data):
    command = data.split(' ')
    if command[0] == '/setname':
        clients[fd] = ' '.join(command[1:])
        fd.send('named changed to {}'.format(clients[fd]).encode())
    elif command[0] == '/whoisthere':
        fd.send(' '.join([client[1] for client in clients.items()]).encode())
    elif command[0] == '/quit':
        disconnect(fd)
    else:
        fd.send('unrecognized command: {}'.format(command[0]).encode())


def broadcast(message):
    for connection, _ in clients.items():
        connection.send(message.encode())


def service():
    while incoming:
        readable, writable, exceptional = select(incoming, [], incoming)
        for fd in readable:
            if fd == listener:
                connection, address = listener.accept()
                clients[connection] = 'anon'
                incoming.append(connection)
            else:
                data = fd.recv(1024).decode().rstrip('\n')
                if data[0] == '/':
                    handleCommand(fd, data)
                else:
                    broadcast('{}: {}'.format(clients[fd], data))
        for fd in exceptional:
            disconnect(fd)


if __name__ == '__main__':
    parser = ArgumentParser(description='PyChat Service')
    parser.add_argument('host', help='IPv4 address of host')
    parser.add_argument('port', type=int, help='chat service port')
    args = parser.parse_args()
    listener = socket()
    listener.bind((args.host, args.port))
    listener.listen(10)
    incoming.append(listener)
    service()
