#!/usr/bin/env python
import readline
import cmd
import sys, time, threading
from multiprocessing.connection import Client

class CliClient(cmd.Cmd):

    def __init__(self,address,id):
        self.id = id
        self.connection = Client(address, authkey='secret password')
        cmd.Cmd.__init__(self)

    def onecmd(self,line):
        self.connection.send(("creator",line))
        while self.connection.poll(0.1):
            print self.connection.recv()        
        

def startCli(address,m):
    cli = CliClient(address,m)
    server_thread = threading.Thread(target=cli.cmdloop)
    server_thread.setDaemon(True)
    server_thread.start()
    return cli

if __name__ == "__main__":
    address = ('localhost', 6000)
    cli = startCli(address,sys.argv[1])

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    except BaseException, e:
        print e
