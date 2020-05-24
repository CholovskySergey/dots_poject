import socket
import pickle


class Network:
    def __init__(self, port=1487):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = '25.41.111.123'
        self.port = port
        self.addr = (self.server, self.port)
        self.p = -1
        self.connect()

    def get_player(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            # return pickle.loads(self.client.recv(2048*32))
        except:
            pass

    def set_p(self):
        try:
            self.client.send(pickle.dumps('player'))
            self.p = pickle.loads(self.client.recv(2048*32))
        except:
            pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048*32))
        except socket.error as e:
            print(e)
