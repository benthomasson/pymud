#!/usr/bin/env python

import threading
import time
from multiprocessing.connection import Listener
from pymud.mob import Mob
from pymud.formatter import ColorTextFormatter
from pymud.persist import P

class ApiHandler(ColorTextFormatter,object):

    number = 0

    def __init__(self,connection):
        self.connection = connection
        self.mobs = {}
        self.id = "apihandler" + str(ApiHandler.number)
        ApiHandler.number += 1
        self.messages = []

    def handle(self):
        try:
            while True:
                if self.connection.poll():
                    id, command = self.connection.recv()
                    print id,command
                    if id not in self.mobs:
                        self.mobs[id] = P.persist.get(id)
                        self.mobs[id].addListener(self)
                    if command:
                        self.mobs[id].appendCommand(command + "\n")
                self.receiveMessages()
                time.sleep(0.01)
        except Exception,e:
            print str(e)
        finally:
            self.finish()

    def finish(self):
        self.connection.close()
        print "finished"

    def receiveMessage(self,message):
        print "Recieved message: ", message.type
        self.messages.append(message)

    def receiveMessages(self):
        if not self.messages: return
        for message in self.messages:
            print "Sending message: ", message.type
            self.connection.send(self.formatMessage(message))
        self.messages = []

class ApiServer(object):

    def __init__(self,address,handler):
        self.listener = Listener(address,authkey='secret password')
        self.handler = handler
        self.done = False

    def serve_forever(self):
        while not self.done:
            conn = self.listener.accept()
            print 'connection accepted from', self.listener.last_accepted
            handler = self.handler(conn)
            handler_thread = threading.Thread(target=handler.handle)
            handler_thread.start()

    def shutdown(self):
        self.done = True
        self.listener.close()

def startServer():
    HOST, PORT = "", 6000
    server = ApiServer((HOST,PORT),ApiHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()
    print "Server loop running"
    return server

if __name__ == '__main__':
    try:
        server = startServer()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.shutdown()

