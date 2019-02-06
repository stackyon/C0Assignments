"""SimpleWebServer.py: A simple web server implemented in Python 3"""

__author__      = "Rong Zheng"
__copyright__   = "Copyright 2019, McMaster University"

# Import socket and relevant modules
import socket, sys, threading,time,optparse,os

# Define an error message for files not found
ErrorMsg404 = '<html><head></head><body><h1>404 Not Found</h1></body></html>'

def validate_port(x):
    """
    Check if the port number is within range
    Inputs:
        - x: port number

    Output:
        - True or False
    """
    if not x.isdigit():
        return False
    i = int(x)
    if i < 0 or i > 65535:
            return False
    return True

#A simple multi-thread  webserver

class SimpleWebServer:
    def __init__(self, port):
        threading.Thread.__init__(self)

        self.port = port
        self.BUFFER_SIZE = 8192

        #Create a server socket
        self.server = socket.socket()

        try:
            self.server.bind('127.0.0.1', port)
        except socket.error:
            print('Bind failed %s' % socket.error)
            sys.exit()

        #Listen to the server socket
        self.server.listen()    #YOUR CODE; 1 line

    def run_thread(self, conn, addr):
        # connection timeout after 60-second inactivity
        conn.settimeout(60.0)

        print('Client connected with ' + addr[0] + ':' + str(addr[1]))

        while True:
            try:
                # Receives the request message from the client
                message =  #YOUR CODE
                if not message: break

                # Extract the path of the requested object from the message
                # The path is the second part of HTTP header, identified by [1]
                filename = message.split()[1].decode()
                print('Client request ' + filename)

                # Extract the file extention to determine file type
                filename_extension = os.path.splitext(filename)[1]

                # Open the local file f specified in filename for reading
                # Because the extracted path of the HTTP request includes
                # a character '\', we read the path from the second character
                f = #YOUR CODE

                # Store the entire content of the requested file in a temporary buffer
                msg = #YOUR CODE

                # Send the HTTP response headers to the connection socket
                # 1. HTTP version and status code
                # YOUR CODE 1-line

                # 2. Keep-Alive field
                # YOUR CODE 1-line

                # 3. Content length field
                # YOUR CODE 1 - 3 lines

                # 4. Content type field (based on the file type)
                # YOUR CODE

                # Send the HTTP response body
                for i in range(0, len(msg), self.BUFFER_SIZE):
                    end = min(i + self.BUFFER_SIZE, len(msg))
                    conn.send(msg[i: end])

            # Exception handlieng
            except FileNotFoundError:
                # Send HTTP response message for file not found
                # YOUR CODE  1 - 3 lines

            except socket.timeout:
                #Socket timeout
                print("Conn socket timeout!")
                break
            except socket.error as e:
                #Other socket exceptions
                print("Socket error: %s" % e)
                break

        conn.close() # Close socket

    def run(self):
        print('Waiting for connections on port %s' % (self.port))
        while True:
            #Accept a new connection
            try:
                #Waiting for connection request
                (conn, addr) = self.server.accept()

                #Start a new thread to handle HTTP request/response
                threading.Thread(target=self.run_thread, args=(conn, addr)).start()
            except:
                break

        # Close the server socket
        self.exit()

    def exit(self):
        """Close server socket"""
        self.server.close()

if __name__ == '__main__':
    parser = optparse.OptionParser(usage="%prog ServerPort")
    options, args = parser.parse_args()
    if len(args) < 1:
        parser.error("No ServerPort")
    else:
        if validate_port(args[0]):
            server_port = int(args[0])
        else:
            parser.error("ServerPort invalid!")

    #Create and start the server
    server = SimpleWebServer(server_port)
    server.run()