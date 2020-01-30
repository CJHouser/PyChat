# Python Chatroom

## Required
* Written using Python 3.6.9

## Usage
### Server
Run the server from the command line

    ./server.py <IPv4> <port>

Use CTRL+C to terminate the server.

### Client
Run the client from the command line

    ./client.py <IPv4> <port> <username>

Use CTRL+C to terminate the client.

## User commands
Change your username

    /setname <username>

List connected users (draws incorrectly client-side)

    /whoisthere

## TODO SERVER
* Avoid creating thread for each client
* Server control (exit, restart, etc)
* Explicitly write protocol grammar
* Synchronized time stamps
* Duplicate name checking
* Passworded server
* Message history
* Private messaging?
* ~~Scrap old server-client protocol~~
* ~~Clean up threads on shutdown~~
* ~~Switch from Click to argparse~~

## TODO CLIENT
* Scrolling message log
* User list
* ~~Ratio scaled UI~~
* ~~Resizability~~
