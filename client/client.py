#!/usr/bin/env python3


from argparse import ArgumentParser
from collections import deque
from curses import KEY_RESIZE, newpad, wrapper
from math import ceil
from select import select
from socket import socket
from sys import stdin


def drawBorders(stdscr, terminalHeight, terminalWidth, textPadHeight):
    separatorHeight = terminalHeight - textPadHeight - 2
    stdscr.clear()
    stdscr.border()
    stdscr.addch(separatorHeight, 0,'├')
    for i in range(1, terminalWidth):
        stdscr.addch(separatorHeight, i, '─')
    stdscr.addch(separatorHeight, terminalWidth - 1, '┤')
    stdscr.refresh()


def main(stdscr):
    sock = socket()
    sock.connect((args.host, args.port))
    sock.sendall('/setname {}\n'.format(args.name).encode())

    terminalHeight, terminalWidth = stdscr.getmaxyx()
    textPadHeight = 5

    drawBorders(stdscr, terminalHeight, terminalWidth, textPadHeight)

    chatPadHeight = terminalHeight - textPadHeight - 3
    chatPadWidth = terminalWidth - 2
    chatPad = newpad(chatPadHeight, chatPadWidth)
    chatPad.refresh(0, 0, 1, 1, chatPadHeight, chatPadWidth)

    textPadWidth = terminalWidth - 2
    textPad = newpad(textPadHeight, textPadWidth)
    textPad.refresh(0, 0, terminalHeight - textPadHeight - 1, 1,
                    terminalHeight - 1, textPadWidth)
    
    chatPadCursorY = 0
    sendString = ''
    inbound = [sock, stdin]
    outbound = [sock]
    messageQueue = deque()
    while True:
        readable, writable, exceptional = select(inbound, outbound, [])
        for fd in readable:
            if fd == stdin:
                c = stdin.read(1)
                if c == '\r':
                    messageQueue.append(sendString)
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
                textPad.refresh(0, 0, terminalHeight - textPadHeight - 1, 1,
                                terminalHeight - 1, textPadWidth)
            elif fd == sock:
                decodedRecv = sock.recv(256).decode()
                rowCount = int(ceil(len(decodedRecv) / 78))
                if rowCount + chatPadCursorY >= chatPadHeight:
                    chatPadCursorY = 0
                    chatPad.clear()
                chatPad.addstr(chatPadCursorY, 0, decodedRecv)
                chatPadCursorY += rowCount
                chatPad.refresh(0, 0, 1, 1, terminalHeight - 6,
                                terminalWidth - 2)
        for fd in writable:
            if fd == sock and messageQueue:
                fd.sendall(messageQueue.popleft().encode())
        
    
if __name__ == '__main__':
    parser = ArgumentParser(description='PyChat Service')
    parser.add_argument('host', help='IPv4 address of host')
    parser.add_argument('port', type=int, help='chat service port')
    parser.add_argument('name', help='chatroom display name')
    args = parser.parse_args()
    wrapper(main)
