#!/usr/bin/env python3


from argparse import ArgumentParser
from socket import socket
from select import select

listener = None
incoming = []
clients = dict()


def disconnect(fd):
    username = clients[fd]
    incoming.remove(fd)
    del clients[fd]
    fd.close()
    broadcast('{} left'.format(username))


def handleCommand(fd, data):
    command = data.split(' ')
    response = 'unrecognized command: {}'.format(command[0])
    if command[0] == '/setname':
        clients[fd] = ' '.join(command[1:])
        response = 'named changed to {}'.format(clients[fd])
    elif command[0] == '/whoisthere':
        response = ' '.join([client[1] for client in clients.items()])
    elif command[0] == '/quit':
        disconnect(fd)
        response = ''
    return response


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
                    response = handleCommand(fd, data)
                    if response:
                        fd.send(response.encode())
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
