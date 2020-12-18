import socket
import pickle
import lib.Elgamal as Elgamal


class Connection:

    def __init__(self, SERVER, PORT):
        self.SERVER = SERVER
        self.PORT = PORT
        self.HEADER = 10
        self.FORMAT = 'utf-8'
        self.DISCONNECT_MSG = "Disconnect"
        self.ADDR = (self.SERVER, self.PORT)
        self.sk = 0
        self.pk = 0
        self.server_pk = 0
        self.Channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect()

    def send(self, msg):
        ct = self.encrypt(msg)
        #print(ct)
        data = pickle.dumps(ct)
        msg_length = len(data)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.Channel.send(send_length)
        self.Channel.send(data)
        #print("Endded")

    def recv(self):
        while True:
            msg_length = self.Channel.recv(self.HEADER)
            # to make sure that it is not null
            if msg_length:
            # convert the message length to an integer
                msg_length = int(msg_length)
            # receive the actual message with the message length as the new Buffer
                data = self.Channel.recv(msg_length)
            # load the message from the picle obj
                ct = pickle.loads(data)
                # print(ct)
            # make sure to close the connection
                return self.decrypt(ct,self.sk)

    def encrypt(self, msg):
        if type(msg) == int and msg < self.server_pk[0]:
            return Elgamal.encrypt(self.server_pk, msg)
        else:
            return msg


    def decrypt(self, ct,sk):
        if type(ct) == tuple and ct[0] < sk[0]:
            return Elgamal.decrypt(sk, ct)
        else:
            return ct



    def generate_keys(self):
        pk, sk = Elgamal.generate_keys()
        return pk, sk

    def key_exchange(self, client_pk):
        data = pickle.dumps(client_pk)
        pk_length = len(data)
        send_length = str(pk_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))

        self.Channel.send(send_length)
        self.Channel.send(data)

        #wait for the server public key
        while True:
            pk_length = self.Channel.recv(self.HEADER)
            if pk_length:
                pk_length = int(pk_length)
                data = self.Channel.recv(pk_length)
                return pickle.loads(data)

    def connect(self):
        self.Channel.connect(self.ADDR)
        self.pk, self.sk = self.generate_keys()
        self.server_pk = self.key_exchange(self.pk)
