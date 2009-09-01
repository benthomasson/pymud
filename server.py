#!/usr/bin/env python

from pymud.mob import Mob
from pymud.scheduler import Scheduler
from pymud import cli
from pymud import telnetserver
from pymud.persist import P, Persistence
import time


if __name__ == "__main__":
    P.persist = Persistence("server.db")
    if P.persist.exists('scheduler'):
        scheduler = P.persist.get('scheduler')
    else:
        scheduler = Scheduler()
        scheduler.id = 'scheduler'
        print 'New Scheduler'
        P.persist.persist(scheduler)

    P.persist.syncAll()

    if P.persist.exists('mob'):
        mob = P.persist.get("mob")
    else:
        mob = Mob(stdout=None,stdin=None,id="mob")
        P.persist.persist(mob)
        scheduler.schedule(mob)

    cli.startCli(P(mob))
    server = telnetserver.startServer(scheduler)

    try:
        while True:
            time.sleep(0.1)
            scheduler.run()
    except BaseException, e:
        print e

    server.shutdown()
    P.persist.close()
