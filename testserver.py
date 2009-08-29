#!/usr/bin/env python

from pymud.mob import Mob
from pymud.scheduler import Scheduler
import pymud.chainedmap
from pymud.persist import P, Persistence
import time

P.persist = Persistence("test.db")
print P.persist.id

if P.persist.exists('scheduler'):
    scheduler = P.persist.get('scheduler')
else:
    scheduler = Scheduler()
    scheduler.id = 'scheduler'
    print 'New Scheduler'
    P.persist.persist(scheduler)

P.persist.sync(100)

print scheduler.id

for x in xrange(100):
    m = Mob()
    P.persist.persist(m)
    print m.id
    scheduler.schedule(m)

for x in xrange(100):
    scheduler.run()

try:
    while True:
        scheduler.run()
        time.sleep(0.000000001)
except KeyboardInterrupt, e:
    pass

P.persist.sync(100)

P.persist.close()

