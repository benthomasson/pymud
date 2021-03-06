#!/usr/bin/env python

from pymud.sim import Sim
from pymud.persist import P, Persistence, MockPersistence
from pymud.scheduler import Scheduler
from pymud.mobmarket import MobMarket
from pymud.formatter import ColorTextFormatter
import unittest
import os
import sys
from pymud import builder

class TestInterface(ColorTextFormatter):

    def start(self):
        self.id = 'test'
        self.messages = []
        self.listeningTo = []

    def listenTo(self,o):
        if hasattr(o,'addListener'):
            self.listeningTo.append(o)
            o.addListener(self)

    def receiveMessage(self,message):
        sys.stdout.write(self.formatMessage(message))
        sys.stdout.write("\n")
        sys.stdout.flush()
        self.messages.append(message)
    
    def close(self):
        for o in self.listeningTo:
            o.removeListener(self)

class TestFixture(TestInterface,unittest.TestCase):

    def setUp(self):
        if os.path.exists("test.db"): os.remove("test.db")
        if os.path.exists("test.db.db"): os.remove("test.db.db")
        P.persist = MockPersistence()
        P.instances = {}
        Scheduler.scheduler = P.persist.getOrCreate('scheduler',Scheduler)
        MobMarket.market = MobMarket()
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
        self.room = builder.create(Room,'world')
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

class ZoneTestFixture(TestFixture,Sim):

    def setUp(self):
        from pymud.room import Room
        Sim.__init__(self)
        self.name = self.__class__.__name__
        from pymud.room import Zone
        TestFixture.setUp(self)
        self.location = P.null
        self.zone = builder.add2dZone(3,3,Room).zone()
        for x in self.zone.rooms.values():
            x().addListener(self)
        self.room = self.zone.rooms[1,1,0]()

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

