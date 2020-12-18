import socket
import threading
import pickle
import lib.Elgamal as Elgamal
import Server_Handler as h


class Server:

    def __init__(self, PORT):
        # getting the IP address
        self.HOST = socket.gethostbyname(socket.gethostname())
        # HOST = "192.168.3.14"
        # random port number
        self.PORT = PORT
        self.ADDR = (self.HOST, PORT)
        # number of bytes will be recived from the client to determine the size of the message
        self.HEADER = 10
        self.FORMAT = 'utf-8'
        # to diconnect the client from the server
        self.DISCONNECT_MSG = "Disconnect"
        # create the server socket
        self.Channel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the server socket with the IP address and port number
        self.Channel.bind(self.ADDR)
        self.start()

    # handle client, it was created to support multiple clients at the same time.
    def handle(self, address, client, client_pk, sk):
        print(f"[NEW CONNECTION] {address} connected.")
        
        try:
            h.Handler(client, client_pk, sk).run()
        except Exception as error:
            if(error.__class__.__name__!="ConnectionResetError"):
                print(address," Error:", str(error))
        print(f"[CLOSED CONNECTION] {address}.")

    # start the server
    def start(self):
        # start listening for connections
        self.Channel.listen()
        print(f"[LISTENING] Server is listening on {self.HOST}")
        # infinite loop for clients to connect
        while True:
            # accept new connection
            client, address = self.Channel.accept()
            # generate keys and exchange them
            pk, sk = self.generate_keys()
            client_pk = self.key_exchange(client, pk)
            # make a thread to be handled by the hanle function with arguments client, address and sk
            thread = threading.Thread(target=self.handle, args=(
                address, client,  client_pk, sk))
            # start the thread
            thread.start()

            print(f"[ACTIVE CONNECTION] {threading.activeCount()-1}")

    def generate_keys(self):
        pk, sk = Elgamal.generate_keys()
        return pk, sk

    def key_exchange(self, client, server_pk):
        data = pickle.dumps(server_pk)
        pk_length = len(data)
        send_length = str(pk_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        client.send(send_length)
        client.send(data)
        #wait for the client public key
        while True:
            pk_length = client.recv(self.HEADER)
            if pk_length:
                pk_length = int(pk_length)
                data = client.recv(pk_length)
                return pickle.loads(data)
