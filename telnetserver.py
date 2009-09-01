#!/usr/bin/env python

import socket
import threading
import SocketServer

import pymud.checker as checker
from pymud.persist import P, Persistence
from pymud.scheduler import Scheduler
from pymud.coroutine import finish
from pymud.mob import Mob
import time
from pymud.formatter import ColorTextFormatter

class TelnetInterface(SocketServer.BaseRequestHandler, ColorTextFormatter):

    scheduler = None

    def __init__(self,*args,**kwargs):
        self.id = "telnetui"
        SocketServer.BaseRequestHandler.__init__(self,*args,**kwargs)

    def prompt(self):
        return "%s>" % self.mob.id 

    def handle(self):
        self.socketFile = self.request.makefile('rw')
        if P.persist.exists("mob"):
            self.mob = P.persist.get("mob")
        else:
            self.mob = Mob(stdin=None,stdout=None,id="mob")
            P.persist.persist(self.mob)
        TelnetInterface.scheduler.schedule(self.mob)
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


def startServer(scheduler):
    TelnetInterface.scheduler = scheduler
    HOST, PORT = "localhost", 8000
    server = ThreadedTCPServer((HOST, PORT), TelnetInterface)
    ip, port = server.server_address
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()
    print "Server loop running at %s:%d:" % (ip,port)
    return server

if __name__ == "__main__":
    P.persist = Persistence("telnet_test.db")

    if P.persist.exists('scheduler'):
        scheduler = P.persist.get('scheduler')
    else:
        scheduler = Scheduler()
        scheduler.id = 'scheduler'
        print 'New Scheduler'
        P.persist.persist(scheduler)

    server = startServer(scheduler)

    try:
        while True:
            time.sleep(0.001)
            scheduler.run()
            P.persist.sync(1)
    except KeyboardInterrupt, e:
        pass
    server.shutdown()
    P.persist.close()

