#!/usr/bin/env python

from pymud.mob import Mob
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
            self.scheduler = P.persist.get('scheduler')
        else:
            self.scheduler = Scheduler()
            self.scheduler.id = 'scheduler'
            print 'New Scheduler'
            P.persist.persist(self.scheduler)

        P.persist.syncAll()

        if P.persist.exists('mob'):
            mob = P.persist.get("mob")
        else:
            mob = Mob(stdout=None,stdin=None,id="mob")
            P.persist.persist(mob)
            self.scheduler.schedule(mob)

        cli.startCli(P(mob))
        self.server = telnetserver.startServer(self.scheduler)

    def run(self):
        try:
            while True:
                time.sleep(0.1)
                self.scheduler.run()
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

