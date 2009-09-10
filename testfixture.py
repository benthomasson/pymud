#!/usr/bin/env python

from pymud.persist import P, Persistence
from pymud.scheduler import Scheduler
from pymud.formatter import ColorTextFormatter
import unittest
import os
import sys


class TestFixture(ColorTextFormatter,unittest.TestCase):

    def receiveMessage(self,message):
        sys.stdout.write(self.formatMessage(message))
        sys.stdout.write("\n")

    def setUp(self):
        if os.path.exists("test.db"): os.remove("test.db")
        if os.path.exists("test.db.db"): os.remove("test.db.db")
        P.persist = Persistence("test.db")
        Scheduler.scheduler = P.persist.getOrCreate('scheduler',Scheduler)
        P.persist.syncAll()
        self.persist = P.persist
        self.scheduler = Scheduler.scheduler
        self.id = 'test'


class RoomTestFixture(TestFixture):

    def setUp(self):
        from pymud.room import Room
        TestFixture.setUp(self)
        self.room = self.persist.getOrCreate('world',Room)

class TestTestFixture(RoomTestFixture):

    def test(self):
        from pymud.mob import Mob
        mob = self.persist.getOrCreate("mob",Mob)
        mob.location = P(self.room)
        self.assertEquals(mob.id,"mob")
        self.assertEquals(mob.location(),self.room)

if __name__ == "__main__":
    unittest.main()

