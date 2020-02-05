# Python Chatroom

## Required
* Written using Python 3.6.9

## Usage
### Server
Run the server from the command line

    ./newserver.py <IPv4> <port>

Use CTRL+C to terminate the server.

### Client
Run the client from the command line

    ./newclient.py <IPv4> <port> <username>

Enter '/quit' in the textbox to close the client.

## User commands
Change your username

    /setname <username>

List connected users (draws incorrectly client-side)

    /whoisthere

## TODO SERVER
* Server control (exit, restart, etc)
* Explicitly write protocol grammar
* Synchronized time stamps
* Duplicate name checking
* Passworded server
* Message history
* ~~Avoid creating thread for each client~~
* ~~Scrap old server-client protocol~~
* ~~Clean up threads on shutdown~~
* ~~Switch from Click to argparse~~

## TODO CLIENT
* Scrolling message log
* User list
* ~~Ratio scaled UI~~
* ~~Resizability~~
