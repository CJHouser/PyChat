#!/usr/bin/env python3


from argparse import ArgumentParser
from curses import newpad, wrapper
from math import ceil
from select import select
from socket import socket
from sys import stdin


def drawBorders(stdscr, y, x):
    stdscr.clear()
    stdscr.border()
    stdscr.addch(y - 5, 0,'├')
    for i in range(1, x):
        stdscr.addch(y - 5, i, '─')
    stdscr.addch(y - 5, x - 1, '┤')
    stdscr.refresh()


def main(stdscr):
    sock = socket()
    sock.connect((args.host, args.port))
    sock.sendall('/setname {}\n'.format(args.name).encode())

    termy, termx = stdscr.getmaxyx()
    drawBorders(stdscr, termy, termx)
    chatPad = newpad(termy - 6, termx - 2)
    chatPad.refresh(0, 0, 1, 1, termy - 6, termx - 2)
    textPad = newpad(3, 78)
    textPad.refresh(0, 0, 20, 1, 23, 78)
    
    chatPadCursorY = 0
    sendString = ''

    rlist = [sock, stdin]
    while True:
        readable, writable, erroneous = select(rlist, [], [])
        for fd in readable:
            if fd == sock:
                decodedRecv = sock.recv(256).decode()
                rowCount = int(ceil(len(decodedRecv) / 78))
                if rowCount + chatPadCursorY > termy - 6:
                    chatPadCursorY = 0
                    chatPad.clear()
                chatPad.addstr(chatPadCursorY, 0, decodedRecv)
                chatPadCursorY += rowCount
                chatPad.refresh(0, 0, 1, 1, termy - 6, termx - 2)
            elif fd == stdin:
                c = stdin.read(1)
                if c == '\r':
                    sock.sendall(sendString.encode())
                    sendString = ''
                    textPad.clear()
                elif c == '\x7f':
                    sendString = sendString[:-1]
                    textPad.clear()
                elif len(sendString) > 232:
                    pass
                else:
                    sendString += c
                textPad.addstr(0, 0, sendString)
                textPad.refresh(0, 0, 20, 1, 23, 78)
        
    
if __name__ == '__main__':
    parser = ArgumentParser(description='PyChat Service')
    parser.add_argument('host', help='IPv4 address of host')
    parser.add_argument('port', type=int, help='chat service port')
    parser.add_argument('name', help='chatroom display name')
    args = parser.parse_args()
    wrapper(main)
