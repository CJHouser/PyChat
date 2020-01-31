#!/usr/bin/env python3


from argparse import ArgumentParser
from socket import socket
from select import select


def service(host, port):
    listener = socket()
    listener.bind((host, port))
    listener.listen(10)
    clients = dict()
    incoming = [listener]
    while incoming:
        readable, writable, exceptional = select(incoming, [], incoming)
        for fd in readable:
            if fd == listener:
                connection, address = listener.accept()
                clients[connection] = 'anon'
                incoming.append(connection)
                for conn, un in clients.items():
                    conn.send('SERVER: {} joined'.format(clients[connection]).encode())
            else:
                data = fd.recv(1024).decode().rstrip('\n')
                if data:
                    if data[0] == '/': # handle commands
                        parsedCommand = data.split(' ')
                        if parsedCommand[0] == '/setname':
                            clients[fd] = ' '.join(parsedCommand[1:])
                        elif parsedCommand[0] == '/whoisthere':
                            for connection, username in clients.items():
                                userList = '{} {}'.format(userList, username)
                            fd.send('SERVER: {}'.format(userList).encode())
                        else:
                            fd.send('SERVER: unrecognized command'.encode())
                    else: # chatroom broadcast
                        username = clients[fd]
                        message = '{}: {}'.format(username, data).encode()
                        for connection, un in clients.items():
                            connection.send(message)
                else: # client side closed
                    disconnUsername = clients[fd]
                    incoming.remove(fd)
                    del clients[fd]
                    fd.close()
                    for connection, un in clients.items():
                        connection.send('SERVER: {} left'.format(disconnUsername).encode())
        for fd in exceptional:
            disconnUsername = clients[fd]
            incoming.remove(fd)
            del clients[fd]
            fd.close()
            for connection, un in clients.items():
                connection.send('SERVER: {} left'.format(disconnUsername).encode())


if __name__ == '__main__':
    parser = ArgumentParser(description='PyChat Service')
    parser.add_argument('host', help='IPv4 address of host')
    parser.add_argument('port', type=int, help='chat service port')
    args = parser.parse_args()
    service(args.host, args.port)
