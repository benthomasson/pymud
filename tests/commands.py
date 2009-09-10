#!/usr/bin/env python

import unittest
from pymud.testfixture import RoomTestFixture
from pymud.persist import P

class TestCommands(RoomTestFixture):

    def setUp(self):
        RoomTestFixture.setUp(self)
        from pymud.mob import Mob
        self.createHere("mob",Mob)

    def testSay(self):
        self.mob.doCommand("say hi")
        self.assertEquals(len(self.messages),2)

    def testSet(self):
        self.mob.doCommand("set a 5")
        self.assertEquals(self.mob.variables['a'],'5')
        self.assertEquals(len(self.messages),1)

    def testLook(self):
        self.mob.doCommand("look")
        self.assertEquals(len(self.messages),1)

    def testLook2(self):
        self.mob.doCommand("look mob")
        self.assertEquals(len(self.messages),1)

    def testHelp(self):
        self.mob.doCommand("help")
        self.assertEquals(len(self.messages),1)

    def testHelp2(self):
        self.mob.doCommand("help commands")
        self.assertEquals(len(self.messages),1)

    def testCommands(self):
        self.mob.doCommand("commands")
        self.assertEquals(len(self.messages),1)

    def testGetDrop(self):
        from pymud.item import Item
        self.createHere('thingy',Item)
        self.assertEquals(self.thingy.location(),self.room)
        self.mob.doCommand("get thing")
        self.mob.doCommand("inventory")
        self.assertEquals(self.thingy.location(),self.mob)
        self.mob.doCommand("drop thing")
        self.assertEquals(self.thingy.location(),self.room)
        self.assertEquals(len(self.messages),1)

    def testGo(self):
        from pymud.room import Room
        self.create('home',Room)
        self.room.exits['home'] = P(self.home)
        self.assertEquals(self.mob.location(),self.room)
        self.mob.doCommand("go home")
        self.assertEquals(self.mob.location(),self.home)


if __name__ == "__main__":
    unittest.main()
