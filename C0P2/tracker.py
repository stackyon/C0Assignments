import socket, sys, threading, json,time,optparse,os


def validate_ip(s):
    """
    Check if an input string is a valid IP address dot decimal format
    Inputs:
    - a: a string

    Output:
    - True or False
    """
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True


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


class Tracker(threading.Thread):
    def __init__(self, port, host='0.0.0.0'):
        threading.Thread.__init__(self)
        self.port = port    # port used by tracker
        self.host = host    # tracker's IP address
        self.BUFFER_SIZE = 8192
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket to accept connections from peers

        # Track (ip, port, exp time) for each peer using a dictionary
        # You can optionally use (ip,port) as key
        self.users = []

        # Track (ip, port, modified time) for each file
        # Only the most recent modified time and the respective peer are store
        # {'ip':,'port':,'mtime':}
        self.files = []

        self.lock = threading.Lock()
        try:
            self.server.bind(('127.0.0.1', port))
        except socket.error:
            print(('Bind failed %s' % (socket.error)))
            sys.exit()

        # listen for connections
        self.server.listen()

    def check_user(self):
        # Check if the peers are alive or not
        """Steps:
            1. check if a peer has expired or not
            2. if expired, remove items self.users and self.files ()
            [Pay attention to race conditions (Hint: use self.lock)]
        """
        # YOUR CODE
        self.lock.acquire()
        for user in self.users:
            user['etime'] = user['etime'] - 20
            if user['etime'] <= 0:
                self.users.pop(user)
                for file in self.files:
                    if file['ip'] == user['ip']:
                        self.files.pop(file)
        self.lock.release()

        # schedule the method to be called periodically
        t = threading.Timer(20, self.check_user)
        t.start()

    # Ensure sockets are closed on disconnect (This function is Not used)
    def exit(self):
        self.server.close()

    def run(self):
        # start the timer to check if peers are alive or not
        t = threading.Timer(20, self.check_user)
        t.start()

        print(('Waiting for connections on port %s' % (self.port)))
        while True:
            # accept incoming connection
            conn, addr = self.server.accept()

            # process the message from a peer
            threading.Thread(target=self.process_messages, args=(conn, addr)).start()

    def process_messages(self, conn, addr):
        conn.settimeout(180.0)
        print(('Client connected with ' + addr[0] + ':' + str(addr[1])))

        while True:
            # receiving data from a peer
            data = ''
            while True:
                part = conn.recv(self.BUFFER_SIZE).decode()
                data = data + part
                if len(part) < self.BUFFER_SIZE:
                    break

            # Check if the received data is a json string of the anticipated format. If not, ignore.
            if not(data.startswith('{')) or not(data.endswith('}')):
                break

            # deserialize
            data_dic = json.loads(data)

            """
            1) Update self.users and self.files if nessesary
            2) Send directory response message
            Steps:1. Check message type (initial or keepalive). See Table I in description.
                  2. If this is an initial message from a peer and the peer is in self.users, create the corresponding entry in self.users
                  2. If this is a  keepalive message, update the expire time with the respective peer
                  3. For an intial message, check the list of files. Create a new entry in user.files if one does not exist,
                  or, update the last modifed time to the most recent one
                  4. Pay attention to race conditions (Hint: use self.lock)
            """
            # YOUR CODE
            self.lock.acquire()
            if len(data_dic.items()) == 1:
                # it's a keepalive
                for user in self.users:
                    if user['ip'] == addr and user['port'] == conn:
                        user['etime'] = 180
            elif len(data_dic.items()) == 2:
                # it's an init message
                # clean out existing version
                for user in self.users:
                    if user['ip'] == addr and user['port'] == conn:
                        self.users.pop(user)
                # add user
                new_user = {
                    'ip': addr,
                    'port': conn,
                    'etime': 180
                }
                self.users.append(new_user)
                unknown_file = True
                for new_file in data_dic['files']:
                    # format the file to be associated to the peer
                    # don't accept it as new yet
                    associated_file = {
                        'name': new_file['name'],
                        'ip': addr,
                        'port': conn,
                        'mtime': new_file['mtime']
                    }
                    for existing_file in self.files:
                        if existing_file['name'] == new_file['name']:
                            unknown_file = False
                            if new_file['mtime'] > existing_file['mtime']:
                                self.files.pop(existing_file)
                                self.files.append(associated_file)
                    if unknown_file:
                        self.files.append(new_file)
            else:
                # ignore the message, it's not for the Tracker
                pass
        self.lock.release()
        conn.close()    # Close
        print(self.files[0]['name'])


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="%prog ServerIP ServerPort")
    options, args = parser.parse_args()
    if len(args) < 1:
        parser.error("No ServerIP and ServerPort")
    elif len(args) < 2:
        parser.error("No  ServerIP or ServerPort")
    else:
        if validate_ip(args[0]) and validate_port(args[1]):
            server_ip = args[0]
            server_port = int(args[1])
        else:
            parser.error("Invalid ServerIP or ServerPort")
    tracker = Tracker(server_port, server_ip)
    tracker.start()
