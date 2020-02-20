#!/usr/bin/env python3


from argparse import ArgumentParser
from socket import MSG_PEEK, socket
from select import select
from time import time


clients = {}
incoming = []
listener = None


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
        message = 'named changed to {}'.format(clients[fd])
    elif command[0] == '/whoisthere':
        message = ' '.join([client[1] for client in clients.items()])
    elif command[0] == '/quit':
        disconnect(fd)
        return
    else:
        message = 'unrecognized command: {}'.format(command[0])
    fd.send(appendTimestamp(message))


def appendTimestamp(message):
    timestamp = int(time()).to_bytes(4, 'big')
    return timestamp + message.encode()


def broadcast(message):
    stampedMessage = appendTimestamp(message)
    for connection, _ in clients.items():
        connection.send(stampedMessage)


def service():
    while incoming:
        readable, writable, exceptional = select(incoming, [], incoming)
        for fd in exceptional:
            disconnect(fd)
        for fd in readable:
            if fd == listener:
                connection, address = listener.accept()
                clients[connection] = 'anon'
                incoming.append(connection)
            else:
                recvBuffer = fd.recv(256, MSG_PEEK)
                # frame size (first byte) should be sanitized
                # 0 < frame_size < 256
                # need some way to not wait forever if client only sends message size
                if not recvBuffer:
                    disconnect(fd)
                elif len(recvBuffer) > recvBuffer[0]:
                    data = fd.recv(recvBuffer[0] + 1).decode()[1:]
                    if data[0] == '/':
                        handleCommand(fd, data)
                    else:
                        broadcast('{}: {}'.format(clients[fd], data))


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
