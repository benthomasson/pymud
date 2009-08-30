#!/usr/bin/env python

import socket
import threading
import SocketServer

import pymud.checker as checker
from pymud.scheduler import Scheduler
from pymud.coroutine import finish
from pymud.mob import Mob
import time
from pymud.formatter import ColorTextFormatter


class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler, ColorTextFormatter):

    def __init__(self,*args,**kwargs):
        self.id = "telnetui"
        SocketServer.BaseRequestHandler.__init__(self,*args,**kwargs)

    def prompt(self):
        return ">>>"

    def handle(self):
        global scheduler
        self.socketFile = self.request.makefile('rw')
        self.mob = Mob(stdin=None,stdout=None)
        scheduler.schedule(self.mob)
        self.mob.addListener(self)
        self.socketFile.write(self.prompt())
        self.socketFile.flush()
        try:
            while True:
                command = self.socketFile.readline()
                if not command: break
                self.onecmd(command.strip())
                self.socketFile.flush()
        except BaseException, e:
            print str(e)

    def onecmd(self,line):
        try:
            if line:
                print "Command<>%s<>" % line
                self.mob.commandQueue.append(line + "\n")
            self.socketFile.write("\n")
            self.socketFile.write(self.prompt())
            self.socketFile.flush()
        except Exception,e:
            print str(e)

    def receiveMessage(self,message):
        self.socketFile.write("\n")
        self.socketFile.write(self.formatMessage(message))
        self.socketFile.write("\n")
        self.socketFile.write(self.prompt())
        self.socketFile.flush()

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


if __name__ == "__main__":
    HOST, PORT = "localhost", 8000

    global scheduler
    scheduler = Scheduler()
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ip, port = server.server_address

    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()
    print "Server loop running in thread:", server_thread.getName()

    try:
        while True:
            time.sleep(0.001)
            scheduler.run()
    except KeyboardInterrupt, e:
        pass
    server.shutdown()

