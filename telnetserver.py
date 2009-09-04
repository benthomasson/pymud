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
from pymud.mobmarket import MobMarket
from pymud.message import Message

class TelnetInterface(SocketServer.BaseRequestHandler, ColorTextFormatter):

    instances = {}

    def __init__(self,*args,**kwargs):
        self.id = "telnetui"
        TelnetInterface.instances[self] = 1
        SocketServer.BaseRequestHandler.__init__(self,*args,**kwargs)

    def prompt(self):
        if self.mob():
            return "%s>" % self.mob.id 
        else:
            return ""

    def handle(self):
        self.socketFile = self.request.makefile('rw')
        self.mob = MobMarket.market.getNext()
        if not self.mob():
            self.receiveMessage(Message("notice",notice=\
                "There are no available mobs to play right now. Try again later."))
            self.socketFile.flush()
            return
        self.mob().addListener(self)
        self.socketFile.write(self.prompt())
        self.socketFile.flush()
        try:
            while True:
                command = self.socketFile.readline()
                if None == command: break
                self.onecmd(command.strip())
                self.socketFile.flush()
        except BaseException, e:
            print str(e)

    def finish(self):
        if self.mob():
            self.mob().removeListener(self)
            MobMarket.market.add(self.mob())
            self.mob = P()
        del TelnetInterface.instances[self]

    def onecmd(self,line):
        try:
            if line:
                print "Command<>%s<>" % line
                self.mob().commandQueue.append(line + "\n")
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


def startServer():
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
        Scheduler.scheduler = P.persist.get('scheduler')
    else:
        Scheduler.scheduler = Scheduler()
        Scheduler.scheduler.id = 'scheduler'
        print 'New Scheduler'
        P.persist.persist(Scheduler.scheduler)

    server = startServer()

    try:
        while True:
            time.sleep(0.001)
            Scheduler.scheduler.run()
            P.persist.sync(1)
    except KeyboardInterrupt, e:
        pass
    server.shutdown()
    P.persist.close()

