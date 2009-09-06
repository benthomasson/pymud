
import socket
import threading
import SocketServer
import time
import socket

import pymud.checker as checker
from pymud.persist import P, Persistence
from pymud.scheduler import Scheduler
from pymud.coroutine import finish
from pymud.mob import Mob
from pymud.formatter import ColorTextFormatter
from pymud.mobmarket import MobMarket
from pymud.message import Message

class TelnetInterface(SocketServer.BaseRequestHandler, ColorTextFormatter):

    instances = {}

    def __init__(self,*args,**kwargs):
        self.id = "telnetui"
        TelnetInterface.instances[self] = 1
        self.line = ""
        self.done = False
        self.messages = []
        SocketServer.BaseRequestHandler.__init__(self,*args,**kwargs)

    def prompt(self):
        if self.mob and self.mob():
            return "%s>" % self.mob.id 
        else:
            return "XXX"

    def handle(self):
        self.request.setblocking(0)
        self.socketFile = self.request.makefile('rw')
        self.mob = MobMarket.market.getNext()
        self.line = ""
        if not self.mob:
            self.receiveMessage(Message("notice",notice=\
                "There are no available mobs to play right now. Try again later."))
            self.socketFile.flush()
            return
        self.mob().addListener(self)
        self.mob().interface = self
        self.socketFile.write(self.prompt())
        self.socketFile.flush()
        try:
            while not self.done:
                if not self.mob or not self.mob():
                    break
                while not self.done:
                    try:
                        self.receiveMessages()
                        if not self.mob or not self.mob():
                            self.done = True
                            break
                        read = self.socketFile.read(1)
                        if len(read) == 0:
                            self.done = True
                            break
                        self.line += read
                        if "\n" in self.line:
                            command,newline,self.line = self.line.partition("\n")
                            break
                    except socket.error, error:
                        time.sleep(0.01)
                        if error[0] == 35:
                            pass
                        else:
                            print error[0]
                            self.done = True
                            break
                if self.done: break
                if None == command: break
                self.onecmd(command.strip())
                self.socketFile.flush()
                if not self.mob or not self.mob():
                    self.receiveMessage(Message("notice",notice="Goodbye"))
                    break
        except BaseException, e:
            print e.__class__, str(e)
        self.socketFile.flush()

    def quit(self):
        if self.mob and self.mob():
            self.mob().removeListener(self)
            MobMarket.market.add(self.mob())
            self.mob = None

    def finish(self):
        self.receiveMessages()
        self.quit()
        del TelnetInterface.instances[self]
        self.socketFile.close()

    def onecmd(self,line):
        try:
            if line:
                self.mob().commandQueue.append(line + "\n")
            self.socketFile.write("\n")
            self.socketFile.write(self.prompt())
            self.socketFile.flush()
        except Exception,e:
            print str(e)

    def receiveMessage(self,message):
        self.messages.append(message)

    def receiveMessages(self):
        if not self.messages: return
        for message in self.messages:
            self.socketFile.write("\n")
            self.socketFile.write(self.formatMessage(message))
        self.socketFile.write("\n")
        self.socketFile.write(self.prompt())
        self.socketFile.flush()
        self.messages = []

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

