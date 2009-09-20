#!/usr/bin/env python

import threading
import time
from multiprocessing.connection import Listener
from pymud.mob import Mob

class ApiHandler(object):

    def __init__(self,connection):
        self.connection = connection

    def handle(self):
        self.connection.send(Mob(id="mob"))
        self.connection.close()

class ApiServer(object):

    def __init__(self,address,handler):
        self.listener = Listener(address,authkey='secret password')
        self.handler = handler

    def serve_forever(self):
        while True:
            conn = self.listener.accept()
            print 'connection accepted from', self.listener.last_accepted
            self.handler(conn).handle()
            time.sleep(0.01)

    def close(self):
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
        server.close()

