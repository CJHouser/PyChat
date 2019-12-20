# Python Chatroom

## Required
* Python 3.8.1

## Usage
### Server
Run the server from the command line

    ./chat-server.py <port>

NOTE: use a port in range 49152-65535, inclusive.
    
Use CTRL+C to terminate the server.

### Client
nc is used to simulate the client. Use localhost as the IP if running the server locally.

    nc <IP> <port>

The first message a client sends to the server is the user's name.

The server understands messages that follow these formats:

* Send message to other clients
      
      mess: <message>\n

* Refresh the client timeout

      alive:\n

* Retrieve a list of connected clients

      whoisthere:\n

## TODO
* The interface between the client and the server needs to be redone. That is, the messages that the client sends to the server ('alive:\n', 'whoisthere:\n', etc...) is ugly.
* The chatroom is based on TCP. The server processes incoming data one byte at a time. The server should group packets together, stopping at some delimiter.
* Server should properly clean up threads on shutdown.
* Server does not have control commands. Shutdown is currently done with CTRL+C.
* Entire client needs to be written.
* Switch CLI from Click to argparse.
* Needs signup/login.
* Private messaging?
* Message history
