import socket
import threading
import pickle
import lib.Elgamal as Elgamal
import json
import random
from paillier.crypto import secure_addition, scalar_multiplication, secure_subtraction
from paillier.keygen import generate_keys
from paillier.crypto import encrypt, decrypt


class Handler:

    def __init__(self, client, client_pk, server_sk):
        self.server_sk = server_sk
        self.client = client
        self.HEADER = 10
        self.FORMAT = 'utf-8'
        self.client_pk = client_pk
        self.DISCONNECT_MSG = 0
        self.file = None

    def CreateFile(self):
        wrongRand = True
        # get the file name from the client
        filename = self.recv()
        files = json.loads(open("server.json").read())
        for f in files:
            if(f["filename"] == filename):
                # if the file name already exists then send 0 to the client and exit
                self.send(0)
                return
        # if not then generate new id and return it to the client
        while wrongRand:
            wrongRand = False
            id = random.randint(1, 1000)
            for f in files:
                if(f["id"] == id):
                    wrongRand = True
                    break
        self.send(id)
        pk = self.recv()
        fileContent = {"id": id,
                       "filename": filename,
                       "content": [],
                       "pk": [pk[0], pk[1]]
                       }
        fileContent = json.dumps(fileContent)
        self.file = json.loads(fileContent)
        files.append(self.file)
        file = open("server.json", "w")
        json.dump(files, file)
        file.close()

    def OpenFile(self):
        idf = self.recv()
        pk = self.recv()
        files = json.loads(open("server.json").read())
        for file in files:
            if(file["id"] == idf and file["pk"] == pk):
                self.file = file
                self.send(1)
                return
        self.send(0)

    def SaveFile(self):
        if self.file:
            files = json.loads(open("server.json").read())
            for i in range(len(files)):
                if(files[i]["id"] == self.file["id"]):
                    files[i] = self.file
                    file = open("server.json", "w")
                    json.dump(files, file)
                    file.close()
                    self.send(1)
                    return
        self.send(0)

    def CloseFile(self):
        if self.file:
            files = json.loads(open("server.json").read())
            for i in range(len(files)):
                if(files[i]["id"] == self.file["id"]):
                    files[i] = self.file
                    file = open("server.json", "w")
                    json.dump(files, file)
                    file.close()
                    self.file = None
                    self.send(1)
                    return
        self.send(0)

    def getFile(self):
        self.send(self.file["content"])

    def replaceLine(self):
        # get the line number from the client
        line = self.recv()-1
        if(line < 0 or line >= len(self.file["content"])):
            self.send(0)
            return
        else:
            self.send(1)
            # get the segmants from the client
            segmants = self.recv()
            # replace the line
            self.file["content"][line]= segmants
            # tell the client that everthing is okay
            self.send(1)

    def appendNewLine(self):
        # get the segmants from the client
        segmants = self.recv()
        # add the segmants to the file
        self.file["content"].append(segmants)
        # tell the client that everthing is okay
        self.send(1)

    def appendAtTheEnd(self):

        ll = len(self.file["content"])-1
        # in case the file was new
        if(ll < 0):
            self.send(0)
            return

        ls = len(self.file["content"][ll])-1
        lastsegmant = self.file["content"][ll][ls]
        self.send(lastsegmant)
        # get the scale
        scale = self.recv()
        lastsegmant = scalar_multiplication(
            lastsegmant, scale, self.file["pk"][0])
        # get the segmants from the client
        segmants = self.recv()

        lastsegmant = secure_addition(
            lastsegmant, segmants[0], self.file["pk"][0])
        self.file["content"][ll][ls] = lastsegmant
        # add the rest of segmants to the file
        if(len(segmants[1:]) > 0):
            self.file["content"][ll] = self.file["content"][ll]+segmants[1:]
        # tell the client that everthing is okay
        self.send(1)

    def appendAtTheEndOfLine(self):
        ll = self.recv()-1
        # in case the file was new
        if(ll < 0 or ll >= len(self.file["content"])):
            self.send(0)
            return
        else:
            self.send(1)
        ls = len(self.file["content"][ll])-1
        lastsegmant = self.file["content"][ll][ls]
        self.send(lastsegmant)
        # get the scale
        scale = self.recv()
        lastsegmant = scalar_multiplication(
            lastsegmant, scale, self.file["pk"][0])
        # get the segmants from the client
        segmants = self.recv()

        lastsegmant = secure_addition(
            lastsegmant, segmants[0], self.file["pk"][0])
        self.file["content"][ll][ls] = lastsegmant
        # add the rest of segmants to the file
        if(len(segmants[1:]) > 0):
            self.file["content"][ll] = self.file["content"][ll]+segmants[1:]
        # tell the client that everthing is okay
        self.send(1)

    def insertLine(self):
        # get the line number from the client
        line = self.recv()-1
        if(line < 0 or line > len(self.file["content"])):
            self.send(0)
            return
        else:
            self.send(1)
            # get the segmants from the client
            segmants = self.recv()

            # insert the line
            self.file["content"].insert(line, segmants)
            # tell the client that everthing is okay
            self.send(1)

    def removeLine(self):
        # get the line number from the client
        line = self.recv()-1
        # in case the file was new
        if(line < 0 or line >= len(self.file["content"])):
            self.send(0)
            return
        else:
            # remove the line
            self.file["content"].pop(line)
            # tell the client that everthing is okay
            self.send(1)

    def clear(self):
        self.file["content"] = []
        # tell the client that everthing is okay
        self.send(1)

    def switch(self, i):
        switcher = {
            1: self.CreateFile,
            2: self.OpenFile,
            3: self.CloseFile,
            4: self.getFile,
            5: self.replaceLine,
            6: self.appendNewLine,
            7: self.appendAtTheEnd,
            8: self.appendAtTheEndOfLine,
            9: self.insertLine,
            10: self.removeLine,
            11: self.clear,
            12: self.SaveFile
        }
        switcher.get(i, lambda: 'Invalid')()

    def recv(self):
        while True:
            msg_length = self.client.recv(self.HEADER)
            #print(msg_length)
            # to make sure that it is not null
            if msg_length:
                #print("I am inside")
                msg_length = int(msg_length)
                # receive the actual message with the message length as the new Buffer
                data = self.client.recv(msg_length)
                # load the message from the picle obj
                ct = pickle.loads(data)
                #print(ct)
                return self.decrypt(ct, self.server_sk)

    def send(self, msg):
        ct = self.encrypt(msg)
        # print(ct)
        data = pickle.dumps(ct)
        msg_length = len(data)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(data)

    def encrypt(self, msg):
         if type(msg) == int and msg < self.client_pk[0]:
            return Elgamal.encrypt(self.client_pk, msg)
         else:
            return msg

    def decrypt(self, ct, sk):
         if type(ct) == tuple and ct[0] < sk[0]:
            return Elgamal.decrypt(sk, ct)
         else:
            return ct

    def run(self):
        # infinite loop to recv messages from the client
        while True:
            # receive the message length from the client (HEADER SIZE)
            msg_length = self.client.recv(self.HEADER)
            # to make sure that it is not null
            if msg_length:
                # convert the message length to an integer
                msg_length = int(msg_length)
                # receive the actual message with the message length as the new Buffer
                data = self.client.recv(msg_length)
                # load the message from the picle obj
                ct = pickle.loads(data)
                #print(ct)
                fun = self.decrypt(ct, self.server_sk)
                # make sure to close the connection
                if fun == self.DISCONNECT_MSG:
                    self.client.close()
                    return
                self.switch(fun)
