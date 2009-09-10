#!/usr/bin/env python

from pymud.mob import Mob
from pymud.creator import Creator
from pymud.chat import ChatRoom
from pymud.scheduler import Scheduler
from pymud import cli
from pymud import telnetserver
from pymud.persist import P, Persistence
from pymud.exceptions import *
from pymud.mobmarket import MobMarket
import sys
import time
import datetime
import traceback
import item
import room

class Server(object):

    def __init__(self):
        pass

    def start(self):
        P.persist = Persistence("server.db")
        Scheduler.scheduler = P.persist.getOrCreate('scheduler',Scheduler)
        MobMarket.market = P.persist.getOrCreate('market',MobMarket)
        creator = P.persist.getOrCreate("creator",Creator)
        chat = P.persist.getOrCreate("globalchat",ChatRoom,name="global")
        chat.addListener(creator)
        Scheduler.scheduler.schedule(creator)

        P.persist.syncAll()

        self.theCli = cli.startCli(P(creator))
        self.server = telnetserver.startServer()

    def run(self):
        try:
            tick = time.time()
            while True:
                if Scheduler.scheduler.run():
                    #print time.time() - tick
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
        self.server.shutdown()
        P.persist.close()

if __name__ == "__main__":

    server = Server()

    server.start()
    server.run()
    server.close()

