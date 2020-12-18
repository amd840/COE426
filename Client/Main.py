import Client as c
import json
import time
import os
from paillier.crypto import secure_addition, scalar_multiplication, secure_subtraction
from paillier.keygen import generate_keys
from paillier.crypto import encrypt, decrypt
from lib.Converter import *

FileOpend = False
dirty = False
conn = None
file = None
width = os.get_terminal_size().columns
lineBreak = "#" * width

def formats(format):

    switcher = {
        'red':  '\033[31m',
        'green':  '\033[32m',
        'bold':  '\033[1m',
        'end':  '\033[0m\n',
        'yellow': '\033[33m',
        'subH': '\033[42;3;30;1m'
    }

    return switcher.get(format, "None")
    


def App():

    
    print(lineBreak)
    print("\033[95;1mWelcome to \033[0m".center(width))
    print("\033[95;1mColaborative Text Editor\033[0m".center(width))
    print(lineBreak)
    print("\033[95;1mThis Text Editor is Secured Using Homomorphic Encyption\033[0m".center(width))
    print("\033[95;1mNo One Will Be Able to Know the Content of Your File :)\033[0m".center(width))
    print(lineBreak +"\n\n")

    while True:
        if(not FileOpend):
            print("Console >> \033[3;1;47;30mTo use the text editor you need to open a file or create new file \033[0m")
            print("Console >>   To open a file, type open [File Name]")
            print("Console >>   To create new file, type create [File Name]")


            line = input().split(" ")
            if(line[0].lower() != "create" and line[0].lower() != "open" and line[0].lower() != "exit"):
                print("Console >>",formats('red')," Error: You need to open or create new file before proceesding.",formats('end'))
            else:
                switch(line)
        else:
            time.sleep(0.1)
            print("Console >> \033[3;1;47;30mPlease enter a command \033[0m")
            line = input().strip().split(" ")
            switch(line)

def commands(args):
	print("\nConsole >> \033[3;1;47;30mList of Avaliable Functionality:\033[0m\n")
	print("Console >>  ",formats('subH'),"append: to append text with several options \033[0m ")
	print("Console >>	usage: append [OPTION] [TEXT]")
	print("Console >>	OPTION:")
	print("Console >>	  -n: To append a new line")
	print("Console >>	  -e: To append at the end of the file")
	print("Console >>	  -l: To append at line [INT] in the file\n")
	print("Console >>  ",formats('subH'),"insert: to insert text in a specific line \033[0m")
	print("Console >>	usage: insert [INT] [TEXT]\n")
	print("Console >>  ",formats('subH'),"remove: to remove line from the file \033[0m")
	print("Console >>	usage: remove [INT]\n")
	print("Console >>  ",formats('subH'),"replace: to replace text in a selected line with other text \033[0m")
	print("Console >>	usage: replace [INT] [TEXT]\n")
	print("Console >>  ",formats('subH'),"getfile: to get the content of the file \033[0m")
	print("Console >>	usage: getfile\n")
	print("Console >>  ",formats('subH'),"clear: to clear the file content \033[0m")
	print("Console >>	usage: clear\n")
	print("Console >>  ",formats('subH'),"save: to save the file content \033[0m")
	print("Console >>	usage: save\n")
	print("Console >>  ",formats('subH'),"close: to close and save the file content \033[0m")
	print("Console >>	usage: close\n")
	print("Console >>  ",formats('subH'),"exit: to exit from the file editor \033[0m")
	print("Console >>	usage: exit\n")
	return

def createFile(args):
    global FileOpend

    if(len(args) != 1):
        print("Console >> ", formats('red'),"Create command takes 1 input but ", len(args), " was given", formats('end'))
        return

    
    # send to the server that you want to create new File
    print("Console >> Creating new file, please wait...")
    conn.send(1)
    files = json.loads(open("client.json").read())
    filename = args[0]

    # send the name of the file to the server
    conn.send(filename)

    # Wait for the id of the file from the server
    id = conn.recv()
    # print(str(id) + " Hello")

    # if id was 0 then this means the name is already used
    if id == 0:
        print("Console >> \033[31mError: This file name is already being used\033[0m\n")
    else:
        # generate pk and sk key for this file
        pk, sk = generate_keys()
        #print(pk)

        # send the public key to the server
        conn.send(pk)

        sl = list(sk)
        data = {"id": id,
                "filename": filename,
                "pk": [pk[0], pk[1]],
                "sk": [sl[0], sl[1]]
                }
        files.append(json.loads(json.dumps(data)))
        writer = open("client.json", "w")
        json.dump(files, writer)
        writer.close()
        FileOpend = True
        print("Console >> ",formats('green'),formats('bold'),filename ,"\033[0m \033[32mCreated with ID: ", id, formats('end'))
        openFile([filename])

