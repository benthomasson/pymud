#!/usr/bin/env python

from pymud.sim import Sim
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
        self.messages.append(message)

    def setUp(self):
        if os.path.exists("test.db"): os.remove("test.db")
        if os.path.exists("test.db.db"): os.remove("test.db.db")
        P.persist = Persistence("test.db")
        Scheduler.scheduler = P.persist.getOrCreate('scheduler',Scheduler)
        P.persist.syncAll()
        self.persist = P.persist
        self.scheduler = Scheduler.scheduler
        self.id = 'test'
        self.messages = []

class RoomTestFixture(TestFixture,Sim):

    def setUp(self):
        Sim.__init__(self)
        self.name = self.__class__.__name__
        from pymud.room import Room
        TestFixture.setUp(self)
        self.location = P.null
        self.room = self.persist.getOrCreate('world',Room)
        self.room.addListener(self)

    def create(self,id,klass,*args,**kwargs):
        o = self.persist.getOrCreate(id,klass,*args,**kwargs)
        self.__dict__[id] = o
        if hasattr(o,'addListener'):
            o.addListener(self)
        return o

    def createHere(self,id,klass,*args,**kwargs):
        o = self.persist.getOrCreate(id,klass,*args,**kwargs)
        self.room.add(o)
        self.__dict__[id] = o
        if hasattr(o,'addListener'):
            o.addListener(self)
        return o

class TestTestFixture(RoomTestFixture):

    def test(self):
        from pymud.mob import Mob
        mob = self.createHere("mob",Mob)
        self.assertEquals(mob.id,"mob")
        self.assertEquals(mob.location(),self.room)
        mob.doCommand("say hi\n")
        self.assertEquals(len(self.messages),2)

if __name__ == "__main__":
    unittest.main()

