#!/usr/bin/env python3


from argparse import ArgumentParser
from curses import KEY_RESIZE, newpad, wrapper
from datetime import datetime
from math import floor, ceil
from socket import socket


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
    sock.setblocking(False)
    sock.send(len('/setname {}'.format(args.name)).to_bytes(1, 'big'))
    sock.send('/setname {}'.format(args.name).encode())

    terminalHeight, terminalWidth = stdscr.getmaxyx()
    textPadHeight = floor((terminalHeight - 3) * .1)

    chatPadHeight = ceil((terminalHeight - 3) * .9)
    chatPadWidth = terminalWidth - 2
    chatPad = newpad(chatPadHeight, chatPadWidth)
    chatPad.refresh(0, 0, 1, 1, chatPadHeight, chatPadWidth)

    textPadWidth = terminalWidth - 2
    textPad = newpad(textPadHeight, textPadWidth)
    textPad.nodelay(1)
    textPad.refresh(0, 0, terminalHeight - textPadHeight - 1, 1,
                    terminalHeight - 1, textPadWidth)
    
    drawBorders(stdscr, terminalHeight, terminalWidth, textPadHeight)

    chatPadCursorY = 0
    sendString = ''
    decodedRecv = ''
    c = ''
    while True:
        try:
            c = textPad.getkey()
        except:
            pass
        if c:
            if c == 'KEY_RESIZE':
                terminalHeight, terminalWidth = stdscr.getmaxyx()
                textPadHeight = floor((terminalHeight - 3) * .1)
                
                chatPadHeight = ceil((terminalHeight - 3) * .9)
                chatPadWidth = terminalWidth - 2
                chatPad = newpad(chatPadHeight, chatPadWidth)
                chatPad.refresh(0, 0, 1, 1, chatPadHeight, chatPadWidth)
                
                textPadWidth = terminalWidth - 2
                textPad = newpad(textPadHeight, textPadWidth)
                textPad.nodelay(1)
                textPad.refresh(0, 0, terminalHeight - textPadHeight - 1, 1,
                                terminalHeight - 1, textPadWidth)
                
                drawBorders(stdscr, terminalHeight, terminalWidth, textPadHeight)
            
                chatPadCursorY = 0
            elif c == '\n':
                sock.send(len(sendString).to_bytes(1, 'big'))
                sock.send(sendString.encode())
                if sendString == '/quit':
                    break
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
            c = ''
        try:
            recvd = sock.recv(1024)
        except:
            pass
        if recvd:
            timestamp = datetime.utcfromtimestamp(int.from_bytes(recvd[0:4], 'big')).isoformat()
            decodedRecv = '[{}] {}'.format(timestamp, recvd[4:].decode())
            rowCount = int(ceil(len(decodedRecv) / chatPadWidth))
            if rowCount + chatPadCursorY >= chatPadHeight:
                chatPadCursorY = 0
                chatPad.clear()
            chatPad.addstr(chatPadCursorY, 0, decodedRecv)
            chatPadCursorY += rowCount
            chatPad.refresh(0, 0, 1, 1, chatPadHeight, chatPadWidth)
            recvd = ''
            decodedRecv = ''
        
    
if __name__ == '__main__':
    parser = ArgumentParser(description='PyChat Service')
    parser.add_argument('host', help='IPv4 address of host')
    parser.add_argument('port', type=int, help='chat service port')
    parser.add_argument('name', help='chatroom display name')
    args = parser.parse_args()
    wrapper(main)
