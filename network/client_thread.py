import socket

class ClientThread:
    
    CLIENT_PORT : int = 6000
    BUFSIZE : int = 1024

    def __init__(self):

        # socket initialisation
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', self.CLIENT_PORT))
        self.ip, _ = self.socket.getsockname()

        #TODO fix structure (see broadcast_thread for reference)
        data, server_node = self.broadcast_socket.recvfrom(self.BUFSIZE)


    def __exit__(self):
        self.socket.close()
    