def openFile(args):
    if(len(args) != 1):
        print("Console >> ", formats('red'),"Open command takes 1 input but ", len(args), " was given",formats('end'))
        return

    filename = args[0]
    files = json.loads(open("client.json").read())
    print("Console >> Opening file, please wait...")
    time.sleep(0.5)
    for f in files:
        if(f["filename"] == filename):
            # send to the server that you want to open a file
            conn.send(2)

            # send the id and pk to the server
            conn.send(f["id"])
            conn.send(f["pk"])

            # wait for the server respons
            respons = conn.recv()

            if(respons == 1):
                global FileOpend
                global file
                file = f
                FileOpend = True
                print("Console >> ", formats('green'),"The file \"",formats('bold'), filename, "\033[0m",formats('green'), "\" has been opend successfully",formats('end'), sep = "")
                return
            else:
                print("Console >> ", formats('red'),"Error: Access denied", formats('end'))
                return

    print("Console >> ", formats('red'),"Error: You do not have file called\"", filename, formats('end'), sep ="")

def saveFile(args):
    global dirty

    if(len(args) != 0):
    	if(args[0] == "--help"):
    		print("Console >> usage: save ")
    		print("Console >> This command will save your changes in the file.")
    		return
    	print("Console >> ",formats('red'),"Close command takes 0 input but ", len(args), " was given",formats('end'))
    	return

    # send to the server that you want to save the file
    conn.send(12)

    # wait for the server response
    respons = conn.recv()
    print("Saving you file, please wait...")
    time.sleep(0.8)
    if(respons == 1):
        dirty = False
        print("Console >> ", formats('green'), "Your file has been saved successfully", formats('end'))
        return
    else:
        print("Console >> ", formats('red'),"Error: We could not save your file please try again", formats('end'))
        return

def closeFile(args):
    global FileOpend
    global dirty

    if(len(args) != 0):
    	if(args[0] == "--help"):
    		print("Console >> usage: close")
    		print("Console >> This command will close and save your changes in the file.")
    		return
    	else:
    		print("Console >> ", formats('red'),"Close command takes 0 input but ", len(args), " was given", formats("end"))
    		return
    
    if dirty:
        res = input("Console >> \033[33mDo you want to save the changes made in the document?\nYour changes will be lost if you do not save them(y or n)\033[0m\n")
        if (res.lower() == 'no' or res.lower() == 'n'):
            print("Console >> ", formats('green'),"Your file has been closed successfully", formats('end'))
            FileOpend = False
            dirty = False
            return

    # send to the server that you want to close the file
    conn.send(3)

    # wait for the server response
    respons = conn.recv()
    print("Console >> Closing you file, please wait...")
    time.sleep(0.5)
    if(respons == 1):
        FileOpend = False
        dirty = False
        print("Console >> ",formats('green'),"Your file has been closed successfully", formats('end'))
        return
    else:
        print("Console >> ",formats("red"),"Error: We could not close your file please try again", formats('end'))
        return

def getFile(args):

    if(len(args) != 0):
        if(args[0] == "--help"):
            print("Console >> usage: getfile\n")
            print("Console >> This command will print the content of the file.")
            return
        print("Console >> ", formats('red'),"Error: getfile command takes 0 input but ", len(args), " was given", formats('end'))
        return

    # send to the server that you want to get the file content
    conn.send(4)

    # wait for the content from the server
    content = conn.recv()
    if len(content)>0:
        print("Console >> File content: ")
        print(lineBreak)
        for line in content:
            for segmant in line:
                print(Decode(decrypt(file["pk"], file["sk"], segmant)).center(width)[1:], end="")
            print("\n"+lineBreak)
    else:
        print("Console >> ",formats('red'),"Your file is empty.", formats('end'))

def ReplaceLine(args):
    global dirty

    if(len(args) < 2):
        if(args[0] == "--help"):
            print("Console >> usage: replace [INT] [TEXT]")
            print("Console >> This command will replace text in a selected line with other text.")
            return
        print("Console >> ", formats('red'),"Error: replaceLine command takes 2 input but ", len(args), " was given", formats('end'))
        return

    line = int(args[0])
    text = ""
    for word in args[1:]:
        text += word+" "
    text = text.strip()

    if(len(text) == 0):
        print("Console >> ", formats('red'),"Error: Empty text, please add some text to replace", formats('end'))
        return

    # check if we need to split the text into segmants
    segmants = []
    for i in range(0, len(text), 200):
        segmants.append(encrypt(file["pk"], Encode(text[i:i+200])))

    # tell the server that you are calling for ReplaceLine function
    conn.send(5)

    # send the line number to the server
    conn.send(line)

    # wait for the server confirmation of the line
    respons = conn.recv()
    if(respons == 0):
        print("Console >> ",formats('red'),"Error: line ", line, "dose not exists", formats('end'))
        return

    conn.send(segmants)
    respons = conn.recv()
    print("Console >> Replacing line ", line, " with ", text,", please wait...")
    time.sleep(0.8)
    if(respons == 1):
        dirty = True
        print("Console >> ",formats('green'),"Line ", line, " has been updated", formats('end'))
    else:
        print("Console >> ", formats('red'),"Error: We could not replace the line please try again", formats('end'))

