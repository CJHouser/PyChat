#!/usr/bin/env python3

import sys
import socket
import threading
import time
import argparse

parser = argparse.ArgumentParser(description='PyChat service.')
parser.add_argument('port', type=int, nargs=1,
                    help='port where chat service listens')

isOnline = True
clients = set()
lock = threading.Lock()

def service(port):
    try:
        sock = socket.socket()
        sock.bind(('', port))
        sock.listen(10)
        while True:
            conn, addr = sock.accept()
            thread = threading.Thread(target=chatter, args=(conn,))
            thread.start()
            print("New Connection")
    except KeyboardInterrupt:
        print('\nInterrupt. Waiting for threads to join...')
        global isOnline
        isOnline = False
        sock.close()
        sys.exit()

def chatter(conn):
    # Allow 30 seconds for chatter to choose name
    conn.settimeout(30)
    try:
        name = getData(conn)
        name = name.replace('\n', '')
        name = name.replace(':', '')
    except socket.timeout:
        conn.close()
        return
    print("Got Name")
    identity = (conn, name)
    lock.acquire()
    clients.add(identity)
    lock.release()
    wall('joined: ' + name + '\n')
    # Check for keep alive experation every second
    conn.settimeout(1)
    aliveUntil = time.time() + 30
    while aliveUntil > time.time() and isOnline:
        try:
            data = getData(conn)
        except socket.timeout:
            if aliveUntil - time.time() < 0:
                break
            continue
        except OSError:
            break
        
        if data == '':
            break
        print("recieved data")
        # Handle messages from client
        if data == 'alive:\n':
            aliveUntil = time.time() + 30
            lock.acquire()
            send('alive:\n', conn)
            lock.release()
        elif data == 'whoisthere:\n':
            lock.acquire()
            [send('present: ' + client[1] + '\n', conn) for client in clients]
            lock.release()
            conn.sendall('present:\n'.encode())
        elif data[:6] == 'mess: ' and data[-1] == '\n':
            msg = data[6:-1].replace('\n', '')
            wall('mess-' + name + ': ' + msg + '\n')
    
    # Client cleanup
    wall('left: ' + name + '\n')
    lock.acquire()
    clients.discard(identity)
    lock.release()
    conn.close()

def wall(data):
    lock.acquire()
    [send(data, client[0]) for client in clients]
    lock.release()

def send(data, receiver):
    try:
        receiver.sendall(data.encode())
    except BrokenPipeError:
        return

def getData(conn):
    data = ""
    while True:
        temp = conn.recv(1).decode()
        if temp == '\n':
            data += temp
            return data
        else:
            data += temp

if __name__ == '__main__':
    args = parser.parse_args()
    port = args.port[0]
    service(port)
