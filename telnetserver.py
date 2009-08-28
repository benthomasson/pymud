#!/usr/bin/env python

import socket
import threading
import SocketServer

import checker
import interpreter
from coroutine import finish
from mob import Mob

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):

    def prompt(self):
        return ">>>"

    def handle(self):
        socketFile = self.request.makefile('rw')
        self.mob = Mob(stdin=socketFile,stdout=socketFile)
        try:
            while True:
                socketFile.write(self.prompt())
                socketFile.flush()
                command = socketFile.readline()
                if not command: break
                self.onecmd(command.strip())
                socketFile.flush()
        except BaseException, e:
            print str(e)

    def onecmd(self,line):
        try:
            print "Command<>%s<>" % line
            checker.check(line + "\n",self.mob.commands,self.mob.variables)
            finish(interpreter.interpret(line + "\n",
                                            self.mob,))
        except Exception,e:
            print str(e)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = "localhost", 8000

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.setDaemon(True)
    server_thread.start()
    print "Server loop running in thread:", server_thread.getName()

    try:
        server.serve_forever()
    except BaseException, e:
        pass
    server.shutdown()