def AppendNewLine(args):
    global dirty

    text = ""
    for word in args:
        text += word+" "
    text = text.strip()

    if(len(text) == 0):
        print("Console >> ",formats('red'),"Error: Empty text", formats('end'))
        return

    # check if we need to split the text into segmants
    segmants = []
    for i in range(0, len(text), 200):
        segmants.append(encrypt(file["pk"], Encode(text[i:i+200])))

    # tell the server that you are calling for AppendNewLine function
    conn.send(6)

    # send the segmants to the server
    conn.send(segmants)
    
    # wait for the server confirmation
    respons = conn.recv()
    if(respons == 1):
        dirty = True
        print("Console >> ",formats('green'),"Your text has been appended in a new line",formats('end'))
    else:
        print("Console >> ", formats('red'),"Error: We could not append the line please try again", formats('red'))

def appendAtTheEnd(args):
    global dirty

    text = ""
    for word in args:
        text += word+" "
    text = text.strip()

    if(len(text) == 0):
        print("Console >> ",formats('red'),"Error: Empty text",formats('end'))
        return

    # tell the server that you are calling for appendAtTheEnd function
    conn.send(7)

    # wait for the last segmant from the server
    lsegmant = conn.recv()
    if(lsegmant == 0):
        AppendNewLine(args)
        return
    
    length = len(Decode(decrypt(file["pk"], file["sk"], lsegmant)))
    Scale = 10**(len(str(Encode(text[0:(200-length)])))+1)
    print(Scale)
    print(Encode(text[0:(200-length)]))
    segmants = []
    segmants.append(encrypt(file["pk"], Encode(text[0:(200-length)])))

    for i in range(length, len(text), 200):
        segmants.append(encrypt(file["pk"], Encode(text[i:i+200])))

    # Send the scale factor to the server
    conn.send(Scale)

    # send the segmants to the server
    conn.send(segmants)

    # wait for the server confirmation
    respons = conn.recv()
    if(respons == 1):
        dirty = True
        print("Console >> ",formats('green'),"Your text has been appended in the last line", formats('end'))
    else:
        print("Console >> ",formats('red'),"Error: We could not append the line please try again",formats('end'))

def appendAtTheEndOfLine(args):
    global dirty

    line = int(args[0])
    text = ""

    #segment the text
    for word in args[1:]:
        text += word+" "
    text = text.strip()

    if(len(text) == 0):
        print("Console >> ",formats('red'),"Error: Empty text",formats('end'))
        return

    # tell the server that you are calling for appendAtTheEndOfLine function
    conn.send(8)

    # send the line number to the server
    conn.send(line)

    # wait for the server confirmation of the line
    respons = conn.recv()
    if(respons == 0):
        print("Console >> ",formats('red'),"Error: line ", line, "dose not exists\nPlease try again", formats('end'))
        return

    # wait for the last segmant from the server
    lsegmant = conn.recv()
    length = len(Decode(decrypt(file["pk"], file["sk"], lsegmant)))
    Scale = 10**(len(str(Encode(text[0:(200-length)])))+1)
    segmants = []
    segmants.append(encrypt(file["pk"], Encode(text[0:(200-length)])))

    for i in range(length, len(text), 200):
        segmants.append(encrypt(file["pk"], Encode(text[i:i+200])))

    # Send the scale factor to the server
    conn.send(Scale)

    # send the segmants to the server
    conn.send(segmants)

    # wait for the server confirmation
    respons = conn.recv()

    if(respons == 1):
        dirty = True
        print("Console >> ",formats('green'),"Your text has been appended in line ", line, formats('end'))
    else:
        print("Console >> ",formats('red'),"Error: We could not append the line please try again",formats('end'))

