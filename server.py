#!/usr/bin/env python

from pymud.mob import Mob
from pymud.creator import Creator
from pymud.scheduler import Scheduler
from pymud import cli
from pymud import telnetserver
from pymud.persist import P, Persistence
import time

class Server(object):

    def __init__(self):
        pass

    def start(self):
        P.persist = Persistence("server.db")
        if P.persist.exists('scheduler'):
            Scheduler.scheduler = P.persist.get('scheduler')
        else:
            Scheduler.scheduler = Scheduler()
            Scheduler.scheduler.id = 'scheduler'
            print 'New Scheduler'
            P.persist.persist(Scheduler.scheduler)

        P.persist.syncAll()

        if P.persist.exists('creator'):
            creator = P.persist.get("creator")
        else:
            creator = Creator(id="creator")
            P.persist.persist(creator)
            Scheduler.scheduler.schedule(creator)

        cli.startCli(P(creator))
        self.server = telnetserver.startServer()

    def run(self):
        try:
            while True:
                time.sleep(0.1)
                Scheduler.scheduler.run()
        except BaseException, e:
            print e

    def close(self):
        self.server.shutdown()
        P.persist.close()

if __name__ == "__main__":

    server = Server()

    server.start()
    server.run()
    server.close()

