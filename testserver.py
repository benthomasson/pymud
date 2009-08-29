#!/usr/bin/env python

from pymud.mob import Mob
from pymud.scheduler import Scheduler
import pymud.chainedmap
from pymud.persist import P, persist, Persistence

persist = Persistence("test.db")

scheduler = Scheduler()

for x in xrange(100):
    m = Mob()
    persist.persist(m)
    print m.id




