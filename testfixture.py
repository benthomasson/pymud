#!/usr/bin/env python

from pymud.persist import P, Persistence
from pymud.scheduler import Scheduler
import unittest
import os


class TestFixture(unittest.TestCase):

    def setUp(self):
        if os.path.exists("test.db"): os.remove("test.db")
        if os.path.exists("test.db.db"): os.remove("test.db.db")
        P.persist = Persistence("test.db")
        Scheduler.scheduler = P.persist.getOrCreate('scheduler',Scheduler)
        P.persist.syncAll()
        self.persist = P.persist
        self.scheduler = Scheduler.scheduler


class TestTestFixture(TestFixture):

    def test(self):
        from pymud.mob import Mob
        mob = self.persist.getOrCreate("mob",Mob)
        self.assertEquals(mob.id,"mob")

if __name__ == "__main__":
    unittest.main()

