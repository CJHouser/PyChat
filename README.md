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

## User commands
Change your username

    /setname <username>

List connected users (draws incorrectly client-side)

    /whoisthere

Leave the chatroom

    /quit

## TODO SERVER
* Server control (exit, restart, etc)
* Duplicate name checking
* Passworded server
* Message history
* ~~Avoid creating thread for each client~~
* ~~Scrap old server-client protocol~~
* ~~Clean up threads on shutdown~~
* ~~Switch from Click to argparse~~
* ~~Synchronized timestamps~~
