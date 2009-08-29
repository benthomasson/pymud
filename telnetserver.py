#!/usr/bin/env python

import socket
import threading
import SocketServer

import pymud.checker as checker
import pymud.interpreter as interpreter
from pymud.coroutine import finish
from pymud.mob import Mob
import time

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

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()
    print "Server loop running in thread:", server_thread.getName()

    try:
        while True:
            time.sleep(1)
    except BaseException, e:
        pass
    server.shutdown()

