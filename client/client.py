#!/usr/bin/env python3


from argparse import ArgumentParser
from curses import newpad, wrapper
from math import ceil
import select
from socket import socket
import sys
from threading import Thread


def drawBorders(stdscr, y, x):
    stdscr.clear()
    stdscr.border()
    stdscr.addch(y - 5, 0,'├')
    for i in range(1, x):
        stdscr.addch(y - 5, i, '─')
    stdscr.addch(y - 5, x - 1, '┤')
    stdscr.refresh()


def receive(sock, chatPad):
    cursorY = 0
    while True:
        encodedRecv = sock.recv(1024)
        decodedRecv = encodedRecv.decode('ascii')
        y, x = chatPad.getmaxyx()
        lineCount = int(ceil(len(decodedRecv) / x))
        if cursorY + lineCount >= y:
            chatPad.clear()
            chatPad.refresh(0, 0, 1, 1, y, x)
            cursorY = 0
        for i in range(lineCount):
            index = i * (x - 2)
            line = decodedRecv[index:index + (x - 2)]
            chatPad.addstr(cursorY, 0, line)
            cursorY += 1
        chatPad.refresh(0, 0, 1, 1, y, x)


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

    rlist = [sock, sys.stdin]
    while True:
        readable, writable, erroneous = select.select(rlist, [], [])
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
            elif fd == sys.stdin:
                c = sys.stdin.read(1)
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