def InsertLine(args):
    global dirty

    if(len(args) < 2):
        #check if the user input help command
        if(args[0] == "--help"):
            print("Console >> usage: insert [INT] [TEXT]")
            print("Console >> This command will insert text in a specific line.\n")
            return
        print("Console >> ",formats('red'),"Error: InsertLine command takes 2 input but ", len(args), " was given",formats('end'))
        return
    
    line = int(args[0])
    text = ""

    for word in args[1:]:
        text += word+" "
    text = text.strip()

    if(len(text) == 0):
        print("Console >> ",formats('red'),"Error: Empty text, please add some text", formats('end'))
        return

    # check if we need to split the text into segmants
    segmants = []
    for i in range(0, len(text), 200):
        segmants.append(encrypt(file["pk"], Encode(text[i:i+200])))

    # tell the server that you are calling for InsertLine function
    conn.send(9)

    # send the line number to the server
    conn.send(line)

    # wait for the server confirmation of the line
    respons = conn.recv()

    if(respons == 0):
        print("Console >> ",formats('red'),"Error: line ", line, "dose not exists\nPlease try again",formats('end'))
        return

    conn.send(segmants)
    respons = conn.recv()

    if(respons == 1):
        dirty = True
        print("Console >> ",formats('green'),"Your text has been inserted in line ", line,formats('end'))
    else:
        print("Console >> ",formats('red'),"Error: We could not insert the line, please try again", formats('end'))

def removeLine(args):
    if(len(args) != 1):
        if(args[0] == "--help"):
            print("Console >> usage: remove [INT]")
            print("Console >> This command will remove a line from the file.\n")
            return
        print("Console >> ",formats('red'),"Error: remove command takes 1 input but ", len(args), " was given",formats('end'))
        return
    line = int(args[0])
    # tell the server that you are calling for removeLine function
    conn.send(10)
    # send the line number to the server
    conn.send(line)
    # wait for the server confirmation of the line
    respons = conn.recv()
    if(respons == 0):
        print("Console >> ",formats('red'),"Error: line ", line, "dose not exists\nPlease try again", formats("end"))
        return
    else:
        global dirty
        dirty = True
        print("Console >> ",formats('green'),"Line ", line, " has been removed successfully", formats('end'))

def Clear(args):
    if(len(args) != 0):
        print("Clear command takes 0 input but ", len(args), " was given")
        return
    # tell the server that you are calling for Clear function
    res = input("\033[93mWarning!! this will wipe your file content from our servers forever\nAre you sure ?(y or n)\033[0m>\n")

    if(res.lower() =="yes" or res.lower() =="y"):
	    conn.send(11)
	    respons = conn.recv()
	    if(respons == 1):
	        global dirty
	        dirty = True
	        print("\033[32mYour file has been cleard successfully\nThe content of your file has been wiped forever!\033[0m\n")
	    else:
	        print("There was a problem in clearing the file\n")
    else:
	    print("You have cancelled the operation\n")
	    return

def exitApp(args):

	if dirty:
		res = input("Console >> \033[33mYou have unsaved changes, do you want to save ?(y or n)\033[0m")
		if(res == 'y'):
			switch(["save"])

	print("\n\n" + lineBreak)
	print("\033[95;1mThanks For Using This Text Editor".center(width))
	print("Hope to See you Again".center(width))
	print("Bye\033[0m".center(width))
	print(lineBreak)
	exit()

def append_switch(i):
    if(not i or i[0] == "--help" ):
        print("Console >> usage: append [OPTION] [TEXT]")
        print("Console >>   OPTION:")
        print("Console >> 	   n: To append in a new line")
        print("Console >> 	   e: To append at the end of the file")
        print("Console >> 	   l: To append at line [INT] in the file\n")
        return
    switcher = {
        "-n": AppendNewLine,
        "-e": appendAtTheEnd,
        "-l": appendAtTheEndOfLine
    }
    switcher.get(i[0], lambda x: print(
        "Console >> wrong input for the append, type append --help for further assisteance"))(i[1:])

def switch(i):

    switcher = {
        "create": createFile,
        "open": openFile,
        "close": closeFile,
        "save": saveFile,
        "getfile": getFile,
        "replace": ReplaceLine,
        "append": append_switch,
        "insert": InsertLine,
        "remove": removeLine,
        "clear": Clear,
        "exit": exitApp,
        "--help": commands,
        "help": commands,
    }

    switcher.get(i[0], lambda x: print('Console >> ',formats("red"),'Error: No such command called',formats('bold'), i[0], '\033[0m',formats('red'),' you can enter (help) for assistance',formats('end')))(i[1:])
 
def main():
    SERVER = "127.0.0.1"
    PORT = 60548
    global conn
    try:
        conn = c.Connection(SERVER, PORT)
        App()
    except Exception as error:
    	print("Error: ", str(error))
    	exit()

if __name__ == '__main__':
    main()
