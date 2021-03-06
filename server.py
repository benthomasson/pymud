#!/usr/bin/env python

from pymud.mob import Mob
from pymud.creator import Creator
from pymud.chat import ChatRoom
from pymud.scheduler import Scheduler
from pymud import cli
from pymud import telnetserver
from pymud import proxyserver
from pymud.persist import P, Persistence, getP, MockPersistence
from pymud.exceptions import *
from pymud.mobmarket import MobMarket
import sys
import time
import datetime
import traceback
import item
import room
import logging
import logging.handlers

errorLogger = logging.getLogger("pymud.error")

class Server(object):

    def __init__(self):
        pass

    def start(self):
        errorLogger.setLevel(logging.DEBUG)
        loghandler = logging.handlers.RotatingFileHandler("error.log",maxBytes=1000000,backupCount=0)
        errorLogger.addHandler(loghandler)
        P.persist = Persistence("server.db")
        Scheduler.scheduler = P.persist.getOrCreate('scheduler',Scheduler)
        MobMarket.market = P.persist.getOrCreate('market',MobMarket)
        self.creator = P.persist.getOrCreate("creator",Creator)
        chat = P.persist.getOrCreate("globalchat",ChatRoom,name="global")
        chat.addListener(self.creator)
        Scheduler.scheduler.schedule(self.creator)

        P.persist.syncAll()

        self.theCli = cli.startCli(getP(self.creator))
        self.telnetserver = telnetserver.startServer()
        self.proxyserver = proxyserver.startServer()

    def run(self):
        try:
            tick = time.time()
            while True:
                Scheduler.scheduler.run()
                tick = time.time()
                time.sleep(0.01)
                self.theCli.receiveMessages()
        except ShutdownSignal, e:
            print "Shutting down server"
        except BaseException, e:
            print e
            traceback.print_exception(*sys.exc_info())

    def close(self):
        print "Saving state"
        for instance in telnetserver.TelnetInterface.instances.copy():
            instance.finish()
        self.telnetserver.shutdown()
        P.persist.close()

class TestServer():

    def start(self):
        P.persist = None
        P.instances = {}
        Scheduler.scheduler = None
        MobMarket.market = None
        P.persist = MockPersistence()
        Scheduler.scheduler = P.persist.getOrCreate('scheduler',Scheduler)
        MobMarket.market = P.persist.getOrCreate('market',MobMarket)
        self.creator = P.persist.getOrCreate("creator",Creator)
        chat = P.persist.getOrCreate("globalchat",ChatRoom,name="global")
        chat.addListener(self.creator)
        Scheduler.scheduler.schedule(self.creator)

        P.persist.syncAll()

        #self.theCli = cli.startCli(getP(self.creator))

    def run(self,ticks):
        try:
            for i in xrange(ticks):
                Scheduler.scheduler.run()
                #time.sleep(0.01)
                #self.theCli.receiveMessages()
        except ShutdownSignal, e:
            print "Shutting down server"
        except BaseException, e:
            print e
            traceback.print_exception(*sys.exc_info())

    def close(self):
        P.persist.close()
        P.persist = None
        P.instances = {}
        Scheduler.scheduler = None
        MobMarket.market = None

if __name__ == "__main__":

    server = Server()

    server.start()
    server.run()
    server.close()

